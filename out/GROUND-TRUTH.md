# Ground truth — Contoso Industrial warranty adjudication

**Generated. Do not edit by hand.**  
`.venv/Scripts/python.exe build/ground_truth.py`

Produced 2026-10-06 from `scenario/spec/` via `build/adjudicate.py`. Every row is computed by the same engine that the corpus documents are rendered from, so the expected answer and the text a model will read cannot disagree.

| Split | Claims |
| --- | --- |
| Evaluation | 30 |
| Training | 60 |
| **Total** | **90** |

Outcome mix: **approve** 52, **decline** 24, **escalate** 5, **request_evidence** 9.

---

## Evaluation set — 30 claims

| Claim | Slice | Traps | Serial | Decision | Governing | Payable | Code |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04101` | covered-simple | - | `CIE-4000-CH-01050` | **approve** | ADD-IN-2.1 | ₹69,575 | STD |
| `C-2026-04102` | covered-simple | - | `CIE-4000-CH-01052` | **approve** | ADD-IN-2.1 | ₹48,420 | STD |
| `C-2026-04103` | covered-simple | - | `CIE-2200-AC-00320` | **approve** | ADD-IN-2.1 | ₹19,150 | STD |
| `C-2026-04109` | declined-simple | - | `CIE-4000-CH-01900` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04110` | declined-simple | - | `CIE-2200-AC-00330` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04114` | precedence | 1, 2, 5 | `CIE-4000-CH-01700` | **approve** | TSB-C-0051 | ₹199,175 | TSB |
| `C-2026-04115` | precedence | 1, 2, 5 | `CIE-4000-CH-01640` | **approve** | TSB-C-0051 | ₹755,050 | TSB |
| `C-2026-04116` | precedence | 1, 2, 5 | `CIE-4000-CH-01950` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04117` | precedence | 1, 2, 5 | `CIE-2200-AC-00800` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04118` | precedence | 1, 2, 5 | `CIE-2200-AC-00600` | **approve** | TSB-P-0112 | ₹67,500 | TSB |
| `C-2026-04129` | serial-boundary | 4 | `CIE-4000-CH-01199` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04130` | serial-boundary | 4 | `CIE-4000-CH-01200` | **approve** | TSB-C-0051 | ₹198,450 | TSB |
| `C-2026-04131` | serial-boundary | 4 | `CIE-4000-CH-01850` | **approve** | TSB-C-0051 | ₹198,450 | TSB |
| `C-2026-04132` | serial-boundary | 4 | `CIE-4000-CH-01851` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04139` | dual-limit | 3 | `CIE-4000-CH-01400` | **decline** | TSB-C-0051 | - | NC |
| `C-2026-04140` | dual-limit | 3 | `CIE-4000-CH-01410` | **decline** | TSB-C-0051 | - | NC |
| `C-2026-04141` | dual-limit | 3 | `CIE-4000-CH-01420` | **approve** | TSB-C-0051 | ₹199,175 | TSB |
| `C-2026-04148` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01440` | **approve** | TSB-C-0051 | ₹208,735 | TSB |
| `C-2026-04149` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01442` | **approve** | TSB-C-0051 | ₹753,880 | TSB |
| `C-2026-04150` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01444` | **approve** | TSB-C-0051 | ₹755,050 | TSB |
| `C-2026-04151` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01446` | **approve** | TSB-C-0051 | ₹31,030 | TSB |
| `C-2026-04152` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01448` | **approve** | TSB-C-0051 | ₹197,000 | TSB |
| `C-2026-04153` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01450` | **approve** | ADD-IN-2.1 | ₹72,945 | STD |
| `C-2026-04166` | stale-deck | 6 | `CIE-4000-CH-01300` | **approve** | TSB-C-0051 | ₹199,175 | TSB |
| `C-2026-04167` | stale-deck | 6 | `CIE-4000-CH-01302` | **approve** | TSB-C-0051 | ₹755,050 | TSB |
| `C-2026-04171` | authority | 11 | `CIE-4000-CH-01960` | **escalate** | ADD-IN-2.1 | - | GW |
| `C-2026-04172` | authority | 11 | `CIE-4000-CH-01962` | **escalate** | ADD-IN-2.1 | - | GW |
| `C-2026-04176` | abstention | 12 | `CIE-4000-CH-02100` | **request_evidence** | — | - | NC |
| `C-2026-04177` | abstention | 12 | `CIE-4000-CH-09990` | **request_evidence** | — | - | NC |
| `C-2026-04178` | abstention | 12 | `CIE-4000-CH-02110` | **request_evidence** | ADD-IN-2.1 | - | NC |

## Training set — 60 claims

| Claim | Slice | Traps | Serial | Decision | Governing | Payable | Code |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04104` | covered-simple | - | `CIE-4000-CH-01054` | **approve** | ADD-IN-2.1 | ₹29,725 | STD |
| `C-2026-04105` | covered-simple | - | `CIE-2200-AC-00322` | **approve** | ADD-IN-2.1 | ₹104,220 | STD |
| `C-2026-04106` | covered-simple | - | `CIE-4000-CH-01056` | **approve** | ADD-IN-2.1 | ₹26,875 | STD |
| `C-2026-04107` | covered-simple | - | `CIE-2200-AC-00324` | **approve** | ADD-IN-2.1 | ₹224,375 | STD |
| `C-2026-04108` | covered-simple | - | `CIE-4000-CH-01058` | **approve** | ADD-IN-2.1 | ₹2,900 | STD |
| `C-2026-04111` | declined-simple | - | `CIE-4000-CH-01902` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04112` | declined-simple | - | `CIE-2200-AC-00332` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04113` | declined-simple | - | `CIE-4000-CH-01904` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04119` | precedence | 1, 2, 5 | `CIE-4000-CH-01701` | **approve** | TSB-C-0051 | ₹199,175 | TSB |
| `C-2026-04120` | precedence | 1, 2, 5 | `CIE-4000-CH-01641` | **approve** | TSB-C-0051 | ₹755,050 | TSB |
| `C-2026-04121` | precedence | 1, 2, 5 | `CIE-4000-CH-01951` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04122` | precedence | 1, 2, 5 | `CIE-2200-AC-00801` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04123` | precedence | 1, 2, 5 | `CIE-2200-AC-00601` | **approve** | TSB-P-0112 | ₹67,500 | TSB |
| `C-2026-04124` | precedence | 1, 2, 5 | `CIE-4000-CH-01702` | **approve** | TSB-C-0051 | ₹199,175 | TSB |
| `C-2026-04125` | precedence | 1, 2, 5 | `CIE-4000-CH-01642` | **approve** | TSB-C-0051 | ₹755,050 | TSB |
| `C-2026-04126` | precedence | 1, 2, 5 | `CIE-4000-CH-01952` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04127` | precedence | 1, 2, 5 | `CIE-2200-AC-00802` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04128` | precedence | 1, 2, 5 | `CIE-2200-AC-00602` | **approve** | TSB-P-0112 | ₹67,500 | TSB |
| `C-2026-04133` | serial-boundary | 4 | `CIE-4000-CH-01198` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04134` | serial-boundary | 4 | `CIE-4000-CH-01201` | **approve** | TSB-C-0051 | ₹198,450 | TSB |
| `C-2026-04135` | serial-boundary | 4 | `CIE-4000-CH-01848` | **approve** | TSB-C-0051 | ₹198,450 | TSB |
| `C-2026-04136` | serial-boundary | 4 | `CIE-4000-CH-01849` | **approve** | TSB-C-0051 | ₹198,450 | TSB |
| `C-2026-04137` | serial-boundary | 4 | `CIE-4000-CH-01852` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04138` | serial-boundary | 4 | `CIE-4000-CH-01853` | **decline** | ADD-IN-2.1 | - | NC |
| `C-2026-04142` | dual-limit | 3 | `CIE-4000-CH-01403` | **decline** | TSB-C-0051 | - | NC |
| `C-2026-04143` | dual-limit | 3 | `CIE-4000-CH-01413` | **decline** | TSB-C-0051 | - | NC |
| `C-2026-04144` | dual-limit | 3 | `CIE-4000-CH-01423` | **approve** | TSB-C-0051 | ₹199,175 | TSB |
| `C-2026-04145` | dual-limit | 3 | `CIE-4000-CH-01406` | **decline** | TSB-C-0051 | - | NC |
| `C-2026-04146` | dual-limit | 3 | `CIE-4000-CH-01416` | **decline** | TSB-C-0051 | - | NC |
| `C-2026-04147` | dual-limit | 3 | `CIE-4000-CH-01426` | **approve** | TSB-C-0051 | ₹199,175 | TSB |
| `C-2026-04154` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01452` | **approve** | TSB-C-0051 | ₹208,735 | TSB |
| `C-2026-04155` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01454` | **approve** | TSB-C-0051 | ₹753,880 | TSB |
| `C-2026-04156` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01456` | **approve** | TSB-C-0051 | ₹755,050 | TSB |
| `C-2026-04157` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01458` | **approve** | TSB-C-0051 | ₹31,030 | TSB |
| `C-2026-04158` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01460` | **approve** | TSB-C-0051 | ₹197,000 | TSB |
| `C-2026-04159` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01462` | **approve** | ADD-IN-2.1 | ₹72,945 | STD |
| `C-2026-04160` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01464` | **approve** | TSB-C-0051 | ₹208,735 | TSB |
| `C-2026-04161` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01466` | **approve** | TSB-C-0051 | ₹753,880 | TSB |
| `C-2026-04162` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01468` | **approve** | TSB-C-0051 | ₹755,050 | TSB |
| `C-2026-04163` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01470` | **approve** | TSB-C-0051 | ₹31,030 | TSB |
| `C-2026-04164` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01472` | **approve** | TSB-C-0051 | ₹197,000 | TSB |
| `C-2026-04165` | valuation | 7, 8, 9, 10 | `CIE-4000-CH-01474` | **approve** | ADD-IN-2.1 | ₹72,945 | STD |
| `C-2026-04168` | stale-deck | 6 | `CIE-4000-CH-01304` | **approve** | TSB-C-0051 | ₹199,175 | TSB |
| `C-2026-04169` | stale-deck | 6 | `CIE-4000-CH-01306` | **approve** | TSB-C-0051 | ₹755,050 | TSB |
| `C-2026-04170` | stale-deck | 6 | `CIE-4000-CH-01308` | **approve** | TSB-C-0051 | ₹29,725 | TSB |
| `C-2026-04173` | authority | 11 | `CIE-4000-CH-01964` | **escalate** | ADD-IN-2.1 | - | GW |
| `C-2026-04174` | authority | 11 | `CIE-4000-CH-01966` | **escalate** | ADD-IN-2.1 | - | GW |
| `C-2026-04175` | authority | 11 | `CIE-4000-CH-01968` | **escalate** | ADD-IN-2.1 | - | GW |
| `C-2026-04179` | abstention | 12 | `CIE-4000-CH-02101` | **request_evidence** | — | - | NC |
| `C-2026-04180` | abstention | 12 | `CIE-4000-CH-09991` | **request_evidence** | — | - | NC |
| `C-2026-04181` | abstention | 12 | `CIE-4000-CH-02111` | **request_evidence** | ADD-IN-2.1 | - | NC |
| `C-2026-04182` | abstention | 12 | `CIE-4000-CH-02102` | **request_evidence** | — | - | NC |
| `C-2026-04183` | abstention | 12 | `CIE-4000-CH-09992` | **request_evidence** | — | - | NC |
| `C-2026-04184` | abstention | 12 | `CIE-4000-CH-02112` | **request_evidence** | ADD-IN-2.1 | - | NC |
| `C-2026-04185` | exclusion | reserve | `CIE-4000-CH-01360` | **approve** | TSB-C-0051 | ₹199,175 | TSB |
| `C-2026-04186` | exclusion | reserve | `CIE-4000-CH-01362` | **decline** | TSB-C-0051 | - | NC |
| `C-2026-04187` | exclusion | reserve | `CIE-4000-CH-01364` | **approve** | TSB-C-0051 | ₹199,175 | TSB |
| `C-2026-04188` | exclusion | reserve | `CIE-4000-CH-01366` | **decline** | TSB-C-0051 | - | NC |
| `C-2026-04189` | repair-warranty | reserve | `CIE-4000-CH-01980` | **approve** | POL-WAR-4.2 6.1 | ₹69,575 | RW |
| `C-2026-04190` | repair-warranty | reserve | `CIE-4000-CH-01981` | **approve** | POL-WAR-4.2 6.1 | ₹69,575 | RW |

