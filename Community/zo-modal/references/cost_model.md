# Modal Cost Model

## Pricing Structure

Modal charges per GPU-second of active compute. No charges when functions are idle (scaled to zero). Storage volumes cost $0.025/GB/month after 1GB free.

## Real-World Estimates

### vLLM Inference Server
| Scenario | GPU | Active hrs/day | Daily | Monthly |
|----------|-----|---------------|-------|---------|
| Light (10 calls/day) | L4 | 0.5h | $0.22 | $6.60 |
| Medium (50 calls/day) | L4 | 1.5h | $0.66 | $19.80 |
| Heavy (200 calls/day) | L40S | 3h | $1.77 | $53.10 |

### LoRA Fine-Tuning
| Scenario | GPU | Time | Cost/run |
|----------|-----|------|----------|
| Small dataset (1K samples, 50 steps) | A10G | 4 min | $0.08 |
| Medium dataset (10K samples, 100 steps) | A10G | 10 min | $0.20 |
| Large dataset (50K samples, 200 steps) | A100 | 30 min | $1.70 |

### GPU OCR (Tesseract)
| Scenario | GPU | PDFs/week | Time | Monthly |
|----------|-----|----------|------|---------|
| Light (10 PDFs/week) | T4 | 10 | 0.5h | $0.60 |
| Medium (50 PDFs/week) | T4 | 50 | 2h | $2.40 |
| Heavy (200 PDFs/week) | T4 | 200 | 8h | $9.60 |

## Cost-Saving Patterns

1. **Scale to zero**: Functions shut down after 5 min idle → $0 charge during quiet periods
2. **Spot instances**: Modal uses spot pricing by default (~60% cheaper than on-demand)
3. **Model caching**: Store downloaded models on volumes → no re-download cost
4. **Batch when possible**: Send multiple queries in one request → fewer cold starts
5. **Right-size GPU**: 7B models on L4 ($0.44) not L40S ($0.59)

## Budget Guardrails

Modal doesn't have native spend caps. Best practices:
- Set `scaledown_window` to 300s (5 min) or lower
- Monitor with `python3 scripts/cost_watch.py` weekly
- Use spot instances (default) not on-demand
- For fine-tuning, set explicit `max_steps` not epochs

## Zo Integration Cost

Typical Wizaya setup (vLLM + OCR + weekly forge):
- vLLM server (L4, ~1h/day): ~$13/month
- Weekly forge (A10G, 10 min/week): ~$0.80/month
- OCR (T4, 2h/week): ~$2.40/month
- Volume storage (1-2GB): ~$0.03/month
- **Total: ~$16/month**
