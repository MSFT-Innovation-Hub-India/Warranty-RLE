from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

from ui.console import (
    CLI, WARRANTY_ENV, CommandError, Reply, Store, baseline_counts, database_action,
    decode_json, invoke, new_record, records, refresh, response_text, rubric_rows,
    run_args, submit,
)

BASELINE = "drafts evidence_requests escalations claims_not_seeded\n------ ----- ----- -----\n0 0 0 0\nOK: 1 batch(es) executed"
EID = "c9fffec9-426a-4eca-93b6-2b0616acd810"
SID = "cf00d339-5217-4cd1-b390-cc0d911735da"


def reply(payload=None, stdout="", command=None):
    return Reply(command or ["frontier-tuning"], stdout, "", payload)


def context():
    return {
        "environment": {"name": "wce-main"},
        "skills": [{"id": SID, "displayName": "warranty-assistant", "isEnabled": True}],
        "details": {SID: {
            "skill": {"prompt": "Use evidence and record the claim draft.", "description": "Adjudicate claims."},
            "rubrics": [{"rubricName": "Coverage", "isEnabled": True, "checklistItems": ["Check limits."]}],
        }},
        "models": {"trainingModels": [
            {"id": "sol", "displayName": "Sol", "isEnabled": True, "isSelected": True},
        ]},
    }