---

## Evaluation set — full working

One block per evaluation claim, so a reviewer can check any answer by hand in under two minutes.

### `C-2026-04101` — covered-simple

**APPROVE** · ADD-IN-2.1 · funding `STD` · payable **₹69,575**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01050` (4000-CH, India) |
| Commissioned | 2025-03-15 |
| Partner | D-IN-01 |
| Operation | `CTRL-BD-RR` |
| Repair date | 2026-05-10 |
| Hours at repair | 2400 |
| Claimed | 1.5 h, part `P-44900` |
| Part fitted | `P-44900` |

**Reason.** Covered under ADD-IN-2.1: 18 months from commissioning (2025-03-15) expiring 2026-09-15, limit 5000 h; repair 2026-05-10 at 2400 h.

**Expiry basis.** 18 months from 2025-03-15 → 2026-09-15; limit 5000 h; at repair 2400 h.

**Instruments considered.** `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 1.5 h × ₹1,450 | ₹2,175 |
| Parts | `P-44900` | ₹67,400 |
| Uplift | | ₹0 |
| **Total** | | **₹69,575** |


### `C-2026-04102` — covered-simple

**APPROVE** · ADD-IN-2.1 · funding `STD` · payable **₹48,420**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01052` (4000-CH, India) |
| Commissioned | 2025-01-08 |
| Partner | D-IN-01 |
| Operation | `COND-FAN-RR` |
| Repair date | 2026-02-18 |
| Hours at repair | 1900 |
| Claimed | 3.5 h, part `P-44520` |
| Part fitted | `P-44520` |

**Reason.** Covered under ADD-IN-2.1: 18 months from commissioning (2025-01-08) expiring 2026-07-08, limit 5000 h; repair 2026-02-18 at 1900 h.

**Expiry basis.** 18 months from 2025-01-08 → 2026-07-08; limit 5000 h; at repair 1900 h.

**Instruments considered.** `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 3.5 h × ₹1,320 | ₹4,620 |
| Parts | `P-44520` | ₹43,800 |
| Uplift | | ₹0 |
| **Total** | | **₹48,420** |


