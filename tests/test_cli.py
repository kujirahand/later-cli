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
    def run(*args, **kwargs):
        return runner.invoke(app, ["--file", str(taskfile), *args], **kwargs)

    return run


def test_add_writes_to_selected_file_and_show_reads_it(invoke, taskfile):
    result = invoke("add", "now", "テスト用タスク")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    tasks = data["tasks"]
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
    assert "Deleted task: 削除するタスク" in result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["tasks"] == []


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

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["task"] == "来週月曜のタスク"
    assert tasks[0]["date"].endswith("08:00:00")


def test_add_with_nth_weekday(invoke, taskfile):
    result = invoke("add", "来月第二月曜", "来月第二月曜のタスク")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["task"] == "来月第二月曜のタスク"
    assert tasks[0]["date"].endswith("08:00:00")


def test_cal_mode_shows_tasks_in_calendar(invoke, taskfile):
    invoke("add", "now", "今日の予定")
    invoke("add", "明日", "明日の予定")
    invoke("add", "来週", "来週の予定")

    result = invoke("cal")
    assert result.exit_code == 0, result.output
    assert "■ Weekly Calendar" in result.output
    assert "今日の予定" in result.output
    assert "明日の予定" in result.output
    assert "来週の予定" not in result.output


def test_add_with_specific_time(invoke, taskfile):
    result = invoke("add", "明日10時", "明日の予定タスク")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["task"] == "明日の予定タスク"
    assert tasks[0]["date"].endswith("10:00:00")


def test_add_with_specific_date(invoke, taskfile):
    result = invoke("add", "12/3 15:30", "特定の日の予定")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["task"] == "特定の日の予定"
    assert "12-03 15:30:00" in tasks[0]["date"]


def test_add_with_full_date(invoke, taskfile):
    result = invoke("add", "2026-05-25 15:30", "年明示の予定")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["task"] == "年明示の予定"
    assert tasks[0]["date"] == "2026-05-25 15:30:00"


def test_add_with_today(invoke, taskfile):
    result = invoke("add", "今日", "今日の朝の予定")
    assert result.exit_code == 0, result.output
    assert taskfile.exists()

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["task"] == "今日の朝の予定"
    assert tasks[0]["date"].endswith("08:00:00")


def test_version_command(invoke):
    result = invoke("version")
    assert result.exit_code == 0, result.output
    assert "later-cli v" in result.output


def test_no_command_displays_help_when_tasks_are_two_or_fewer(invoke, taskfile):
    # タスクが0件のとき（2つ以下）
    result = invoke()
    assert result.exit_code == 0, result.output
    assert "Usage: " in result.output

    # タスクが2件のとき（2つ以下）
    invoke("add", "now", "タスク1")
    invoke("add", "now", "タスク2")
    result = invoke()
    assert result.exit_code == 0, result.output
    assert "Usage: " in result.output


def test_no_command_displays_tasks_when_tasks_are_more_than_two(invoke, taskfile):
    # タスクが3件のとき（2つより多い）
    invoke("add", "now", "タスク1")
    invoke("add", "now", "タスク2")
    invoke("add", "now", "タスク3")
    result = invoke()
    assert result.exit_code == 0, result.output
    assert "■ Saved Tasks" in result.output
    assert "タスク1" in result.output
    assert "タスク2" in result.output
    assert "タスク3" in result.output


def test_language_toggle(invoke, taskfile):
    # 初期状態は英語 (en)
    result = invoke("add", "now", "タスク1")
    assert "Added new task!" in result.output

    # 日本語に変更
    result = invoke("language", "ja")
    assert result.exit_code == 0, result.output
    assert "表示言語を日本語(ja)に設定しました。" in result.output

    # 日本語になっていることを確認
    result = invoke("show")
    assert "■ 保存したタスク一覧" in result.output

    # 英語に戻す
    result = invoke("language", "en")
    assert result.exit_code == 0, result.output
    assert "Display language has been set to English(en)." in result.output

    result = invoke("show")
    assert "■ Saved Tasks" in result.output


