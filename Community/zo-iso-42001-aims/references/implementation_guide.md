# Implementation Guide — ISO/IEC 42001:2023 AIMS

Step-by-step walkthrough for bootstrapping your AI Management System with this skill.

---

## Step 1: Run the Bootstrap Script

```bash
python3 /home/workspace/Skills/zo-iso-42001-aims/scripts/bootstrap.py
```

The script asks 12 questions about your ecosystem. Expect to spend 20-30 minutes. You'll need to know:

- What AI systems you run (LLMs, agents, automations, models)
- Where your data comes from (databases, PDFs, APIs, user uploads)
- Who operates the system and their domain expertise
- Your hardware/resources
- What the AI system is used for and by whom

The script generates all four baseline documents in `AIMS/`.

## Step 2: Review the Generated Documents

Open each document and verify accuracy:

1. **AIMS_POLICY.md** — Do the principles reflect your actual practices? Are roles correctly assigned?
2. **STATEMENT_OF_APPLICABILITY.md** — Are the APPLIED/PARTIAL/EXCLUDED classifications honest? Are target dates realistic?
3. **AI_IMPACT_ASSESSMENT.md** — Are all risks captured? Are severity ratings appropriate?
4. **HANDOVER_LOG.md** — Does it accurately log the initial baseline?

Edit freely. These are your documents. The templates are a starting point, not gospel.

## Step 3: Install the Automations

After reviewing, tell Zo:

```
install the AIMS conformity monitor and gap closure agent
```

Zo will create two monthly automations:
- **Conformity Monitor**: Runs 1st Sunday of each month at 14:00. Audits all APPLIED controls, checks policy review dates, verifies protocol documents exist, emails a report.
- **Gap Closure Agent**: Runs 1st Monday of each month at 14:00. Closes the next earliest PARTIAL gap. Creates missing documents, updates the SoA and Handover Log, emails a report.

## Step 4: First Audit

After the first month (or immediately, if you want a baseline):

```bash
python3 /home/workspace/Skills/zo-iso-42001-aims/scripts/audit.py
```

This runs the same audit the automated agent runs. Outputs a conformity report.

## Step 5: Maintain

### Monthly (Automatic)
- Conformity Monitor audits your AIMS
- Gap Closure closes one PARTIAL control

### Every 6-12 Months (Manual)
- Review `AIMS_POLICY.md` — does it still reflect reality?
- Re-read `AI_IMPACT_ASSESSMENT.md` — any new AI systems or risks?
- Check that all 27+ APPLIED controls still have valid evidence
- Update the review date in the policy document

### On System Change (Manual)
- New AI capability added → update impact assessment
- New data source → update provenance register, SoA
- New model/provider → supplier assessment
- Incident → log in HANDOVER_LOG.md, update impact assessment if needed

---

## Example: Single-Operator Engineering AI Ecosystem

Here's what a typical outcome looks like (this is the Wizaya reference implementation, anonymised):

**Ecosystem**: 26 agents, 12 ChromaDB collections, 13 autonomic cron loops, multi-tier LLM routing. Single operator (Chief Engineer). Used for engineering analysis, historical research, and tribology/lubrication diagnostics.

**Conformity Outcome**: 27 APPLIED, 7 PARTIAL, 4 EXCLUDED = 89% conformity from Day 1.

**7 PARTIAL gaps** with target closure dates spanning 1-7 months. After 7 months of Gap Closure agent runs, all controls reach APPLIED.

**Cost**: Zero. All processing is local. Conformity audit runs on local models.

---

## Example: Small Consultancy Using ChatGPT + Make

| Control | Assessment |
|---------|-----------|
| A.2.2 (AI Policy) | PARTIAL — no written policy. **Create one in 30 min.** |
| A.5.4 (Fairness) | PARTIAL — no bias check on outputs. **Add manual review step.** |
| A.10.3 (Suppliers) | PARTIAL — no assessment of OpenAI as supplier. **Write one-page assessment.** |

Most PARTIAL gaps are documentation, not technical work. The heaviest lift is writing down what you already know about your systems.

---

## Why This Approach Works

- **No consultants**: Self-assessment guided by plain-language controls
- **Living system**: Automations keep it current, not a one-time PDF that rots
- **Progressive**: 89% conformity on Day 1, 100% within 7 months via automated gap closure
- **Lightweight**: All files are Markdown. All processing is local. No SaaS lock-in.
- **Auditable**: Version-controlled handover log + monthly audit reports create an evidence trail

---

## FAQ

**Q: Do I need formal ISO certification?**
A: No. Conformity is self-declared. You can pursue third-party certification later if clients require it — this system provides the evidence base.

**Q: What if I have fewer than 26 AI agents?**
A: The bootstrap script adapts. A single ChatGPT integration with one automation is a valid scope. The 38 controls scale down to any size of AI operation.

**Q: What if I already have some policies?**
A: The templates can be merged with existing policies. The SoA assessment is the key — it shows which controls are already covered by your existing governance.

**Q: Do I need to keep all 4 documents?**
A: The Policy and SoA are minimum mandatory. Impact Assessment is needed if your AI affects individuals or society (almost always yes). Handover Log is recommended for tracking changes.

**Q: What about future ISO updates?**
A: ISO 42001 is Edition 1 (2023). The next systematic review is 2028. When the standard updates, update the controls reference and re-assess.