### `C-2026-04103` — covered-simple

**APPROVE** · ADD-IN-2.1 · funding `STD` · payable **₹19,150**

| | |
| --- | --- |
| Serial | `CIE-2200-AC-00320` (2200-AC, India) |
| Commissioned | 2025-05-02 |
| Partner | D-IN-01 |
| Operation | `SEAL-KIT-RR` |
| Repair date | 2026-04-22 |
| Hours at repair | 2750 |
| Claimed | 3.0 h, part `P-22120` |
| Part fitted | `P-22120` |

**Reason.** Covered under ADD-IN-2.1: 18 months from commissioning (2025-05-02) expiring 2026-11-02, limit 5000 h; repair 2026-04-22 at 2750 h.

**Expiry basis.** 18 months from 2025-05-02 → 2026-11-02; limit 5000 h; at repair 2750 h.

**Instruments considered.** `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 3.0 h × ₹1,450 | ₹4,350 |
| Parts | `P-22120` | ₹14,800 |
| Uplift | | ₹0 |
| **Total** | | **₹19,150** |


### `C-2026-04109` — declined-simple

**DECLINE** · ADD-IN-2.1 · funding `NC` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01900` (4000-CH, India) |
| Commissioned | 2023-06-01 |
| Partner | D-IN-01 |
| Operation | `CTRL-BD-RR` |
| Repair date | 2026-05-10 |
| Hours at repair | 5200 |
| Claimed | 1.5 h, part `P-44900` |
| Part fitted | `P-44900` |

