# World configuration

What is configured in the Frontier Tuning environment, and where each piece comes from. Read live on 2026-10-09/10 🖥️. How to build all of this from scratch is in [world-builder/SETUP.md](../world-builder/SETUP.md) (steps P0–P10).

## The environments

| | `wce-main` (the climb) | `wce-dev` (trials) |
| --- | --- | --- |
| Environment ID | `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` | `6bec3bf9-0222-4285-8a5b-214867ac42cc` |
| Skill `warranty-assistant` | `cf00d339-5217-4cd1-b390-cc0d911735da` | `8e9d12a2-b0a5-4683-95f1-b225ed9ade44` |
| MCP registration `contoso-service` | `1c171d49-7f85-4997-8126-ae20829a4dbf` | `34d14238-…` |

The environment's own description and instructions: [world-builder/env.md](../world-builder/env.md).

## Knowledge sources (grounding)

| Source | Type | URL / location |
| --- | --- | --- |
| Warranty Operations | SharePoint folder | `https://microsoftapc.sharepoint.com/teams/ContosoFieldService/Warranty%20Operations` |
| Field Escalations | Teams channel | team `1d67f268-f548-46ec-b5d0-ce84dc68e032` |
| Warranty Policy Updates | Teams channel | same team |
| Partner Fabrikam | Teams channel | same team |

Check: `frontier-tuning knowledge list --env-id <env> -o json`. Labels (`Grounding` / `Training` / `Rules`, via `knowledge set-label`) are not set. 🔬 The tuning job reported `Reference files included: 0`; whether labels change what training sees is unverified.

### What is in the library

| Folder | Holds | Used for |
| --- | --- | --- |
| `01-Policy` | POL-WAR-4.2 (precedence, 24 mo / 6,000 h standard, missing records, pricing, goodwill), regional addenda (India ADD-IN-2.1: 18 mo / 5,000 h), Goodwill and Authority Matrix | The rules |
| `02-Bulletins` | 12 technical service bulletins (TSB-C-0051 extends cover to 36 mo / 8,000 h for serials 01200–01850) | Exceptions that beat the addendum |
| `03-RateCards` | Labour workbook (flat-rate hours per operation; rates by region and effective date) · parts price list with supersession | Valuation |
| `04-PartnerAgreements` | Partner terms (Northwind 5% uplift; Fabrikam none) | Uplift |
| `05-Reviews` | Quarterly review decks; **Q2 is stale** | A distractor |
| `06-ClaimEvidence` | Inspection reports by claim | Exclusions |
| `07-Reference` | Service manual extract, partner FAQ | Rarely needed |

Generated from `world-builder/spec/` into `world-builder/out/sharepoint/`; Teams messages are in `world-builder/out/teams/`.

## Tools

### Connectors on the environment

| Connector | Enabled | What the agent uses it for |
| --- | --- | --- |
| `contoso-service` (our MCP server) | ✅ | The claim system: one read, three draft writes |
| SharePoint | ✅ | Browse folders, read small files (`getFolderChildren`, `readSmallTextFile`, …) |
| Teams | ✅ | Search and read channel messages |
| Me | ✅ | Profile (not used for claims) |
| Word, OneDrive, M365Chat, Calendar, Email, fabriciq | ❌ | — |

Plus platform built-ins the agent also sees, e.g. `m365__search_enterprise_files` (the main document search), document text extraction, and a sandbox. About **110 tools** in all at evaluation time. Check: `frontier-tuning tools get <connector-id> -o json` (CLI ≥ 1.0: `tools discover`).

### The claim-system tools (MCP server)

| Tool | Kind | Does |
| --- | --- | --- |
| `get_claim_dossier(claim_id)` | Read | Everything the claim system holds for one claim: claim, asset (commissioning date may be missing), running hours at the repair date, service history (`part_fitted`), related claims, partner (`uplift_pct`, `agreement_ref`), parts (supersession, prices), the bulletin index (**deliberately stale** on TSB-C-0051), and the goodwill authority matrix. Records only, no guidance. ~2–4k characters |
| `create_claim_adjudication` | Draft write | Records a draft decision. Returns "No payment has been made" |
| `request_missing_evidence` | Draft write | Records an evidence request; sets the claim to **Held** |
| `escalate_goodwill` | Draft write | Records a request for authority; does not grant it |