def test_done_and_todo_commands(invoke, taskfile):
    # タスクを追加
    invoke("add", "now", "タスク状態テスト")

    # 追加直後のデフォルトは 'todo' であることを確認
    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["tasks"][0].get("status") == "todo"

    # done に変更
    result = invoke("done", "1")
    assert result.exit_code == 0, result.output
    assert "Marked task as done: タスク状態テスト" in result.output

    # tasks.json で状態を確認
    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["tasks"][0].get("status") == "done"

    # todo に戻す
    result = invoke("todo", "1")
    assert result.exit_code == 0, result.output
    assert "Marked task as todo: タスク状態テスト" in result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["tasks"][0].get("status") == "todo"


def test_list_displays_status_column(invoke, taskfile):
    invoke("add", "now", "タスク1")
    invoke("add", "now", "タスク2")
    invoke("done", "2")

    # 英語での出力を確認 (デフォルト)
    result = invoke("show")
    assert result.exit_code == 0, result.output
    assert "Status" in result.output
    assert "todo" in result.output
    assert "done" in result.output

    # 日本語での出力を確認
    invoke("language", "ja")
    result = invoke("show")
    assert result.exit_code == 0, result.output
    assert "状態" in result.output
    assert "todo" in result.output
    assert "完了" in result.output


