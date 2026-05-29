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


def test_sync_command_invalid_api_key(invoke, taskfile):
    set_data_file(taskfile)
    invoke("set", "api_endpoint", "https://example.com")
    invoke("set", "api_key", "invalid_key")
    result = invoke("sync")
    assert result.exit_code != 0
    assert "Invalid API Key format" in result.output


@patch("urllib.request.urlopen")
def test_sync_command_success(mock_urlopen, invoke, taskfile):
    set_data_file(taskfile)
    db_path = get_db_file()

    if os.path.exists(db_path):
        os.remove(db_path)

    # 1. Setup sync configuration with correct API key format
    invoke("set", "api_endpoint", "https://example.com")
    invoke("set", "api_key", "laterapi::mock::key")

    # 2. Add local task to trigger un-synced local events
    invoke("add", "tomorrow", "ローカルタスク1")
    tasks_before = load_tasks()
    task_guid = tasks_before[0]["guid"]

    # 3. Mock urllib.request.urlopen responses (one for post, one for get)
    server_event = {
        "event": "add",
        "guid": "server-task-uuid-1111",
        "timestamp": "2026-05-29 14:00:00",
        "task": "サーバータスク1",
        "status": "todo",
        "date": "2026-05-30 08:00:00",
    }

    mock_res_post = MagicMock()
    mock_res_post.read.return_value = json.dumps({"status": "success"}).encode("utf-8")

    mock_res_get = MagicMock()
    mock_res_get.read.return_value = json.dumps(
        {
            "status": "success",
            "events": [server_event],
        },
        ensure_ascii=False,
    ).encode("utf-8")

    # Use side_effect to return mock_res_post on first call, and mock_res_get on second call
    mock_urlopen.side_effect = [
        MagicMock(__enter__=MagicMock(return_value=mock_res_post)),
        MagicMock(__enter__=MagicMock(return_value=mock_res_get)),
    ]

    # 4. Perform sync
    result = invoke("sync")
    assert result.exit_code == 0, result.output
    assert "Synchronization completed successfully!" in result.output

    # 5. Verify Request structure was correct for both calls
    assert mock_urlopen.call_count == 2

    # 5.1 Verify POST call (record events)
    call_args_post = mock_urlopen.call_args_list[0][0][0]
    assert call_args_post.full_url == "https://example.com/api.php?method=post"
    headers_post = {k.lower(): v for k, v in call_args_post.headers.items()}
    assert headers_post.get("x-api-key") == "laterapi::mock::key"
    assert headers_post.get("authorization") == "Bearer laterapi::mock::key"

    req_body_post = json.loads(call_args_post.data.decode("utf-8"))
    assert len(req_body_post["events"]) == 1
    assert req_body_post["events"][0]["event"] == "add"
    assert req_body_post["events"][0]["guid"] == task_guid

    # 5.2 Verify GET call (fetch events)
    call_args_get = mock_urlopen.call_args_list[1][0][0]
    assert call_args_get.full_url == "https://example.com/api.php?method=get"
    headers_get = {k.lower(): v for k, v in call_args_get.headers.items()}
    assert headers_get.get("x-api-key") == "laterapi::mock::key"
    assert headers_get.get("authorization") == "Bearer laterapi::mock::key"

    req_body_get = json.loads(call_args_get.data.decode("utf-8"))
    assert "date_from" in req_body_get
    assert "date_to" in req_body_get

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
    assert "api_updated_at" in data
    assert data["api_updated_at"] != ""

    # Clean up
    if os.path.exists(db_path):
        os.remove(db_path)


def test_hello_command_without_configuration(invoke, taskfile):
    set_data_file(taskfile)
    result = invoke("sync", "hello")
    assert result.exit_code != 0
    assert "api_endpoint or api_key is not configured" in result.output


def test_hello_command_invalid_api_key(invoke, taskfile):
    set_data_file(taskfile)
    invoke("set", "api_endpoint", "https://example.com")
    invoke("set", "api_key", "invalid_key")
    result = invoke("sync", "hello")
    assert result.exit_code != 0
    assert "Invalid API Key format" in result.output


@patch("urllib.request.urlopen")
def test_hello_command_success(mock_urlopen, invoke, taskfile):
    set_data_file(taskfile)
    invoke("set", "api_endpoint", "https://example.com")
    invoke("set", "api_key", "laterapi::mock::key")

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(
        {"message": "Hello, Later API!"}
    ).encode("utf-8")

    mock_urlopen.return_value.__enter__.return_value = mock_response

    result = invoke("sync", "hello")
    assert result.exit_code == 0, result.output
    assert "API Authentication successful!" in result.output
    assert "Message: Hello, Later API!" in result.output

    # Verify call arguments
    called_req = mock_urlopen.call_args[0][0]
    assert called_req.full_url == "https://example.com/api.php?method=hello"
    headers = {k.lower(): v for k, v in called_req.headers.items()}
    assert headers.get("x-api-key") == "laterapi::mock::key"
    assert headers.get("authorization") == "Bearer laterapi::mock::key"

    req_body = json.loads(called_req.data.decode("utf-8"))
    assert req_body["message"] == "Hello, Later API!"


@patch("urllib.request.urlopen")
def test_hello_command_auth_fail(mock_urlopen, invoke, taskfile):
    set_data_file(taskfile)
    invoke("set", "api_endpoint", "https://example.com")
    invoke("set", "api_key", "laterapi::mock::key")

    # Simulate 401 Unauthorized from server
    from urllib.error import HTTPError

    mock_urlopen.side_effect = HTTPError(
        url="https://example.com/api.php?method=hello",
        code=401,
        msg="Unauthorized",
        hdrs=None,
        fp=None,
    )

    result = invoke("sync", "hello")
    assert result.exit_code != 0
    assert "Authentication failed: Invalid API Key" in result.output