class AdapterTests(unittest.TestCase):
    def test_strategy_arguments(self):
        simple = run_args('Hello "; Remove-Item anything', "Simple", "sol")
        self.assertNotIn("--wait", simple)
        self.assertEqual(simple[3], 'Hello "; Remove-Item anything')
        self.assertNotIn("--early-stop-score", simple)
        self.assertEqual(run_args("q", "BestOfN", best_of_n=4)[-2:], ["--best-of-n", "4"])
        self.assertEqual(run_args("q", "TreeSearch", early_stop=0.95)[-2:], ["--early-stop-score", "0.95"])
        self.assertNotIn("--early-stop-score", run_args("q", "TreeSearch"))
        self.assertNotIn("--best-of-n", run_args("q", "BestOfN"))

    def test_reject_invalid_strategy_parameters(self):
        for kwargs in (
            {"strategy": "Simple", "early_stop": 0.5},
            {"strategy": "TreeSearch", "early_stop": float("nan")},
            {"strategy": "TreeSearch", "early_stop": 1.1},
            {"strategy": "BestOfN", "best_of_n": 0},
            {"strategy": "BestOfN", "best_of_n": 1.5},
            {"strategy": "Simple", "best_of_n": 2},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                run_args("q", **kwargs)

    def test_parse_json_and_progress(self):
        self.assertEqual(decode_json('\ufeff{"status":"Completed"}'), {"status": "Completed"})
        self.assertEqual(decode_json('Waiting...\n{"status":"Completed"}'), {"status": "Completed"})
        for text in ("not json", '{"x":1}\ntrailing garbage', "[]\n{}"):
            with self.assertRaises(ValueError):
                decode_json(text)

    def test_collections_fail_closed(self):
        self.assertEqual(records([]), [])
        self.assertEqual(records({"id": "x", "status": "Cancelled"}), [{"id": "x", "status": "Cancelled"}])
        self.assertEqual(records({"value": []}), [])
        for value in ({}, {"value": [], "nextLink": "page2"}, "oops", [None]):
            with self.assertRaises(ValueError):
                records(value)

    def test_invoke_never_uses_shell_and_preserves_error(self):
        done = subprocess.CompletedProcess(["cli"], 0, '{"id":"x"}', "warning")
        with patch("ui.console.subprocess.run", return_value=done) as run:
            result = invoke(["cli", "literal ; value"])
        self.assertEqual(result.stderr, "warning")
        self.assertFalse(run.call_args.kwargs["shell"])
        with patch("ui.console.subprocess.run", return_value=subprocess.CompletedProcess(["cli"], 7, "out", "err")):
            with self.assertRaises(CommandError) as caught:
                invoke(["cli"])
        self.assertEqual(caught.exception.stdout, "out")
        self.assertEqual(caught.exception.stderr, "err")

    def test_timeout_is_unknown_not_retry(self):
        with patch("ui.console.subprocess.run", side_effect=subprocess.TimeoutExpired(["cli"], 120)) as run:
            with self.assertRaisesRegex(CommandError, "do not resubmit"):
                invoke(["cli"])
        run.assert_called_once()

    def test_idle_checks_all_job_types_and_unknown_status(self):
        cli = CLI("cli")
        with patch.object(cli, "read", side_effect=[reply([]), reply([]), reply([{"id": "x", "status": "Cancelled"}])]) as read:
            self.assertEqual(len(cli.assert_idle(WARRANTY_ENV)), 3)
            self.assertEqual(read.call_args_list[1].args[0], ["evaluate", "list", "--limit", "10000"])
        for status in ("Running", "Pending", "Paused", None):
            with patch.object(cli, "read", return_value=reply([{"id": "x", "status": status}])):
                with self.assertRaisesRegex(ValueError, "active/unknown"):
                    cli.assert_idle(WARRANTY_ENV)

    def test_baseline_is_not_guessed(self):
        self.assertEqual(baseline_counts(BASELINE), (0, 0, 0, 0))
        with self.assertRaises(ValueError):
            baseline_counts("OK")
        with self.assertRaises(ValueError):
            baseline_counts(BASELINE + "\n0 0 0 0")

    def test_response_and_historical_rubrics(self):
        self.assertEqual(response_text({"Response": [{"Content": "# Hello"}]}), "# Hello")
        rows = rubric_rows({"skillResults": [{"rubricResults": [
            {"snapshotData": {"displayName": "Coverage", "importance": "critical"}, "score": 0},
            {"snapshotData": {"displayName": "Gaps"}, "score": None},
        ]}]})
        self.assertEqual(rows[0]["Score"], 0)
        self.assertIsNone(rows[1]["Score"])
        skipped = rubric_rows({"rubricResults": [{"displayName": "Gaps", "score": 0, "scoreReason": ""}]})
        self.assertIsNone(skipped[0]["Score"])


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name))
        self.cli = CLI("cli")

    def tearDown(self):
        self.temp.cleanup()

    def test_store_persists_and_locks(self):
        row = new_record("execution", WARRANTY_ENV)
        row["state"] = "unknown"
        self.store.save(row)
        self.assertEqual(Store(Path(self.temp.name)).load(row["localId"]), row)
        with self.assertRaisesRegex(ValueError, "reconcile"):
            self.store.assert_reconciled()
        with self.store.lock(), self.assertRaises(ValueError):
            with self.store.lock():
                self.fail("Second lock acquired")
        with self.assertRaises(ValueError):
            self.store.load("..\\secret")

    def test_submit_saves_attempt_before_write_and_runs_once(self):
        def execute(command, timeout):
            self.assertEqual(command[0], "cli")
            self.assertEqual(timeout, 180)
            self.assertEqual(self.store.all()[0]["state"], "submitting")
            return reply({"executionId": EID, "status": "Running"}, '{"status":"Running"}')
        with patch.object(self.cli, "assert_idle", return_value=[]), \
             patch("ui.console.sql", return_value=reply(stdout=BASELINE)), \
             patch("ui.console.invoke", side_effect=execute) as call:
            row = submit(self.cli, self.store, WARRANTY_ENV, run_args("q", "Simple"), context())
        self.assertEqual(row["executionId"], EID)
        self.assertEqual(row["state"], "Running")
        call.assert_called_once()

    def test_unknown_submission_blocks_another(self):
        with patch.object(self.cli, "assert_idle", return_value=[]), \
             patch("ui.console.sql", return_value=reply(stdout=BASELINE)), \
             patch("ui.console.invoke", side_effect=CommandError("timeout", ["cli"])) as call:
            with self.assertRaises(CommandError):
                submit(self.cli, self.store, WARRANTY_ENV, run_args("q", "Simple"), context())
            with self.assertRaises(ValueError):
                submit(self.cli, self.store, WARRANTY_ENV, run_args("q", "Simple"), context())
        call.assert_called_once()
        self.assertEqual(self.store.all()[0]["state"], "unknown")

    def test_missing_execution_id_is_not_success(self):
        with patch.object(self.cli, "assert_idle", return_value=[]), \
             patch("ui.console.sql", return_value=reply(stdout=BASELINE)), \
             patch("ui.console.invoke", return_value=reply({"status": "Running"}, '{"status":"Running"}')):
            with self.assertRaisesRegex(ValueError, "did not return an execution ID"):
                submit(self.cli, self.store, WARRANTY_ENV, run_args("q", "Simple"), context())
        self.assertEqual(self.store.all()[0]["state"], "unknown")
        self.assertEqual(self.store.all()[0]["stdout"], '{"status":"Running"}')

    def test_dirty_baseline_never_submits(self):
        with patch.object(self.cli, "assert_idle", return_value=[]), \
             patch("ui.console.sql", return_value=reply(stdout=BASELINE.replace("0 0 0 0", "1 0 0 0"))), \
             patch("ui.console.invoke") as call:
            with self.assertRaisesRegex(ValueError, "not clean"):
                submit(self.cli, self.store, WARRANTY_ENV, run_args("q", "Simple"), context())
        call.assert_not_called()

    def test_refresh_reads_only_and_keeps_original_request(self):
        row = new_record("execution", WARRANTY_ENV)
        row.update(state="Running", executionId=EID, command=["original"])
        with patch.object(self.cli, "read", return_value=reply({"Id": EID, "Status": "Completed"})) as read:
            updated = refresh(self.cli, self.store, row)
        read.assert_called_once_with(["executions", "get", EID], WARRANTY_ENV)
        self.assertEqual(updated["command"], ["original"])
        self.assertEqual(updated["state"], "Completed")

    def test_reset_saves_snapshot_then_rechecks_jobs(self):
        events = []
        def execute(script):
            events.append(script)
            if script == "db-reset-actions.sql":
                self.assertEqual(self.store.all()[0]["snapshot"], "snapshot data")
            return reply(stdout="snapshot data" if script == "db-actions-snapshot.sql" else BASELINE)
        with patch.object(self.cli, "assert_idle", return_value=[]) as idle, \
             patch("ui.console.sql", side_effect=execute):
            row = database_action(self.cli, self.store, WARRANTY_ENV, reset=True)
        self.assertEqual(events, ["db-actions-snapshot.sql", "db-reset-actions.sql", "db-baseline.sql"])
        self.assertEqual(idle.call_count, 2)
        self.assertEqual(row["state"], "reset verified")

    def test_reset_blocks_active_jobs_and_other_environment(self):
        with patch.object(self.cli, "assert_idle", side_effect=ValueError("active")), \
             patch("ui.console.sql") as call:
            with self.assertRaises(ValueError):
                database_action(self.cli, self.store, WARRANTY_ENV, reset=True)
            with self.assertRaises(ValueError):
                database_action(self.cli, self.store, str(uuid4()), reset=True)
        call.assert_not_called()

    def test_second_activity_check_blocks_reset_after_snapshot(self):
        with patch.object(self.cli, "assert_idle", side_effect=[[], ValueError("active")]), \
             patch("ui.console.sql", return_value=reply(stdout="snapshot")) as call:
            with self.assertRaises(ValueError):
                database_action(self.cli, self.store, WARRANTY_ENV, reset=True)
        self.assertEqual(call.call_count, 1)
        self.assertEqual(self.store.all()[0]["snapshot"], "snapshot")

    def test_unknown_reset_blocks_future_submissions_and_resets(self):
        with patch.object(self.cli, "assert_idle", return_value=[]), \
             patch("ui.console.sql", side_effect=[reply(stdout="snapshot"), CommandError("timeout", ["sql"])]):
            with self.assertRaises(CommandError):
                database_action(self.cli, self.store, WARRANTY_ENV, reset=True)
        self.assertTrue(self.store.all()[0]["resetAttempted"])
        with self.assertRaisesRegex(ValueError, "reconcile"):
            self.store.assert_reconciled()


