# ISO/IEC 42001:2023 — Annex A Controls Reference

All 38 controls explained in plain language. Use this to assess your own AI ecosystem.

---

## A.2 — POLICIES RELATED TO AI

| Control | What It Means | How To Satisfy |
|---------|---------------|----------------|
| **A.2.2** AI policy | You need a written document stating your principles, commitments, and rules for AI | Create `AIMS_POLICY.md` — the template covers this |
| **A.2.3** Alignment with other policies | Your AI policy must reference your other policies (security, quality, privacy) | List your existing policies in the policy's §6 |
| **A.2.4** Review of AI policy | You must review and update the policy on a schedule | Set a 6- or 12-month review cycle. Document the next review date. |

---

## A.3 — INTERNAL ORGANISATION

| Control | What It Means | How To Satisfy |
|---------|---------------|----------------|
| **A.3.2** AI roles and responsibilities | Someone must own AI governance. Roles must be defined. | Assign: AI System Owner, Auditor, and any domain-specific roles |
| **A.3.3** Reporting of concerns | There must be a way for people to report problems with AI systems | Create a reporting channel — even a simple email address or form counts |

---

## A.4 — RESOURCES FOR AI SYSTEMS

| Control | What It Means | How To Satisfy |
|---------|---------------|----------------|
| **A.4.2** Resource documentation | Document what resources your AI systems use | List your hardware, databases, models, and tools |
| **A.4.3** Data resources | Document what data your AI systems consume and produce | Describe your datasets — origin, size, type |
| **A.4.4** Tooling resources | Document the tools used to build/run AI | List frameworks, libraries, services |
| **A.4.5** System and computing resources | Document your compute infrastructure | CPU, RAM, GPU, storage, networking |
| **A.4.6** Human resources | Document who is competent to operate/manage the AI system | List domain expertise of operators |

---

## A.5 — ASSESSING IMPACTS OF AI SYSTEMS

| Control | What It Means | How To Satisfy |
|---------|---------------|----------------|
| **A.5.2** Impact assessment process | You need a documented process for assessing AI impacts | Create and follow `AI_IMPACT_ASSESSMENT.md` |
| **A.5.3** Documenting impact assessments | Each assessment must be written down and retained | Save assessments with dates, keep them accessible |
| **A.5.4** Fairness assessment | Assess whether your AI system treats people fairly | Check for bias in training data, outputs, and access |
| **A.5.5** Societal impact assessment | Assess wider societal effects (environmental, economic, cultural) | Document per Annex B.5.5 categories |

---

## A.6 — AI SYSTEM LIFE CYCLE

| Control | What It Means | How To Satisfy |
|---------|---------------|----------------|
| **A.6.1.2** Objectives for responsible development | State what "responsible" means for your development process | Principle statements in your AI policy |
| **A.6.1.3** Processes for responsible design | Have documented design and development processes | System architecture docs, AGENTS.md |
| **A.6.2.2** AI system requirements and specification | Document what your AI systems must do | Requirements docs, protocol documents |
| **A.6.2.3** Documentation of design and development | Record how systems were designed and built | Architecture diagrams, design decisions log |
| **A.6.2.4** Verification and validation | Prove your AI does what it should, correctly | Automated tests, manual review, fact-checking |
| **A.6.2.5** Deployment | Have a deployment process | Use managed deployment (Zo services/agents) |
| **A.6.2.6** Operation and monitoring | Monitor your AI systems in production | Logging, health checks, alerting |
| **A.6.2.7** Technical documentation | Keep technical docs current | AGENTS.md, SOUL.md, protocol files |
| **A.6.2.8** Event logging | Log significant AI system events | Guardian logs, operation logs, error logs |

---

## A.7 — DATA FOR AI SYSTEMS

| Control | What It Means | How To Satisfy |
|---------|---------------|----------------|
| **A.7.2** Data for development and enhancement | Manage data used to build or improve AI | Data pipeline documentation |
| **A.7.3** Acquisition of data | Know where your data comes from and that you have rights to it | Document data sources, licenses, acquisition methods |
| **A.7.4** Quality of data | Your data must be fit for purpose | Track completeness, accuracy, freshness metrics |
| **A.7.5** Data provenance | Know the full chain from origin to use | Provenance register: origin→acquisition→transformation |
| **A.7.6** Data preparation | Document how raw data becomes AI-ready | Cleaning, chunking, embedding processes |

---

## A.8 — INFORMATION FOR INTERESTED PARTIES

| Control | What It Means | How To Satisfy |
|---------|---------------|----------------|
| **A.8.2** System documentation for users | Users must have access to understandable system docs | README, AGENTS.md, user guides |
| **A.8.3** External reporting | If you have external stakeholders, report to them | N/A for internal-only systems — can exclude |
| **A.8.4** Communication of incidents | Have a plan for communicating when things go wrong | Incident communication protocol document |
| **A.8.5** Information for interested parties | Make docs available to stakeholders | If no external stakeholders, can exclude |

---

## A.9 — USE OF AI SYSTEMS

| Control | What It Means | How To Satisfy |
|---------|---------------|----------------|
| **A.9.2** Processes for responsible use | Have rules for how AI systems are used day-to-day | Usage policy, tiered access, approval gates |
| **A.9.3** Objectives for responsible use | State what responsible use looks like | In your AI policy §2 |
| **A.9.4** Intended use | Document what the AI system is supposed to do (and not do) | Scope statement, use-case documentation |

---

## A.10 — THIRD-PARTY AND CUSTOMER RELATIONSHIPS

| Control | What It Means | How To Satisfy |
|---------|---------------|----------------|
| **A.10.2** Allocating responsibilities | Clarify who is responsible when third parties are involved | For internal-only systems, can exclude |
| **A.10.3** Suppliers | Assess your AI suppliers (model providers, data providers, tool vendors) | Supplier assessment document |
| **A.10.4** Customers | If you serve external customers, manage the relationship | For internal-only systems, can exclude |

---

## Quick Assessment Checklist

Go through these 38 items and mark each APPLIED, PARTIAL, or EXCLUDED. For PARTIAL items, set a target closure date. The bootstrap script automates this.
