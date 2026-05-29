import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from typer.testing import CliRunner

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from later import app
from storage import get_db_file, set_data_file, load_tasks


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def taskfile(tmp_path):
    return tmp_path / "tasks.json"


@pytest.fixture
def invoke(runner, taskfile):
    def run(*args, **kwargs):
        return runner.invoke(app, ["--file", str(taskfile), *args], **kwargs)

    return run


def test_sync_command_without_configuration(invoke, taskfile):
    set_data_file(taskfile)
    # Verify it exits with error since api_endpoint and api_key are unconfigured
    result = invoke("sync")
    assert result.exit_code != 0
    assert "api_endpoint or api_key is not configured" in result.output


@patch("urllib.request.urlopen")
def test_sync_command_success(mock_urlopen, invoke, taskfile):
    set_data_file(taskfile)
    db_path = get_db_file()

    if os.path.exists(db_path):
        os.remove(db_path)

    # 1. Setup sync configuration
    invoke("set", "api_endpoint", "https://example.com/api/sync")
    invoke("set", "api_key", "mock_key")

    # 2. Add local task to trigger un-synced local events
    invoke("add", "tomorrow", "ローカルタスク1")
    tasks_before = load_tasks()
    task_guid = tasks_before[0]["guid"]

    # 3. Mock urllib.request.urlopen response
    server_event = {
        "event": "add",
        "guid": "server-task-uuid-1111",
        "timestamp": "2026-05-29 14:00:00",
        "task": "サーバータスク1",
        "status": "todo",
        "date": "2026-05-30 08:00:00",
    }

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(
        {
            "status": "success",
            "timestamp": "2026-05-29 15:00:00",
            "events": [server_event],
        },
        ensure_ascii=False,
    ).encode("utf-8")

    mock_urlopen.return_value.__enter__.return_value = mock_response

    # 4. Perform sync
    result = invoke("sync")
    assert result.exit_code == 0, result.output
    assert "Synchronization completed successfully!" in result.output

    # 5. Verify Request structure was correct
    called_req = mock_urlopen.call_args[0][0]
    assert called_req.full_url == "https://example.com/api/sync"
    assert called_req.headers["X-api-key"] == "mock_key"

    req_body = json.loads(called_req.data.decode("utf-8"))
    assert req_body["api_key"] == "mock_key"
    assert len(req_body["events"]) == 1
    assert req_body["events"][0]["event"] == "add"
    assert req_body["events"][0]["guid"] == task_guid

    # 6. Verify server changes applied to database
    tasks_after = load_tasks()
    assert len(tasks_after) == 2
    assert any(t["task"] == "サーバータスク1" for t in tasks_after)
    assert any(t["task"] == "ローカルタスク1" for t in tasks_after)

    # 7. Verify synced local events moved from events to events_logs
    import sqlite3

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        # events table must be empty
        cursor.execute("SELECT count(*) FROM events")
        assert cursor.fetchone()[0] == 0

        # events_logs must have 1 archived log entry
        cursor.execute("SELECT task_id, json_str FROM events_logs")
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == task_guid
        log_data = json.loads(rows[0][1])
        assert log_data["event"] == "add"
        assert log_data["task"] == "ローカルタスク1"
    finally:
        conn.close()

    # 8. Verify last sync timestamp was updated in JSON config
    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["api_updated_at"] == "2026-05-29 15:00:00"

    # Clean up
    if os.path.exists(db_path):
        os.remove(db_path)
