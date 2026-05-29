#!/usr/bin/env python
"""CLIでタスクを管理するプログラム"""

from datetime import datetime, timedelta
import importlib.metadata
from pathlib import Path
import re
import typer
from rich import box
from rich.console import Console
from rich.table import Table
from storage import (
    load_tasks,
    save_tasks,
    get_data_file,
    reset_data_file,
    set_data_file,
    get_language,
)

# TyperやConsoleのインスタンスを作成
app = typer.Typer(no_args_is_help=False, add_completion=True)
console = Console()

MESSAGES = {
    "en": {
        "added_title": "[bold yellow]Added new task![/]",
        "col_pos": "Position",
        "col_task": "Task",
        "col_due": "Due Date",
        "no_tasks": "- [bold green]later:[/bold green] [blue]No tasks found.[/blue]",
        "list_title": "■ Saved Tasks",
        "col_no": "No.",
        "col_remaining": "Remaining",
        "overdue": "[red]Overdue[/red]",
        "overdue_ago": "[red]Overdue ({} ago)[/red]",
        "unknown": "Unknown",
        "soon": "Soon",
        "unit_d": "d",
        "unit_h": "h",
        "unit_m": "m",
        "err_idx_range": "Number must be between 1 and {}.",
        "deleted_task": "Deleted task: {}",
        "clear_confirm": "Do you want to delete overdue tasks?",
        "cancelled": "Cancelled.",
        "clear_done": "Deleted overdue tasks. Remaining tasks: {}",
        "due_tasks_title": "■ Due Tasks",
        "cal_title_weekly": "■ Weekly Calendar",
        "cal_title_days": "■ {}-Day Calendar",
        "col_date": "Date",
        "col_offset": "Offset",
        "cal_today": "Today",
        "cal_tomorrow": "Tomorrow",
        "info_saved_in": "Tasks are saved in the following file:",
        "err_invalid_time": "Time must be in the correct range (0-23 hours, 0-59 minutes).",
        "err_invalid_nth_weekday": "The specified date (Nth weekday) does not exist.",
        "err_date_range": "Date or time values are out of range.",
        "err_date_not_exist": "The specified date ({}) does not exist.",
        "err_date_format": "Due date must be in a format like '3d', '2h', weekdays, dates, or specific times.",
    },
    "ja": {
        "added_title": "[bold yellow]新しいタスクを追加しました！[/]",
        "col_pos": "追加位置",
        "col_task": "タスク内容",
        "col_due": "通知日時",
        "no_tasks": "- [bold green]later:[/bold green] [blue]タスクはありません。[/blue]",
        "list_title": "■ 保存したタスク一覧",
        "col_no": "番号",
        "col_remaining": "残り",
        "overdue": "[red]超過[/red]",
        "overdue_ago": "[red]超過 ({}前)[/red]",
        "unknown": "不明",
        "soon": "間もなく",
        "unit_d": "日",
        "unit_h": "時間",
        "unit_m": "分",
        "err_idx_range": "番号は 1 から {} の範囲で指定してください。",
        "deleted_task": "タスクを削除しました: {}",
        "clear_confirm": "期限が過ぎたタスクを削除しますか？",
        "cancelled": "キャンセルしました。",
        "clear_done": "期限が過ぎたタスクを削除しました。残りのタスク数: {}",
        "due_tasks_title": "■ 期限が来たタスク",
        "cal_title_weekly": "■ 週間カレンダー",
        "cal_title_days": "■ {}日カレンダー",
        "col_date": "日付",
        "col_offset": "+d",
        "cal_today": "今日",
        "cal_tomorrow": "明日",
        "info_saved_in": "タスクは以下のファイルに保存されています:",
        "err_invalid_time": "時刻は正しい範囲 (0時〜23時, 0分〜59分) で指定してください。",
        "err_invalid_nth_weekday": "指定された日付（第{}番目の{}曜日）は存在しません。",
        "err_date_range": "日付または時刻の数値が正しい範囲外です。",
        "err_date_not_exist": "指定された日付（{}）はカレンダー上に存在しません。",
        "err_date_format": "期限は '3d' / '2h' や曜日（例: '来週月曜'）、日付（例: '5/25'）、時刻指定（例: '明日10時'）の形式で指定してください。",
    }
}


