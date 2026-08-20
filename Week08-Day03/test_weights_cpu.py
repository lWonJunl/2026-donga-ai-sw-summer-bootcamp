"""Load a base model or a saved LoRA adapter on CPU and generate one answer."""
import argparse
import os
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

DEFAULT_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"


def main() -> None:
    p = argparse.ArgumentParser(description="CPU weight / LoRA adapter smoke test")
    p.add_argument("--model-id", default=DEFAULT_MODEL_ID, help="Base model ID/path, or a saved adapter directory")
    p.add_argument("--base-model-id", default=DEFAULT_MODEL_ID, help="Reviewed base model ID or a trusted local model folder")
    p.add_argument("--allow-remote-model", action="store_true", help="Allow a remote base model other than the reviewed default")
    p.add_argument("--prompt", default="CPU 모드에서 LoRA 학습의 장점을 한 문장으로 설명해 주세요.")
    p.add_argument("--max-new-tokens", type=int, default=96)
    p.add_argument("--cpu-threads", type=int, default=max(1, min(8, os.cpu_count() or 1)))
    args = p.parse_args()
    torch.set_num_threads(args.cpu_threads)
    torch.set_num_interop_threads(1)
    model_path = Path(args.model_id)
    adapter_config = model_path / "adapter_config.json"
    is_adapter = adapter_config.is_file()
    if is_adapter:
        base_model_id = args.base_model_id
        print(f"Loading adapter: {args.model_id}\nBase model: {base_model_id}")
    else:
        base_model_id = args.model_id
        print(f"Loading base model: {base_model_id}")
    if base_model_id != DEFAULT_MODEL_ID and not Path(base_model_id).is_dir() and not args.allow_remote_model:
        raise ValueError("Only the reviewed default remote model is allowed. Use a local folder or pass --allow-remote-model after verifying its source.")
    tokenizer = AutoTokenizer.from_pretrained(base_model_id, use_fast=True, trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        dtype=torch.float32,
        low_cpu_mem_usage=True,
        trust_remote_code=False,
        use_safetensors=True,
    )
    if is_adapter:
        model = PeftModel.from_pretrained(model, args.model_id)
    model.eval()
    messages = [{"role": "user", "content": args.prompt}]
    if getattr(tokenizer, "chat_template", None):
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        text = f"### Instruction:\n{args.prompt}\n\n### Response:\n"
    inputs = tokenizer(text, return_tensors="pt")
    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False, pad_token_id=tokenizer.pad_token_id, eos_token_id=tokenizer.eos_token_id)
    answer = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
    print("\nPrompt:", args.prompt)
    print("Answer:", answer)


if __name__ == "__main__":
    main()
