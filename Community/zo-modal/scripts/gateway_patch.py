#!/usr/bin/env python3
"""Patch Zo LLM gateway to route through Modal vLLM endpoints.

Adds Tier-M routing to your existing llm_gateway.py.
Usage:
    python3 gateway_patch.py --gateway /path/to/llm_gateway.py --endpoint https://...
    python3 gateway_patch.py --check  # verify Modal gateway integration
"""
import sys, os, argparse, textwrap

PATCH_CODE = textwrap.dedent('''
    # === MODAL VLLM TIER-M (auto-inserted by zo-modal skill) ===
    import urllib.request
    MODAL_VLLM_URL = os.environ.get("MODAL_VLLM_URL", "")

    def call_tier_m(prompt: str, model: str = "qwen2.5-7b", max_tokens: int = 500) -> str | None:
        """Tier-M: Modal vLLM on-demand GPU. Cost: $0.44/hr L4 → scale-to-zero when idle."""
        if not MODAL_VLLM_URL:
            return None
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "temperature": 0.3
        }).encode()
        req = urllib.request.Request(f"{MODAL_VLLM_URL}/v1/chat/completions",
            data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read())["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[Tier-M] Modal unavailable: {e}", file=sys.stderr)
            return None
    # === END MODAL VLLM PATCH ===
''').strip()

def main():
    parser = argparse.ArgumentParser(description="Patch LLM gateway for Modal")
    parser.add_argument("--gateway", default="/home/workspace/llm_gateway.py", help="Path to gateway")
    parser.add_argument("--endpoint", default="", help="Modal vLLM endpoint URL")
    parser.add_argument("--check", action="store_true", help="Check integration")
    args = parser.parse_args()

    if args.check:
        gw = args.gateway
        if not os.path.exists(gw):
            print(f"Gateway not found: {gw}")
            sys.exit(1)
        content = open(gw).read()
        checks = {
            "PATCH INSTALLED": "MODAL_VLLM_URL" in content,
            "call_tier_m present": "def call_tier_m" in content,
            "MODAL_VLLM_URL env": bool(os.environ.get("MODAL_VLLM_URL")),
        }
        for check, ok in checks.items():
            print(f"{'[OK]' if ok else '[MISSING]'} {check}")
        sys.exit(0 if checks["PATCH INSTALLED"] else 1)

    if not args.endpoint:
        print("ERROR: --endpoint required. Get it from: modal app show <your-vllm-app>")
        sys.exit(1)

    if not os.path.exists(args.gateway):
        print(f"Gateway not found: {args.gateway}. Create it first or specify --gateway path.")
        sys.exit(1)

    content = open(args.gateway).read()
    if "MODAL_VLLM_URL" in content:
        print("Gateway already patched. Updating endpoint...")
        # Simple replace — real implementation can be more surgical
        content = content.replace(
            'MODAL_VLLM_URL = os.environ.get("MODAL_VLLM_URL", "")',
            ''
        )

    with open(args.gateway, "a") as f:
        f.write("\n" + PATCH_CODE + "\n")

    # Also set env for discovery
    os.environ["MODAL_VLLM_URL"] = args.endpoint

    print(f"Gateway patched: {args.gateway}")
    print(f"Endpoint: {args.endpoint}")
    print("\nTo persist the endpoint, add to Zo Settings > Advanced > Secrets:")
    print(f"  Key: MODAL_VLLM_URL  Value: {args.endpoint}")

if __name__ == "__main__":
    main()
