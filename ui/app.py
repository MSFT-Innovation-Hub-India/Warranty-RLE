"""Run from the repository root: python -m streamlit run ui\\app.py."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

from ui.console import (
    CLI, DATA, WARRANTY_ENV, CommandError, Store, baseline_counts, database_action,
    field, identifier, new_record, refresh, response_text, rubric_rows, run_args,
    score_ground_truth, sql, submit,
)

st.set_page_config(page_title="Frontier Tuning console", page_icon=":material/tune:", layout="wide")
st.html(Path(__file__).with_name("theme.html").read_text(encoding="utf-8"), unsafe_allow_javascript=True)
st.title("Frontier Tuning console")
st.caption("Local CLI workspace · inspect live configuration, execute a strategy, explain the returned evidence")


def show_error(exc: Exception) -> None:
    st.error(str(exc))
    if isinstance(exc, CommandError):
        with st.expander("Failed command and CLI output", expanded=True):
            st.code(subprocess.list2cmdline(exc.command), language="powershell")
            st.code(exc.stdout or "(no stdout)", language="text")
            st.code(exc.stderr or "(no stderr)", language="text")


def raw_json(label: str, value: object, stdout: str = "") -> None:
    with st.expander(label):
        with st.container(height=420):
            st.json(value, expanded=1)
        if stdout:
            st.download_button("Download exact CLI stdout", stdout, "cli-response.json", "application/json",
                               key=f"download-{label}")


@st.cache_data(ttl=60, max_entries=8)
def load_context(env: str) -> dict:
    return CLI().context(env)


@st.cache_data(ttl=60, max_entries=1)
def configured_environment() -> str:
    payload = CLI().read(["config", "show"]).payload
    if not isinstance(payload, dict):
        raise ValueError("CLI config was not an object.")
    config = payload.get("config", {})
    value = field(config, "env_id", "envId")
    if not value:
        raise ValueError("No environment is set in CLI config. Set one with the CLI first.")
    return identifier(value)


try:
    cli = CLI()
    store = Store()
    default_env = configured_environment()
except (CommandError, ValueError, OSError) as exc:
    show_error(exc)
    st.stop()

with st.sidebar:
    st.header("Workspace")
    st.caption("Defaults come from the CLI config. This UI does not change that config.")
    env_text = st.text_input("Environment ID", default_env)
    if st.button("Refresh live configuration", icon=":material/refresh:"):
        load_context.clear()
        configured_environment.clear()
    st.caption("Saved locally:")
    st.code(str(DATA), language=None, wrap_lines=True)
    st.warning("Runs may incur charges and write real draft records. Search can repeat those writes.")

try:
    env = identifier(env_text)
    with st.spinner("Reading environment, skills, rubrics and model catalog from the CLI..."):
        context = load_context(env)
except (CommandError, ValueError, OSError) as exc:
    show_error(exc)
    st.stop()

environment = context["environment"]
if isinstance(environment, dict):
    st.subheader(field(environment, "displayName", "name", "Name", default="Selected environment"))
st.code(env, language=None)
st.caption(f"Live configuration read: {context.get('readUtc', 'not reported')} (cached up to 60 seconds)")

inspect_tab, run_tab, history_tab, database_tab = st.tabs(
    ["Live skill & rubrics", "Execute", "Saved runs & results", "Claim database"]
)

with inspect_tab:
    st.info(
        "Inspecting a skill does not select it for execution. The service routes your query to a deployed "
        "skill; returned results show what it actually used. Stage folders are not platform selections."
    )
    skills = context["details"]
    if not skills:
        st.warning("No enabled skills were returned for this environment.")
    else:
        sid = st.selectbox(
            "Inspect enabled skill", list(skills),
            format_func=lambda key: next(
                f"{field(row, 'displayName', 'name', default=key)} · {key}"
                for row in context["skills"] if field(row, "id", "Id") == key
            ),
        )
        detail = skills[sid]
        skill = field(detail, "skill", "Skill", default=detail)
        st.write(field(skill, "description", "Description", default=""))
        with st.expander("Deployed skill instructions", expanded=True):
            st.markdown(field(skill, "prompt", "Prompt", "instructions", default="No instructions returned."))
        for rubric in field(detail, "rubrics", "Rubrics", default=[]):
            name = field(rubric, "rubricName", "RubricName", "name", default="Rubric")
            enabled = field(rubric, "isEnabled", "IsEnabled", default=False)
            with st.expander(f"{name} · {'enabled' if enabled else 'disabled'}"):
                st.caption(f"Importance: {field(rubric, 'importance', 'Importance', default='not reported')}")
                for item in field(rubric, "checklistItems", "ChecklistItems", default=[]):
                    st.markdown(f"- {item}")
        raw_json("Raw skill and rubrics JSON", detail)

with run_tab:
    st.subheader("Run a query")
    strategy = st.segmented_control("Strategy", ["Simple", "TreeSearch", "BestOfN"], default="Simple")
    catalog = context["models"]["trainingModels"]
    available = {field(row, "id", "Id"): row for row in catalog if field(row, "isEnabled", default=False)}
    selected = next((key for key, row in available.items() if row.get("isSelected")), "")
    model_keys = ["", *available]
    model = st.selectbox(
        "Model", model_keys, index=model_keys.index(selected),
        format_func=lambda key: (
            f"{field(available[key], 'displayName', 'name', default=key)} · {key}"
            if key else "Service default (omit --model)"
        ),
    )
    st.caption("Catalog availability is not proof that a model can complete this task.")
    n, cutoff = None, None
    if strategy == "BestOfN":
        if st.checkbox("Set candidate count explicitly", value=True):
            n = st.number_input("Candidates (N)", min_value=1, value=4, step=1)
        else:
            st.caption("Candidate count omitted: service default, whose effective value may not be returned.")
    if strategy == "TreeSearch":
        if st.checkbox("Set early-stop score explicitly", value=True):
            cutoff = st.number_input("Early-stop score", min_value=0.0, max_value=1.0, value=0.95, step=0.01)
            st.caption("A platform candidate-score threshold, not a percentage of independently measured accuracy.")
        else:
            st.caption("Cutoff omitted: service default. Its numeric value and stop reason may not be returned.")
    query = st.text_area("Query", value="Adjudicate claim C-2026-04101.", height=130)
    args = None
    try:
        args = run_args(query, strategy or "", model, n, cutoff)
        st.code(subprocess.list2cmdline(cli.command(args, env)), language="powershell", wrap_lines=True)
    except ValueError as exc:
        st.warning(str(exc))
    st.caption(
        "Submission runs once without --wait. Reopen the saved execution and refresh by ID; "
        "refresh never resubmits. A clean database and no active/unknown jobs are required."
    )
    approved = st.checkbox("I approve this paid execution and its possible claim-system writes.")
    if env != WARRANTY_ENV:
        st.warning("Execution is restricted to the Contoso warranty environment because its database checks are specific to this repository.")
    if st.button("Execute once", type="primary", disabled=not approved or args is None or env != WARRANTY_ENV,
                 icon=":material/play_arrow:"):
        try:
            with st.spinner("Checking jobs and baseline, then submitting once..."):
                record = submit(cli, store, env, args, context)
            st.session_state["selected_run"] = record["localId"]
            st.success(f"Submitted execution {record['executionId']}. Open Saved runs & results to refresh.")
        except (CommandError, ValueError, OSError) as exc:
            show_error(exc)

with history_tab:
    st.subheader("Saved runs & results")
    st.caption("Reading existing executions is not a new model run. Local history survives app restarts.")
    with st.expander("Open an existing execution by ID"):
        existing = st.text_input("Execution ID")
        if st.button("Read execution", disabled=not existing.strip()):
            try:
                record = new_record("execution", env)
                record["state"] = "unknown"
                with st.spinner("Reading execution..."):
                    record = refresh(cli, store, record, existing)
                st.session_state["selected_run"] = record["localId"]
            except (CommandError, ValueError, OSError) as exc:
                show_error(exc)
    saved = [record for record in store.all() if record["kind"] == "execution" and record["env"] == env]
    if not saved:
        st.info("No saved executions yet. Execute a query or open an existing execution above.")
    else:
        ids = [record["localId"] for record in saved]
        if st.session_state.get("selected_run") not in ids:
            st.session_state["selected_run"] = ids[0]
        lookup = {record["localId"]: record for record in saved}
        local_id = st.selectbox(
            "Saved execution", ids, key="selected_run",
            format_func=lambda key: (
                f"{lookup[key]['createdUtc'][:19]} · {lookup[key]['state']} · "
                f"{lookup[key].get('executionId', 'submission outcome unknown')}"
            ),
        )
        record = lookup[local_id]
        if record.get("executionId"):
            if st.button("Refresh execution by ID", icon=":material/refresh:"):
                try:
                    with st.spinner("Reading current status..."):
                        record = refresh(cli, store, record)
                except (CommandError, ValueError, OSError) as exc:
                    show_error(exc)
        else:
            st.error("Submission outcome unknown. Do not run the query again. Inspect service executions and attach the matching ID.")
            if st.button("List service executions (read-only)"):
                try:
                    reply = cli.read(["executions", "list"], env)
                    st.json(reply.payload, expanded=1)
                except (CommandError, ValueError) as exc:
                    show_error(exc)
            recovered = st.text_input("Recovered execution ID", key=f"recover-{local_id}")
            if st.button("Attach recovered ID", disabled=not recovered.strip()):
                try:
                    record = refresh(cli, store, record, recovered)
                except (CommandError, ValueError, OSError) as exc:
                    show_error(exc)
            reason = st.text_input("Reconciliation evidence (only if the platform confirms no execution was created)")
            confirmed = st.checkbox("I verified the submission was not created; this only unlocks local controls.")
            if st.button("Mark not submitted", disabled=not confirmed or not reason.strip()):
                record.update(state="reconciled", reconciliation=reason)
                store.save(record)
                st.rerun()
        st.write(f"**Status:** {record['state']}")
        if record.get("executionId"):
            st.code(record["executionId"], language=None)
        if record.get("command"):
            with st.expander("Original submission command"):
                st.code(subprocess.list2cmdline(record["command"]), language="powershell", wrap_lines=True)
        if record.get("error"):
            st.warning(record["error"])
        payload = record.get("result", {})
        if payload:
            returned_strategy = field(payload, "harnessStrategyType", "strategyType", "StrategyType", default="Not reported")
            st.caption(f"Returned strategy: {returned_strategy}")
            used_skills = field(payload, "skillResults", "skills", "Skills", default=[])
            with st.expander("Skill actually used (historical metadata)", expanded=True):
                if used_skills:
                    for used in used_skills:
                        snapshot = field(used, "snapshotData", "skillSnapshot", default=used)
                        st.write({
                            "name": field(snapshot, "displayName", "name", "Name", default="Not reported"),
                            "id": field(used, "id", "Id", default=field(snapshot, "id")),
                            "version": field(used, "version", default="Not reported"),
                            "overall score": field(used, "score", "Score", default="Not reported"),
                        })
                else:
                    st.caption("No executed-skill metadata returned.")
            st.subheader("Agent response")
            text = response_text(payload)
            if text:
                st.markdown(text)
            else:
                st.info("No answer returned yet. Refresh by execution ID; do not resubmit.")
            st.subheader("Rubric results")
            rows = rubric_rows(payload)
            if rows:
                st.dataframe(rows, hide_index=True, width="stretch")
            else:
                st.caption("No rubric results returned.")
            st.caption("Rubric scores are not independent accuracy. Branch scores/selection reasons may not be exposed.")
            if st.button("Check ground-truth accuracy", disabled=record["state"].lower() != "completed"):
                try:
                    with st.spinner("Running the repository's local ground-truth scorer..."):
                        score_ground_truth(store, record)
                except (CommandError, ValueError, OSError) as exc:
                    show_error(exc)
            if record.get("groundTruth"):
                with st.expander("Independent ground-truth check", expanded=True):
                    st.markdown(record["groundTruth"])
            else:
                st.info("Independent accuracy has not been checked for this saved run. Use the local scorer above.")
            with st.expander("Usage and tool activity"):
                st.json(field(payload, "billingSummary", "BillingSummary", default={}))
                tools = field(payload, "toolExecutions", "ToolExecutions", default=[])
                st.caption(f"{len(tools)} exported tool records. Counts may differ from billed invocations.")
                for index, tool in enumerate(tools):
                    with st.expander(f"{index + 1}. {field(tool, 'title', 'Title', 'displayName', default='Tool')}"):
                        st.json(tool, expanded=1)
                st.caption("This is an activity log, not a reconstructed TreeSearch branch graph.")
            raw_json("Raw execution JSON", payload, record.get("stdout", ""))
        if record.get("stderr"):
            with st.expander("CLI stderr / diagnostic output"):
                st.code(record["stderr"], language="text")
        if not payload and record.get("stdout"):
            with st.expander("CLI stdout from unresolved submission"):
                st.code(record["stdout"], language="text")

with database_tab:
    st.subheader("Claim database")
    st.warning(
        "These controls affect the shared Contoso warranty database. Reset deletes draft adjudications, "
        "evidence requests and goodwill escalations, and restores seeded claim statuses. "
        "Do not start external jobs while a snapshot/reset is in progress."
    )
    st.caption(
        "Uses the existing SQL scripts and your Azure CLI identity. SQL public access/firewall must already be ready. "
        "The UI never re-seeds, cancels jobs, changes networking, or resets automatically."
    )
    enabled = env == WARRANTY_ENV
    if st.button("Read database baseline", disabled=not enabled):
        try:
            with st.spinner("Reading baseline..."):
                reply = sql("db-baseline.sql")
            st.write(dict(zip(["Drafts", "Evidence requests", "Escalations", "Claims not seeded"],
                              baseline_counts(reply.stdout))))
            st.code(reply.stdout, language="text")
        except (CommandError, ValueError) as exc:
            show_error(exc)
    snapshot_ok = st.checkbox("I approve reading and saving a local snapshot of the claim-system actions.")
    if st.button("Save action snapshot", disabled=not enabled or not snapshot_ok):
        try:
            with st.spinner("Checking service activity and saving snapshot..."):
                record = database_action(cli, store, env)
            st.success(f"Snapshot saved: {record['localId']}")
        except (CommandError, ValueError, OSError) as exc:
            show_error(exc)
    reset_ok = st.checkbox("I approve resetting the shared claim database after its snapshot is saved.")
    reset_phrase = st.text_input("Type RESET to confirm")
    if st.button("Snapshot, then reset", disabled=not enabled or not reset_ok or reset_phrase != "RESET"):
        try:
            with st.spinner("Checking jobs, saving snapshot, resetting, and verifying baseline..."):
                record = database_action(cli, store, env, reset=True)
            st.success(f"Snapshot saved and baseline verified 0 0 0 0: {record['localId']}")
        except (CommandError, ValueError, OSError) as exc:
            show_error(exc)
    for audit in [row for row in store.all() if row["kind"] == "database" and row["env"] == env]:
        with st.expander(f"{audit['createdUtc'][:19]} · {audit['state']}"):
            if audit.get("error"):
                st.error(audit["error"])
            st.code(audit.get("snapshot", "No snapshot returned."), language="text")
            st.download_button("Download database audit", json.dumps(audit, indent=2),
                               f"database-{audit['localId']}.json", "application/json", key=audit["localId"])
            if audit.get("resetAttempted") and audit["state"] not in {"reset verified", "reconciled"}:
                st.warning("Reset outcome needs reconciliation. New submissions/resets are blocked.")
                evidence = st.text_input("Manual reconciliation evidence", key=f"db-evidence-{audit['localId']}")
                verified = st.checkbox("I verified no SQL reset is still running and checked the actual database.",
                                       key=f"db-verified-{audit['localId']}")
                if st.button("Record database reconciliation", disabled=not evidence.strip() or not verified,
                             key=f"db-reconcile-{audit['localId']}"):
                    audit.update(state="reconciled", reconciliation=evidence)
                    store.save(audit)
                    st.rerun()
