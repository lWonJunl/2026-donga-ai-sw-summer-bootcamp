"""CPU-only LoRA SFT for a small Hugging Face causal language model.

Input JSONL: each row must contain {"prompt": "...", "response": "..."}.
"""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from peft import LoraConfig, TaskType, get_peft_model
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, get_linear_schedule_with_warmup


DEFAULT_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"  # Replace with a local model folder if desired.


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="CPU-only LoRA fine-tuning")
    p.add_argument("--model-id", default=DEFAULT_MODEL_ID, help="Hugging Face repository ID or local weight directory")
    p.add_argument("--allow-remote-model", action="store_true", help="Allow a remote model other than the reviewed default")
    p.add_argument("--train-file", type=Path, default=Path("data/sample_train.jsonl"))
    p.add_argument("--output-dir", type=Path, default=Path("outputs/qwen2_5_0_5b_lora"))
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch-size", type=int, default=1, help="Keep at 1 on CPU")
    p.add_argument("--gradient-accumulation", type=int, default=8)
    p.add_argument("--learning-rate", type=float, default=2e-4)
    p.add_argument("--max-length", type=int, default=256)
    p.add_argument("--lora-r", type=int, default=8)
    p.add_argument("--lora-alpha", type=int, default=16)
    p.add_argument("--lora-dropout", type=float, default=0.05)
    p.add_argument("--cpu-threads", type=int, default=max(1, min(8, os.cpu_count() or 1)))
    p.add_argument("--seed", type=int, default=42)
    return p


def build_prompt(tokenizer: Any, prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]
    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return f"### Instruction:\n{prompt}\n\n### Response:\n"


class PromptResponseDataset(Dataset):
    def __init__(self, path: Path, tokenizer: Any, max_length: int):
        if not path.is_file():
            raise FileNotFoundError(f"Training data was not found: {path}")
        self.items = []
        for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not raw.strip():
                continue
            row = json.loads(raw)
            if not isinstance(row.get("prompt"), str) or not isinstance(row.get("response"), str):
                raise ValueError(f"Line {number} must contain string prompt and response fields.")
            prompt_ids = tokenizer(build_prompt(tokenizer, row["prompt"]), add_special_tokens=False)["input_ids"]
            answer_ids = tokenizer(row["response"], add_special_tokens=False)["input_ids"] + [tokenizer.eos_token_id]
            input_ids = (prompt_ids + answer_ids)[:max_length]
            labels = ([-100] * len(prompt_ids) + answer_ids)[:max_length]
            if any(label != -100 for label in labels):
                self.items.append({"input_ids": input_ids, "labels": labels})
        if not self.items:
            raise ValueError("No usable training rows remain after tokenization.")

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, list[int]]:
        return self.items[index]


def collate(batch: list[dict[str, list[int]]], pad_id: int) -> dict[str, torch.Tensor]:
    width = max(len(row["input_ids"]) for row in batch)
    input_ids, labels, attention = [], [], []
    for row in batch:
        padding = width - len(row["input_ids"])
        input_ids.append(row["input_ids"] + [pad_id] * padding)
        labels.append(row["labels"] + [-100] * padding)
        attention.append([1] * len(row["input_ids"]) + [0] * padding)
    return {"input_ids": torch.tensor(input_ids), "labels": torch.tensor(labels), "attention_mask": torch.tensor(attention)}


def lora_targets(model: torch.nn.Module) -> list[str]:
    candidates = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    names = {name.rsplit(".", 1)[-1] for name, _ in model.named_modules()}
    targets = [name for name in candidates if name in names]
    if not targets:
        raise ValueError("Could not find LLaMA-style projection modules. Inspect model.named_modules() and set target modules.")
    return targets


def main() -> None:
    args = parser().parse_args()
    project_root = Path(__file__).resolve().parent
    if not args.train_file.is_absolute():
        args.train_file = project_root / args.train_file
    if not args.output_dir.is_absolute():
        args.output_dir = project_root / args.output_dir
    if args.epochs < 1 or args.batch_size < 1 or args.gradient_accumulation < 1:
        raise ValueError("epochs, batch-size, and gradient-accumulation must be positive.")
    if args.model_id != DEFAULT_MODEL_ID and not Path(args.model_id).is_dir() and not args.allow_remote_model:
        raise ValueError("Only the reviewed default remote model is allowed. Use a local folder or pass --allow-remote-model after verifying its source.")
    torch.manual_seed(args.seed)
    torch.set_num_threads(args.cpu_threads)
    torch.set_num_interop_threads(1)
    print(f"Device: cpu | PyTorch threads: {torch.get_num_threads()}")
    print(f"Loading base model: {args.model_id}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, use_fast=True, trust_remote_code=False)
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
    targets = lora_targets(model)
    model = get_peft_model(model, LoraConfig(
        task_type=TaskType.CAUSAL_LM, r=args.lora_r, lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout, bias="none", target_modules=targets,
    ))
    trainable_params = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    total_params = sum(parameter.numel() for parameter in model.parameters())
    model.print_trainable_parameters()
    dataset = PromptResponseDataset(args.train_file, tokenizer, args.max_length)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, collate_fn=lambda x: collate(x, tokenizer.pad_token_id))
    steps_per_epoch = (len(loader) + args.gradient_accumulation - 1) // args.gradient_accumulation
    total_steps = steps_per_epoch * args.epochs
    optimizer = AdamW((p for p in model.parameters() if p.requires_grad), lr=args.learning_rate)
    scheduler = get_linear_schedule_with_warmup(optimizer, 0, total_steps)
    model.train()
    optimizer.zero_grad(set_to_none=True)
    epoch_metrics = []
    for epoch in range(1, args.epochs + 1):
        loss_sum = 0.0
        for step, batch in enumerate(loader, start=1):
            result = model(**batch)
            loss = result.loss / args.gradient_accumulation
            loss.backward()
            loss_sum += result.loss.item()
            if step % args.gradient_accumulation == 0 or step == len(loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
        mean_loss = loss_sum / len(loader)
        epoch_metrics.append({"epoch": epoch, "mean_loss": round(mean_loss, 6)})
        print(f"epoch={epoch}/{args.epochs} mean_loss={mean_loss:.4f}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.output_dir, safe_serialization=True)
    tokenizer.save_pretrained(args.output_dir)
    public_config = vars(args).copy()
    public_config["train_file"] = str(Path(args.train_file).name)
    public_config["output_dir"] = str(Path(args.output_dir).name)
    (args.output_dir / "training_config.json").write_text(json.dumps(public_config, default=str, ensure_ascii=False, indent=2), encoding="utf-8")
    result = {
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
        "device": "cpu",
        "model_id": args.model_id,
        "training_examples": len(dataset),
        "trainable_parameters": trainable_params,
        "total_parameters": total_params,
        "trainable_parameter_ratio_percent": round(trainable_params / total_params * 100, 4),
        "settings": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "gradient_accumulation": args.gradient_accumulation,
            "learning_rate": args.learning_rate,
            "max_length": args.max_length,
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
            "cpu_threads": args.cpu_threads,
        },
        "epoch_metrics": epoch_metrics,
    }
    (args.output_dir / "training_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved LoRA adapter and tokenizer to: {args.output_dir.resolve()}")
    print(f"Saved training results to: {(args.output_dir / 'training_results.json').resolve()}")


if __name__ == "__main__":
    main()
