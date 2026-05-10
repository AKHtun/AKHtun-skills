# Gateway Routing — Modal vLLM Integration

## Architecture

```
QUERY → llm_gateway.py (classify)
├─ tier-0   (local Ollama)        < 100 tokens, status/help
├─ tier-M   (Modal vLLM 7B)        classification, routing
├─ tier-M14 (Modal vLLM 14B)       engineering analysis
├─ tier-M32 (Modal vLLM 32B-AWQ)   deep reasoning
├─ tier-V   (Vertex AI)            history, scholarly
├─ tier-4   (DeepSeek V4 API)      technical fallback
└─ tier-5   (Claude 3.5 Sonnet)    synthesis, critical
```

## Injecting Modal into Your Gateway

### 1. Deploy a vLLM Server

```bash
python3 Skills/zo-modal/scripts/vllm_deploy.py
```

Get the endpoint URL:
```bash
modal app show zo-vllm-server | grep URL
```

### 2. Patch Your Gateway

```bash
python3 Skills/zo-modal/scripts/gateway_patch.py \
  --gateway /home/workspace/llm_gateway.py \
  --endpoint https://your-name--zo-vllm-server-serve.modal.run
```

### 3. Add the Route to Your Classification Logic

In your `classify_query()` function:

```python
def classify_query(prompt: str) -> str:
    tokens = len(prompt.split())
    
    if tokens < 50:
        return "tier-0"      # local Ollama, instant
    
    if any(kw in prompt.lower() for kw in ["iso 4406", "viscosity", "tribology", "wear", "oil"]):
        return "tier-m14"    # Modal 14B — engineering
    
    if any(kw in prompt.lower() for kw in ["classify", "route", "sort", "category"]):
        return "tier-m"      # Modal 7B — classification
    
    if any(kw in prompt.lower() for kw in ["chain of thought", "reasoning", "why", "explain"]):
        return "tier-m32"    # Modal 32B — deep reasoning
    
    if any(kw in prompt.lower() for kw in ["history", "pyu", "archaeological"]):
        return "tier-v"      # Vertex AI — historical
    
    return "tier-0"          # default local
```

### 4. Call the Right Tier

```python
route = classify_query(prompt)
if route.startswith("tier-m"):
    model = {
        "tier-m":   "qwen2.5-7b",
        "tier-m14": "qwen2.5-14b",
        "tier-m32": "deepseek-32b",
    }.get(route, "qwen2.5-7b")
    return call_tier_m(prompt, model=model) or call_tier_0(prompt)
```

## Cold Start Handling

Modal functions scale to zero after 5 min idle. First call after idle triggers a cold start (30-90s). Strategy:

```python
def call_with_warmup(prompt: str) -> str:
    result = call_tier_m(prompt)
    if result is None:
        # Modal cold starting — fall back to local Tier-0 immediately
        return call_tier_0(prompt)
    return result
```

## Pre-Warming

For predictable workloads, send a no-op ping 90s before expected use:

```bash
python3 Skills/zo-modal/scripts/vllm_deploy.py --test "ping"  # warm start
```

## Monitoring

```bash
# Check deployment status
python3 Skills/zo-modal/scripts/vllm_deploy.py --status

# Cost tracking
python3 Skills/zo-modal/scripts/cost_watch.py

# Gateway integration check
python3 Skills/zo-modal/scripts/gateway_patch.py --check
```
