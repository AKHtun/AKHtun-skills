#!/usr/bin/env python3
"""Deploy vLLM inference server on Modal GPU.

Target: L4 GPU ($0.44/hr), auto-scale-to-zero after 5 min idle.
OpenAI-compatible API at /v1/chat/completions.

Usage:
    python3 vllm_deploy.py                     # deploy default (Qwen2.5-7B)
    python3 vllm_deploy.py --model Qwen/Qwen2.5-14B-Instruct --gpu L40S
    python3 vllm_deploy.py --status             # check deployment
    python3 vllm_deploy.py --test "What is tribology?"  # test endpoint
"""
import modal, os, sys, json, subprocess, time, urllib.request, argparse

HF_MODEL_MAP = {
    "qwen2.5-7b":   "Qwen/Qwen2.5-7B-Instruct",
    "qwen2.5-14b":  "Qwen/Qwen2.5-14B-Instruct",
    "deepseek-32b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    "llama3.1-8b":  "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "mistral-7b":   "mistralai/Mistral-7B-Instruct-v0.3",
}

GPU_MAP = {
    "7b":   "L4",
    "8b":   "L4", 
    "14b":  "L40S",
    "32b":  "L40S",
}

def get_gpu_for_model(model_name):
    for size, gpu in GPU_MAP.items():
        if size in model_name:
            return gpu
    return "L4"

def build_vllm_image():
    return (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install("vllm>=0.5.0", "transformers", "torch==2.3.1", "huggingface_hub", "httpx")
        .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    )

def main():
    parser = argparse.ArgumentParser(description="Modal vLLM Deploy")
    parser.add_argument("--model", default="qwen2.5-7b", help="Model key or HF path")
    parser.add_argument("--gpu", default="", help="GPU type (L4, L40S, A10G)")
    parser.add_argument("--app-name", default="zo-vllm-server", help="Modal app name")
    parser.add_argument("--max-len", default=4096, type=int, help="Max model context length")
    parser.add_argument("--status", action="store_true", help="Check deployment status")
    parser.add_argument("--test", default="", help="Test with a prompt")
    parser.add_argument("--volume", default="model-store", help="Modal volume name")
    args = parser.parse_args()

    hf_model = HF_MODEL_MAP.get(args.model, args.model)
    gpu = args.gpu or get_gpu_for_model(args.model)
    model_key = args.model.replace("/", "_").replace(".", "_")

    if args.status:
        result = subprocess.run(["modal", "app", "list"], capture_output=True, text=True)
        print(result.stdout)
        return

    if args.test:
        endpoint = os.environ.get("MODAL_VLLM_URL", "")
        if not endpoint:
            print("Set MODAL_VLLM_URL env var or deploy first.\nGet it: modal app show " + args.app_name)
            sys.exit(1)
        payload = json.dumps({
            "model": model_key,
            "messages": [{"role": "user", "content": args.test}],
            "max_tokens": 300, "temperature": 0.3
        }).encode()
        req = urllib.request.Request(f"{endpoint}/v1/chat/completions", data=payload,
            headers={"Content-Type": "application/json"})
        try:
            resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
            print(resp["choices"][0]["message"]["content"])
        except Exception as e:
            print(f"Error: {e}")
        return

    app = modal.App(args.app_name)
    volume = modal.Volume.from_name(args.volume, create_if_missing=True)

    @app.function(image=build_vllm_image(), gpu=gpu, volumes={"/models": volume},
                  timeout=1800, scaledown_window=300, memory=32768,
                  secrets=[modal.Secret.from_name("huggingface")] if os.environ.get("HF_TOKEN") else [])
    def serve():
        model_path = f"/models/{model_key}"
        if not os.path.exists(model_path):
            from huggingface_hub import snapshot_download
            snapshot_download(hf_model, local_dir=model_path)
            volume.commit()

        proc = subprocess.Popen([
            "python", "-m", "vllm.entrypoints.openai.api_server",
            "--model", model_path, "--max-model-len", str(args.max_len),
            "--dtype", "half", "--port", "8000", "--host", "0.0.0.0",
            "--enforce-eager",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for i in range(300):
            try:
                urllib.request.urlopen("http://localhost:8000/health")
                break
            except: time.sleep(1)

        print(f"[vLLM] {hf_model} ready on {gpu} GPU")
        proc.wait()

    print(f"Deploying {hf_model} on {gpu} GPU...")
    print(f"App: {args.app_name} | Volume: {args.volume} | Max len: {args.max_len}")
    print(f"Cost: ${'0.44' if gpu == 'L4' else '0.59' if gpu == 'L40S' else '1.20'}/hr (idle → $0)")

    with app.run():
        serve.remote()

    print("\nGet endpoint: modal app show " + args.app_name)

if __name__ == "__main__":
    main()
