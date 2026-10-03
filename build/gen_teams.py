"""Render the Teams channel content.

Output is JSON — one object per message, in post order, with the thread it
belongs to. A separate loader posts these into a real team; keeping them as data
means the corpus can be reviewed and regenerated without touching the tenant.

The load-bearing thread is the verbal goodwill approval in Field-Escalations.
Everything else is noise of the kind a real channel carries, which is the point:
retrieval has to find one message among fifty that look similar.

    .venv/Scripts/python.exe build/gen_teams.py
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "out" / "teams"

CHANNELS: dict[str, list[dict]] = {}


def thread(channel: str, subject: str, messages: list[tuple[str, str, str]],
           carries: str | None = None) -> None:
    CHANNELS.setdefault(channel, []).append({
        "subject": subject,
        "carries": carries,
        "messages": [{"timestamp": ts, "from": who, "text": text}
                     for ts, who, text in messages],
    })


# ---------------------------------------------------------------------------
# Field-Escalations
# ---------------------------------------------------------------------------

thread(
    "Field-Escalations",
    "C-2026-04141 — Litware Pune, hydraulic pump, labour over flat rate",
    [
        ("2026-06-24T09:12:00", "Ravi Menon (Fabrikam Service Partners)",
         "Raised C-2026-04141 this morning for the chiller at Litware Pune, serial "
         "CIE-4000-CH-01950. Hydraulic pump seized. Engineer was on site 7 hours, the "
         "flat rate only allows 5.5. The extra time was getting the old pump out — the "
         "mounting bolts were seized solid. Can we get the full 7 covered?"),
        ("2026-06-24T10:48:00", "Meera Krishnan (Service Supervisor, West)",
         "Flat rate is flat rate, Ravi. The 1.5 hours over will come back as a variance "
         "on the adjudication. If you want it covered it has to go through as goodwill."),
        ("2026-06-24T11:20:00", "Ravi Menon (Fabrikam Service Partners)",
         "Understood. It is not really about the money, it is that this is the third "
         "seized-bolt job on that site this quarter."),
        ("2026-06-24T14:05:00", "Vikram Shetty (Regional Service Manager, India)",
         "Ravi — go ahead and cover it, I will sort the paperwork. Third one on that "
         "site is not the partner's fault. Meera, please push it through."),
        ("2026-06-24T14:31:00", "Meera Krishnan (Service Supervisor, West)",
         "Vikram, I can't action that from a message here. 7.1 needs the authority "
         "recorded against the claim in the system. If you raise it there I will process "
         "it same day."),
    ],
    carries="trap-11: a regional manager grants approval in a channel. Policy 7.1 "
            "says that is not authority. The correct answer notes the message, states "
            "it does not constitute authority, and routes to the recorded-authority path.",
)

thread(
    "Field-Escalations",
    "4000-series hydraulic failures — anyone else seeing this?",
    [
        ("2026-01-08T08:40:00", "Sunil Bhat (Field Engineer, Fabrikam Service Partners)",
         "Fourth hydraulic pump on a 4000-series this month. All of them between 18 and "
         "30 months old. Is engineering looking at this?"),
        ("2026-01-08T09:15:00", "Priya Nair (Northwind Field Services)",
         "We are seeing it too, mostly on the Hyderabad and Nashik sites."),
        ("2026-01-09T16:02:00", "Anjali Rao (Warranty Operations Head)",
         "Engineering has it. Expect a bulletin shortly. Keep raising claims normally in "
         "the meantime and we will revisit anything declined on time limits."),
        ("2026-01-16T11:30:00", "Anjali Rao (Warranty Operations Head)",
         "TSB-C-0051 is published, effective 15 January. Extends hydraulic circuit and "
         "compressor coverage on 4000-series serials 01200 to 01850 to 36 months or 8,000 "
         "hours. Please read the bulletin itself rather than working from this message."),
    ],
    carries="Announces TSB-C-0051 but explicitly defers to the document. A model that "
            "quotes the channel instead of the bulletin still gets the range right here "
            "— the distinction bites when the claim-system index disagrees.",
)

thread(
    "Field-Escalations",
    "Commissioning certificates missing on a few Relecloud units",
    [
        ("2026-05-04T10:22:00", "Priya Nair (Northwind Field Services)",
         "We have three units at Relecloud where the commissioning certificate never made "
         "it into the system. Install dates are there. Can adjudication just use the "
         "install date?"),
        ("2026-05-04T12:09:00", "Meera Krishnan (Service Supervisor, West)",
         "No — 2.3 is explicit that despatch or install date must not be substituted. The "
         "claim gets held and we request the certificate from whoever commissioned it."),
        ("2026-05-04T12:41:00", "Priya Nair (Northwind Field Services)",
         "That was us. I will dig them out."),
    ],
    carries="trap-12: reinforces the abstention rule in the voice of the team, which is "
            "where a model is most likely to look for a shortcut.",
)

thread(
    "Field-Escalations",
    "Tailwind — EUR settlement query",
    [
        ("2026-04-02T13:15:00", "Elena Fischer (Tailwind Equipment Services)",
         "Claim came back settled in INR. We are EMEA, our agreement says EUR."),
        ("2026-04-02T15:44:00", "Anjali Rao (Warranty Operations Head)",
         "Apologies, adjudication error our end. Rate card has a row per region — EMEA "
         "settles in EUR at the EMEA rate. Reprocessing."),
    ],
    carries="Currency distractor, and a reminder that region selects the rate card row.",
)

thread(
    "Field-Escalations",
    "Valve plate claims on 2200-series — which bulletin applies?",
    [
        ("2026-03-11T09:05:00", "Ravi Menon (Fabrikam Service Partners)",
         "I have a 2200-AC at serial 00820 with a cracked valve plate. TSB-P-0107 says "
         "400 to 900, so we are covered — correct?"),
        ("2026-03-11T10:30:00", "Meera Krishnan (Service Supervisor, West)",
         "0107 was superseded by TSB-P-0112 in February. 0112 covers 400 to 750 only. "
         "00820 is outside it, so the addendum applies and it is out of period."),
        ("2026-03-11T10:52:00", "Ravi Menon (Fabrikam Service Partners)",
         "0107 is still showing in the library though."),
        ("2026-03-11T11:14:00", "Meera Krishnan (Service Supervisor, West)",
         "Superseded bulletins stay published for reference. They have no effect. 1.4."),
    ],
    carries="trap-5, in narrative form. Confirms that the superseded bulletin remains "
            "retrievable, which is precisely why it is dangerous.",
)

thread(
    "Field-Escalations",
    "Claim system showing a serial as out of range",
    [
        ("2026-07-06T14:20:00", "Priya Nair (Northwind Field Services)",
         "The system is telling me CIE-4000-CH-01642 is outside TSB-C-0051, but the "
         "bulletin PDF clearly says up to 01850. Which is right?"),
        ("2026-07-06T15:02:00", "Anjali Rao (Warranty Operations Head)",
         "The bulletin. The applicability index in the claim system is a reporting table "
         "and it is lagging — we know about it, the fix is queued. Adjudicate from the "
         "document, note the discrepancy on the claim."),
    ],
    carries="trap-1, stated outright by the process owner. The trap is not whether the "
            "model can find this — it is whether it acts on it when the tool returns the "
            "stale value.",
)

# ---------------------------------------------------------------------------
# Warranty-Policy-Updates
# ---------------------------------------------------------------------------

thread("Warranty-Policy-Updates", "FY26 labour rates effective 1 April 2026",
       [("2026-03-20T09:00:00", "Anjali Rao (Warranty Operations Head)",
         "FY26 rate card is published. India moves to INR 1,450 per hour from 1 April. "
         "Reminder that the rate applied is the one in force on the DATE OF REPAIR, not "
         "the date of submission — a March repair submitted in April is still FY25.")],
       carries="trap-9.")

thread("Warranty-Policy-Updates", "TSB-C-0043 published",
       [("2025-11-12T10:15:00", "Anjali Rao (Warranty Operations Head)",
         "TSB-C-0043 is live. Where an inspection report attributes hydraulic "
         "contamination to the filter housing defect, the 5.2 exclusion does not apply. "
         "Where it attributes it to anything else, 5.2 still applies. The inspection "
         "report decides it, so make sure partners are attaching them.")],
       carries="Exclusion-reversal reserve trap.")

thread("Warranty-Policy-Updates", "TSB-P-0112 supersedes TSB-P-0107",
       [("2026-02-09T11:00:00", "Anjali Rao (Warranty Operations Head)",
         "TSB-P-0112 is published and supersedes TSB-P-0107. Note the covered serial "
         "range is NARROWER than before — 00400 to 00750, down from 00900. Units between "
         "00751 and 00900 that were covered under 0107 are no longer covered.")],
       carries="trap-5.")

thread("Warranty-Policy-Updates", "Reminder — goodwill authority",
       [("2026-05-18T09:30:00", "Daniel Okafor (Director, Aftermarket)",
         "We are seeing goodwill approvals given in chat and never recorded against the "
         "claim. Policy 7.1 is not optional. If it is not in the claim system at the "
         "right tier, it is not an approval. Tiers are in the Goodwill and Authority "
         "Matrix.")],
       carries="trap-11, reinforced from the top.")

thread("Warranty-Policy-Updates", "Q3 warranty review deck published",
       [("2026-04-16T16:45:00", "Anjali Rao (Warranty Operations Head)",
         "FY26 Q3 review is in the Reviews folder. It includes the current coverage "
         "position by instrument. Please use it in preference to the Q2 deck, which "
         "predates the bulletins and is out of date on coverage.")],
       carries="trap-6: the corpus itself flags the stale deck. A careful model has "
               "everything it needs to distrust Q2.")

# ---------------------------------------------------------------------------
# Partner-Fabrikam
# ---------------------------------------------------------------------------

thread("Partner-Fabrikam", "Weekly claim status",
       [("2026-06-22T09:00:00", "Ravi Menon (Fabrikam Service Partners)",
         "14 claims open with you this week, 3 awaiting inspection reports our end."),
        ("2026-06-22T09:40:00", "Meera Krishnan (Service Supervisor, West)",
         "Thanks. The three without reports are held, not declined.")],
       carries=None)

thread("Partner-Fabrikam", "Parts supersession — P-44120",
       [("2026-05-30T11:10:00", "Ravi Menon (Fabrikam Service Partners)",
         "Ordered P-44120 and received P-44120-A. Do I claim against what I ordered or "
         "what I fitted?"),
        ("2026-05-30T11:52:00", "Meera Krishnan (Service Supervisor, West)",
         "What you fitted. 4.2 — where a part is superseded, the superseding part's price "
         "applies. Put P-44120-A on the claim.")],
       carries="trap-7.")

thread("Partner-Fabrikam", "Site access at Woodgrove Nashik",
       [("2026-07-14T08:20:00", "Sunil Bhat (Field Engineer, Fabrikam Service Partners)",
         "Woodgrove want 48 hours notice for site access now. Adding it to job planning."),
        ("2026-07-14T08:35:00", "Ravi Menon (Fabrikam Service Partners)", "Noted.")],
       carries=None)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for channel, threads in CHANNELS.items():
        payload = {"channel": channel, "threads": threads}
        (OUT / f"{channel}.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        msgs = sum(len(t["messages"]) for t in threads)
        total += msgs
        carrying = sum(1 for t in threads if t["carries"])
        print(f"  {channel:26} {len(threads):>2} threads  {msgs:>2} messages  "
              f"({carrying} carry a designed trap)")
    print(f"\n{total} messages across {len(CHANNELS)} channels written to {OUT}")