**Reason.** Outside coverage under ADD-IN-2.1: both the time and running-hours limits is exceeded (expiry 2024-12-01 / 5000 h; repair 2026-05-10 at 5200 h).

**Expiry basis.** 18 months from 2023-06-01 → 2024-12-01; limit 5000 h; at repair 5200 h.

**Instruments considered.** `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.


### `C-2026-04110` — declined-simple

**DECLINE** · ADD-IN-2.1 · funding `NC` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-2200-AC-00330` (2200-AC, India) |
| Commissioned | 2023-02-14 |
| Partner | D-IN-01 |
| Operation | `SEAL-KIT-RR` |
| Repair date | 2026-03-03 |
| Hours at repair | 6100 |
| Claimed | 3.0 h, part `P-22120` |
| Part fitted | `P-22120` |

**Reason.** Outside coverage under ADD-IN-2.1: both the time and running-hours limits is exceeded (expiry 2024-08-14 / 5000 h; repair 2026-03-03 at 6100 h).

**Expiry basis.** 18 months from 2023-02-14 → 2024-08-14; limit 5000 h; at repair 6100 h.

**Instruments considered.** `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.


### `C-2026-04114` — precedence

**APPROVE** · TSB-C-0051 · funding `TSB` · payable **₹199,175**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01700` (4000-CH, India) |
| Commissioned | 2024-04-04 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-06-18 |
| Hours at repair | 4120 |
| Claimed | 5.5 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Covered under TSB-C-0051: 36 months from commissioning (2024-04-04) expiring 2027-04-04, limit 8000 h; repair 2026-06-18 at 4120 h.

**Expiry basis.** 36 months from 2024-04-04 → 2027-04-04; limit 8000 h; at repair 4120 h.

**Instruments considered.** `TSB-C-0051` ← governs, `TSB-C-0043`, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 5.5 h × ₹1,450 | ₹7,975 |
| Parts | `P-44120-A` | ₹191,200 |
| Uplift | | ₹0 |
| **Total** | | **₹199,175** |

**Notes the answer must carry.**

- The service system applicability index records TSB-C-0051 as ending at serial 1500; the bulletin document states 1850. The document governs (policy 1.4).
- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).


### `C-2026-04115` — precedence

**APPROVE** · TSB-C-0051 · funding `TSB` · payable **₹755,050**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01640` (4000-CH, India) |
| Commissioned | 2024-04-04 |
| Partner | D-IN-01 |
| Operation | `COMP-RR` |
| Repair date | 2026-07-02 |
| Hours at repair | 4400 |
| Claimed | 9.0 h, part `P-44310` |
| Part fitted | `P-44310` |

**Reason.** Covered under TSB-C-0051: 36 months from commissioning (2024-04-04) expiring 2027-04-04, limit 8000 h; repair 2026-07-02 at 4400 h.

**Expiry basis.** 36 months from 2024-04-04 → 2027-04-04; limit 8000 h; at repair 4400 h.

**Instruments considered.** `TSB-C-0051` ← governs, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 9.0 h × ₹1,450 | ₹13,050 |
| Parts | `P-44310` | ₹742,000 |
| Uplift | | ₹0 |
| **Total** | | **₹755,050** |

**Notes the answer must carry.**

- The service system applicability index records TSB-C-0051 as ending at serial 1500; the bulletin document states 1850. The document governs (policy 1.4).
- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).


### `C-2026-04116` — precedence

**DECLINE** · ADD-IN-2.1 · funding `NC` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01950` (4000-CH, India) |
| Commissioned | 2024-09-01 |
| Partner | D-IN-01 |
| Operation | `CTRL-BD-RR` |
| Repair date | 2026-05-01 |
| Hours at repair | 3000 |
| Claimed | 1.5 h, part `P-44900` |
| Part fitted | `P-44900` |

**Reason.** Outside coverage under ADD-IN-2.1: the time limit is exceeded (expiry 2026-03-01 / 5000 h; repair 2026-05-01 at 3000 h).

**Expiry basis.** 18 months from 2024-09-01 → 2026-03-01; limit 5000 h; at repair 3000 h.

