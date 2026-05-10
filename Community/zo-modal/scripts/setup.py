#!/usr/bin/env python3
"""Modal setup — install CLI, validate token, create secrets template."""
import subprocess, sys, os, json

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def main():
    print("=== Modal Zo Setup ===\n")

    token_id = os.environ.get("MODAL_TOKEN_ID", "")
    token_secret = os.environ.get("MODAL_TOKEN_SECRET", "")

    if not token_id or not token_secret:
        print("SETUP REQUIRED:")
        print("  1. Create a Modal account: https://modal.com/signup")
        print("  2. Generate a token: https://modal.com/settings/tokens")
        print("  3. Add to Zo Settings > Advanced > Secrets:")
        print("     - Key: MODAL_TOKEN_ID")
        print("     - Key: MODAL_TOKEN_SECRET")
        print()
        print("  After adding secrets, re-run: python3 setup.py")
        sys.exit(0)

    print(f"[OK] Secrets found (token_id: {token_id[:8]}...)")

    print("\n[INSTALL] modal package...")
    result = run("pip install modal -q")
    if result.returncode != 0:
        print(f"[ERR] pip install failed: {result.stderr}")
        sys.exit(1)
    print("[OK] modal installed")

    print("\n[AUTH] Setting Modal token...")
    result = run(f"modal token set --token-id {token_id} --token-secret {token_secret}")
    if result.returncode != 0:
        print(f"[ERR] token set failed: {result.stderr}")
        sys.exit(1)

    result = run("modal config show 2>&1")
    print(result.stdout[:500])

    print("\n=== Setup Complete ===")
    print("Next: deploy vLLM server → python3 scripts/vllm_deploy.py")

if __name__ == "__main__":
    main()
