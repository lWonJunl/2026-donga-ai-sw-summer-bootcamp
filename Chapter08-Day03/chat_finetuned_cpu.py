"""Interactive CPU chat with the locally fine-tuned Qwen model."""

import argparse
import csv
import os
import re
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chat with the fine-tuned model on CPU")
    parser.add_argument(
        "--model-dir", type=Path, default=Path("outputs/python_basics_knowledge_model")
    )
    parser.add_argument(
        "--knowledge-file", type=Path, default=Path("data/python_basics_knowledge.csv")
    )
    parser.add_argument("--question", help="Ask one question and exit")
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument(
        "--cpu-threads", type=int, default=max(1, min(4, os.cpu_count() or 1))
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    root = Path(__file__).resolve().parent
    if not args.model_dir.is_absolute():
        args.model_dir = root / args.model_dir
    if not args.knowledge_file.is_absolute():
        args.knowledge_file = root / args.knowledge_file
    if not args.model_dir.is_dir():
        raise FileNotFoundError(f"Fine-tuned model was not found: {args.model_dir}")
    if not args.knowledge_file.is_file():
        raise FileNotFoundError(f"Knowledge CSV was not found: {args.knowledge_file}")
    if args.max_new_tokens < 1 or args.cpu_threads < 1:
        raise ValueError("max-new-tokens and cpu-threads must be positive.")

    torch.set_num_threads(args.cpu_threads)
    torch.set_num_interop_threads(1)
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_dir, local_files_only=True, trust_remote_code=False
    )
    model = AutoModelForCausalLM.from_pretrained(
        args.model_dir,
        dtype=torch.float32,
        local_files_only=True,
        low_cpu_mem_usage=True,
        trust_remote_code=False,
        use_safetensors=True,
    )
    model.eval()

    with args.knowledge_file.open("r", encoding="utf-8-sig", newline="") as handle:
        knowledge_rows = list(csv.DictReader(handle))

    def search_knowledge(question: str) -> dict[str, str] | None:
        normalized_question = question.lower().replace(" ", "")
        stop_terms = {"파이썬", "기초", "문법", "함수", "자료형", "사용", "방법"}
        best_row: dict[str, str] | None = None
        best_score = 0
        for row in knowledge_rows:
            concept = row.get("concept", "").lower()
            terms = re.findall(r"[0-9a-zA-Z_+*]+|[가-힣]+", concept)
            expanded_terms: set[str] = set()
            for term in terms:
                for part in re.split(r"[과와]", term):
                    stripped = re.sub(r"(으로|에서|에게|의|은|는|이|가|을|를)$", "", part)
                    if len(stripped) >= 2 and stripped not in stop_terms:
                        expanded_terms.add(stripped)
            score = sum(len(term) for term in expanded_terms if term in normalized_question)
            if score > best_score:
                best_score = score
                best_row = row
        return best_row if best_score > 0 else None

    def generate_answer(question: str) -> str:
        knowledge = search_knowledge(question)
        if knowledge:
            return knowledge["content"]
        messages = [
            {
                "role": "system",
                "content": (
                    "당신은 한국어로 답하는 파이썬 기초 튜터입니다. "
                    "질문에 핵심 설명과 짧은 예제를 제공하세요."
                ),
            },
            {"role": "user", "content": question},
        ]
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                repetition_penalty=1.15,
                no_repeat_ngram_size=4,
                pad_token_id=tokenizer.eos_token_id,
            )
        answer_tokens = outputs[0, inputs["input_ids"].shape[1] :]
        return tokenizer.decode(answer_tokens, skip_special_tokens=True).strip()

    if args.question:
        print("답변>", generate_answer(args.question.strip()))
        return

    print("파이썬 기초 모델입니다. 종료하려면 '종료'를 입력하세요.")
    while True:
        try:
            question = input("\n질문> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break
        if question.lower() in {"exit", "quit", "종료"}:
            print("종료합니다.")
            break
        if not question:
            continue
        print("답변>", generate_answer(question))


if __name__ == "__main__":
    main()