Nothing pays, sends or notifies. Code: [world-builder/mcp/](../world-builder/mcp/README.md). Hosted on Azure Container Apps (`contoso-service-mcp`, South India, 5 replicas, stateless), endpoint `https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/mcp`, health at `/healthz`. Registered `NoAuth` (endpoint auth deferred).

⚠️ The tools carry no MCP annotations (no `readOnlyHint`). 🖥️ The tuning job excluded 36 tools as "can make changes", and the claim-system tools never appeared in training rollouts. See [P7](06-platform-issues.md#p7-tuning-excludes-the-claim-system-tools).

### The claim database

Azure SQL `az-sqldb-common` / `contoso-warranty`, Entra-only sign-in. Seed: `world-builder/out/db/`. The agent's writes land in three action tables (`ClaimAdjudicationDraft`, `EvidenceRequest`, `GoodwillEscalation`) and may change a claim's status. They are reset between runs: [05-operations.md](05-operations.md#the-claim-database).

## The skill

One skill, `warranty-assistant`. The instructions are a **business brief**: what to establish (decision, governing instrument, coverage period, payable, next action), which sources exist, and how to write for an adjudicator. It contains no method, tool names or rules; the rules are in the policy documents. Current text: [climb/stage-0/config/skill.md](../climb/stage-0/config/skill.md).

## The rubrics (the grader's checklist, and the RFT reward)

Six hand-written rubrics, each a binary checklist scored 0–1:

| Rubric | Importance | Checks, in short |
| --- | --- | --- |
| Coverage determination | critical | Outcome stated; limits named; repair date and hours compared |
| Precedence discipline | critical | One governing instrument, justified; superseded or out-of-range bulletins rejected; document over index |
| Evidence grounding | high | Every term, date, rate attributed to its source; nothing invented |
| Valuation accuracy | critical | When covered: labour cap, rate on repair date, part fitted, uplift only if granted, total and variance |
| Authority and action | critical | Next action and owner; goodwill above authority escalated; chat approval not treated as authority; draft recorded |
| Gaps reported, not filled | high | Names a missing record and the absent field instead of guessing |

Full text: [climb/stage-0/config/rubrics.md](../climb/stage-0/config/rubrics.md). `RedFlags` lists are empty on all six.

## Samples

| Set | Count | Type | Used for |
| --- | --- | --- | --- |
| Evaluation | 30 claims (C-2026-041xx) | `Evaluation` | Every stage's measurement. Never used for refinement or training |
| Training | 60 different claims | `Training` | `skills refine` and `tune start` only. 🖥️ The tuning job took these 60 (54 train / 6 validation) |

A sample is only a prompt, e.g. `{"Prompt": "Adjudicate claim C-2026-04101."}`. 📄 Samples can't carry their own rubrics or expected answer; the grader uses the skill's rubrics. Samples **capture the rubrics at upload**, so changing the rubrics means re-uploading the samples.

**The `*-sample-ids.json` files** map each claim number to the platform's sample ID, e.g. `{"claim": "C-2026-04101", "id": "90dfe727-…"}`. `evaluate start --sample-id` needs the IDs; the scorer and reports need the claim numbers. Without the map, results can't be matched to the answer key.

## Models

| Role | Model ID | Display name |
| --- | --- | --- |
| Frontier reference | `prod-gpt-56-reasoning-sol` | GPT-5.6-Sol |
| Climbing model (evaluation) | `dev-ct-mai-code-mp` | MAI-CODE-5b |
| Tuning base | `mai-code-1-flash` | MAI-Code-1-Flash |
| Grader | undisclosed, chosen by the platform | — |

🔬 Whether `dev-ct-mai-code-mp` and `mai-code-1-flash` are the same weights is unverified.
