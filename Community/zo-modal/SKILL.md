---
name: zo-modal
description: Integrate Modal serverless GPU cloud with Zo Computer. Deploy vLLM inference servers, fine-tune models via LoRA, run GPU-accelerated OCR, and connect Modal endpoints to your Zo LLM gateway. Sets up secrets, monitors GPU spend, and configures auto-scale-to-zero.
compatibility: Created for Zo Computer
metadata:
  author: akh.zo.computer
allowed-tools: Bash, Read
---
# zo-modal — Modal GPU Cloud for Zo

Integrate Modal's serverless GPU cloud with your Zo Computer. Deploy custom LLM inference servers, fine-tune domain-specific models, process PDFs with GPU-accelerated OCR, and route through your Zo LLM gateway.

## Usage

### Prerequisites

- Modal account (free tier available): https://modal.com/signup
- Modal API token: https://modal.com/settings/tokens
- Add to Zo Settings > Advanced > Secrets:
  - `MODAL_TOKEN_ID` — your token ID
  - `MODAL_TOKEN_SECRET` — your token secret

### Quick Start

```bash
# 1. Setup
python3 Skills/zo-modal/scripts/setup.py

# 2. Deploy a vLLM Inference Server
python3 Skills/zo-modal/scripts/vllm_deploy.py

# 3. Get your endpoint
modal app show zo-vllm-server

# 4. Patch your LLM gateway
python3 Skills/zo-modal/scripts/gateway_patch.py \
  --endpoint https://your-name--zo-vllm-server-serve.modal.run

# 5. Fine-tune a model (LoRA)
python3 Skills/zo-modal/scripts/forge.py \
  --dataset /path/to/data.jsonl \
  --output my-engineering-model \
  --base mistral

# 6. Run GPU OCR
python3 Skills/zo-modal/scripts/ocr_batch.py \
  --dir /home/workspace/pdf_dropzone/
```

## Scripts

| Script | What it does |
|--------|-------------|
| `setup.py` | Install Modal CLI, validate token, guide secrets setup |
| `vllm_deploy.py` | Deploy vLLM inference server on L4/L40S GPU |
| `forge.py` | LoRA fine-tuning on A10G GPU |
| `ocr_batch.py` | GPU-accelerated OCR via Tesseract on T4 |
| `cost_watch.py` | Monitor GPU spend and forecast monthly cost |
| `gateway_patch.py` | Inject Modal routes into your `llm_gateway.py` |

## Automation Templates

### Weekly Cost Report

Create a Zo automation to monitor Modal spend:

```
Instruction: Run this command and email the output:
python3 Skills/zo-modal/scripts/cost_watch.py
Schedule: Every Monday 09:00 SGT
```

### Modal OCR Batch

```
Instruction: Run this command and email the summary:
python3 Skills/zo-modal/scripts/ocr_batch.py --dir /home/workspace/pdf_dropzone/
Schedule: Every Sunday 19:00 SGT
```

## References

- `references/modal_overview.md` — What Modal is, GPU options, comparison
- `references/cost_model.md` — Pricing, estimates, cost-saving patterns
- `references/gateway_routing.md` — Full routing architecture with cold start handling
