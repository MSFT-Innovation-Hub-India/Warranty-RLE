# Issue: final hand-ins rejected by the finish tool's formatter (GPT-5.4-Mini)

**World:** `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` · CLI 0.3.16 · strategy `simple` · skill `cf00d339-5217-4cd1-b390-cc0d911735da` (custom skill; MCP server + SharePoint + Teams sources)

## What happens

With **GPT-5.4-Mini (`dev-ct-gpt-54-mini-mp`)**, the agent's final answer is often **rejected at hand-in** (the finish tool). The agent then hands in a short fallback such as *"I could not complete the final completion step"*, and that fallback is what gets delivered and graded. The full answer, often correct, is lost.

We can only see this through the **grader's reasoning**; nothing in the data exposed to us records it. Examples, verbatim:
- *"The fuller attempted messages were rejected by the finish tool and were not successfully delivered."*
- *"…sourced analysis contained only in rejected finish calls… despite appearing in finish calls rejected by the formatter."*
- *"The successful final response is an error/status message rather than the adjudication. It says, 'I could not complete the final completion step'."*
- *"…the successful finish carried an empty sources list."* / *"…begins with a tool-formatting disclaimer… supplies no valid source list."*

## How often, by model

| Model | Runs | Hand-in rejected (per grader) |
| --- | --- | --- |
| **GPT-5.4-Mini** `dev-ct-gpt-54-mini-mp` | eval job `73fa5456-45f6-411c-92e1-b553931acab8` (28 graded) + 4 chat runs | **22 of 28** eval runs; **4 of 4** chat runs |
| GPT-5.6-Sol `prod-gpt-56-reasoning-sol` | eval jobs `555d5dd2…`, `cf102eae…`, `53495f74…`, `95f7d234…`, `9f4ad313…` | **0 of 62** |
| MAI-CODE-5b `dev-ct-mai-code-mp` | 2 chat runs (`ce09af1e…` graded, no rejection; `181a5c12…` returned **no grading at all**) | not observed (n = 2) |

Chat runs that show it (full records via `executions get`): `d04446c1-6e93-4a11-bc1d-3b9a9659f63d`, `c9c64dc9-4cd5-4456-bf1c-d673beed33c9`, `b377f130-cf32-4689-af3e-70ef6042fbf6`, `ad565697-c2af-4d31-8a0b-56bfa1198c7f`, `934bcb81-c91b-439b-9b05-db639a848626`. In the last one, the stored answer is a correct, fully worked *"Approve under TSB-C-0051 — INR 755,050"*, but the grader says the delivered submission *"begins with inability to calculate… has no inline citations… no arithmetic"*.

Also: `c6a77b7d-5176-49b8-9b3d-646321677ecd` (GPT-5.4-Mini, 2026-10-05 07:13–07:26 UTC) ended **Failed** with `ErrorCode 8, "Exception"`: *"We encountered an issue while processing your request. Please try again in a new chat."*

So far it's **only seen with GPT-5.4-Mini**. Our hypothesis (unconfirmed) is that the model's finish payload, probably its structured sources list, fails the formatter's validation. Skill guidance didn't help, in two variants: "cite sources in the text; if the hand-in is rejected, resubmit the same full answer", and then "put every citation in the answer text and leave the hand-in's separate sources list empty".

## Why we can't diagnose it ourselves

- `diag execution <id>` and `executions diagnostics <id>` → `403 … The execution diagnostics API is not enabled.`
- `executions get <id>` lists only **successful** tool calls; rejected finish attempts and their errors are missing.
- The exported `Response` is the agent's **last attempted** message, not the delivered one, so they disagree when a hand-in was rejected.
- `executions get` returns "not found" for **evaluation** execution IDs.

## What we'd like

1. **Enable the execution diagnostics API** for this tenant/world, or share the formatter's rejection message for the runs above.
2. **The finish tool's schema and validation rules** (especially the sources field), so the skill can state the format correctly.
3. Clarification: **which answer is graded, and what `Response` holds**, when a hand-in is rejected. Should `Response` be the delivered message?

## Update 2026-10-06: also seen on MAI-CODE-5b

The same rejection now appears with `dev-ct-mai-code-mp`. In wce-dev (two skills: library-research, then warranty-assistant), **4 of 8** completed adjudication-skill invocations (2026-10-05 22:03 to 2026-10-06 07:19) had their full answers rejected; **0 of 8** earlier ones did; the only accepted hand-ins were probes such as *"A test [cite:claim]"* and *"Test sentence [cite:src1]"* (grader notes). Each rejection was followed by the platform **re-invoking the skill**, which wrote a duplicate draft. Example: execution `33cee794-392a-4a9b-ab53-b27e2f0d2535` (C-2026-04185: 2 invocations, 3 drafts, outcome rubrics 0.0 although the decision delivered to the user was correct). Others: `8577bdbd-…`, `6e8ca35f-…` (2026-10-05). The `[cite:…]` text suggests the model is probing the citation format the finish tool expects. Removing our skill's instruction to *leave the hand-in's sources list empty* gave **0 rejections in 3 runs** of the same claim (2026-10-06 08:00; executions `7960457c-…`, `6d0418ef-…`, `65529d26-…`). That's suggestive, not proof. **Question:** what citation and sources format does the finish tool require, and what does it reject?

## Related, seen in the same period

- **Model identity.** The runnable MAI model here is `dev-ct-mai-code-mp`, displayed as **"MAI-CODE-5b"** (BaseModel `DEV-CT-MAI-CODE-MP`). The fine-tune base is `mai-code-1-flash` ("MAI-Code-1-Flash"). "MAI-CODE-5b" isn't in Microsoft's public MAI documentation. Is it the same weights as MAI-Code-1-Flash, a different checkpoint, or an internal build? And is `dev-ct-gpt-54-mini-mp` the same weights as the tune base `gpt-54-mini`? This decides whether a before-and-after comparison is like for like.
- **MAI context window.** With MAI-CODE-5b the skill sub-agent fails with `ErrorCode 2 "ContextLength"` once its tool output reaches ~230–275k characters (≈90–100k tokens including the tool catalogue); the platform then re-invokes the skill and the run comes back **ungraded**. Runs: `4c2b8243-…`, `09e562d7-…`, `0af5028b-…`, and the v1 run `181a5c12-…`. What is the model's context window? Does fine-tuning see these failed skill runs (with no reward)?
- **A model per skill.** With two skills (research, then adjudication), could research run on a large model and adjudication on a small one? We found no control for this: skills have no model field, `run --model` applies to the whole run, and the playbook describes repeated `--model` only as a candidate set with blended results. What does an "ordered multi-model execution" do: which model runs the coordinator, and which runs each skill sub-agent? What is the environment's `Models.SearchModels` field for? Executions don't record a model, so we can't observe this ourselves.
- Eval job `73fa5456…` (GPT-5.4-Mini, 30 samples): 2 runs (C-2026-04118, C-2026-04110) hung from 16:49 UTC with resubmissions 5 → 8; cancelled at 17:23 UTC. GPT-5.6-Sol ran 30 concurrently with 0 retries. Is there a lower throughput quota on `dev-ct-*` deployments?
- Some runs graded twice (two sets of rubric results); MAI run `181a5c12…` not graded, with no error.
- `m365__call_copilot` vanished from `tools available` between 03:30 and 05:40 UTC on 2026-10-05 (137 → 136 tools); `tools available` also returns short counts (88, 106) on some reads.
