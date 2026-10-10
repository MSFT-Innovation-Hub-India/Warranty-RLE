# The scenario

## The job

Contoso Industrial makes industrial chillers and air compressors. Authorised service partners repair them for customers in India, EMEA and APAC and send in **warranty claims**. An adjudicator decides each claim. The agent prepares that decision.

For every claim the agent must answer what an adjudicator would:

| Question | Example answer |
| --- | --- |
| Is it covered? | Approve · Decline · Escalate for goodwill · Hold and request evidence |
| Under which rule? | "TSB-C-0051 governs: it names this serial and overrides the India addendum" |
| How much is payable? | "₹199,175: labour 5.5 h × ₹1,450 (rate on the repair date) = ₹7,975, plus part fitted ₹191,200" (C-2026-04114) |
| What happens next, and who does it? | "Draft approval recorded; adjudicator to confirm" |

Every answer is a decision plus a number, so it can be checked against the answer key, [GROUND-TRUTH.md](../world-builder/out/GROUND-TRUTH.md).

## Where the facts live

No single source answers a claim. That is deliberate.

| Source | What's in it | How the agent reaches it |
| --- | --- | --- |
| SharePoint library *Warranty Operations* | Global policy, regional addenda, 12 technical bulletins, rate cards (Excel), partner agreements, quarterly review decks (PowerPoint), inspection reports | M365 file search and SharePoint tools |
| 3 Teams channels | Field escalations, policy announcements, partner chatter | Teams tools |
| Claim system (Azure SQL, via our MCP server) | Assets, running hours, service history, claims, partners, parts, a bulletin index, the goodwill authority matrix | One read (`get_claim_dossier`) and three draft-only writes |

Details: [02-world-configuration.md](02-world-configuration.md).

## Why it's hard: 12 traps

A few examples. All 12 are in [scenario design § 7](../world-builder/docs/03-scenario-design.md).

| Trap | The wrong answer it invites |
| --- | --- |
| The claim system's bulletin index says TSB-C-0051 ends at serial 1500; the bulletin itself says 1850 | Trusting the database over the controlling document |
| Bulletin ▸ India addendum ▸ global policy, and the addendum is *shorter* | Picking the most generous rule, or the first one found |
| An old review deck says "24 months standard" | Quoting a confident but stale slide |
| A manager says "go ahead and cover it" in Teams | Treating a chat message as approval |
| Some assets have no commissioning date | Guessing from the install date instead of asking for the record |

## The 30 evaluation claims, by type

| Type (slice) | Claims | What it tests |
| --- | --- | --- |
| covered-simple | 3 | The basic money path |
| declined-simple | 2 | Recognising out-of-cover |
| precedence | 5 | Which instrument governs |
| serial-boundary | 4 | Bulletin serial ranges, document over index |
| valuation | 6 | Labour cap, rate by repair date, part fitted, supersession, uplift |
| stale-deck | 2 | Ignoring the out-of-date deck |
| dual-limit | 3 | Months *and* running hours |
| abstention | 3 | Stopping when a record is missing |
| authority | 2 | Escalating goodwill instead of declining or approving |

A further **60 Training claims** (different claim numbers, same types) are used only for refinement and tuning.

## How a run works

1. A request ("Adjudicate claim C-2026-04114") goes to the world.
2. The platform routes it to the `warranty-assistant` **skill**, which runs as an agent with the skill's instructions and every enabled tool (~110).
3. The model calls tools, reads results, and decides.
4. It records a draft in the claim system and **hands in** its answer through the platform's finish tool.
5. A **grader model** (the platform's, undisclosed) scores the answer against the skill's six **rubrics**. That score is the platform's number, and in fine-tuning it is the reward.
6. We score the same answer against the answer key with `scripts/score_ground_truth.py`. That is the second number.

How the agent should reason through a claim, step by step: [03-claim-execution-flow.md](03-claim-execution-flow.md).
