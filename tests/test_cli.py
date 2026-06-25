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


def test_add_with_english_keywords(invoke, taskfile):
    from datetime import datetime, timedelta

    # today
    result = invoke("add", "today", "Today task")
    assert result.exit_code == 0, result.output
    # tomorrow
    result = invoke("add", "tomorrow", "Tomorrow task")
    assert result.exit_code == 0, result.output
    # tomorrow 20:00
    result = invoke("add", "tomorrow 20:00", "Tomorrow 20:00 task")
    assert result.exit_code == 0, result.output
    # day after tomorrow
    result = invoke("add", "day after tomorrow", "Day after tomorrow task")
    assert result.exit_code == 0, result.output
    # next week
    result = invoke("add", "next week", "Next week task")
    assert result.exit_code == 0, result.output
    # next Monday
    result = invoke("add", "next Monday", "Next Monday task")
    assert result.exit_code == 0, result.output
    # Wednesday
    result = invoke("add", "Wednesday", "Wednesday task")
    assert result.exit_code == 0, result.output
    # next month second Monday
    result = invoke("add", "next month second Monday", "Next month second Monday task")
    assert result.exit_code == 0, result.output
    # tomorrow 10:00
    result = invoke("add", "tomorrow 10:00", "Tomorrow 10:00 task")
    assert result.exit_code == 0, result.output
    # Dec 3 15:30
    result = invoke("add", "Dec 3 15:30", "Monthly report")
    assert result.exit_code == 0, result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    tasks = {t["task"]: t["date"] for t in data["tasks"]}

    now = datetime.now()

    # Assert today at 8:00
    expected_today = now.replace(hour=8, minute=0, second=0, microsecond=0).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    assert tasks["Today task"] == expected_today

    # Assert tomorrow at 8:00
    expected_tomorrow = (
        (now + timedelta(days=1))
        .replace(hour=8, minute=0, second=0, microsecond=0)
        .strftime("%Y-%m-%d %H:%M:%S")
    )
    assert tasks["Tomorrow task"] == expected_tomorrow

    # Assert tomorrow at 20:00
    expected_tomorrow_20 = (
        (now + timedelta(days=1))
        .replace(hour=20, minute=0, second=0, microsecond=0)
        .strftime("%Y-%m-%d %H:%M:%S")
    )
    assert tasks["Tomorrow 20:00 task"] == expected_tomorrow_20

    # Assert day after tomorrow at 8:00
    expected_dat = (
        (now + timedelta(days=2))
        .replace(hour=8, minute=0, second=0, microsecond=0)
        .strftime("%Y-%m-%d %H:%M:%S")
    )
    assert tasks["Day after tomorrow task"] == expected_dat

    # Assert next week (next Monday)
    days_to_monday = 7 - now.weekday()
    expected_next_week = (
        (now + timedelta(days=days_to_monday))
        .replace(hour=8, minute=0, second=0, microsecond=0)
        .strftime("%Y-%m-%d %H:%M:%S")
    )
    assert tasks["Next week task"] == expected_next_week

    # Assert next Monday
    expected_next_monday = (
        (now + timedelta(days=days_to_monday))
        .replace(hour=8, minute=0, second=0, microsecond=0)
        .strftime("%Y-%m-%d %H:%M:%S")
    )
    assert tasks["Next Monday task"] == expected_next_monday

    # Assert Wednesday (nearest future Wednesday)
    days_ahead = 2 - now.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    expected_wednesday = (
        (now + timedelta(days=days_ahead))
        .replace(hour=8, minute=0, second=0, microsecond=0)
        .strftime("%Y-%m-%d %H:%M:%S")
    )
    assert tasks["Wednesday task"] == expected_wednesday

    # Assert next month second Monday
    def get_target_year_month(year, month, shift):
        m = month - 1 + shift
        return year + (m // 12), (m % 12) + 1

    def calculate_nth_weekday(y, m_val, n, w):
        first_day_w = datetime(y, m_val, 1).weekday()
        first_target_d = 1 + (w - first_day_w) % 7
        target_d = first_target_d + (n - 1) * 7
        return datetime(y, m_val, target_d, 8, 0, 0)

    t_year, t_month = get_target_year_month(now.year, now.month, 1)
    expected_second_monday = calculate_nth_weekday(t_year, t_month, 2, 0).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    assert tasks["Next month second Monday task"] == expected_second_monday

    # Assert tomorrow 10:00
    expected_tomorrow_10 = (
        (now + timedelta(days=1))
        .replace(hour=10, minute=0, second=0, microsecond=0)
        .strftime("%Y-%m-%d %H:%M:%S")
    )
    assert tasks["Tomorrow 10:00 task"] == expected_tomorrow_10

    # Assert Dec 3 15:30
    target_year = now.year
    expected_dec3 = datetime(target_year, 12, 3, 15, 30, 0)
    if expected_dec3 < now:
        expected_dec3 = datetime(target_year + 1, 12, 3, 15, 30, 0)
    assert tasks["Monthly report"] == expected_dec3.strftime("%Y-%m-%d %H:%M:%S")


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

    # 具体的な日付で期限を指定 (12/3 15:30)
    result = invoke("renew", "1", "12/3 15:30")
    assert result.exit_code == 0
    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert "12-03 15:30:00" in data["tasks"][0]["date"]

    # 具体的な日付で期限を指定 (6/1)
    result = invoke("renew", "1", "6/1")
    assert result.exit_code == 0
    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert "06-01 08:00:00" in data["tasks"][0]["date"]

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


def test_set_config_command(invoke, taskfile):
    from storage import set_data_file
    import json

    set_data_file(taskfile)

    # 1. 文字列キーの設定 (language)
    result = invoke("set", "language", "ja")
    assert result.exit_code == 0
    assert "language" in result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["language"] == "ja"

    # 2. 真偽値キーの設定 (notifications_enabled -> true)
    result = invoke("set", "notifications_enabled", "true")
    assert result.exit_code == 0

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["notifications_enabled"] is True

    # 3. 数値キーの設定 (port -> 8080)
    result = invoke("set", "port", "8080")
    assert result.exit_code == 0

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    assert data["port"] == 8080

    # 4. tasks キーへの設定拒否の検証
    result = invoke("set", "tasks", "[]")
    assert result.exit_code != 0
    assert "reserved" in result.output or "Cannot set" in result.output


def test_datetime_format_customization(invoke, taskfile):
    from storage import set_data_file

    set_data_file(taskfile)

    # Add a task
    result_add = invoke("add", "2026-06-01 10:30", "フォーマットテストタスク")
    assert result_add.exit_code == 0, result_add.output

    # 1. Default format is m/d[weekday]H:i (e.g., 06/01Mon10:30 for English default)
    result = invoke("list")
    assert result.exit_code == 0
    assert "06/01Mon10:30" in result.output

    # 2. Japanese locale test (e.g., 06/01月10:30)
    invoke("set", "language", "ja")
    result_ja = invoke("list")
    assert result_ja.exit_code == 0
    assert "06/01月10:30" in result_ja.output

    # 3. Custom format via tasks.json (e.g. YYYY/MM/DD)
    invoke("set", "datetime_format", "%Y/%m/%d")
    result_custom = invoke("list")
    assert result_custom.exit_code == 0
    assert "2026/06/01" in result_custom.output
    assert "10:30" not in result_custom.output


def test_datetime_in_format_customization(invoke, taskfile):
    from storage import set_data_file

    set_data_file(taskfile)

    # 1. Set custom input format
    invoke("set", "datetime_in_format", "%Y.%m.%d %H:%M")

    # 2. Add task using this custom format
    result = invoke("add", "2026.07.15 14:45", "カスタム入力タスク")
    assert result.exit_code == 0, result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["task"] == "カスタム入力タスク"
    assert tasks[0]["date"] == "2026-07-15 14:45:00"

    # 3. Test with a custom format that omits the year (e.g. "%m-%d %H:%M")
    invoke("set", "datetime_in_format", "%m-%d %H:%M")

    # We add a task for Dec 25 at 18:00. This should default to this year (or next year if past)
    result = invoke("add", "12-25 18:00", "年省略カスタム入力")
    assert result.exit_code == 0, result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    target_task = [t for t in data["tasks"] if t["task"] == "年省略カスタム入力"][0]
    assert "-12-25 18:00:00" in target_task["date"]

    # 4. Test renew using the custom input format
    # Let's renew "カスタム入力タスク" (which is due 2026-07-15 14:45:00) to "11-30 09:00" using custom format "%m-%d %H:%M"
    result = invoke("renew", "1", "11-30 09:00")
    assert result.exit_code == 0, result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    updated_task = [t for t in data["tasks"] if t["task"] == "カスタム入力タスク"][0]
    assert "-11-30 09:00:00" in updated_task["date"]

    # 5. European style "%d/%m %H:%M" (day before month)
    invoke("set", "datetime_in_format", "%d/%m %H:%M")
    # We add a task on June 15th (15/06) at 12:00
    result = invoke("add", "15/06 12:00", "欧州スタイルタスク")
    assert result.exit_code == 0, result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    european_task = [t for t in data["tasks"] if t["task"] == "欧州スタイルタスク"][0]
    assert "-06-15 12:00:00" in european_task["date"]

    # 6. Japanese style "%m/%d %H:%M" (month before day)
    invoke("set", "datetime_in_format", "%m/%d %H:%M")
    # We add a task on June 15th (06/15) at 12:00
    result = invoke("add", "06/15 12:00", "日本スタイルタスク")
    assert result.exit_code == 0, result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    japanese_task = [t for t in data["tasks"] if t["task"] == "日本スタイルタスク"][0]
    assert "-06-15 12:00:00" in japanese_task["date"]

    # 7. Date-only European style "%d/%m" (no time)
    invoke("set", "datetime_in_format", "%d/%m")
    # We add a task on July 20th (20/07) without time
    result = invoke("add", "20/07", "日付のみ欧州スタイル")
    assert result.exit_code == 0, result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    task_eu_date = [t for t in data["tasks"] if t["task"] == "日付のみ欧州スタイル"][0]
    assert "-07-20 08:00:00" in task_eu_date["date"]

    # 8. Date-only Japanese style "%m/%d" (no time)
    invoke("set", "datetime_in_format", "%m/%d")
    # We add a task on July 20th (07/20) without time
    result = invoke("add", "07/20", "日付のみ日本スタイル")
    assert result.exit_code == 0, result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    task_ja_date = [t for t in data["tasks"] if t["task"] == "日付のみ日本スタイル"][0]
    assert "-07-20 08:00:00" in task_ja_date["date"]

    # 9. Test dedicated "date_in_format" (e.g. "%m.%d")
    invoke("set", "date_in_format", "%m.%d")
    # We add a task on August 10th (08.10) without time
    result = invoke("add", "08.10", "date_in_formatタスク")
    assert result.exit_code == 0, result.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    task_dedicated_date = [
        t for t in data["tasks"] if t["task"] == "date_in_formatタスク"
    ][0]
    assert "-08-10 08:00:00" in task_dedicated_date["date"]

    # 10. Test coexistence of both "datetime_in_format" and "date_in_format"
    invoke("set", "datetime_in_format", "%Y/%m/%d %H:%M")
    invoke("set", "date_in_format", "%m.%d")

    # input matching datetime_in_format
    result_dt = invoke("add", "2026/09/05 16:40", "共存時datetime入力")
    assert result_dt.exit_code == 0, result_dt.output

    # input matching date_in_format
    result_d = invoke("add", "09.05", "共存時date入力")
    assert result_d.exit_code == 0, result_d.output

    data = json.loads(taskfile.read_text(encoding="utf-8"))
    task_dt_coexist = [t for t in data["tasks"] if t["task"] == "共存時datetime入力"][0]
    task_d_coexist = [t for t in data["tasks"] if t["task"] == "共存時date入力"][0]

    assert task_dt_coexist["date"] == "2026-09-05 16:40:00"
    assert "-09-05 08:00:00" in task_d_coexist["date"]


def test_list_formats(invoke, taskfile):
    from storage import set_data_file, save_tasks
    import csv
    import io

    set_data_file(taskfile)

    # 1. Test empty tasks list for json and csv
    save_tasks([])
    result_json_empty = invoke("list", "--format=json")
    assert result_json_empty.exit_code == 0
    empty_tasks = json.loads(result_json_empty.output)
    assert empty_tasks == []

    result_csv_empty = invoke("list", "--format=csv")
    assert result_csv_empty.exit_code == 0
    csv_reader = csv.reader(io.StringIO(result_csv_empty.output))
    rows = list(csv_reader)
    assert len(rows) == 1
    assert rows[0] == ["no", "guid", "task", "due", "remaining", "status"]

    # 2. Add some tasks and check format outputs
    res1 = invoke("add", "2026-06-01 12:00", "タスクCSV_JSON1")
    assert res1.exit_code == 0, res1.output
    res2 = invoke("add", "2026-06-02 15:00", "タスクCSV_JSON2")
    assert res2.exit_code == 0, res2.output
    res3 = invoke("done", "2")
    assert res3.exit_code == 0, res3.output

    # JSON test
    result_json = invoke("list", "--format=json")
    assert result_json.exit_code == 0, result_json.output
    json_data = json.loads(result_json.output)
    assert len(json_data) == 2
    assert json_data[0]["no"] == 1
    assert "guid" in json_data[0]
    assert len(json_data[0]["guid"]) > 0
    assert json_data[0]["task"] == "タスクCSV_JSON1"
    assert json_data[0]["due"] == "2026-06-01 12:00:00"
    assert json_data[0]["status"] == "todo"
    assert "remaining" in json_data[0]

    assert json_data[1]["no"] == 2
    assert "guid" in json_data[1]
    assert len(json_data[1]["guid"]) > 0
    assert json_data[1]["task"] == "タスクCSV_JSON2"
    assert json_data[1]["due"] == "2026-06-02 15:00:00"
    assert json_data[1]["status"] == "done"

    # CSV test
    result_csv = invoke("list", "--format=csv")
    assert result_csv.exit_code == 0
    csv_reader = csv.reader(io.StringIO(result_csv.output))
    rows = list(csv_reader)
    assert len(rows) == 3
    assert rows[0] == ["no", "guid", "task", "due", "remaining", "status"]
    assert rows[1][0] == "1"
    assert len(rows[1][1]) > 0
    assert rows[1][2] == "タスクCSV_JSON1"
    assert rows[1][3] == "2026-06-01 12:00:00"
    assert rows[1][5] == "todo"

    assert rows[2][0] == "2"
    assert len(rows[2][1]) > 0
    assert rows[2][2] == "タスクCSV_JSON2"
    assert rows[2][3] == "2026-06-02 15:00:00"
    assert rows[2][5] == "done"
