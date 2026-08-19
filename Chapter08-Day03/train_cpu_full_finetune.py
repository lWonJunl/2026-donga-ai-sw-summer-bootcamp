"""Fully fine-tune Qwen2.5-0.5B on a Python basics knowledge CSV.

The CSV contains facts and examples, not generated question-answer pairs.
Generic training prompts are built from each concept only in memory. Every model
parameter is updated on CPU and the result is saved as a full model.
"""

import argparse
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import Adafactor, AutoModelForCausalLM, AutoTokenizer


DEFAULT_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CPU-only full fine-tuning from a Python basics knowledge CSV"
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument(
        "--allow-remote-model",
        action="store_true",
        help="Allow a remote model other than the reviewed default",
    )
    parser.add_argument(
        "--train-file", type=Path, default=Path("data/python_basics_knowledge.csv")
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("outputs/python_basics_knowledge_model")
    )
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--max-length", type=int, default=160)
    parser.add_argument(
        "--max-steps",
        type=int,
        help="Stop after this many optimizer steps; useful for a smoke test",
    )
    parser.add_argument(
        "--cpu-threads", type=int, default=max(1, min(4, os.cpu_count() or 1))
    )
    parser.add_argument("--seed", type=int, default=42)
    return parser


def training_prompts(concept: str) -> tuple[str, str]:
    return (
        f"파이썬의 {concept}에 대해 설명해 주세요.",
        f"파이썬에서 {concept}은 무엇인가요?",
    )


class KnowledgeDataset(Dataset):
    REQUIRED_COLUMNS = {"id", "category", "concept", "content", "source_url"}

    def __init__(self, path: Path, tokenizer: Any, max_length: int):
        if not path.is_file():
            raise FileNotFoundError(f"Training data was not found: {path}")

        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = self.REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")
            rows = list(reader)

        self.examples: list[dict[str, list[int]]] = []
        for row_number, row in enumerate(rows, start=2):
            if not all(row.get(column, "").strip() for column in self.REQUIRED_COLUMNS):
                raise ValueError(f"CSV row {row_number} contains an empty required value.")
            for prompt in training_prompts(row["concept"]):
                messages = [
                    {
                        "role": "system",
                        "content": "당신은 한국어로 답하는 파이썬 기초 튜터입니다.",
                    },
                    {"role": "user", "content": prompt},
                ]
                prompt_text = tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
                answer_ids = tokenizer(
                    row["content"], add_special_tokens=False
                )["input_ids"] + [tokenizer.eos_token_id]
                input_ids = (prompt_ids + answer_ids)[:max_length]
                labels = ([-100] * len(prompt_ids) + answer_ids)[:max_length]
                if any(label != -100 for label in labels):
                    self.examples.append({"input_ids": input_ids, "labels": labels})

        if not self.examples:
            raise ValueError("The training CSV contains no usable rows.")

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, index: int) -> dict[str, list[int]]:
        return self.examples[index]


def collate(rows: list[dict[str, list[int]]], pad_id: int) -> dict[str, torch.Tensor]:
    width = max(len(row["input_ids"]) for row in rows)
    input_ids, labels, masks = [], [], []
    for row in rows:
        pad = width - len(row["input_ids"])
        input_ids.append(row["input_ids"] + [pad_id] * pad)
        labels.append(row["labels"] + [-100] * pad)
        masks.append([1] * len(row["input_ids"]) + [0] * pad)
    return {
        "input_ids": torch.tensor(input_ids),
        "labels": torch.tensor(labels),
        "attention_mask": torch.tensor(masks),
    }


def main() -> None:
    args = build_parser().parse_args()
    root = Path(__file__).resolve().parent
    if not args.train_file.is_absolute():
        args.train_file = root / args.train_file
    if not args.output_dir.is_absolute():
        args.output_dir = root / args.output_dir

    positive_values = (
        args.epochs,
        args.batch_size,
        args.gradient_accumulation,
        args.max_length,
        args.cpu_threads,
    )
    if min(positive_values) < 1:
        raise ValueError("Epochs, batch size, accumulation, length, and threads must be positive.")
    if args.max_length < 2:
        raise ValueError("max-length must be at least 2.")
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {args.output_dir}")
    if (
        args.model_id != DEFAULT_MODEL_ID
        and not Path(args.model_id).is_dir()
        and not args.allow_remote_model
    ):
        raise ValueError(
            "Only the reviewed default remote model is allowed. Verify another source "
            "before passing --allow-remote-model."
        )

    torch.manual_seed(args.seed)
    torch.set_num_threads(args.cpu_threads)
    torch.set_num_interop_threads(1)
    print(f"Full CPU fine-tuning with {torch.get_num_threads()} threads")
    print(f"Knowledge CSV: {args.train_file.resolve()}")

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_id, use_fast=True, trust_remote_code=False
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        dtype=torch.float32,
        low_cpu_mem_usage=True,
        trust_remote_code=False,
        use_safetensors=True,
    )
    model.config.use_cache = False
    total_parameters = sum(parameter.numel() for parameter in model.parameters())
    dataset = KnowledgeDataset(args.train_file, tokenizer, args.max_length)
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=lambda rows: collate(rows, tokenizer.pad_token_id),
    )
    optimizer = Adafactor(
        model.parameters(),
        lr=args.learning_rate,
        scale_parameter=False,
        relative_step=False,
        warmup_init=False,
        clip_threshold=1.0,
    )

    model.train()
    optimizer.zero_grad(set_to_none=True)
    epoch_metrics: list[dict[str, float | int]] = []
    global_step = 0
    stop = False
    for epoch in range(1, args.epochs + 1):
        loss_sum = 0.0
        batches = 0
        for batch_index, batch in enumerate(loader, start=1):
            loss = model(**batch).loss / args.gradient_accumulation
            loss.backward()
            loss_sum += loss.item() * args.gradient_accumulation
            batches += 1
            if batch_index % args.gradient_accumulation == 0 or batch_index == len(loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
                global_step += 1
                if args.max_steps and global_step >= args.max_steps:
                    stop = True
                    break
        mean_loss = loss_sum / batches
        epoch_metrics.append(
            {
                "epoch": epoch,
                "mean_loss": round(mean_loss, 6),
                "optimizer_steps": global_step,
            }
        )
        print(
            f"epoch={epoch}/{args.epochs} mean_loss={mean_loss:.4f} "
            f"optimizer_steps={global_step}"
        )
        if stop:
            break

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.output_dir, safe_serialization=True)
    tokenizer.save_pretrained(args.output_dir)
    summary = {
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
        "domain": "python_basics",
        "dataset_format": "knowledge_csv_without_stored_questions",
        "training_method": "full_parameter_supervised_fine_tuning",
        "device": "cpu",
        "model_id": args.model_id,
        "training_examples": len(dataset),
        "trainable_parameters": total_parameters,
        "total_parameters": total_parameters,
        "trainable_parameter_ratio_percent": 100.0,
        "optimizer": "Adafactor",
        "settings": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "gradient_accumulation": args.gradient_accumulation,
            "learning_rate": args.learning_rate,
            "max_length": args.max_length,
            "cpu_threads": args.cpu_threads,
            "max_steps": args.max_steps,
        },
        "epoch_metrics": epoch_metrics,
    }
    result_path = args.output_dir / "training_results.json"
    result_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Saved full fine-tuned model to: {args.output_dir.resolve()}")
    print(f"Saved training results to: {result_path.resolve()}")


if __name__ == "__main__":
    main()
