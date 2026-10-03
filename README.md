# Contoso Industrial — warranty adjudication RLE

A Microsoft 365 Frontier Tuning world: a synthetic warranty-adjudication domain
with a deterministic ground-truth engine, a document corpus, a database, an MCP
server, and evaluation samples.

Start with [docs/](docs/README.md). The design rationale is in
[docs/03-scenario-design.md](docs/03-scenario-design.md); build and provisioning
steps are in [docs/04-walkthrough.md](docs/04-walkthrough.md).

Everything here is **synthetic**. Fictional companies, fictional serial numbers,
fictional money. No customer or private content.

---

## The rule this directory exists to enforce

> **One set of numbers, one arbiter.** Every Word document, spreadsheet, deck,
> database row and sample is *generated from* `spec/`, and every expected answer
> is *computed by* `build/adjudicate.py`. Nothing is hand-written twice.

The alternative — authoring documents first and reconciling them afterwards —
produces a corpus that silently contradicts itself. A model then gets marked
wrong for reading the corpus correctly, the rubric scores become noise, and
under RFT that noise is trained in. This is design principle 7 in guide 03, and
it is why the engine was built before a single document.

---

## Layout

```text
contoso-warranty-rle/
├── docs/                      design, walkthrough, runbook, cross-cutting references
├── spec/                      the source of truth - hand-authored, reviewed
│   ├── entities.json          manufacturer, families, partners, customers, people, authority tiers
│   ├── instruments.json       policy clauses, regional addenda, 12 bulletins
│   └── catalog.json           operations and flat rates, labour rates, parts and supersession
├── build/
│   ├── adjudicate.py          the ground-truth engine + worked-example self-test
│   ├── test_traps.py          one assertion set per trap in guide 03 section 7
│   ├── populate.py            assets, telemetry, claims - with a conformance gate
│   ├── ground_truth.py        renders out/GROUND-TRUTH.md
│   ├── gen_docs.py            34 Word documents
│   ├── gen_sheets.py          3 Excel workbooks
│   ├── gen_decks.py           2 PowerPoint decks
│   └── gen_teams.py           3 Teams channels
├── mcp/                       the MCP server - 9 read + 3 action tools, ACA deploy
└── out/                       generated artefacts (committed, reproducible from spec/)
    ├── data/                  assets.json, telemetry.json, claims.json
    ├── sharepoint/            the document corpus, ready to upload
    ├── teams/                 channel content as JSON, ready to post
    ├── db/                    schema+seed .sqlite.sql and .azuresql.sql, contoso.db
    ├── samples/               eval / train / smoke JSONL + UPLOAD.md
    └── GROUND-TRUTH.md        the human audit trail
```

## Status

| Step | Output | Status |
| --- | --- | --- |
| 1. Canonical spec | `spec/*.json` | ✅ Authored |
| 2. Ground-truth engine | `build/adjudicate.py` | ✅ **14/14 self-test checks pass** — guide 03 § 8 reproduces at ₹199,175 |
| 3. Trap validation | `build/test_traps.py` | ✅ **31/31 checks pass** across all 12 traps |
| 4. Asset + claim population | `out/data/` — 120 assets, 3,101 telemetry rows, 86 claims | ✅ **Design conformance OK** — 30 eval / 56 train, all four decision types |
| 5. `GROUND-TRUTH.md` | `out/GROUND-TRUTH.md` — 990 lines, full working per eval claim | ✅ Generated |
| 6. Word documents | `out/sharepoint/` — **34 documents** across 6 folders | ✅ Generated |
| 7. Excel workbooks | `out/sharepoint/03-RateCards/` — 3 workbooks, 54 parts | ✅ Generated |
| 8. PowerPoint decks | `out/sharepoint/05-Reviews/` — Q2 (stale) and Q3, 6 slides each | ✅ Generated |
| 9. Teams threads | `out/teams/` — 3 channels, 14 threads, 31 messages | ✅ Generated |
| 10. Database seed | `out/db/` — 11 tables in **two dialects**: SQLite + Azure SQL T-SQL | ✅ **trap 1 armed** — index says 1500, document says 1850 |
| 11. MCP server | `mcp/` — 9 read + 3 action tools, ODBC image, ACA + Azure SQL deploy guide | ✅ **37/37 checks pass** |
| 12. Samples | `out/samples/` — 30 eval, 60 train, 3 smoke | ✅ Generated |