**Instruments considered.** `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.


### `C-2026-04117` — precedence

**DECLINE** · ADD-IN-2.1 · funding `NC` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-2200-AC-00800` (2200-AC, India) |
| Commissioned | 2024-03-01 |
| Partner | D-IN-01 |
| Operation | `VALVE-PLT-RR` |
| Repair date | 2026-06-01 |
| Hours at repair | 3000 |
| Claimed | 4.0 h, part `P-22450-C` |
| Part fitted | `P-22450-C` |

**Reason.** Outside coverage under ADD-IN-2.1: the time limit is exceeded (expiry 2025-09-01 / 5000 h; repair 2026-06-01 at 3000 h).

**Expiry basis.** 18 months from 2024-03-01 → 2025-09-01; limit 5000 h; at repair 3000 h.

**Instruments considered.** `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.

**Notes the answer must carry.**

- TSB-P-0107 names this asset but has been superseded and has no effect (policy 1.4).


### `C-2026-04118` — precedence

**APPROVE** · TSB-P-0112 · funding `TSB` · payable **₹67,500**

| | |
| --- | --- |
| Serial | `CIE-2200-AC-00600` (2200-AC, India) |
| Commissioned | 2024-03-01 |
| Partner | D-IN-01 |
| Operation | `VALVE-PLT-RR` |
| Repair date | 2026-06-01 |
| Hours at repair | 3000 |
| Claimed | 4.0 h, part `P-22450-C` |
| Part fitted | `P-22450-C` |

**Reason.** Covered under TSB-P-0112: 30 months from commissioning (2024-03-01) expiring 2026-09-01, limit 7000 h; repair 2026-06-01 at 3000 h.

**Expiry basis.** 30 months from 2024-03-01 → 2026-09-01; limit 7000 h; at repair 3000 h.

**Instruments considered.** `TSB-P-0112` ← governs, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 4.0 h × ₹1,450 | ₹5,800 |
| Parts | `P-22450-C` | ₹61,700 |
| Uplift | | ₹0 |
| **Total** | | **₹67,500** |

**Notes the answer must carry.**

- TSB-P-0112 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).
- TSB-P-0107 names this asset but has been superseded and has no effect (policy 1.4).


### `C-2026-04129` — serial-boundary

**DECLINE** · ADD-IN-2.1 · funding `NC` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01199` (4000-CH, India) |
| Commissioned | 2024-04-04 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-06-18 |
| Hours at repair | 4120 |
| Claimed | 5.0 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Outside coverage under ADD-IN-2.1: the time limit is exceeded (expiry 2025-10-04 / 5000 h; repair 2026-06-18 at 4120 h).

**Expiry basis.** 18 months from 2024-04-04 → 2025-10-04; limit 5000 h; at repair 4120 h.

**Instruments considered.** `TSB-C-0043`, `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.


### `C-2026-04130` — serial-boundary

**APPROVE** · TSB-C-0051 · funding `TSB` · payable **₹198,450**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01200` (4000-CH, India) |
| Commissioned | 2024-04-04 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-06-18 |
| Hours at repair | 4120 |
| Claimed | 5.0 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Covered under TSB-C-0051: 36 months from commissioning (2024-04-04) expiring 2027-04-04, limit 8000 h; repair 2026-06-18 at 4120 h.

**Expiry basis.** 36 months from 2024-04-04 → 2027-04-04; limit 8000 h; at repair 4120 h.

**Instruments considered.** `TSB-C-0051` ← governs, `TSB-C-0043`, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 5.0 h × ₹1,450 | ₹7,250 |
| Parts | `P-44120-A` | ₹191,200 |
| Uplift | | ₹0 |
| **Total** | | **₹198,450** |

**Notes the answer must carry.**

- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).


### `C-2026-04131` — serial-boundary

**APPROVE** · TSB-C-0051 · funding `TSB` · payable **₹198,450**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01850` (4000-CH, India) |
| Commissioned | 2024-04-04 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-06-18 |
| Hours at repair | 4120 |
| Claimed | 5.0 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Covered under TSB-C-0051: 36 months from commissioning (2024-04-04) expiring 2027-04-04, limit 8000 h; repair 2026-06-18 at 4120 h.

**Expiry basis.** 36 months from 2024-04-04 → 2027-04-04; limit 8000 h; at repair 4120 h.

**Instruments considered.** `TSB-C-0051` ← governs, `TSB-C-0043`, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 5.0 h × ₹1,450 | ₹7,250 |
| Parts | `P-44120-A` | ₹191,200 |
| Uplift | | ₹0 |
| **Total** | | **₹198,450** |

**Notes the answer must carry.**

- The service system applicability index records TSB-C-0051 as ending at serial 1500; the bulletin document states 1850. The document governs (policy 1.4).
- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).


### `C-2026-04132` — serial-boundary

**DECLINE** · ADD-IN-2.1 · funding `NC` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01851` (4000-CH, India) |
| Commissioned | 2024-04-04 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-06-18 |
| Hours at repair | 4120 |
| Claimed | 5.0 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Outside coverage under ADD-IN-2.1: the time limit is exceeded (expiry 2025-10-04 / 5000 h; repair 2026-06-18 at 4120 h).

**Expiry basis.** 18 months from 2024-04-04 → 2025-10-04; limit 5000 h; at repair 4120 h.