def get_msg(key: str, *args, **kwargs) -> str:
    """設定された言語に応じたメッセージを取得する"""
    lang = get_language()
    msg_tpl = MESSAGES.get(lang, MESSAGES["en"]).get(key, MESSAGES["en"][key])
    return msg_tpl.format(*args, **kwargs)


def get_version() -> str:
    """パッケージのメタデータ、またはpyproject.tomlからバージョン情報を取得する"""
    try:
        return importlib.metadata.version("later-cli")
    except importlib.metadata.PackageNotFoundError:
        pass

    pyproject_path = Path(__file__).parent / "pyproject.toml"
    if not pyproject_path.exists():
        return "unknown"
    try:
        content = pyproject_path.read_text(encoding="utf-8")
        match = re.search(r'^version\s*=\s*"(.*?)"', content, re.MULTILINE)
        if match:
            return match.group(1)
    except Exception:
        pass
    return "unknown"


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    taskfile: Path | None = typer.Option(
        None,
        "--file",
        help="タスクを保存する JSON ファイルを指定します。",
    ),
):
    """CLIでタスクを管理するプログラム"""
    if taskfile is not None:
        set_data_file(taskfile)
    else:
        reset_data_file()

    if ctx.invoked_subcommand is None:
        tasks = load_tasks()
        if len(tasks) <= 2:
            console.print(ctx.get_help())
            raise typer.Exit()
        else:
            show_tasks(tasks, get_msg("list_title"))
            print("[HELP] `later --help`")


@app.command("version")
def version_cmd():
    """バージョン情報を表示する"""
    version = get_version()
    console.print(f"later-cli v{version}")


WEEKDAY_MAP = {
    "月": 0, "火": 1, "水": 2, "木": 3, "金": 4, "土": 5, "日": 6,
    "月曜": 0, "火曜": 1, "水曜": 2, "木曜": 3, "金曜": 4, "土曜": 5, "日曜": 6,
    "月曜日": 0, "火曜日": 1, "水曜日": 2, "木曜日": 3, "金曜日": 4, "土曜日": 5, "日曜日": 6,
}

N_MAP = {
    "第一": 1, "第二": 2, "第三": 3, "第四": 4, "第五": 5,
    "第1": 1, "第2": 2, "第3": 3, "第4": 4, "第5": 5,
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
}


