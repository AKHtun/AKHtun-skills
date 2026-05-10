---
name: zo-iso-42001-aims
description: Bootstrap an ISO/IEC 42001:2023 AI Management System from zero. Guided setup wizard generates policy, statement of applicability, impact assessment, and installs monthly conformity + gap-closure automations. For organisations deploying AI systems who need a lightweight, auditable governance baseline — no consultant required.
compatibility: Created for Zo Computer
metadata:
  author: akh.zo.computer
  category: governance
  requires: python3
---

# ISO/IEC 42001:2023 AIMS — Bootstrap Skill

Bootstrap a complete, auditable AI Management System (AIMS) conformant to ISO/IEC 42001:2023. This skill:

1. **Guides** you through a structured assessment of your AI ecosystem
2. **Generates** four baseline documents (Policy, SoA, Impact Assessment, Handover Log)
3. **Installs** two monthly automation agents (Conformity Monitor + Gap Closure)
4. **Leaves** you with a living governance system — not a one-time PDF

## What ISO/IEC 42001 Is

ISO/IEC 42001:2023 is the international standard for AI management systems. It defines 38 controls across 9 domains: policies, organisation, resources, impact assessment, lifecycle, data, information, use, and third-party relationships. It's the AI equivalent of ISO 9001 (quality) or ISO 14001 (environmental).

## Who This Is For

- Engineering firms deploying AI for analysis/automation
- Industrial plants with AI-assisted maintenance/diagnostics
- Research organisations wanting auditable AI governance
- Anyone who needs to demonstrate "we manage AI responsibly" to clients, regulators, or insurers

## Usage

### Quick Start

```
bootstrap my AI management system to ISO 42001
```

Zo will walk you through a guided conversation. The bootstrap script asks about your AI systems, generates your documents, and installs automations.

### Manual

```bash
python3 /home/workspace/Skills/zo-iso-42001-aims/scripts/bootstrap.py
```

### Run Conformity Audit Manually

```bash
python3 /home/workspace/Skills/zo-iso-42001-aims/scripts/audit.py
```

## What Gets Created

| Artifact | Path | Purpose |
|----------|------|---------|
| AIMS Policy | `AIMS/AIMS_POLICY.md` | Governing principles, roles, review cycle |
| Statement of Applicability | `AIMS/STATEMENT_OF_APPLICABILITY.md` | 38 controls assessed: APPLIED/PARTIAL/EXCLUDED |
| AI Impact Assessment | `AIMS/AI_IMPACT_ASSESSMENT.md` | Risk matrix, individual + societal impacts |
| Handover Log | `AIMS/HANDOVER_LOG.md` | Version-controlled change tracking |

### Automations (Optional)

| Agent | Schedule | What It Does |
|-------|----------|-------------|
| AIMS Conformity Monitor | Monthly, 1st Sunday, 14:00 local | Audits all APPLIED controls, tracks PARTIAL gaps, checks policy review dates |
| Gap Closure Agent | Monthly, 1st Monday, 14:00 local | Closes one PARTIAL gap per month — creates the missing artefact, updates SoA + handover log |

## Prerequisites

- Zo Computer (free tier sufficient)
- 30 minutes for initial bootstrap
- Knowledge of your existing AI systems (what they do, where data comes from)

No API keys required. All processing is local-first.

## References

- `references/iso42001_overview.md` — What the standard covers, clause by clause
- `references/controls_reference.md` — All 38 Annex A controls explained in plain language
- `references/implementation_guide.md` — Step-by-step implementation walkthrough with examples

## After Bootstrap

Your AIMS is live. The conformity monitor runs monthly and emails you a report. Each month, the gap closure agent closes one PARTIAL control. Within 7 months, you reach 100% APPLIED conformity from a standing start.

Update `AIMS/AIMS_POLICY.md` whenever your AI ecosystem changes significantly. Re-run the impact assessment when adding new AI capabilities.