**Instruments considered.** `TSB-C-0043`, `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.


### `C-2026-04139` — dual-limit

**DECLINE** · TSB-C-0051 · funding `NC` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01400` (4000-CH, India) |
| Commissioned | 2025-06-01 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-06-01 |
| Hours at repair | 8400 |
| Claimed | 5.5 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Outside coverage under TSB-C-0051: the running-hours limit is exceeded (expiry 2028-06-01 / 8000 h; repair 2026-06-01 at 8400 h).

**Expiry basis.** 36 months from 2025-06-01 → 2028-06-01; limit 8000 h; at repair 8400 h.

**Instruments considered.** `TSB-C-0051` ← governs, `TSB-C-0043`, `ADD-IN-2.1`, `POL-WAR-4.2`.

**Notes the answer must carry.**

- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).


### `C-2026-04140` — dual-limit

**DECLINE** · TSB-C-0051 · funding `NC` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01410` (4000-CH, India) |
| Commissioned | 2023-02-01 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-06-01 |
| Hours at repair | 2100 |
| Claimed | 5.5 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Outside coverage under TSB-C-0051: the time limit is exceeded (expiry 2026-02-01 / 8000 h; repair 2026-06-01 at 2100 h).

**Expiry basis.** 36 months from 2023-02-01 → 2026-02-01; limit 8000 h; at repair 2100 h.

**Instruments considered.** `TSB-C-0051` ← governs, `TSB-C-0043`, `ADD-IN-2.1`, `POL-WAR-4.2`.

**Notes the answer must carry.**

- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).


### `C-2026-04141` — dual-limit

**APPROVE** · TSB-C-0051 · funding `TSB` · payable **₹199,175**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01420` (4000-CH, India) |
| Commissioned | 2023-07-01 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-06-20 |
| Hours at repair | 7900 |
| Claimed | 5.5 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Covered under TSB-C-0051: 36 months from commissioning (2023-07-01) expiring 2026-07-01, limit 8000 h; repair 2026-06-20 at 7900 h.

**Expiry basis.** 36 months from 2023-07-01 → 2026-07-01; limit 8000 h; at repair 7900 h.

**Instruments considered.** `TSB-C-0051` ← governs, `TSB-C-0043`, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 5.5 h × ₹1,450 | ₹7,975 |
| Parts | `P-44120-A` | ₹191,200 |
| Uplift | | ₹0 |
| **Total** | | **₹199,175** |

**Notes the answer must carry.**

- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).


### `C-2026-04148` — valuation

**APPROVE** · TSB-C-0051 · funding `TSB` · payable **₹208,735**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01440` (4000-CH, India) |
| Commissioned | 2024-10-01 |
| Partner | D-IN-02 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-06-18 |
| Hours at repair | 3000 |
| Claimed | 8.0 h, part `P-44120` |
| Part fitted | `P-44120-A` |

**Reason.** Covered under TSB-C-0051: 36 months from commissioning (2024-10-01) expiring 2027-10-01, limit 8000 h; repair 2026-06-18 at 3000 h.

**Expiry basis.** 36 months from 2024-10-01 → 2027-10-01; limit 8000 h; at repair 3000 h.

**Instruments considered.** `TSB-C-0051` ← governs, `TSB-C-0043`, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 5.5 h × ₹1,450 | ₹7,975 |
| Parts | `P-44120-A` | ₹191,200 |
| Uplift | | ₹9,560 |
| **Total** | | **₹208,735** |

**Notes the answer must carry.**

- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).
- Partner claimed P-44120; service history records P-44120-A fitted.
- 5.0% handling uplift granted by SPA-2024-NWD-IN (policy 4.3).
- 2.5 h claimed above the 5.5 h flat-rate allowance for HYD-PUMP-RR is not payable (policy 4.1).


### `C-2026-04149` — valuation

**APPROVE** · TSB-C-0051 · funding `TSB` · payable **₹753,880**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01442` (4000-CH, India) |
| Commissioned | 2024-10-01 |
| Partner | D-IN-01 |
| Operation | `COMP-RR` |
| Repair date | 2026-03-31 |
| Hours at repair | 3000 |
| Claimed | 9.0 h, part `P-44310` |
| Part fitted | `P-44310` |

**Reason.** Covered under TSB-C-0051: 36 months from commissioning (2024-10-01) expiring 2027-10-01, limit 8000 h; repair 2026-03-31 at 3000 h.

**Expiry basis.** 36 months from 2024-10-01 → 2027-10-01; limit 8000 h; at repair 3000 h.

**Instruments considered.** `TSB-C-0051` ← governs, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 9.0 h × ₹1,320 | ₹11,880 |
| Parts | `P-44310` | ₹742,000 |
| Uplift | | ₹0 |
| **Total** | | **₹753,880** |

**Notes the answer must carry.**

- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).


### `C-2026-04150` — valuation

