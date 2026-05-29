import json
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from later import app
from storage import DEFAULT_DATA_FILE


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def taskfile(tmp_path):
    return tmp_path / "tasks.json"


@pytest.fixture
def invoke(runner, taskfile):
    def run(*args):
        return runner.invoke(app, ["--file", str(taskfile), *args])

    return run


def test_add_writes_to_selected_file_and_show_reads_it(invoke, taskfile):
    result = invoke("add", "now", "テスト用タスク")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    tasks = json.loads(taskfile.read_text(encoding="utf-8"))
    assert len(tasks) == 1
    assert tasks[0]["task"] == "テスト用タスク"

    result = invoke("show")
    assert result.exit_code == 0, result.output
    assert "テスト用タスク" in result.output


def test_delete_removes_task_from_selected_file(invoke, taskfile):
    result = invoke("add", "now", "削除するタスク")
    assert result.exit_code == 0, result.output

    result = invoke("delete", "1")
    assert result.exit_code == 0, result.output
    assert "タスクを削除しました: 削除するタスク" in result.output

    tasks = json.loads(taskfile.read_text(encoding="utf-8"))
    assert tasks == []


def test_info_shows_selected_file(invoke, taskfile):
    result = invoke("info")
    assert result.exit_code == 0, result.output
    assert str(taskfile) in result.output


def test_file_option_does_not_change_default_task_file(invoke):
    default_file = Path(DEFAULT_DATA_FILE)
    before = default_file.read_bytes() if default_file.exists() else None

    result = invoke("add", "now", "標準ファイルに入らないタスク")
    assert result.exit_code == 0, result.output

    after = default_file.read_bytes() if default_file.exists() else None
    assert before == after


def test_add_with_weekday(invoke, taskfile):
    result = invoke("add", "来週月曜", "来週月曜のタスク")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    tasks = json.loads(taskfile.read_text(encoding="utf-8"))
    assert len(tasks) == 1
    assert tasks[0]["task"] == "来週月曜のタスク"
    assert tasks[0]["date"].endswith("08:00:00")


def test_add_with_nth_weekday(invoke, taskfile):
    result = invoke("add", "来月第二月曜", "来月第二月曜のタスク")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    tasks = json.loads(taskfile.read_text(encoding="utf-8"))
    assert len(tasks) == 1
    assert tasks[0]["task"] == "来月第二月曜のタスク"
    assert tasks[0]["date"].endswith("08:00:00")


def test_cal_mode_shows_tasks_in_calendar(invoke, taskfile):
    invoke("add", "now", "今日の予定")
    invoke("add", "明日", "明日の予定")
    invoke("add", "来週", "来週の予定")

    result = invoke("cal")
    assert result.exit_code == 0, result.output
    assert "■ 週間カレンダー" in result.output
    assert "今日の予定" in result.output
    assert "明日の予定" in result.output
    assert "来週の予定" not in result.output


def test_add_with_specific_time(invoke, taskfile):
    result = invoke("add", "明日10時", "明日の予定タスク")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    tasks = json.loads(taskfile.read_text(encoding="utf-8"))
    assert len(tasks) == 1
    assert tasks[0]["task"] == "明日の予定タスク"
    assert tasks[0]["date"].endswith("10:00:00")


def test_add_with_specific_date(invoke, taskfile):
    result = invoke("add", "12/3 15:30", "特定の日の予定")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    tasks = json.loads(taskfile.read_text(encoding="utf-8"))
    assert len(tasks) == 1
    assert tasks[0]["task"] == "特定の日の予定"
    assert "12-03 15:30:00" in tasks[0]["date"]


def test_add_with_full_date(invoke, taskfile):
    result = invoke("add", "2026-05-25 15:30", "年明示の予定")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    tasks = json.loads(taskfile.read_text(encoding="utf-8"))
    assert len(tasks) == 1
    assert tasks[0]["task"] == "年明示の予定"
    assert tasks[0]["date"] == "2026-05-25 15:30:00"


def test_add_with_today(invoke, taskfile):
    result = invoke("add", "今日", "今日の朝の予定")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    tasks = json.loads(taskfile.read_text(encoding="utf-8"))
    assert len(tasks) == 1
    assert tasks[0]["task"] == "今日の朝の予定"
    assert tasks[0]["date"].endswith("08:00:00")


def test_version_command(invoke):
    result = invoke("version")
    assert result.exit_code == 0, result.output
    assert "later-cli v" in result.output