## Running the checks

Create a virtual environment first:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then, from `build/`:

```powershell
cd build
..\.venv\Scripts\python.exe adjudicate.py      # worked example, 14 checks
..\.venv\Scripts\python.exe test_traps.py      # all traps, 31 checks
..\.venv\Scripts\python.exe populate.py        # population + conformance gate
..\.venv\Scripts\python.exe ground_truth.py    # renders out/GROUND-TRUTH.md
..\.venv\Scripts\python.exe gen_docs.py        # 34 Word documents
..\.venv\Scripts\python.exe gen_sheets.py      # 3 Excel workbooks
..\.venv\Scripts\python.exe gen_decks.py       # 2 PowerPoint decks
..\.venv\Scripts\python.exe gen_teams.py       # 3 Teams channels
```

Run in that order — the document generators read `out/data/`, so the population
has to exist first.

The first two must pass before any artefact is generated — they are the contract
between the design and the corpus. `populate.py` exits non-zero if the trap
distribution drifts from guide 03 § 10, so the eval set cannot quietly lose a
slice.

---

## Why the engine comes first

Three things it buys, none of which are obvious until they are missing:

| | |
| --- | --- |
| **The traps are proven buildable** | A trap that cannot be expressed as a passing assertion is not a trap, it is an ambiguity. Two candidates were cut at this stage rather than discovered later as unanswerable samples |
| **Ground truth is free** | 75 claims in, 75 expected adjudications out — with the governing instrument, the payable amount and the traps each one exercises. Hand-computing those is where a week disappears |
| **The corpus can be checked against itself** | Documents are rendered from the same clause text the engine reasons over, so a rate card and a policy cannot drift |

## Design notes worth knowing before reviewing `spec/`

| Choice | Why |
| --- | --- |
| The India addendum is **shorter** than base policy (18 months vs 24) | A model that assumes a regional variation is always more generous fails. Regional terms being *worse* than global is common and counter-intuitive — exactly the shape of trap worth having |
| `TSB-P-0112` **narrows** the range it inherits from `TSB-P-0107` (900 → 750) | Assets at 751–900 were covered and are no longer. Reading only the old bulletin over-pays; merging both over-pays; reading only the new one is right |
| `TSB-C-0043` reverses an exclusion but sets **no coverage period** | Breaks the assumption that every bulletin is a coverage extension. It is considered but never governs the term |
| The applicability index in the database is **stale on purpose** (`index_serial_to: 1500` vs a document saying 1850) | Trap 1. The tool description will say the index is informational — the trap is whether the model acts on that, not whether it was told |
| Nothing in the action surface is irreversible | Every action tool writes a draft. Nothing sends, pays or notifies |

⚠️ A deliberately rejected trap: a unit mismatch between two telemetry tables.
It produces defensible disagreement about the right answer, which corrupts the
rubric *and* the training signal. Difficulty is welcome; ambiguity is not.

---

## Two bugs the engine caught before they became samples

Both surfaced while generating the population, and both would have shipped as
silently-wrong samples if the corpus had been authored first.

**A serial collision destroyed the abstention slice.** The valuation slice had
already claimed serial `CIE-4000-CH-01560`, so when the abstention slice asked
for that serial *without* a commissioning date, it got back the existing asset —
which had one. Two of three abstention samples approved instead of abstaining,
and nothing reported it. `asset()` now raises on a conflicting redefinition
rather than silently returning the incumbent.

**A third abstention path was never implemented.** A claim with no running-hours
reading was being approved, because the engine only tested the hours limit when
a reading existed. The governing instrument sets a two-part limit; if half of it
cannot be tested, the honest answer is to say so. Now `request_evidence`.

One design correction came out of the same pass: **trap 1 was bleeding into the
valuation slice.** Any serial above 1500 trips the stale-index conflict, and
several valuation assets sat above it — so a lost point could not be attributed
to either trap. Valuation serials are now held below 1500. Design principle 6
exists for exactly this, and it took a generated population to notice it was
being broken.