**APPROVE** · TSB-C-0051 · funding `TSB` · payable **₹755,050**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01444` (4000-CH, India) |
| Commissioned | 2024-10-01 |
| Partner | D-IN-01 |
| Operation | `COMP-RR` |
| Repair date | 2026-04-01 |
| Hours at repair | 3000 |
| Claimed | 9.0 h, part `P-44310` |
| Part fitted | `P-44310` |

**Reason.** Covered under TSB-C-0051: 36 months from commissioning (2024-10-01) expiring 2027-10-01, limit 8000 h; repair 2026-04-01 at 3000 h.

**Expiry basis.** 36 months from 2024-10-01 → 2027-10-01; limit 8000 h; at repair 3000 h.

**Instruments considered.** `TSB-C-0051` ← governs, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 9.0 h × ₹1,450 | ₹13,050 |
| Parts | `P-44310` | ₹742,000 |
| Uplift | | ₹0 |
| **Total** | | **₹755,050** |

**Notes the answer must carry.**

- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).


### `C-2026-04151` — valuation

**APPROVE** · TSB-C-0051 · funding `TSB` · payable **₹31,030**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01446` (4000-CH, India) |
| Commissioned | 2025-01-10 |
| Partner | D-IN-02 |
| Operation | `FILT-HSG-RR` |
| Repair date | 2026-05-20 |
| Hours at repair | 3000 |
| Claimed | 3.5 h, part `P-44080` |
| Part fitted | `P-44080` |

**Reason.** Covered under TSB-C-0051: 36 months from commissioning (2025-01-10) expiring 2028-01-10, limit 8000 h; repair 2026-05-20 at 3000 h.

**Expiry basis.** 36 months from 2025-01-10 → 2028-01-10; limit 8000 h; at repair 3000 h.

**Instruments considered.** `TSB-C-0051` ← governs, `TSB-C-0043`, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 2.5 h × ₹1,450 | ₹3,625 |
| Parts | `P-44080-B` | ₹26,100 |
| Uplift | | ₹1,305 |
| **Total** | | **₹31,030** |

**Notes the answer must carry.**

- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).
- P-44080 is superseded by P-44080-B; priced at the superseding part (policy 4.2).
- Partner claimed P-44080; service history records P-44080 fitted.
- 5.0% handling uplift granted by SPA-2024-NWD-IN (policy 4.3).
- 1.0 h claimed above the 2.5 h flat-rate allowance for FILT-HSG-RR is not payable (policy 4.1).


### `C-2026-04152` — valuation

**APPROVE** · TSB-C-0051 · funding `TSB` · payable **₹197,000**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01448` (4000-CH, India) |
| Commissioned | 2025-01-10 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-05-20 |
| Hours at repair | 3000 |
| Claimed | 4.0 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Covered under TSB-C-0051: 36 months from commissioning (2025-01-10) expiring 2028-01-10, limit 8000 h; repair 2026-05-20 at 3000 h.

**Expiry basis.** 36 months from 2025-01-10 → 2028-01-10; limit 8000 h; at repair 3000 h.

**Instruments considered.** `TSB-C-0051` ← governs, `TSB-C-0043`, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 4.0 h × ₹1,450 | ₹5,800 |
| Parts | `P-44120-A` | ₹191,200 |
| Uplift | | ₹0 |
| **Total** | | **₹197,000** |

**Notes the answer must carry.**

- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).


### `C-2026-04153` — valuation

**APPROVE** · ADD-IN-2.1 · funding `STD` · payable **₹72,945**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01450` (4000-CH, India) |
| Commissioned | 2025-02-01 |
| Partner | D-IN-02 |
| Operation | `CTRL-BD-RR` |
| Repair date | 2026-06-05 |
| Hours at repair | 3000 |
| Claimed | 2.5 h, part `P-44900` |
| Part fitted | `P-44900` |

**Reason.** Covered under ADD-IN-2.1: 18 months from commissioning (2025-02-01) expiring 2026-08-01, limit 5000 h; repair 2026-06-05 at 3000 h.

**Expiry basis.** 18 months from 2025-02-01 → 2026-08-01; limit 5000 h; at repair 3000 h.

**Instruments considered.** `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 1.5 h × ₹1,450 | ₹2,175 |
| Parts | `P-44900` | ₹67,400 |
| Uplift | | ₹3,370 |
| **Total** | | **₹72,945** |

**Notes the answer must carry.**

- 5.0% handling uplift granted by SPA-2024-NWD-IN (policy 4.3).
- 1.0 h claimed above the 1.5 h flat-rate allowance for CTRL-BD-RR is not payable (policy 4.1).


### `C-2026-04166` — stale-deck

**APPROVE** · TSB-C-0051 · funding `TSB` · payable **₹199,175**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01300` (4000-CH, India) |
| Commissioned | 2024-02-20 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-08-12 |
| Hours at repair | 5300 |
| Claimed | 5.5 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Covered under TSB-C-0051: 36 months from commissioning (2024-02-20) expiring 2027-02-20, limit 8000 h; repair 2026-08-12 at 5300 h.

**Expiry basis.** 36 months from 2024-02-20 → 2027-02-20; limit 8000 h; at repair 5300 h.

**Instruments considered.** `TSB-C-0051` ← governs, `TSB-C-0043`, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 5.5 h × ₹1,450 | ₹7,975 |
| Parts | `P-44120-A` | ₹191,200 |
| Uplift | | ₹0 |
| **Total** | | **₹199,175** |

**Notes the answer must carry.**

- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).


### `C-2026-04167` — stale-deck

