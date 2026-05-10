#!/usr/bin/env python3
"""Modal LoRA fine-tuning — train custom models on GPU.

Usage:
    python3 forge.py --dataset /path/to/data.jsonl --output my-model
    python3 forge.py --base mistral --dataset data.jsonl --steps 100 --r 16
"""
import modal, os, sys, json, argparse

BASE_MODELS = {
    "mistral": "mistralai/Mistral-7B-Instruct-v0.2",
    "qwen":    "Qwen/Qwen2.5-7B-Instruct",
    "llama":   "meta-llama/Meta-Llama-3.1-8B-Instruct",
}

def build_forge_image():
    return (
        modal.Image.debian_slim(python_version="3.10")
        .apt_install("git")
        .pip_install("torch==2.4.0", "torchvision==0.19.0", index_url="https://download.pytorch.org/whl/cu121")
        .pip_install("transformers==4.44.2", "trl==0.9.6", "datasets", "accelerate==0.33.0",
                     "bitsandbytes==0.43.1", "peft", "rich")
    )

def main():
    parser = argparse.ArgumentParser(description="Modal LoRA Forge")
    parser.add_argument("--dataset", required=True, help="Path to JSONL dataset")
    parser.add_argument("--output", required=True, help="Output model name")
    parser.add_argument("--base", default="mistral", choices=list(BASE_MODELS), help="Base model")
    parser.add_argument("--steps", default=50, type=int, help="Training steps")
    parser.add_argument("--r", default=16, type=int, dest="lora_r", help="LoRA rank")
    parser.add_argument("--gpu", default="A10G", help="GPU type")
    parser.add_argument("--volume", default="model-store", help="Modal volume")
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(f"ERROR: Dataset not found: {args.dataset}")
        sys.exit(1)

    with open(args.dataset) as f:
        data = [json.loads(line) for line in f]
    if not data:
        print("ERROR: Empty dataset")
        sys.exit(1)
    for i, row in enumerate(data):
        if "text" not in row:
            print(f"ERROR: Missing 'text' field in row {i}")
            sys.exit(1)

    print(f"Dataset: {len(data)} samples from {args.dataset}")
    print(f"Base: {BASE_MODELS[args.base]} | Output: {args.output}")
    print(f"LoRA r={args.lora_r} | Steps: {args.steps} | GPU: {args.gpu}")

    app = modal.App("zo-forge")
    volume = modal.Volume.from_name(args.volume, create_if_missing=True)

    @app.function(
        image=build_forge_image(),
        gpu=args.gpu, timeout=7200,
        volumes={"/models": volume},
        scaledown_window=300, memory=40960
    )
    def train(dataset_content: bytes, output_name: str, base_model: str, lora_r: int, max_steps: int):
        import torch
        from datasets import Dataset
        from transformers import (AutoModelForCausalLM, AutoTokenizer, TrainingArguments,
                                  BitsAndBytesConfig)
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from trl import SFTTrainer

        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

        with open("/tmp/data.jsonl", "wb") as f:
            f.write(dataset_content)
        raw = [json.loads(line) for line in open("/tmp/data.jsonl")]
        dataset = Dataset.from_list(raw).shuffle(seed=42)

        bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16,
                                        bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4")

        model = AutoModelForCausalLM.from_pretrained(base_model, quantization_config=bnb_config,
                                                     device_map="auto", torch_dtype=torch.float16)
        model = prepare_model_for_kbit_training(model)
        model.gradient_checkpointing_enable()

        tokenizer = AutoTokenizer.from_pretrained(base_model)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        peft_config = LoraConfig(r=lora_r, lora_alpha=lora_r, lora_dropout=0.05,
                                 bias="none", task_type="CAUSAL_LM")
        model = get_peft_model(model, peft_config)

        trainer = SFTTrainer(
            model=model, tokenizer=tokenizer, train_dataset=dataset,
            dataset_text_field="text", max_seq_length=512,
            args=TrainingArguments(per_device_train_batch_size=2, gradient_accumulation_steps=4,
                                   max_steps=max_steps, learning_rate=2e-4, fp16=True,
                                   logging_steps=10, save_steps=25, save_total_limit=2,
                                   output_dir="/tmp/output", report_to="none")
        )

        trainer.train()
        save_path = f"/models/{output_name}"
        model.save_pretrained(save_path)
        tokenizer.save_pretrained(save_path)
        volume.commit()
        return {"status": "done", "path": save_path, "samples": len(raw), "steps": max_steps}

    with open(args.dataset, "rb") as f:
        content = f.read()

    print("Submitting forge job...")
    result = train.remote(content, args.output, BASE_MODELS[args.base], args.lora_r, args.steps)
    print(f"Done: {json.dumps(result)}")
    print(f"Retrieve: modal volume get {args.volume} {args.output} .")

if __name__ == "__main__":
    main()
