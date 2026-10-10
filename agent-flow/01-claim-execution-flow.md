# How the agent processes a warranty claim

A business-level walk-through of what the agent does between *"Adjudicate claim C-2026-04114"* and the answer an adjudicator reads. Written from the repository's own files and from recorded runs.

Legend: 🖥️ measured on this tenant · 💭 reasoning / design intent · 🔬 unverified. Tool names are the real ones seen in recorded runs.

---

## 1. The idea in one minute

The agent behaves like a junior adjudicator with a good filing system:

1. **Read the claim file** (one database call).
2. **Look up the rules that apply to *this* machine** in the document library (1–3 searches).
3. **Do the arithmetic**: is the repair inside the coverage window, and what is payable?
4. **Check chat only when money outside warranty is requested** (goodwill).
5. **Record a draft decision** in the claim system (nothing is paid or sent) and **write up the answer** for the human adjudicator.

No step is hard-coded. The documents and the claim's own facts decide which path is taken.

| | |
| --- | --- |
| **Decides** | Approve · Decline · Escalate for goodwill · Request evidence (hold) |
| **Never does** | Pay, notify a partner, or grant goodwill. It writes **drafts** a human reviews |
| **Quality gate** | Ground truth (decision, governing instrument, payable) **and** six hand-written rubrics ([stage 1](../stages/stage-1/rubrics.md)) |

---

## 2. The four places the agent can look

| Source | Holds | Reached through | Trusted for |
| --- | --- | --- | --- |
| **Claim system** (Azure SQL, via our MCP server) | The claim, asset, commissioning date, running hours, service history, partner terms, part records, a bulletin index, the goodwill authority matrix | `get_claim_dossier` (read) · `create_claim_adjudication`, `request_missing_evidence`, `escalate_goodwill` (draft-only writes) | **Facts about this claim and machine**. Not rules |
| **SharePoint library** `Warranty Operations` | Controlled documents, by folder (below) | M365 file search (`search_enterprise_files`), plus SharePoint browse tools | **The rules and the prices** |
| **Teams channels** (Field Escalations, Warranty Policy Updates, Partner Fabrikam) | Conversations, announcements, verbal approvals | Teams search tools | **Context only**. Never authority |
| **The skill** ([warranty-assistant.md](../stages/stage-0/warranty-assistant.md)) | The job, the five things to establish, how to write the answer | Loaded at start | **The brief**, not the rules |

The library folders and what each is used for:

| Folder | Used for |
| --- | --- |
| `01-Policy` | **POL-WAR-4.2** (precedence, standard 24 mo / 6,000 h, missing records, pricing, goodwill), regional **addenda** (India: 18 mo / 5,000 h), the **Goodwill and Authority Matrix** |
| `02-Bulletins` | 12 technical bulletins. TSB-C-0051 extends 4000-series hydraulic + compressor cover to 36 mo / 8,000 h for serials 01200–01850 |
| `03-RateCards` | One workbook: **flat-rate hours** per operation, **labour rates** by region and effective date. A second workbook: **parts prices** and supersession |
| `04-PartnerAgreements` | Whether the partner gets a handling uplift (Northwind 5%, Fabrikam none) |
| `05-Reviews` | Quarterly decks. **Q2 is stale** (still says "24 months") |
| `06-ClaimEvidence` | Inspection reports, by claim number. Needed only when an exclusion turns on them |
| `07-Reference` | Service manual extract, partner FAQ. Rarely needed |

### Who wins when sources disagree

| Conflict | Winner | Where the rule is written |
| --- | --- | --- |
| Bulletin vs India addendum vs global policy | **Bulletin that names the serial** ▸ addendum ▸ policy | POL-WAR-4.2 §1.4 |
| Claim-system bulletin index vs the bulletin document | **The document**. The index is reporting only | POL-WAR-4.2 §1.4 |
| Superseded bulletin vs its replacement | **The replacement**. The old one has no effect | POL-WAR-4.2 §1.4 |
| Q2 deck vs the bulletin | **The bulletin** | Q3 deck, Teams announcement |
| Teams "go ahead and cover it" vs the matrix | **Recorded authority in the claim system, at the right tier** | POL-WAR-4.2 §7.1 |
| Part ordered vs part fitted | **Part fitted**; if superseded, the **new** part's price | POL-WAR-4.2 §4.2 |
| Repair date vs submission date for the labour rate | **Repair date** | POL-WAR-4.2 §4.1, rate card notes |

