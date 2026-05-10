#!/usr/bin/env python3
"""
ISO/IEC 42001:2023 AIMS Bootstrap Script

Generates the four baseline AIMS documents from user-provided configuration.
Non-interactive — accepts a JSON config file or individual arguments.
Designed to be called by the Zo agent during guided setup.

Usage:
    python3 bootstrap.py --config aims_config.json
    python3 bootstrap.py --output-dir /home/workspace/AIMS \
        --org-name "Acme Corp" \
        --owner "Jane Doe, CTO" \
        ...
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "assets"
DEFAULT_OUTPUT = Path("/home/workspace/AIMS")

TEMPLATE_FILES = {
    "AIMS_POLICY.md": "policy_template.md",
    "STATEMENT_OF_APPLICABILITY.md": "soa_template.md",
    "AI_IMPACT_ASSESSMENT.md": "impact_assessment_template.md",
    "HANDOVER_LOG.md": "handover_template.md",
}


def load_template(name):
    path = TEMPLATES_DIR / name
    if not path.exists():
        print(f"ERROR: template missing: {path}")
        sys.exit(1)
    return path.read_text()


def fill_template(template, variables):
    result = template
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        if placeholder in result:
            result = result.replace(placeholder, str(value))
    unfilled = [p for p in ["{{" + k + "}}" for k in variables] if p in result]
    if unfilled:
        print(f"WARNING: unfilled placeholders: {unfilled}")
    return result


def build_soa_table(variables):
    """Build the SoA with per-control status and evidence from config."""
    controls = {
        "A22": ("AI policy", "AIMS_POLICY.md — AI system policy documented"),
        "A23": ("Alignment with other policies", "AIMS_POLICY.md §6 lists aligned policies"),
        "A24": ("Review of AI policy", f"AIMS_POLICY.md §7 — review cycle, next review {variables.get('NEXT_REVIEW_DATE', 'TBD')}"),
        "A32": ("AI roles and responsibilities", "AIMS_POLICY.md §4 — roles assigned"),
        "A33": ("Reporting of concerns", variables.get("A33_EVIDENCE", "PARTIAL — no formal reporting channel")),
        "A42": ("Resource documentation", "AGENTS.md or equivalent system documentation"),
        "A43": ("Data resources", variables.get("A43_EVIDENCE", "Data sources documented")),
        "A44": ("Tooling resources", variables.get("A44_EVIDENCE", "Tools documented in system docs")),
        "A45": ("System and computing resources", variables.get("A45_EVIDENCE", "Hardware specs documented")),
        "A46": ("Human resources", variables.get("A46_EVIDENCE", "Operator expertise documented")),
        "A52": ("Impact assessment process", "AI_IMPACT_ASSESSMENT.md documents process"),
        "A53": ("Documentation of impact assessments", "AI_IMPACT_ASSESSMENT.md retained in AIMS/"),
        "A54": ("Fairness assessment", variables.get("A54_EVIDENCE", "PARTIAL — no formal fairness assessment template")),
        "A55": ("Societal impact assessment", variables.get("A55_EVIDENCE", "PARTIAL — no formal societal impact template")),
        "A612": ("Objectives for responsible development", "AIMS_POLICY.md §2 — governing principles"),
        "A613": ("Processes for responsible design", "System architecture documentation"),
        "A622": ("AI system requirements", variables.get("A622_EVIDENCE", "Requirements documented in system docs")),
        "A623": ("Documentation of design", "AGENTS.md and protocol documents"),
        "A624": ("Verification and validation", variables.get("A624_EVIDENCE", "Testing and review processes")),
        "A625": ("Deployment", variables.get("A625_EVIDENCE", "Managed deployment via Zo services/agents")),
        "A626": ("Operation and monitoring", variables.get("A626_EVIDENCE", "Logging, health checks in place")),
        "A627": ("Technical documentation", "AGENTS.md, SOUL.md, protocol files"),
        "A628": ("Event logging", variables.get("A628_EVIDENCE", "Operation logs in production")),
        "A72": ("Data for development", "Data pipeline documentation"),
        "A73": ("Acquisition of data", variables.get("A73_EVIDENCE", "Data sources documented with provenance")),
        "A74": ("Quality of data", variables.get("A74_EVIDENCE", "PARTIAL — no formal data quality metrics")),
        "A75": ("Data provenance", variables.get("A75_EVIDENCE", "PARTIAL — no full provenance chain documented")),
        "A76": ("Data preparation", variables.get("A76_EVIDENCE", "Data preparation pipeline documented")),
        "A82": ("System documentation for users", "AGENTS.md, README files available"),
        "A83": ("External reporting", variables.get("A83_EVIDENCE", "EXCLUDED — internal-only system, no external stakeholders")),
        "A84": ("Communication of incidents", variables.get("A84_EVIDENCE", "PARTIAL — no formal incident communication protocol")),
        "A85": ("Information for interested parties", variables.get("A85_EVIDENCE", "EXCLUDED — no external interested parties")),
        "A92": ("Processes for responsible use", variables.get("A92_EVIDENCE", "Usage guidelines, tiered access controls")),
        "A93": ("Objectives for responsible use", "AIMS_POLICY.md §2 — governing principles"),
        "A94": ("Intended use", variables.get("A94_EVIDENCE", "Scope defined in system documentation")),
        "A102": ("Allocating responsibilities", variables.get("A102_EVIDENCE", "EXCLUDED — no third parties or customers")),
        "A103": ("Suppliers", variables.get("A103_EVIDENCE", "PARTIAL — no formal supplier assessment")),
        "A104": ("Customers", variables.get("A104_EVIDENCE", "EXCLUDED — no external customers")),
    }

    applied = 0
    partial = 0
    excluded = 0
    partial_gaps = []
    rows = []

    for cid, (topic, evidence) in controls.items():
        status = "APPLIED"
        if evidence.startswith("PARTIAL"):
            status = "PARTIAL"
            partial += 1
            gap_text = evidence.replace("PARTIAL — ", "")
            partial_gaps.append((cid, topic, gap_text))
        elif evidence.startswith("EXCLUDED"):
            status = "EXCLUDED"
            excluded += 1
        else:
            applied += 1

        rows.append(f"| {cid} | {topic} | **{status}** | {evidence} |")

    controls_table = "\n".join(rows)

    # Partial gaps with realistic dates (earliest 1 month out, spread over up to 7 months)
    base_date = datetime.strptime(variables.get("DATE", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
    gap_rows = []
    for i, (cid, topic, gap_text) in enumerate(partial_gaps):
        # Earliest gap 1 month out, each subsequent gap +1 month
        target = base_date + timedelta(days=30 * (i + 1))
        gap_rows.append(f"| {cid} | {topic} | {gap_text} | {target.strftime('%Y-%m-%d')} |")
    gaps_table = "\n".join(gap_rows) if gap_rows else "| — | No partial gaps | — | — |"

    return {
        "SOA_CONTROLS_TABLE": controls_table,
        "GAPS_TABLE": gaps_table,
        "APPLIED_COUNT": str(applied),
        "PARTIAL_COUNT": str(partial),
        "EXCLUDED_COUNT": str(excluded),
        "APPLIED_PCT": str(round(100 * applied / 38)),
        "TOTAL_PCT": str(round(100 * (applied + partial) / 38)),
    }


def generate_documents(config, output_dir):
    config.setdefault("DATE", datetime.now().strftime("%Y-%m-%d"))
    config.setdefault("DATE_COMPACT", datetime.now().strftime("%Y%m%d"))
    config.setdefault("DOC_REF_PREFIX", config.get("ORG_NAME", "ORG").upper().replace(" ", "-"))
    config.setdefault("OPERATOR", "Zo Computer — ISO 42001 Bootstrap Skill")
    config.setdefault("REVIEW_INTERVAL", "6 months")
    base = datetime.strptime(config["DATE"], "%Y-%m-%d")
    config.setdefault("NEXT_REVIEW_DATE", (base + timedelta(days=183)).strftime("%Y-%m-%d"))
    config.setdefault("FIRST_AUDIT_DATE", "first Sunday after " + config["DATE"])
    config.setdefault("FIRST_GAP_DATE", "first Monday after " + config["DATE"])

    # Build SoA data
    soa = build_soa_table(config)
    config.update(soa)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    for out_name, template_name in TEMPLATE_FILES.items():
        template = load_template(template_name)
        filled = fill_template(template, config)
        out_path = output_dir / out_name
        out_path.write_text(filled)
        results[out_name] = str(out_path)
        print(f"CREATED: {out_path}")

    # Summary
    print()
    print("=" * 60)
    print("AIMS BOOTSTRAP COMPLETE")
    print("=" * 60)
    print(f"Organisation: {config.get('ORG_NAME', 'Unknown')}")
    print(f"Output:       {output_dir}")
    print(f"Applied:      {soa['APPLIED_COUNT']}/38 ({soa['APPLIED_PCT']}%)")
    print(f"Partial:      {soa['PARTIAL_COUNT']}/38")
    print(f"Excluded:     {soa['EXCLUDED_COUNT']}/38")
    print(f"Conformity:   {soa['TOTAL_PCT']}% (APPLIED + PARTIAL)")
    print()
    print("DOCUMENTS CREATED:")
    for name, path in results.items():
        print(f"  {name}: {path}")
    print()
    print("NEXT STEPS:")
    print("  1. Review all 4 documents — verify accuracy, edit freely")
    print("  2. Install automations: ask Zo to 'install AIMS conformity monitor and gap closure agent'")
    print("  3. Schedule first manual audit: python3 scripts/audit.py")
    print("=" * 60)

    return results


def main():
    parser = argparse.ArgumentParser(description="Bootstrap ISO/IEC 42001:2023 AIMS")
    parser.add_argument("--config", help="JSON config file with all variables")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT), help="Output directory (default: /home/workspace/AIMS)")
    parser.add_argument("--org-name", help="Organisation name")
    parser.add_argument("--owner", help="AI System Owner (name + title)")

    args = parser.parse_args()

    config = {}

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        # Build config from environment/args — minimal mode
        config["ORG_NAME"] = args.org_name or os.environ.get("AIMS_ORG_NAME", "My Organisation")
        config["OWNER_TITLE"] = args.owner or os.environ.get("AIMS_OWNER", "AI System Owner")
        config["AI_SYSTEM_OWNER"] = config["OWNER_TITLE"].split(",")[0].strip() if "," in config["OWNER_TITLE"] else config["OWNER_TITLE"]

    if not config.get("ORG_NAME"):
        print("ERROR: --org-name required (or --config with org_name field)")
        sys.exit(1)

    config.setdefault("AI_ECOSYSTEM_NAME", config.get("ORG_NAME", "My Organisation") + " AI Ecosystem")
    config.setdefault("AI_SYSTEM_OWNER", config.get("OWNER_TITLE", "AI System Owner").split(",")[0].strip())
    config.setdefault("OWNER_TITLE", config.get("OWNER_TITLE", config.get("AI_SYSTEM_OWNER", "AI System Owner")))

    generate_documents(config, args.output_dir)


if __name__ == "__main__":
    main()