def test_clear_overdue_tasks(invoke, taskfile):
    from datetime import datetime, timedelta
    from storage import save_tasks, set_data_file

    set_data_file(taskfile)
    two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    three_days_later = (datetime.now() + timedelta(days=3)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    tasks = [
        {"date": two_days_ago, "task": "過去のタスク", "status": "todo"},
        {"date": three_days_later, "task": "未来のタスク", "status": "todo"},
    ]
    save_tasks(tasks)

    result = invoke("clear", input="y\n")
    assert result.exit_code == 0, result.output
    assert "Deleted overdue tasks" in result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["task"] == "未来のタスク"


def test_clear_done_tasks(invoke, taskfile):
    from storage import save_tasks, set_data_file

    set_data_file(taskfile)
    tasks = [
        {"date": "2026-06-01 08:00:00", "task": "未完了タスク", "status": "todo"},
        {"date": "2026-06-02 08:00:00", "task": "完了タスク", "status": "done"},
    ]
    save_tasks(tasks)

    result = invoke("clear", "--target", "done", input="y\n")
    assert result.exit_code == 0, result.output
    assert "Deleted overdue tasks" in result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["task"] == "未完了タスク"


def test_clear_all_tasks(invoke, taskfile):
    from storage import save_tasks, set_data_file

    set_data_file(taskfile)
    tasks = [
        {"date": "2026-06-01 08:00:00", "task": "タスク1", "status": "todo"},
        {"date": "2026-06-02 08:00:00", "task": "タスク2", "status": "done"},
    ]
    save_tasks(tasks)

    result = invoke("clear", "--target", "all", input="y\n")
    assert result.exit_code == 0, result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["tasks"] == []


def test_clear_cancel(invoke, taskfile):
    from storage import save_tasks, set_data_file

    set_data_file(taskfile)
    tasks = [
        {"date": "2026-06-01 08:00:00", "task": "タスク1", "status": "todo"},
        {"date": "2026-06-02 08:00:00", "task": "タスク2", "status": "done"},
    ]
    save_tasks(tasks)

    # overdue でキャンセル
    result = invoke("clear", "--target", "overdue", input="n\n")
    assert result.exit_code == 0, result.output
    assert "Cancelled." in result.output

    # done でキャンセル
    result = invoke("clear", "--target", "done", input="n\n")
    assert result.exit_code == 0, result.output
    assert "Cancelled." in result.output

    # all でキャンセル
    result = invoke("clear", "--target", "all", input="n\n")
    assert result.exit_code == 0, result.output
    assert "Cancelled." in result.output

    # データが何も消えていないことを確認
    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert len(data["tasks"]) == 2


def test_clear_japanese(invoke, taskfile):
    from datetime import datetime, timedelta
    from storage import save_tasks, set_data_file

    set_data_file(taskfile)

    # 日本語に変更
    invoke("language", "ja")

    two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    tasks = [{"date": two_days_ago, "task": "過去のタスク", "status": "done"}]
    save_tasks(tasks)

    # ja の overdue でクリア
    result = invoke("clear", "--target", "overdue", input="y\n")
    assert result.exit_code == 0, result.output
    assert "期限が過ぎたタスクを削除しました" in result.output

    # データが削除されたことを確認
    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["tasks"] == []

    # 英語に戻しておく (他テストへの影響を避けるため)
    invoke("language", "en")


def test_show_with_targets(invoke, taskfile):
    from datetime import datetime, timedelta
    from storage import save_tasks, set_data_file

    set_data_file(taskfile)

    two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    one_day_later = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    five_days_later = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    fifteen_days_later = (datetime.now() + timedelta(days=15)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    tasks = [
        {"date": two_days_ago, "task": "期限切れ todo", "status": "todo"},
        {"date": one_day_later, "task": "1日後 done", "status": "done"},
        {"date": five_days_later, "task": "5日後 todo", "status": "todo"},
        {"date": fifteen_days_later, "task": "15日後 todo", "status": "todo"},
    ]
    save_tasks(tasks)

    # 1. target = all (デフォルト)
    result = invoke("show", "--target", "all")
    assert result.exit_code == 0
    assert "期限切れ todo" in result.output
    assert "1日後 done" in result.output
    assert "5日後 todo" in result.output
    assert "15日後 todo" in result.output

    # 2. target = due
    result = invoke("show", "--target", "due")
    assert result.exit_code == 0
    assert "期限切れ todo" in result.output
    assert "1日後 done" not in result.output
    assert "5日後 todo" not in result.output
    assert "15日後 todo" not in result.output

    # 3. target = week
    result = invoke("show", "--target", "week")
    assert result.exit_code == 0
    assert "期限切れ todo" in result.output
    assert "1日後 done" in result.output
    assert "5日後 todo" in result.output
    assert "15日後 todo" not in result.output

    # 4. target = month
    result = invoke("show", "--target", "month")
    assert result.exit_code == 0
    assert "期限切れ todo" in result.output
    assert "1日後 done" in result.output
    assert "5日後 todo" in result.output
    assert "15日後 todo" in result.output

    # 5. target = todo
    result = invoke("show", "--target", "todo")
    assert result.exit_code == 0
    assert "期限切れ todo" in result.output
    assert "1日後 done" not in result.output
    assert "5日後 todo" in result.output
    assert "15日後 todo" in result.output

    # Parse table rows to extract displayed indices
    indices = []
    for line in result.output.splitlines():
        if "│" in line:
            parts = [p.strip() for p in line.split("│")]
            if len(parts) >= 2 and parts[1].isdigit():
                indices.append(parts[1])
    assert indices == ["1", "3", "4"]

    # 6. target = done
    result = invoke("show", "--target", "done")
    assert result.exit_code == 0
    assert "期限切れ todo" not in result.output
    assert "1日後 done" in result.output
    assert "5日後 todo" not in result.output
    assert "15日後 todo" not in result.output

    indices = []
    for line in result.output.splitlines():
        if "│" in line:
            parts = [p.strip() for p in line.split("│")]
            if len(parts) >= 2 and parts[1].isdigit():
                indices.append(parts[1])
    assert indices == ["2"]


def test_ls_todo_command(invoke, taskfile):
    from storage import save_tasks, set_data_file

    set_data_file(taskfile)

    tasks = [
        {"date": "2026-06-01 08:00:00", "task": "todoタスク", "status": "todo"},
        {"date": "2026-06-02 08:00:00", "task": "doneタスク", "status": "done"},
    ]
    save_tasks(tasks)

    result = invoke("ls-todo")
    assert result.exit_code == 0
    assert "todoタスク" in result.output
    assert "doneタスク" not in result.output

    indices = []
    for line in result.output.splitlines():
        if "│" in line:
            parts = [p.strip() for p in line.split("│")]
            if len(parts) >= 2 and parts[1].isdigit():
                indices.append(parts[1])
    assert indices == ["1"]


def test_renew_command(invoke, taskfile):
    from storage import save_tasks, set_data_file

    set_data_file(taskfile)

    tasks = [
        {
            "date": "2026-06-01 10:00:00",
            "task": "期限更新テストタスク",
            "status": "todo",
        }
    ]
    save_tasks(tasks)

    # 期限を7日伸ばす (7d)
    result = invoke("renew", "1", "7d")
    assert result.exit_code == 0
    assert "Renewed task" in result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["tasks"][0]["date"] == "2026-06-08 10:00:00"

    # 期限を3時間伸ばす (3h)
    invoke("renew", "1", "3h")
    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["tasks"][0]["date"] == "2026-06-08 13:00:00"

    # 期限を30分伸ばす (30m)
    invoke("renew", "1", "30m")
    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["tasks"][0]["date"] == "2026-06-08 13:30:00"

    # 日本語単位で3日伸ばす (3日)
    invoke("renew", "1", "3日")
    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["tasks"][0]["date"] == "2026-06-11 13:30:00"

    # 期限を1週間伸ばす (1w)
    invoke("renew", "1", "1w")
    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["tasks"][0]["date"] == "2026-06-18 13:30:00"

    # 日本語単位で2週間伸ばす (2週間)
    invoke("renew", "1", "2週間")
    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["tasks"][0]["date"] == "2026-07-02 13:30:00"

    # 無効なインデックス
    result = invoke("renew", "2", "1d")
    assert result.exit_code != 0

    # 無効なオフセット形式
    result = invoke("renew", "1", "abc")
    assert result.exit_code != 0


def test_guid_allocation(invoke, taskfile):
    from storage import set_data_file, load_tasks
    import json

    # 1. 互換性の検証: GUIDなしの古いタスクをJSONファイルに直接書き込む
    set_data_file(taskfile)
    legacy_data = {
        "language": "en",
        "tasks": [
            {"date": "2026-06-01 10:00:00", "task": "レガシータスク1", "status": "todo"}
        ],
    }
    taskfile.write_text(json.dumps(legacy_data, ensure_ascii=False), encoding="utf-8")

    # load_tasks が呼び出された時点で、GUIDが自動生成され保存されるはず
    tasks = load_tasks()
    assert len(tasks) == 1
    assert "guid" in tasks[0]
    guid1 = tasks[0]["guid"]
    assert len(guid1) == 36  # UUID v4 はハイフン込みで36文字

    # JSONファイルを再読込して、永続化されたことを検証
    saved_data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert saved_data["tasks"][0]["guid"] == guid1

    # 2. 新規追加の検証: CLI経由で新規追加されたタスクにもGUIDが最初から付与されること
    invoke("add", "tomorrow", "新規追加タスク")

    saved_data2 = json.loads(taskfile.read_text(encoding="utf-8"))
    assert len(saved_data2["tasks"]) == 2

    # 元のタスクのGUIDが変わっていないことを検証
    t1 = next(t for t in saved_data2["tasks"] if t["task"] == "レガシータスク1")
    assert t1["guid"] == guid1

    # 新規タスクに新しいGUIDが割り当てられていることを検証
    t2 = next(t for t in saved_data2["tasks"] if t["task"] == "新規追加タスク")
    assert "guid" in t2
    assert len(t2["guid"]) == 36
    assert t2["guid"] != guid1