---

## 3. What the skill tells the agent, and what it does not

🖥️ The skill used in stages 0 and 1 is a **business brief**. It has no method, no tool names and no rules ([stage 0](../stages/stage-0/warranty-assistant.md); stage 1 is identical).

| The skill says | Effect on the flow |
| --- | --- |
| Establish five things: **covered / declined / undecidable**, **which instrument governs and why**, **the coverage period and where the repair falls**, **amount payable (labour, parts, partner terms, currency)**, **next action and who takes it** | These five become the checklist the answer must fill |
| Work from the library, the channels and the claim system | Tells the agent the three sources exist |
| Lead with the decision; show dates and working; **cite where each fact came from**; flag gaps and disagreements | Shapes the write-up |
| Where an action is needed, **record it as a draft** and say so | Triggers the final write tool |

**Everything else comes from the documents.** The skill never says "check the serial range" or "the bulletin beats the addendum". The policy does ([JOURNEY §1](../docs/JOURNEY.md)). Reading it and applying it is the competence being measured.

💭 The step order below is therefore **the intended path**: what the five questions plus the policy lead to. [Stage 2b](../stages/stage-2/warranty-assistant.2b.md) wrote the order down as method (dossier first, then read the policy's precedence clause, then the bulletin, then the rate card, then record the draft). It regressed correctness and was **not** promoted, so the stage 0/1 agent has to work the order out itself.

---

## 4. The flow

```text
 Request names a claim number
            |
            v
 [A] get_claim_dossier  (1 call: claim, asset, hours, history, partner, parts, index, matrix)
            |
            v
 Commissioning date, or running hours, missing?
     |                                   |
    YES                                  NO
     |                                   |
     v                                   v
 request_missing_evidence        [B] Find the rules for THIS asset
 (claim is HELD, not declined)       - policy clause 1.4 (precedence)
     |                               - the region's addendum
     |                               - a bulletin naming this serial and component
     |                                   |
     |                                   v
     |                           [C] Test coverage
     |                               months from COMMISSIONING and running hours at repair
     |                               (either limit ending cover = outside)
     |                                   |
     |                    +--------------+---------------+
     |                    |                              |
     |                 OUTSIDE                        INSIDE
     |                    |                              |
     |                    v                              v
     |          Goodwill requested?              [D] Value the claim
     |            |             |                   flat-rate hours (cap) x labour rate on repair date
     |           NO            YES                   + part FITTED (follow supersession)
     |            |             |                   + uplift only if the agreement grants it
     |            |             v                       |
     |            |      [E] Teams: note any verbal     v
     |            |          OK (not authority);   draft: APPROVE with payable
     |            |          pick tier from matrix
     |            |             |
     |            v             v
     |      draft: DECLINE   escalate_goodwill + draft: ESCALATE
     |            |             |                       |
     +------------+-------------+-----------------------+
                                |
                                v
              [F] Write the answer for the adjudicator
                  decision first, dates and working, sources, gaps, next action and owner
```

Letters [A]–[F] correspond to steps 1, 3, 4, 5, 6 and 8 in the table below.

### Step by step

| # | Step | What the agent does | Tool | Calls |
| --- | --- | --- | --- | --- |
| 1 | **Read the claim file** | Pulls the claim, asset, running hours at the repair date, service history, partner, parts, bulletin index and authority matrix in **one** response (~2–4k characters) | `get_claim_dossier(claim_id)` | 1 |
| 2 | **Triage from the dossier** | Decides which documents matter (see the table below). If a record is missing, jumps to step 7 | none, reasoning only | 0 |
| 3 | **Find the governing rule** | Reads the policy's precedence clause, the region's addendum, and the bulletin whose serial range takes in this asset | file search, scoped to `01-Policy` / `02-Bulletins` | 1–3 |
| 4 | **Test coverage** | Counts months from commissioning (not install date) to the repair date, and compares running hours **at or before** the repair date with the hours limit. **Either** limit ending cover means out | none, arithmetic | 0 |
| 5 | **Value the claim** (covered only) | Looks up flat-rate hours and the labour rate in force on the **repair date** in one workbook; prices the part **fitted**; adds a handling uplift only if the partner's agreement grants one | file search, scoped to `03-RateCards` (+ `04-PartnerAgreements` if confirming uplift) | 1–2 |
| 6 | **Check chat** (goodwill only) | Finds the thread, notes any verbal approval, states it is **not authority**, reads the tier from the matrix | Teams search | 0–1 |
| 7 | **Record one draft** | Writes the decision once | `create_claim_adjudication`, or `request_missing_evidence`, or `escalate_goodwill` (+ the draft) | 1–2 |
| 8 | **Write the answer** | Decision first, dates and working, source for each fact, gaps and disagreements, next action and owner | none | 0 |

### How the dossier steers step 2

| What the agent sees in the dossier | What it does next |
| --- | --- |
| `commissioning_date_missing: true` | **Stop.** Do not use the install date (policy §2.3). Request the commissioning certificate; claim is held |
| No running-hours reading **and** time limit not yet passed | **Stop.** Hours limit cannot be tested. Request the reading |
| `region: India` | Read **ADD-IN-2.1** (18 mo / 5,000 h). EMEA/APAC have their own addenda |
| `family` + `serial` + operation code (gives the component) | Search for a bulletin whose serial range **and component scope** fit. TSB-C-0051 covers hydraulic and compressor, **not** controls |
| `tsb_applicability_index` says *out of range* | Do **not** trust it. Read the bulletin document; if they disagree, the document wins and the answer says so |
| `goodwill_requested` has an amount | Prepare to **escalate**, not approve. Pick the tier from `goodwill_authority_matrix` |
| `service_history` shows a different `part_fitted` than `claimed_part` | Price the part **fitted**, and follow supersession in `parts` |
| `service_partner.uplift_pct` and `agreement_ref` | Uplift only if the percentage is non-zero **and** the agreement grants it |
| `related_claims` | Check whether a repair on the same component was completed in the last 90 days (repair warranty, §6.1) |

---

## 5. Why the tool-call count stays small, and what is really measured

### What "consolidated" means here

| Consolidation | Before (world v2) | Now (world v3) |
| --- | --- | --- |
| **One dossier call** | Nine claim-system reads (claim, asset, hours, history, prior claims, partner, part, bulletin index, authority) | `get_claim_dossier`, ~2–4k characters |
| **One labour workbook** | Two files (flat-rate hours; rates by region) | One workbook, two sheets |
| **Folder-scoped search** (stage 2b guidance only; the stage 1 runs recorded 0 scoped searches) | Whole-library searches returned large, mixed results | Search inside the one folder that holds the document type |
| **One write** (a rule in the stage 2b guidance, not yet observed to hold) | n/a | Record the draft once, after the conclusion |

I found no other consolidation mechanism in the repository. The agent is not summarising or compressing results; the **world was redesigned to need fewer, smaller calls**.

### The numbers

| | Designed (💭) | Measured, naive skill (🖥️) |
| --- | --- | --- |
| Calls per claim | **~4–6** | stage 0 median **10** (range 2–32) · stage 1 mean **16.1** |
| Where calls go | dossier + 1–3 searches + 0–1 Teams + 1 draft | Mostly **searching**: stage 1 mean 9.2 of 16.1 calls are file searches; 4.3 are claim-system calls |
| Context overflows (MAI-CODE-5b) | 0 | **0** in stages 0 and 1 (world v2 failed at ~230–275k characters of tool output) |

⚠️ The 4–6 figure is the **minimum path**, not what the model achieves today. Closing that gap (wandering, repeated reads, failed searches) is what stages 2 and 4 are about.

💭 **Where the context really goes.** The dossier is cheap (~4k characters). A single document search returns **2k–33k characters**. Context pressure comes from search results, which is why the 2b guidance scopes searches to one folder. In stages 0 and 1 the agent searched the whole library and still stayed under the limit.

### Expected path by claim type 💭

| Type of claim | Calls | Path |
| --- | --- | --- |
| **Missing record** (abstention) | ~3 | dossier → policy §2.3 → `request_missing_evidence` |
| **Plain decline** | ~4 | dossier → addendum (+ bulletin check) → draft decline |
| **Covered, simple** | ~5 | dossier → addendum → rate card → draft approve |
| **Covered under a bulletin** | ~5–6 | dossier → policy §1.4 + bulletin → rate card → draft approve |
| **Goodwill beyond cover** | ~5–6 | dossier → addendum → Teams → `escalate_goodwill` + draft |

---

## 6. One claim from start to finish: C-2026-04114

Fabrikam Service Partners, Litware Pune. Hydraulic pump replaced 2026-06-18. **Expected: approve, TSB-C-0051, ₹199,175.**

| Call | The agent asks | It sees | It concludes and does next |
| --- | --- | --- | --- |
| 1 `get_claim_dossier` | Claim file | India asset **CIE-4000-CH-01700**, 4000-CH, commissioned **2024-04-04** (install 2024-03-12), repair **2026-06-18**, **4,120 h** (reading 2026-06-04), op `HYD-PUMP-RR` 5.5 h, part **P-44120-A** fitted, Fabrikam **uplift 0%**, index says TSB-C-0051 ends at serial **1500** (this is 1700: "out of range") | Commissioning present, so coverage is decidable. India addendum applies *unless* a bulletin names serial 01700. Need the bulletin text, the rate card, and the partner agreement |
| 2 search `02-Bulletins` | Does a bulletin name serial 01700? | **TSB-C-0051**: 01200–01850, effective 2026-01-15, hydraulic + compressor, **36 mo / 8,000 h**, "this bulletin governs over the index" | Index (1500) is stale; the document (1850) wins (§1.4). TSB beats the India addendum. Instrument = **TSB-C-0051** |
| 3 search `01-Policy` | Does §1.4 say what I think? | Precedence: bulletin ▸ addendum ▸ policy; document beats index | Confirms step 2. Cite §1.4 |
| 4 reasoning | Coverage test | 2024-04-04 + 36 mo = **2027-04-04**; repair 2026-06-18 is inside. 4,120 h < 8,000 h | **Covered.** For contrast, the India addendum alone gives 2025-10-04, and the claim would be wrongly declined |
| 5 search `03-RateCards` | Flat-rate hours and the rate on the repair date | `HYD-PUMP-RR` = 5.5 h; India **₹1,450/h** from 2026-04-01 (₹1,320 before) | Labour = min(5.5 claimed, 5.5 allowed) × 1,450 = **₹7,975** |
| 6 reasoning | Parts and uplift | P-44120-A list **₹191,200**; Fabrikam agreement grants no uplift | Parts **₹191,200**, uplift **₹0**. Total **₹199,175** |
| 7 `create_claim_adjudication` | Record the draft | `approve`, ₹199,175 INR, refs TSB-C-0051 and POL-WAR-4.2 §1.4 | Draft recorded. "No payment has been made" |
| 8 answer | Write for the adjudicator | | Decision first · facts and dates · working for the amount · sources · **the index disagrees with the bulletin, bulletin governs** · next action: adjudicator reviews and releases the draft |

**What a recorded run did** 🖥️ (stage 2b skill, [results file](../docs/evidence/stage-2/2b/results-04114+04115+04116+04117+04118.json)): correct decision, instrument and amount (approve, TSB-C-0051, ₹199,175, and it noted the index lag). It took **10 calls**: the dossier, seven search or browse calls (several returned empty results before one worked), and **two** draft writes. The reasoning matched the table; the efficiency did not.

**A recorded plain decline, C-2026-04109** 🖥️ (stage 1): dossier (read twice), one policy/bulletin search, one rate-card search, one draft. 5 calls, correct (decline, ADD-IN-2.1, ₹0). It states: commissioned 2023-06-01 + 18 months = 2024-12-01, and 5,200 h > 5,000 h; serial 01900 is outside TSB-C-0051's range.

---

## 7. Where each trap bites in the flow

| Decision point | Trap | The mistake it invites |
| --- | --- | --- |
| Step 2 | **12 · Missing record** | Substituting the install date, or guessing |
| Step 3 | **1 · Stale index** | Trusting the database over the bulletin document |
| Step 3 | **2 · Precedence** | Stopping at the India addendum, which declines a valid claim |
| Step 3 | **4 · Serial boundary** | Off-by-one at 01199 / 01200 / 01850 / 01851 |
| Step 3 | **5 · Superseded bulletin** | Using TSB-P-0107 instead of TSB-P-0112 |
| Step 3 | **6 · Stale deck** | Quoting Q2's "24 months" |
| Step 4 | **3 · Dual limit** | Checking months only; hours can end cover first |
| Step 5 | **7 · Part supersession** | Pricing the part ordered, not fitted |
| Step 5 | **8 · Uplift asymmetry** | Applying Northwind's 5% to Fabrikam, or omitting it for Northwind |
| Step 5 | **9 · Rate date** | Using the submission date's rate |
| Step 5 | **10 · Flat-rate cap** | Paying claimed hours above the allowance (and not stating the variance) |
| Step 6 | **11 · Verbal authority** | Treating "go ahead, I'll sort the paperwork" as approval |

Full definitions: [scenario design §7](../world-builder/docs/03-scenario-design.md).

---

## 8. What the finished answer must contain

| Section | Content | Graded by |
| --- | --- | --- |
| **Decision** (first line) | Approve / decline / escalate / hold | Ground truth + *Coverage determination* |
| **Governing instrument and why** | e.g. TSB-C-0051, because it names the serial; clause cited | Ground truth + *Precedence discipline* |
| **Dates and facts** | Commissioning date, expiry, hours at repair, **with source** | *Evidence grounding* |
| **Amount payable** | Labour × rate + parts + uplift, with working and currency; variance if hours were capped | Ground truth + *Valuation accuracy* |
| **Next action and owner** | e.g. "Regional Service Manager records goodwill authority" | *Authority and action* |
| **Gaps and conflicts** | Missing records; index vs document; Teams chatter that is not authority | *Gaps reported, not filled* |

Ground truth is computed by [adjudicate.py](../world-builder/build/adjudicate.py) and checked by [score_ground_truth.py](../scripts/score_ground_truth.py).

---

## 9. Honest notes

| Note | Detail |
| --- | --- |
| **The skill is thin by design** | Stages 0/1 give no method. Correct today: **23/30** (stage 0 and 1). Misses cluster on authority (0/2), dual-limit (1/3) and stale-deck (1/2) |
| **Authority is the weakest path** 🖥️ | Both goodwill claims were declined instead of escalated in stage 0 |
| **Wandering** 🖥️ | Repeated dossier reads, browsing folders, empty searches, duplicate draft writes |
| **Echoed hand-ins** 🖥️ | On some runs the model handed in the question as its answer. A platform/model hand-in failure, not reasoning |
| **Teams thread mismatch** 🔬 | The verbal-approval thread in Field Escalations is titled **C-2026-04141** (serial 01950). The goodwill eval claims are **04171** and **04172** (serial 01960, 01962). A claim-number search will not find it; only context (Litware Pune, Fabrikam, seized pump, over flat rate) will. Whether this helps or hurts the agent is not measured |
| **What this document is not** | It is the intended flow. Per-claim recorded behaviour is in each stage's `run-summary.md`. Per-question paths come next |
