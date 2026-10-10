## Global Guardrails
- Treat skill entries as defaults; the current user request and verified tool outputs win.
- Load and apply a skill only when the manifest description matches the current task.
- Do not copy evidence constants unless the current prompt or tool output confirms them.

## Skills

### Skill: contoso_industrial_warranty_claims

**Applies when**
- Adjudicating Contoso Industrial warranty claims, including coverage, governing instrument, payable amount, next steps, or an asset’s, partner’s, or part’s warranty position.
- Use decision-ready completion for requested coverage decisions, claim adjudications, valuations, governing instruments, or operational dispositions.

**Does not apply when**
- Do not impose adjudication requirements on repository navigation or general policy, partner, or part inquiries that require no claim decision.
- Do not override the task’s response contract. System writes depend on user intent, authority, evidence, and tool support.

**Current-task authority**
- Follow the task’s scope and response contract. Write to a claim system only when requested or workflow-required, authorized, tool-supported, and evidence-supported.

**Prefer**
- Continue targeted retrieval and analysis to a sourced adjudication or concrete blocker. When broad search is noisy, use authoritative structured repositories deterministically without assuming paths or tool sequences.
- Conclude **covered**, **declined**, or **not yet decidable**.
- Identify the governing instrument by reference, including applicability, scope, supersession, and precedence over plausible competing policies, addenda, or bulletins.
- State the month and running-hours limits and coverage start date; compare the repair date and repair-time hours with both limits and identify the terminating limit.
- Attribute terms and exclusions to clauses; dates and readings to authoritative claim records with as-of dates; and rates and prices to authoritative regional sources with effective dates.
- Calculate payable value only after coverage and required pricing evidence are established.
- Name the disposition—approve, decline, request evidence, or escalate—the responsible role, and its next action.
- If decisive evidence remains unavailable after targeted retrieval, issue an explicit hold, evidence request, or escalation. Name each missing record and field and what it blocks; distinguish confirmed absence from retrieval failure.
- Execute exactly one matching claim-system action only when authorized, supported, and consistent with the disposition.

**Avoid**
- Do not end with retrieval commentary, repository status, or a future retrieval plan.
- Do not invent or substitute facts, terms, dates, hours, rates, prices, references, records, amounts, or neighboring or fuzzy-matched claims or assets.
- Do not decide coverage, valuation, approval, or decline without required evidence, or treat failed retrieval as confirmed absence.
- Do not value declined or undecidable claims or calculate without established pricing inputs.
- Do not present proposed actions as executed, make unauthorized writes, or create duplicate actions.

**Verify before finish**
- Confirm a conclusion of **covered**, **declined**, or **not yet decidable**.
- Confirm the governing instrument and precedence, or the exact missing record and field blocking them.
- Confirm both limits, the coverage start date, and repair-date and repair-hours comparisons, or the exact blockers for each.
- Confirm terms, dates, readings, rates, and prices cite applicable authoritative clauses, records, as-of dates, regions, and effective dates.
- Confirm valuation appears only with supported coverage and pricing.
- Confirm the disposition, responsible role, and owned next action.
- If action was authorized and supported, confirm exactly one matching system action; otherwise state why execution was impossible.
- Confirm no unsupported values, neighboring-record substitutions, or false claims of confirmed absence.

**Evidence support**
- Claim work often ended with retrieval commentary instead of adjudication or a precise evidence hold. This supports a terminal decision gate, exact blocker reporting, instrument precedence, limit comparisons, source attribution, conditional valuation, and one authorized matching action while preserving non-fabrication and exact-record discipline.
- Applies when: the current task matches this skill's named condition and evidence scope.
- Does not apply when: the task requires a different objective, data source, transformation, state change, or output format.
- Current-task authority: current user instructions and verified current-task tool outputs override examples from evidence.
- Prefer: follow the narrow behavior supported by the evidence.
- Avoid: applying the skill from broad topic or artifact overlap alone.
- Verify before finish: confirm requested outputs, state changes, and final-response requirements against current-task evidence.
- Evidence support: selected trajectory evidence supports this skill entry.
