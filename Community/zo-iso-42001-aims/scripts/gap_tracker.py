#!/usr/bin/env python3
"""
ISO/IEC 42001:2023 AIMS — Gap Closure Tracker

Tracks PARTIAL gaps, identifies the next one to close, and generates
the deliverable artefact path and template.

Usage:
    python3 gap_tracker.py [--dir /path/to/AIMS] [--next]
    python3 gap_tracker.py --close A.3.3 --artefact /path/to/new/file.md
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path


DEFAULT_AIMS_DIR = "/home/workspace/AIMS"

GAP_ARTEFACTS = {
    "A.3.3": {
        "deliverable": "CONCERNS_CHANNEL.md",
        "template": "A formal channel for reporting concerns about AI system behaviour. Document: who can report, how to report, how reports are handled, escalation path, and confidentiality. For Zo users: also create a /api/concerns route or a dedicated email address.",
    },
    "A.5.4": {
        "deliverable": "FAIRNESS_ASSESSMENT_TEMPLATE.md",
        "template": "Demographic fairness assessment template for AI outputs. Sections: output type, affected groups, potential bias vectors, testing methodology, results, mitigations. Include a checklist for identifying disparate impact.",
    },
    "A.5.5": {
        "deliverable": "SOCIETAL_IMPACT_TEMPLATE.md",
        "template": "Societal impact documentation template per Annex B.5.5. Sections: environmental sustainability, economic impact, government/political impact, cultural impact, norms/traditions/values. For each: assessment, severity, evidence.",
    },
    "A.7.4": {
        "deliverable": "DATA_QUALITY_METRICS.md",
        "template": "Define quantitative data quality metrics per dataset/collection. Metrics: completeness (%), accuracy (%), freshness (age), duplicate rate (%), null rate (%). Include a Python script snippet to compute these from your data store.",
    },
    "A.7.5": {
        "deliverable": "DATA_PROVENANCE_REGISTER.md",
        "template": "Full data provenance chain. Table per dataset: origin (source organisation/system), acquisition method (API pull, PDF upload, manual), acquisition date, transformation steps (cleaning, chunking, embedding), retention policy, access controls.",
    },
    "A.8.4": {
        "deliverable": "INCIDENT_COMMUNICATION_PROTOCOL.md",
        "template": "Incident communication protocol. Sections: severity levels (P0-P4), notification paths (who gets told, how, within what timeframe), post-incident review template (5 Whys, timeline, corrective actions), and escalation matrix.",
    },
    "A.10.3": {
        "deliverable": "SUPPLIER_ASSESSMENT.md",
        "template": "Supplier assessment for AI dependencies. One section per supplier (model provider, data provider, tool vendor). For each: what they provide, risk assessment (continuity, security, sovereignty), alternatives if supplier fails, review date.",
    },
}


def parse_gaps_from_soa(soa_path):
    """Extract PARTIAL controls with target dates from SoA."""
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
                target = parts[4].strip()
                if cid and cid not in ("Control", "—", ""):
                    gaps.append({"control": cid, "gap": gap, "target": target})
        elif in_gaps_section and past_header and not line.strip().startswith("|"):
            if line.strip():
                in_gaps_section = False
    return gaps


def find_next_gap(aims_dir):
    soa_path = Path(aims_dir) / "STATEMENT_OF_APPLICABILITY.md"
    gaps = parse_gaps_from_soa(str(soa_path))

    if not gaps:
        print("No PARTIAL gaps found — 100% APPLIED conformity achieved.")
        return None

    # Sort by target date
    try:
        gaps.sort(key=lambda g: g.get("target", "9999-99-99"))
    except Exception:
        pass

    next_gap = gaps[0]
    cid = next_gap["control"]

    print("=" * 60)
    print("GAP CLOSURE TRACKER")
    print("=" * 60)
    print(f"Total open gaps:  {len(gaps)}")
    print(f"Next to close:    {cid} — {next_gap['gap']}")
    print(f"Target date:      {next_gap['target']}")
    print()

    if cid in GAP_ARTEFACTS:
        artefact = GAP_ARTEFACTS[cid]
        print(f"Deliverable:      {artefact['deliverable']}")
        print(f"Create at:        {aims_dir}/{artefact['deliverable']}")
        print()
        print("CONTENT GUIDANCE:")
        print(artefact['template'])

    return next_gap


def mark_closed(aims_dir, control_id, artefact_path):
    """Update SoA to mark a control as APPLIED and add evidence."""
    soa_path = Path(aims_dir) / "STATEMENT_OF_APPLICABILITY.md"
    if not soa_path.exists():
        print(f"ERROR: SoA not found at {soa_path}")
        sys.exit(1)

    content = soa_path.read_text()
    new_lines = []
    found = False
    for line in content.split("\n"):
        if f"| {control_id} " in line and "PARTIAL" in line:
            found = True
            # Replace PARTIAL with APPLIED in evidence
            line = line.replace("**PARTIAL**", "**APPLIED**")
            # Add new evidence reference
            if "|" in line and artefact_path:
                parts = line.split("|")
                parts[-1] = f" {artefact_path} |"
                line = "|".join(parts)
        new_lines.append(line)

    if not found:
        print(f"WARNING: control {control_id} not found as PARTIAL in SoA")
    else:
        soa_path.write_text("\n".join(new_lines))
        print(f"UPDATED: {soa_path} — {control_id} marked APPLIED")

    # Update handover log
    handover_path = Path(aims_dir) / "HANDOVER_LOG.md"
    if handover_path.exists():
        hl = handover_path.read_text()
        entry = f"\n| {datetime.now().strftime('%Y-%m-%d')} | 1.{len(hl.split('CHANGELOG'))} | Gap closed: {control_id} — {artefact_path} | Zo AIMS Bootstrap |"
        if "CHANGELOG" in hl:
            # Insert after changelog table header
            lines = hl.split("\n")
            out = []
            in_changelog = False
            for line in lines:
                out.append(line)
                if "CHANGELOG" in line:
                    in_changelog = True
                elif in_changelog and line.startswith("|") and "---" in line:
                    out.append(entry.strip())
                    in_changelog = False
            handover_path.write_text("\n".join(out))
            print(f"UPDATED: {handover_path} — changelog entry added")


def main():
    parser = argparse.ArgumentParser(description="AIMS Gap Closure Tracker")
    parser.add_argument("--dir", default=DEFAULT_AIMS_DIR, help="Path to AIMS directory")
    parser.add_argument("--next", action="store_true", help="Show next gap to close")
    parser.add_argument("--close", help="Control ID to mark as closed (e.g., A.3.3)")
    parser.add_argument("--artefact", help="Path to new artefact file (evidence)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.close:
        mark_closed(args.dir, args.close, args.artefact)
    else:
        gap = find_next_gap(args.dir)
        if gap and args.json:
            print(json.dumps(gap, indent=2))
        elif not gap:
            print(json.dumps({"status": "complete", "message": "All controls APPLIED"}))


if __name__ == "__main__":
    main()