def get_target_year_month(year: int, month: int, shift: int) -> tuple[int, int]:
    """年に月シフト量を加えて、新しい年と月を返す"""
    m = month - 1 + shift
    return year + (m // 12), (m % 12) + 1


def calc_due_date(due: str) -> datetime:
    """期限の表現を解析して、通知日時を計算する"""
    now = datetime.now()
    normalized = due.strip().lower()
    if normalized == "now" or normalized == "すぐ" or normalized == "今":
        return now
    if normalized == "今日" or normalized == "本日":
        return now.replace(
            hour=8, minute=0, second=0, microsecond=0
        )
    if normalized == "明日" or normalized == "tomorrow":
        return (now + timedelta(days=1)).replace(
            hour=8, minute=0, second=0, microsecond=0
        )
    if normalized == "明後日":
        return (now + timedelta(days=2)).replace(
            hour=8, minute=0, second=0, microsecond=0
        )
    if normalized == "来週" or normalized == "nextweek":
        return (now + timedelta(days=7)).replace(
            hour=8, minute=0, second=0, microsecond=0
        )

    # 時刻表現のパース (例: "明日10時", "明後日15時30分", "10:30", "本日18時")
    time_match = re.fullmatch(
        r"^(?P<day_word>今日|本日|明日|明後日|来週)?(?:の)?(?:(?P<hour>\d+)時(?:(?P<minute>\d+)分)?|(?P<hour_colon>\d+):(?P<minute_colon>\d+))$",
        normalized,
    )
    if time_match:
        day_word = time_match.group("day_word")

        # 時・分の取得
        if time_match.group("hour") is not None:
            h = int(time_match.group("hour"))
            m = (
                int(time_match.group("minute"))
                if time_match.group("minute") is not None
                else 0
            )
        else:
            h = int(time_match.group("hour_colon"))
            m = int(time_match.group("minute_colon"))

        if not (0 <= h < 24) or not (0 <= m < 60):
            raise typer.BadParameter(get_msg("err_invalid_time"))

        # 日付のベースを決定
        if day_word == "明日":
            days_offset = 1
        elif day_word == "明後日":
            days_offset = 2
        elif day_word == "来週":
            days_offset = 7
        elif day_word in ("今日", "本日"):
            days_offset = 0
        else:
            # 日付ワードが無い場合 (例: "10時", "10:30")
            # すでにその時間を過ぎている場合は「明日」にする
            temp_date = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if temp_date <= now:
                days_offset = 1
            else:
                days_offset = 0

        return (now + timedelta(days=days_offset)).replace(
            hour=h, minute=m, second=0, microsecond=0
        )

    # 曜日指定のパース (例: "来週月曜", "今週の水曜日", "木曜日")
    weekday_match = re.fullmatch(
        r"^(今週|来週|再来週)?(?:の)?(月|火|水|木|金|土|日)(曜|曜日)?$", normalized
    )
    if weekday_match:
        prefix = weekday_match.group(1)
        weekday_char = weekday_match.group(2)
        target_weekday = WEEKDAY_MAP[weekday_char]
        current_weekday = now.weekday()  # 0=月, 6=日

        if prefix == "来週":
            # 次の月曜日を基準にする
            days_to_monday = 7 - current_weekday
            next_monday = now + timedelta(days=days_to_monday)
            target_date = next_monday + timedelta(days=target_weekday)
        elif prefix == "再来週":
            # 次の次の月曜日を基準にする
            days_to_monday = 7 - current_weekday
            two_weeks_monday = now + timedelta(days=days_to_monday + 7)
            target_date = two_weeks_monday + timedelta(days=target_weekday)
        elif prefix == "今週":
            # 今週の月曜日を基準にする
            this_monday = now - timedelta(days=current_weekday)
            target_date = this_monday + timedelta(days=target_weekday)
            # 過ぎている場合は自動的に来週にする
            if target_date.date() < now.date():
                target_date += timedelta(days=7)
        else:
            # 接頭辞なし（例: "月曜"）: 最も近い未来のその曜日
            days_ahead = target_weekday - current_weekday
            if days_ahead <= 0:  # 今日または過去の曜日の場合は1週間後
                days_ahead += 7
            target_date = now + timedelta(days=days_ahead)

        return target_date.replace(hour=8, minute=0, second=0, microsecond=0)

    # 第N曜日指定のパース (例: "来月第二月曜", "今月の第3水曜日", "第一土曜日")
    nth_match = re.fullmatch(
        r"^(今月|来月|再来月)?(?:の)?(第一|第二|第三|第四|第五|第[1-5]|[1-5])(?:の)?(月|火|水|木|金|土|日)(曜|曜日)?$",
        normalized
    )
    if nth_match:
        prefix = nth_match.group(1)
        nth_str = nth_match.group(2)
        weekday_char = nth_match.group(3)

        nth = N_MAP[nth_str]
        target_weekday = WEEKDAY_MAP[weekday_char]

        # 対象の月シフト量を決定
        shift = 0
        if prefix == "来月":
            shift = 1
        elif prefix == "再来月":
            shift = 2

        def calculate_nth_weekday(y: int, m: int, n: int, w: int) -> datetime:
            # y年m月の第n番目の曜日w(0=月, 6=日)を求める
            # 1日の曜日
            first_day_w = datetime(y, m, 1).weekday()
            first_target_d = 1 + (w - first_day_w) % 7
            target_d = first_target_d + (n - 1) * 7
            # 存在しない日の場合はValueErrorになる
            return datetime(y, m, target_d, 8, 0, 0)

        # ターゲット年月の算出
        t_year, t_month = get_target_year_month(now.year, now.month, shift)

        try:
            target_date = calculate_nth_weekday(t_year, t_month, nth, target_weekday)

            # 過去日付かつ接頭辞が「今月」または無指定の場合は「来月」に補正
            if target_date.date() < now.date() and (prefix == "今月" or not prefix):
                t_year, t_month = get_target_year_month(now.year, now.month, 1)
                target_date = calculate_nth_weekday(t_year, t_month, nth, target_weekday)

            return target_date
        except ValueError:
            raise typer.BadParameter(
                get_msg("err_invalid_nth_weekday", nth, weekday_char)
            )

    # 年を含む特定日付指定のパース (例: "2026-05-25", "2026/5/25 15時", "5/25", "12/3 15:30")
    date_match = re.fullmatch(
        r"^(?:(?P<year>\d{4})[/\-年](?:の)?)?(?P<month>\d{1,2})[/\-月](?P<day>\d{1,2})日?(?:\s*(?:(?P<hour>\d+)時(?:(?P<minute>\d+)分)?|(?P<hour_colon>\d+):(?P<minute_colon>\d+)))?$",
        normalized,
    )
    if date_match:
        m = int(date_match.group("month"))
        d = int(date_match.group("day"))
        year_str = date_match.group("year")

        # 時・分の取得 (デフォルトは朝8時)
        h = 8
        minute_val = 0

        # 時刻指定がある場合
        if date_match.group("hour") is not None:
            h = int(date_match.group("hour"))
            minute_val = (
                int(date_match.group("minute"))
                if date_match.group("minute") is not None
                else 0
            )
        elif date_match.group("hour_colon") is not None:
            h = int(date_match.group("hour_colon"))
            minute_val = int(date_match.group("minute_colon"))

        if (
            not (1 <= m <= 12)
            or not (1 <= d <= 31)
            or not (0 <= h < 24)
            or not (0 <= minute_val < 60)
        ):
            raise typer.BadParameter(get_msg("err_date_range"))

        if year_str is not None:
            # 年が明示されている場合
            t_year = int(year_str)
            try:
                target_date = datetime(t_year, m, d, h, minute_val, 0)
            except ValueError:
                raise typer.BadParameter(
                    get_msg("err_date_not_exist", f"{t_year}-{m:02d}-{d:02d}")
                )
        else:
            # 年が省略されている場合は「今年（過去なら来年）」にする
            t_year = now.year
            try:
                target_date = datetime(t_year, m, d, h, minute_val, 0)
            except ValueError:
                raise typer.BadParameter(
                    get_msg("err_date_not_exist", f"{m:02d}-{d:02d}")
                )

            # 過去日付の場合は「来年」にする
            if target_date.date() < now.date():
                try:
                    target_date = datetime(t_year + 1, m, d, h, minute_val, 0)
                except ValueError:
                    raise typer.BadParameter(
                        get_msg("err_date_not_exist", f"{m:02d}-{d:02d}")
                    )

        return target_date

    match = re.fullmatch(r"(\d+)([dh日])", normalized)
    if not match:
        raise typer.BadParameter(get_msg("err_date_format"))
    amount = int(match.group(1))
    unit = match.group(2)
    if unit == "d":
        return (now + timedelta(days=amount)).replace(
            hour=8, minute=0, second=0, microsecond=0
        )
    if unit == "h":
        return now + timedelta(hours=amount)
    return now


@app.command()
def add(due: str, task: str):
    """
    タスクを追加する

    指定例:
      later.py add "3d" "レポート提出" ... 3日後の朝のタスクを追加
      later.py add "10h" "打ち合わせ" ... 10時間後のタスク
      later.py add "明日" "明日のタスク" ... 明日の朝のタスク
      later.py add "明日10時" "明日10時のタスク" ... 明日の朝10時のタスク
      later.py add "明後日" "明後日のタスク" ... 明後日の朝のタスク
      later.py add "来週" "来週のタスク" ... 来週月曜日の朝のタスク
      later.py add now "今すぐやるタスク" ... 今すぐのタスク
      later.py add 今 "今すぐやるタスク" ... 今すぐ
      later.py add "20時" "今日の20時のタスク" ... 今日の20時にタスクを追加
      later.py add "来週月曜" "レポート提出" ... 来週月曜の朝のタスクを追加
      later.py add "水曜日" "ゴミ出し" ... 次の水曜日の朝のタスクを追加
      later.py add "来月第二月曜" "月次報告" ... 来月の第2月曜日の朝のタスクを追加
    """
    tasks = load_tasks()
    notify_at = calc_due_date(due)
    notify_at_s = notify_at.strftime("%Y-%m-%d %H:%M:%S")
    tasks.append({"date": notify_at_s, "task": task})
    save_tasks(tasks)

    # 追加したタスクのソート後の位置を特定する
    sorted_tasks = load_tasks()
    added_idx = len(sorted_tasks)
    for idx, t in enumerate(sorted_tasks, start=1):
        if t["date"] == notify_at_s and t["task"] == task:
            added_idx = idx
            break

    # 追加成功テーブルを作成
    added_table = Table(
        title=get_msg("added_title"),
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    added_table.add_column(get_msg("col_pos"), justify="center")
    added_table.add_column(get_msg("col_task"), style="cyan")
    added_table.add_column(get_msg("col_due"), style="green")

    added_table.add_row(
        f"[bold green]{added_idx}[/]",
        task,
        notify_at_s
    )
    console.print(added_table)


@app.command("a")
def add_short(due: str, task: str):
    """ alias for `add` command """
    add(due, task)


def get_countdown_str(date_str: str) -> str:
    """期限までのカウントダウン文字列を取得する"""
    try:
        notify_at = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return get_msg("unknown")
    now = datetime.now()
    delta = notify_at - now
    if delta.total_seconds() > 0:
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}{get_msg('unit_d')}")
        if hours > 0:
            parts.append(f"{hours}{get_msg('unit_h')}")
        if minutes > 0:
            parts.append(f"{minutes}{get_msg('unit_m')}")
        
        if not parts:
            return get_msg("soon")
        return "".join(parts)
    else:
        overdue_delta = now - notify_at
        days = overdue_delta.days
        hours, remainder = divmod(overdue_delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}{get_msg('unit_d')}")
        if hours > 0:
            parts.append(f"{hours}{get_msg('unit_h')}")
        if minutes > 0:
            parts.append(f"{minutes}{get_msg('unit_m')}")
            
        if not parts:
            return get_msg("overdue")
        return get_msg("overdue_ago", "".join(parts))


def show_tasks(tasks: list[dict], title: str):
    """タスクのリストを表形式で表示する"""
    if len(tasks) == 0:
        # タスクがない場合はメッセージを表示して終了
        console.print(get_msg("no_tasks"))
        return
    table = Table(
        title=title,
        show_lines=False,
        box=box.ROUNDED)
    table.add_column(get_msg("col_no"), justify="right")
    table.add_column(get_msg("col_task"), style="red")
    table.add_column(get_msg("col_due"), style="green")
    table.add_column(get_msg("col_remaining"), style="cyan")
    for idx, task in enumerate(tasks, start=1):
        countdown = get_countdown_str(task["date"])
        table.add_row(f"{idx}", task["task"], task["date"], countdown)
    console.print(table)


@app.command("list")
def show_alias():
    """タスク一覧を表示"""
    tasks = load_tasks()
    show_tasks(tasks, get_msg("list_title"))


@app.command("ls")
def list_alias():
    """alias for `list` command"""
    tasks = load_tasks()
    show_tasks(tasks, get_msg("list_title"))

@app.command()
def show():
    """alias for `list` command"""
    tasks = load_tasks()
    show_tasks(tasks, get_msg("list_title"))

@app.command()
def delete(number: int):
    """Delete a task by number (例: later.py delete 1)"""
    tasks = load_tasks()
    if number < 1 or number > len(tasks):
        raise typer.BadParameter(get_msg("err_idx_range", len(tasks)))
    deleted_task = tasks.pop(number - 1)
    save_tasks(tasks)
    print(get_msg("deleted_task", deleted_task['task']))
    show()


@app.command("del")
def delelete_alias(number: int):
    """alias for `delete` command"""
    delete(number)


@app.command()
def clear():
    """期限が過ぎたタスクを一括削除する"""
    if not typer.confirm(get_msg("clear_confirm"), default=True):
        print(get_msg("cancelled"))
        return
    tasks = load_tasks()
    now = datetime.now()
    tasks_due = []
    for task in tasks:
        notify_at = datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S")
        remove_date = notify_at - timedelta(days=1)  # 期限が1日以上過ぎたもの
        if remove_date > now:
            tasks_due.append(task)
    save_tasks(tasks_due)
    print(get_msg("clear_done", len(tasks_due)))
    show()  # 更新後のタスクを表示


@app.command()
def check():
    """期限が来たタスクを表示する"""
    tasks = load_tasks()
    now = datetime.now()
    tasks_due = []
    for task in tasks:
        notify_at = datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S")
        if notify_at <= now:
            tasks_due.append(task)
    show_tasks(tasks_due, get_msg("due_tasks_title"))

@app.command("c")
def check_alias():
    """alias for `check` command"""
    check()


def show_cal(days: int = 7):
    """週間予定をカレンダー形式で表示する"""
    title = get_msg("cal_title_weekly") if days == 7 else get_msg("cal_title_days", days)
    tasks = load_tasks()
    now = datetime.now()

    # 日付ごとのタスクマッピング
    from collections import defaultdict
    day_tasks = defaultdict(list)
    for task in tasks:
        try:
            t_date = datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S").date()
            day_tasks[t_date].append(task["task"])
        except ValueError:
            continue

    # 枠線とヘッダーを表示し、カラムを分離して構成
    table = Table(
        title=title,
        show_header=True,
        show_lines=False,
    )
    table.add_column(get_msg("col_date"), justify="center", style="bold")
    table.add_column(get_msg("col_offset"), justify="center")
    table.add_column(get_msg("col_task"), style="cyan")

    for i in range(days):
        target_date = (now + timedelta(days=i)).date()
        date_str = target_date.strftime("%m/%d")

        if i == 0:
            rel_str = get_msg("cal_today")
            color = "bold magenta"
        elif i == 1:
            rel_str = get_msg("cal_tomorrow")
            color = "bold green"
        else:
            rel_str = f"+{i}d"
            color = "cyan"

        tasks_list = day_tasks[target_date]
        tasks_str = ", ".join(tasks_list) if tasks_list else "-"

        table.add_row(
            f"[{color}]{date_str}[/]",
            f"[{color}]{rel_str}[/]",
            f"[{color}]{tasks_str}[/]",
        )

    console.print(table)


@app.command("cal")
def cal(d: int = 7):
    """週間予定をカレンダー形式で表示 `cal --d 10`で任意期間を指定"""
    show_cal(d)

@app.command("cal30")
def cal30():
    """30日分の予定をカレンダー形式で表示 `cal --d 30` と同等"""
    show_cal(30)

@app.command("info")
def info():
    """情報を表示"""
    print(get_msg("info_saved_in"))
    print(get_data_file())


@app.command("language")
def language_cmd(lang: str):
    """
    表示言語を変更する (en / ja)
    
    Change display language (en / ja)
    """
    normalized = lang.strip().lower()
    if normalized not in ("en", "ja"):
        raise typer.BadParameter("Language must be 'en' or 'ja'. (言語は 'en' または 'ja' を指定してください。)")
    
    from storage import set_language
    set_language(normalized)
    
    if normalized == "ja":
        console.print("[green]表示言語を日本語(ja)に設定しました。[/green]")
    else:
        console.print("[green]Display language has been set to English(en).[/green]")


if __name__ == "__main__":
    app()
