# Modal — Serverless GPU Cloud

## What is Modal?

Modal is a serverless cloud platform for GPU-accelerated compute. You deploy Python functions, Modal handles the infrastructure — GPUs scale up when called, scale to zero when idle.

## Key Concepts

| Concept | What it means for you |
|---------|----------------------|
| **App** | A named deployment (e.g. `zo-vllm-server`). Contains functions. |
| **Function** | A Python function decorated with `@app.function()`. Runs on GPU when called. |
| **Volume** | Persistent storage mounted at `/models` or custom path. Survives scale-to-zero. |
| **Image** | The container environment — Debian + pip packages. Built once, cached. |
| **Scaledown window** | Idle timeout before GPU shuts down. Default: 300s (5 min). |

## GPU Options

| GPU | VRAM | $/hr (spot) | Best for |
|-----|------|------------|----------|
| T4 | 16GB | $0.30 | Light OCR, small batch |
| L4 | 24GB | $0.44 | 7B models, vLLM inference |
| A10G | 24GB | $1.20 | Fine-tuning, LoRA training |
| L40S | 48GB | $0.59 | 14B-32B models, AWQ quant |
| A100 | 80GB | $3.40 | Full 70B fine-tuning |

## Modal vs Alternatives

| Factor | Modal | Vertex AI | RunPod | Local Ollama |
|--------|-------|-----------|--------|--------------|
| Setup | Python script | Console + SDK | Web UI | `ollama pull` |
| Cold start | 30-90s | 5-15s | 30-60s | 0s |
| Idle cost | $0 (scale to zero) | $0 (scale to zero) | $0.20/hr storage | Free |
| API | OpenAI-compatible | Vertex SDK | OpenAI-compatible | OpenAI-compatible |
| Fine-tuning | LoRA, full | Vertex tuning | LoRA | N/A |

## When to Use Modal with Zo

- **vLLM inference**: Serve custom/fine-tuned models as OpenAI-compatible endpoints
- **LoRA fine-tuning**: Train domain-specific adapters (e.g., engineering corpus)
- **GPU OCR**: Process scanned PDFs with Tesseract GPU acceleration
- **Batch inference**: Run 1000+ queries through a model without local GPU