**APPROVE** · TSB-C-0051 · funding `TSB` · payable **₹755,050**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01302` (4000-CH, India) |
| Commissioned | 2024-05-06 |
| Partner | D-IN-01 |
| Operation | `COMP-RR` |
| Repair date | 2026-09-01 |
| Hours at repair | 4700 |
| Claimed | 9.0 h, part `P-44310` |
| Part fitted | `P-44310` |

**Reason.** Covered under TSB-C-0051: 36 months from commissioning (2024-05-06) expiring 2027-05-06, limit 8000 h; repair 2026-09-01 at 4700 h.

**Expiry basis.** 36 months from 2024-05-06 → 2027-05-06; limit 8000 h; at repair 4700 h.

**Instruments considered.** `TSB-C-0051` ← governs, `ADD-IN-2.1`, `POL-WAR-4.2`.

| Component | Working | Amount |
| --- | --- | --- |
| Labour | 9.0 h × ₹1,450 | ₹13,050 |
| Parts | `P-44310` | ₹742,000 |
| Uplift | | ₹0 |
| **Total** | | **₹755,050** |

**Notes the answer must carry.**

- TSB-C-0051 names this serial range and takes precedence over ADD-IN-2.1 and POL-WAR-4.2 (policy 1.4).


### `C-2026-04171` — authority

**ESCALATE** · ADD-IN-2.1 · funding `GW` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01960` (4000-CH, India) |
| Commissioned | 2024-09-01 |
| Partner | D-IN-01 |
| Operation | `CTRL-BD-RR` |
| Repair date | 2026-05-01 |
| Hours at repair | 3000 |
| Claimed | 1.5 h, part `P-44900` |
| Part fitted | `P-44900` |
| Goodwill requested | 67400 |

**Reason.** Outside coverage under ADD-IN-2.1: the time limit is exceeded (expiry 2026-03-01 / 5000 h; repair 2026-05-01 at 3000 h).

**Expiry basis.** 18 months from 2024-09-01 → 2026-03-01; limit 5000 h; at repair 3000 h.

**Instruments considered.** `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.

**Approver required.** Regional Service Manager.

**Notes the answer must carry.**

- Goodwill of 67,400 requires tier 2 authority (Regional Service Manager) recorded in the claim system (policy 7.1). An approval given in a channel message does not constitute authority.


### `C-2026-04172` — authority

**ESCALATE** · ADD-IN-2.1 · funding `GW` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-01962` (4000-CH, India) |
| Commissioned | 2024-09-01 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-05-01 |
| Hours at repair | 3000 |
| Claimed | 5.5 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |
| Goodwill requested | 312000 |

**Reason.** Outside coverage under ADD-IN-2.1: the time limit is exceeded (expiry 2026-03-01 / 5000 h; repair 2026-05-01 at 3000 h).

**Expiry basis.** 18 months from 2024-09-01 → 2026-03-01; limit 5000 h; at repair 3000 h.

**Instruments considered.** `TSB-C-0043`, `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.

**Approver required.** Warranty Operations Head.

**Notes the answer must carry.**

- Goodwill of 312,000 requires tier 3 authority (Warranty Operations Head) recorded in the claim system (policy 7.1). An approval given in a channel message does not constitute authority.


### `C-2026-04176` — abstention

**REQUEST_EVIDENCE** · no governing instrument · funding `NC` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-02100` (4000-CH, India) |
| Commissioned | **absent from the registry** |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-06-18 |
| Hours at repair | 3000 |
| Claimed | 5.5 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Coverage cannot be determined: the commissioning record is absent from the asset registry (policy 2.3). The installation date must not be substituted.

**Missing.** `commissioning_date` — required record: commissioning certificate from the installing partner.


### `C-2026-04177` — abstention

**REQUEST_EVIDENCE** · no governing instrument · funding `NC` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-09990` (4000-CH, India) |
| Commissioned | 2024-10-01 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-06-18 |
| Hours at repair | 3000 |
| Claimed | 5.5 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Serial CIE-4000-CH-09990 is not present in the asset registry.

**Missing.** `asset record` — required record: asset registration / proof of supply.


### `C-2026-04178` — abstention

**REQUEST_EVIDENCE** · ADD-IN-2.1 · funding `NC` · payable **-**

| | |
| --- | --- |
| Serial | `CIE-4000-CH-02110` (4000-CH, India) |
| Commissioned | 2025-10-01 |
| Partner | D-IN-01 |
| Operation | `HYD-PUMP-RR` |
| Repair date | 2026-06-18 |
| Hours at repair | **no reading** |
| Claimed | 5.5 h, part `P-44120-A` |
| Part fitted | `P-44120-A` |

**Reason.** Coverage cannot be determined: ADD-IN-2.1 sets a limit of 5000 running hours and the asset registry holds no telemetry reading for CIE-4000-CH-02110 at the date of repair.

**Expiry basis.** 18 months from 2025-10-01 → 2027-04-01; limit 5000 h.

**Instruments considered.** `TSB-C-0043`, `ADD-IN-2.1` ← governs, `POL-WAR-4.2`.

**Missing.** `running_hours` — required record: running-hours reading at or before the date of repair.

