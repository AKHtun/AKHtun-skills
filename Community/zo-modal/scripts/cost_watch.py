#!/usr/bin/env python3
"""Monitor Modal GPU spend and forecast monthly cost.

Usage:
    python3 cost_watch.py               # current month
    python3 cost_watch.py --json        # JSON output
"""
import subprocess, json, sys, argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Modal Cost Monitor")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = subprocess.run(["modal", "app", "list", "--json"], capture_output=True, text=True)
    if result.returncode != 0:
        print(json.dumps({"error": "modal CLI not available"}) if args.json else "Modal CLI not found.")
        sys.exit(1)

    try:
        apps = json.loads(result.stdout)
    except json.JSONDecodeError:
        apps = []

    if not apps:
        print(json.dumps({"apps": 0, "estimated_monthly": 0}) if args.json else "No Modal apps found.")
        return

    gpu_rates = {"L4": 0.44, "L40S": 0.59, "A10G": 1.20, "T4": 0.30, "A100": 3.40}
    total_hourly = 0
    app_details = []

    for app_entry in apps:
        if isinstance(app_entry, dict):
            name = app_entry.get("Name", app_entry.get("name", "unknown"))
            state = app_entry.get("State", app_entry.get("state", "unknown"))
            description = str(app_entry)

            for gpu_name, rate in gpu_rates.items():
                if gpu_name in description:
                    if state in ("deployed", "running", "ready"):
                        total_hourly += rate
                        app_details.append({"app": name, "gpu": gpu_name, "rate_hr": rate, "state": state})
                        break
                    elif state == "stopped":
                        app_details.append({"app": name, "gpu": gpu_name, "rate_hr": 0, "state": "idle (scaled to zero)"})
                        break

    daily = total_hourly * 4  # assume ~4 active hours/day
    monthly = daily * 30

    if args.json:
        print(json.dumps({
            "apps": len(apps),
            "active_gpu_hourly": round(total_hourly, 2),
            "estimated_daily": round(daily, 2),
            "estimated_monthly": round(monthly, 2),
            "details": app_details
        }, indent=2))
    else:
        print(f"=== Modal GPU Cost Estimate ===")
        print(f"Apps: {len(apps)}")
        for d in app_details:
            print(f"  {d['app']}: {d['gpu']} @ ${d['rate_hr']}/hr — {d['state']}")
        print(f"Active hourly: ${total_hourly:.2f}")
        print(f"Daily (4h est): ${daily:.2f}")
        print(f"Monthly est: ${monthly:.2f}")

if __name__ == "__main__":
    main()
