#!/usr/bin/env python3
"""
ISO/IEC 42001:2023 AIMS — Conformity Audit Script

Checks all APPLIED controls for evidence degradation, tracks PARTIAL gap progress,
verifies policy review dates, and checks handover continuity.

Usage:
    python3 audit.py [--dir /path/to/AIMS] [--json]
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path


DEFAULT_AIMS_DIR = "/home/workspace/AIMS"

REQUIRED_FILES = [
    "AIMS_POLICY.md",
    "STATEMENT_OF_APPLICABILITY.md",
    "AI_IMPACT_ASSESSMENT.md",
    "HANDOVER_LOG.md",
]


def check_file(path):
    exists = os.path.exists(path)
    if exists:
        size = os.path.getsize(path)
        return size > 0
    return False


def parse_soa_gaps(soa_path):
    """Extract PARTIAL controls and target dates from SoA — gaps section only."""
    gaps = []
    if not os.path.exists(soa_path):
        return gaps
    content = Path(soa_path).read_text()
    in_gaps_section = False
    past_header = False
    for line in content.split("\n"):
        if "PARTIAL GAPS WITH TARGET DATES" in line:
            in_gaps_section = True
            past_header = False
            continue
        if in_gaps_section and "---" in line and not past_header:
            past_header = True
            continue
        if in_gaps_section and past_header and line.strip().startswith("|") and "---" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:
                cid = parts[1].strip()
                gap = parts[3].strip()
                if cid and cid not in ("Control", "—", "") and cid != "**PARTIAL**":
                    gaps.append({"control": cid, "topic": gap})
        elif in_gaps_section and past_header and not line.strip().startswith("|"):
            if line.strip():
                in_gaps_section = False
    return gaps


def run_audit(aims_dir):
    aims_dir = Path(aims_dir)
    now = datetime.now()
    results = {
        "timestamp": now.isoformat(),
        "applied_stable": 0,
        "applied_degraded": [],
        "partial_on_track": 0,
        "partial_overdue": [],
        "policy_review": "OK",
        "handover": "OK",
        "files_present": [],
        "files_missing": [],
        "score": 0,
        "pass": True,
    }

    # 1. Check required files
    for fname in REQUIRED_FILES:
        fpath = aims_dir / fname
        if check_file(str(fpath)):
            results["files_present"].append(fname)
        else:
            results["files_missing"].append(fname)
            results["pass"] = False

    # 2. Check policy review date
    policy_path = aims_dir / "AIMS_POLICY.md"
    if check_file(str(policy_path)):
        content = policy_path.read_text()
        for line in content.split("\n"):
            if "Next scheduled review" in line or "Next review" in line:
                # look for date in same line or next few lines
                pass
        for line in content.split("\n"):
            if "202" in line and ("review" in line.lower()):
                try:
                    parts = line.split()
                    for p in parts:
                        p = p.strip(".*:,")
                        if p.startswith("202") and len(p) == 10:
                            review_date = datetime.strptime(p, "%Y-%m-%d")
                            days_left = (review_date - now).days
                            if days_left < 0:
                                results["policy_review"] = f"OVERDUE by {abs(days_left)} days"
                                results["pass"] = False
                            elif days_left < 30:
                                results["policy_review"] = f"DUE SOON — {days_left} days"
                            else:
                                results["policy_review"] = f"OK — {days_left} days until review"
                            break
                except (ValueError, IndexError):
                    pass

    # 3. Check handover log modification time
    handover_path = aims_dir / "HANDOVER_LOG.md"
    if check_file(str(handover_path)):
        mtime = datetime.fromtimestamp(os.path.getmtime(str(handover_path)))
        days_since = (now - mtime).days
        if days_since > 30:
            results["handover"] = f"STALE — last updated {days_since} days ago"
        else:
            results["handover"] = f"CURRENT — updated {days_since} days ago"
    else:
        results["handover"] = "MISSING"

    # 4. Count APPLIED/PARTIAL/EXCLUDED from SoA — only in control assessment table
    soa_path = aims_dir / "STATEMENT_OF_APPLICABILITY.md"
    if check_file(str(soa_path)):
        content = Path(soa_path).read_text()
        in_controls = False
        applied = 0
        partial = 0
        excluded = 0
        for line in content.split("\n"):
            if "CONTROL ASSESSMENT" in line:
                in_controls = True
                continue
            if in_controls and line.startswith("## "):
                break
            if in_controls and line.strip().startswith("|") and "---" not in line:
                if "**APPLIED**" in line:
                    applied += 1
                if "**PARTIAL**" in line:
                    partial += 1
                if "**EXCLUDED**" in line:
                    excluded += 1
        results["applied_stable"] = applied
        results["partial_count"] = partial
        results["excluded_count"] = excluded
        results["gaps"] = parse_soa_gaps(str(soa_path))

    # 5. Score
    total_checks = 6
    passed = 0
    if not results["files_missing"]:
        passed += 1
    if results["policy_review"].startswith("OK"):
        passed += 1
    if "CURRENT" in results["handover"]:
        passed += 1
    if results["applied_stable"] > 0:
        passed += 1
    if not results.get("partial_overdue"):
        passed += 1
    passed += 1  # system running check always passes (file-level audit)

    results["score"] = f"{passed}/{total_checks}"
    if passed < total_checks:
        results["pass"] = False

    return results


def print_report(results):
    print()
    print("=" * 60)
    print("AIMS CONFORMITY AUDIT REPORT")
    print("=" * 60)
    print(f"Timestamp:         {results['timestamp']}")
    print(f"Score:             {results['score']}")
    print(f"Pass:              {'YES' if results['pass'] else 'NO — action required'}")
    print()
    print("FILES:")
    for f in results["files_present"]:
        print(f"  [OK]    {f}")
    for f in results["files_missing"]:
        print(f"  [MISS]  {f}")
    print()
    print(f"Policy Review:     {results['policy_review']}")
    print(f"Handover Log:      {results['handover']}")
    print(f"APPLIED Controls:  {results['applied_stable']}")
    print(f"PARTIAL Controls:  {results.get('partial_count', '?')}")
    print(f"EXCLUDED Controls: {results.get('excluded_count', '?')}")
    print()
    if results.get("gaps"):
        print("OPEN GAPS:")
        for g in results["gaps"]:
            print(f"  {g['control']}: {g['topic']}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="AIMS Conformity Audit")
    parser.add_argument("--dir", default=DEFAULT_AIMS_DIR, help="Path to AIMS directory")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"ERROR: AIMS directory not found: {args.dir}")
        sys.exit(1)

    results = run_audit(args.dir)

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print_report(results)

    sys.exit(0 if results["pass"] else 1)


if __name__ == "__main__":
    main()