class AppTests(unittest.TestCase):
    def setUp(self):
        from streamlit.testing.v1 import AppTest
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name))
        self.mock_cli = MagicMock()
        self.mock_cli.read.return_value = reply({"config": {"env_id": WARRANTY_ENV}})
        self.mock_cli.context.return_value = context()
        self.mock_cli.command.side_effect = lambda args, env: ["cli", "-e", env, *args, "-o", "json-legacy"]
        self.cli_patch = patch("ui.console.CLI", return_value=self.mock_cli)
        self.store_patch = patch("ui.console.Store", return_value=self.store)
        self.cli_patch.start()
        self.store_patch.start()
        import streamlit as st
        st.cache_data.clear()
        self.app = AppTest.from_file(str(Path(__file__).with_name("app.py")), default_timeout=20)

    def tearDown(self):
        self.cli_patch.stop()
        self.store_patch.stop()
        self.temp.cleanup()

    def test_initial_ui_and_strategy_controls(self):
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.selectbox[1].value, "sol")
        self.app.segmented_control[0].set_value("TreeSearch").run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.number_input[0].value, 0.95)
        self.app.segmented_control[0].set_value("BestOfN").run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.number_input[0].value, 4)
        self.assertTrue(next(button for button in self.app.button if button.label == "Execute once").disabled)

    def test_saved_result_formats_response_and_json(self):
        row = new_record("execution", WARRANTY_ENV)
        row.update(state="Completed", executionId=EID, result={
            "Id": EID, "Status": "Completed", "Response": [{"Content": "## Decision\n\nApprove **INR 69,575**."}],
            "skillResults": [{"id": SID, "version": 11, "snapshotData": {"displayName": "warranty-assistant"},
                              "score": 1, "rubricResults": [
                                  {"snapshotData": {"displayName": "Coverage"}, "score": 1},
                              ]}],
        })
        self.store.save(row)
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any("69,575" in element.value for element in self.app.markdown))
        self.assertTrue(any(expander.label == "Raw execution JSON" for expander in self.app.expander))
        self.assertTrue(self.app.dataframe)


if __name__ == "__main__":
    unittest.main()
