# Troubleshooting

Problems hit during this exploration, with what was tried and what actually
worked. Kept separate from the guides so the main flow stays readable.

| # | Problem | Status |
| --- | --- | --- |
| 1 | [A OneDrive-scoped world retrieved nothing](#1-a-onedrive-scoped-world-retrieved-nothing) | ⚠️ Worked around — root cause not isolated |
| 2 | [Every programmatic upload route failed](#2-every-programmatic-upload-route-failed) | ⚠️ Worked around — used the web UI |
| 3 | [Newly uploaded files are not immediately retrievable](#3-newly-uploaded-files-are-not-immediately-retrievable) | ℹ️ Expected behaviour |
| 4 | [Reading the JSON — fields that actually matter](#4-reading-the-json--fields-that-actually-matter) | 📖 Reference |

---

## 1. A OneDrive-scoped world retrieved nothing

**Cost: about a day.**

### Symptom

The first world was scoped to **personal OneDrive**. Everything looked healthy:

- `environments init` completed without error
- `knowledge list` showed all sources registered
- The files were present in OneDrive and opened normally

And retrieval returned nothing. Every query, for hours. The agent would search,
get no usable results, and answer from nothing — which reads exactly like a model
that cannot reason.

### What we wrongly blamed

| Hypothesis | Why it was wrong |
| --- | --- |
| The model is too weak | The same model works in the rebuilt world |
| Sensitivity labels are blocking extraction | The labels were non-encrypting |
| The documents failed to extract | Same files, same bytes, work now |
| Indexing had not finished | Waited hours; it never converged |

Each of these is plausible, and each cost time. That is the real lesson: **a world
that cannot see its documents is indistinguishable, from the outside, from a model
that cannot reason.**

### What fixed it

Rebuilding the world against a **SharePoint site** instead of personal OneDrive.

Identical skill, identical model, identical question, identical files. It worked
on the first attempt.

### Honest caveat

> 💭 **We never isolated the precise mechanism.** Upstream documents OneDrive as a
> supported knowledge source. It may have been a tenant policy, a sync state, or
> an indexing quirk specific to this account.
>
> What can be said with confidence is that **scope was the only variable** — it
> was the single thing that changed between the failing world and the working one.
> Recording an honest *"we do not know exactly why"* is more useful than a tidy
> but unverified root cause.

### The generalisable rule

**When retrieval returns nothing, suspect scope before you suspect the model.**

This matches upstream's own diagnostic ordering, which puts retrieval first and
rubric wording third:

1. Retrieval — is every document actually being read?
2. Skill selection — are all samples being graded?
3. Rubric wording — is a bullet unmeetable rather than hard?

### Cost of getting it wrong

⚠️ **Capability URLs are frozen at `environments init`.** There is no edit path,
so a mis-scoped world cannot be corrected — it has to be rebuilt. That also means
new environment and skill IDs, and any stored per-rubric score from the old world
cannot be joined to the new one.

---

## 2. Every programmatic upload route failed

Getting the seed documents into the SharePoint library by API did not work. Three
routes, three different failures:

| Route | Failure |
| --- | --- |
| Server-side cross-drive copy | `403 logicalPermissionAccessDenied` |
| Colon-path `createUploadSession` | `400` |
| Upload session `PUT` | `{"error":{"code":"unauthenticated"}}` |

### What worked

Copying the files through the **SharePoint web UI**.

💡 That turned out to be **better than the API would have been**. SharePoint's
*Copy to* preserves the source file's non-encrypting sensitivity label, whereas a
fresh upload can pick up a default policy that blocks text extraction — which
would have produced the same symptom as problem 1, for a different reason.

### Verify afterwards

⚠️ **Check byte counts against the source.** A truncated or zero-byte file in the
library is indistinguishable, at answer time, from a model that cannot reason.

---

## 3. Newly uploaded files are not immediately retrievable

Indexing lags upload. Minutes are not always enough.

**There is no CLI command that reports index state.** The only reliable check is
to ask a question and look at whether the search tool returned anything real.

```powershell
frontier-tuning chat -q "<a question whose answer is in the new files>" --wait
```

You are not checking the answer — you are checking that retrieval returned real
document names. If the agent starts guessing site paths instead, indexing has not
caught up, or the scope is wrong (see problem 1).

---

## 4. Reading the JSON — fields that actually matter

The traces are where diagnosis happens, and several fields mean less than they
appear to.

### The fields that lie

| Field | Looks like | Actually means |
| --- | --- | --- |
| `IsWorkspaceReady: true` | The world is good | Provisioned and accepting requests. Says **nothing** about whether capability URLs resolved or content is retrievable. This is the trap in problem 1 |
| `Status: Completed` | It worked | The run *finished*. A run that retrieved nothing and hallucinated also says `Completed` |
| `ErrorResponse: null` | No errors | Usually null even on failed runs. Do not read null as success |
| Tool `Status: Completed` | The tool worked | Per-file results sit inside `results`. A tool can report `Completed` while every file failed |

### The single most important field

```json
{ "FileRetrievalDetails": [] }
```

Nothing was retrieved by that call — even though the call and the whole execution
report `Completed`. If this is empty, stop and fix retrieval before looking at
anything else.

### `knowledge list`

| Field | Meaning |
| --- | --- |
| `id` / `url` / `folderUrl` | The URL string you registered — echoed back, **not necessarily resolved** |
| `displayName` | The **resolved** name. Matching your real folder is a good sign; missing or generic is suspicious |
| `isAllItemsIncluded` | `false` = scoped to this folder rather than everything beneath it |
| `sharepointIds.*` | `siteId`, `webId`, `listId`, `uniqueId`. Populated = the service resolved it to a real location |

### `executions get`

| Field | Meaning |
| --- | --- |
| `Skills[]` | Which skill actually fired. Empty means none did — and that sample is **dropped from evaluation averages**, not scored zero |
| `ToolExecutions[].Title` | Tool name. `ServerName` is null; the server is the `Name` prefix before `__` |
| `ToolExecutions[].Inputs[]` | What was requested. `parentFolderId: root` means root browsing — a bad sign |
| `ToolExecutions[].Output` | **Often JSON wrapped inside a text-part array — decode twice** |
| `RubricResults[].Reasoning` | The grader's written justification. The console table hides this |
| `RubricResults[].Skip` | A written reason the rubric did not apply. `Score: null` + `Skip` ≠ zero |
| `LatestChainOfThought` | Reasoning trace; `null` when no gradeable answer was produced |
| `BillingSummary` | Token counts. The console table shows a summary only |

### Two decoding traps

1. **Double-encoded JSON.** Tool output is an array of text parts, and the useful
   JSON sits inside a part's `text` string. A regex over the raw blob misses
   `FileRetrievalDetails` entirely. Decode the outer array, then the inner string.
2. **Matching on raw text.** We once counted four `403`s by searching raw text.
   One was a *successful* response that happened to contain `403` inside a GUID.
   Match on a decoded `StatusCode` field.

> 💡 Always poll with `-o json`. The console table hides `Reasoning`, `Skip`, and
> full tool inputs — see
> probe-sweep.md.

---

## Related

| Document | Covers |
| --- | --- |
| 01-contract-renewal.md | The main build log |
| [rubric-design.md](rubric-design.md) | What a rubric is, why it is required, and the order to build in |
