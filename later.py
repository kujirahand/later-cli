#!/usr/bin/env python
"""CLI application for managing tasks."""

from datetime import datetime, timedelta
import importlib.metadata
from pathlib import Path
import re
import typer
from typing import Literal
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

CLEAR_TARGETS = Literal[
    "overdue",  # Tasks past their due date
    "all",  # All tasks
    "done",  # Completed tasks
]

# Create Typer and Rich console instances
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
        "clear_confirm_done": "Do you want to delete done tasks?",
        "clear_confirm_all": "Do you want to delete all tasks?",
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
        "col_status": "Status",
        "status_todo": "[yellow]todo[/yellow]",
        "status_done": "[green]done[/green]",
        "marked_done": "Marked task as done: {}",
        "marked_todo": "Marked task as todo: {}",
    },
    "ja": {
        "added_title": "[bold yellow]新しいタスクを追加しました！[/]",
        "col_pos": "追加位置",
        "col_task": "タスク内容",
        "col_due": "通知日時",
        "no_tasks": "- [bold green]later:[/bold green] [blue]タスクはありません。[/blue]",
        "list_title": "■ 保存したタスク一覧",
        "col_no": "No",
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
        "clear_confirm_done": "完了(done)のタスクを削除しますか?",
        "clear_confirm_all": "全てのタスクを削除しますか?",
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
        "col_status": "状態",
        "status_todo": "[yellow]todo[/yellow]",
        "status_done": "[green]完了[/green]",
        "marked_done": "タスクを完了にしました: {}",
        "marked_todo": "タスクを未完了にしました: {}",
    },
}


def get_msg(key: str, *args, **kwargs) -> str:
    """Get a localized message for the currently configured language."""
    lang = get_language()
    msg_tpl = MESSAGES.get(lang, MESSAGES["en"]).get(key, MESSAGES["en"][key])
    return msg_tpl.format(*args, **kwargs)


def get_version() -> str:
    """Get version info from package metadata or pyproject.toml."""
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
        help="specify a custom task file (default: tasks.json in the current directory)",
    ),
):
    """CLI for managing tasks with due dates"""
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
    """show version info"""
    version = get_version()
    console.print(f"later-cli v{version}")


WEEKDAY_MAP = {
    "月": 0,
    "火": 1,
    "水": 2,
    "木": 3,
    "金": 4,
    "土": 5,
    "日": 6,
    "月曜": 0,
    "火曜": 1,
    "水曜": 2,
    "木曜": 3,
    "金曜": 4,
    "土曜": 5,
    "日曜": 6,
    "月曜日": 0,
    "火曜日": 1,
    "水曜日": 2,
    "木曜日": 3,
    "金曜日": 4,
    "土曜日": 5,
    "日曜日": 6,
}

N_MAP = {
    "第一": 1,
    "第二": 2,
    "第三": 3,
    "第四": 4,
    "第五": 5,
    "第1": 1,
    "第2": 2,
    "第3": 3,
    "第4": 4,
    "第5": 5,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
}


def get_target_year_month(year: int, month: int, shift: int) -> tuple[int, int]:
    """Return the new year/month after applying a month shift."""
    m = month - 1 + shift
    return year + (m // 12), (m % 12) + 1


def calc_due_date(due: str) -> datetime:
    """Parse a due expression and return the notification datetime."""
    now = datetime.now()
    normalized = due.strip().lower()
    if normalized == "now" or normalized == "すぐ" or normalized == "今":
        return now
    if normalized == "今日" or normalized == "本日":
        return now.replace(hour=8, minute=0, second=0, microsecond=0)
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

    # Parse time expressions (e.g. "明日10時", "明後日15時30分", "10:30", "本日18時")
    time_match = re.fullmatch(
        r"^(?P<day_word>今日|本日|明日|明後日|来週)?(?:の)?(?:(?P<hour>\d+)時(?:(?P<minute>\d+)分)?|(?P<hour_colon>\d+):(?P<minute_colon>\d+))$",
        normalized,
    )
    if time_match:
        day_word = time_match.group("day_word")

        # Extract hour/minute
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

        # Decide the base date offset
        if day_word == "明日":
            days_offset = 1
        elif day_word == "明後日":
            days_offset = 2
        elif day_word == "来週":
            days_offset = 7
        elif day_word in ("今日", "本日"):
            days_offset = 0
        else:
            # If no day word is specified (e.g. "10時", "10:30"),
            # use tomorrow when the time has already passed today.
            temp_date = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if temp_date <= now:
                days_offset = 1
            else:
                days_offset = 0

        return (now + timedelta(days=days_offset)).replace(
            hour=h, minute=m, second=0, microsecond=0
        )

    # Parse weekday expressions (e.g. "来週月曜", "今週の水曜日", "木曜日")
    weekday_match = re.fullmatch(
        r"^(今週|来週|再来週)?(?:の)?(月|火|水|木|金|土|日)(曜|曜日)?$", normalized
    )
    if weekday_match:
        prefix = weekday_match.group(1)
        weekday_char = weekday_match.group(2)
        target_weekday = WEEKDAY_MAP[weekday_char]
        current_weekday = now.weekday()  # 0=Mon, 6=Sun

        if prefix == "来週":
            # Use next Monday as the base
            days_to_monday = 7 - current_weekday
            next_monday = now + timedelta(days=days_to_monday)
            target_date = next_monday + timedelta(days=target_weekday)
        elif prefix == "再来週":
            # Use Monday of the following week as the base
            days_to_monday = 7 - current_weekday
            two_weeks_monday = now + timedelta(days=days_to_monday + 7)
            target_date = two_weeks_monday + timedelta(days=target_weekday)
        elif prefix == "今週":
            # Use this week's Monday as the base
            this_monday = now - timedelta(days=current_weekday)
            target_date = this_monday + timedelta(days=target_weekday)
            # If already passed this week, move to next week
            if target_date.date() < now.date():
                target_date += timedelta(days=7)
        else:
            # Without prefix (e.g. "月曜"): nearest future weekday
            days_ahead = target_weekday - current_weekday
            if days_ahead <= 0:  # Today/past weekday goes to next week
                days_ahead += 7
            target_date = now + timedelta(days=days_ahead)

        return target_date.replace(hour=8, minute=0, second=0, microsecond=0)

    # Parse Nth-weekday expressions (e.g. "来月第二月曜", "今月の第3水曜日", "第一土曜日")
    nth_match = re.fullmatch(
        r"^(今月|来月|再来月)?(?:の)?(第一|第二|第三|第四|第五|第[1-5]|[1-5])(?:の)?(月|火|水|木|金|土|日)(曜|曜日)?$",
        normalized,
    )
    if nth_match:
        prefix = nth_match.group(1)
        nth_str = nth_match.group(2)
        weekday_char = nth_match.group(3)

        nth = N_MAP[nth_str]
        target_weekday = WEEKDAY_MAP[weekday_char]

        # Determine target month shift
        shift = 0
        if prefix == "来月":
            shift = 1
        elif prefix == "再来月":
            shift = 2

        def calculate_nth_weekday(y: int, m: int, n: int, w: int) -> datetime:
            # Compute the nth weekday w in month m of year y (0=Mon, 6=Sun)
            # Weekday of the 1st day of the month
            first_day_w = datetime(y, m, 1).weekday()
            first_target_d = 1 + (w - first_day_w) % 7
            target_d = first_target_d + (n - 1) * 7
            # datetime raises ValueError if the computed day does not exist
            return datetime(y, m, target_d, 8, 0, 0)

        # Calculate target year/month
        t_year, t_month = get_target_year_month(now.year, now.month, shift)

        try:
            target_date = calculate_nth_weekday(t_year, t_month, nth, target_weekday)

            # If in the past and prefix is "今月" or omitted, move to next month
            if target_date.date() < now.date() and (prefix == "今月" or not prefix):
                t_year, t_month = get_target_year_month(now.year, now.month, 1)
                target_date = calculate_nth_weekday(
                    t_year, t_month, nth, target_weekday
                )

            return target_date
        except ValueError:
            raise typer.BadParameter(
                get_msg("err_invalid_nth_weekday", nth, weekday_char)
            )

    # Parse specific-date expressions (e.g. "2026-05-25", "2026/5/25 15時", "5/25", "12/3 15:30")
    date_match = re.fullmatch(
        r"^(?:(?P<year>\d{4})[/\-年](?:の)?)?(?P<month>\d{1,2})[/\-月](?P<day>\d{1,2})日?(?:\s*(?:(?P<hour>\d+)時(?:(?P<minute>\d+)分)?|(?P<hour_colon>\d+):(?P<minute_colon>\d+)))?$",
        normalized,
    )
    if date_match:
        m = int(date_match.group("month"))
        d = int(date_match.group("day"))
        year_str = date_match.group("year")

        # Parse time (default: 08:00)
        h = 8
        minute_val = 0

        # If a time is explicitly specified
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
            # Explicit year was provided
            t_year = int(year_str)
            try:
                target_date = datetime(t_year, m, d, h, minute_val, 0)
            except ValueError:
                raise typer.BadParameter(
                    get_msg("err_date_not_exist", f"{t_year}-{m:02d}-{d:02d}")
                )
        else:
            # If year is omitted, use this year (or next year if already past)
            t_year = now.year
            try:
                target_date = datetime(t_year, m, d, h, minute_val, 0)
            except ValueError:
                raise typer.BadParameter(
                    get_msg("err_date_not_exist", f"{m:02d}-{d:02d}")
                )

            # Move to next year if the date is already in the past
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
        Add a task.

        Examples:
      later.py add 3d "レポート提出" ... add task due in 3 days (default time is 8:00 AM)
      later.py add 10h "打ち合わせ" ... add task due in 10 hours
      later.py add now "今すぐやるタスク" ... add task due now
      later.py add "3/10 15:30" "特定の日のタスク" ... add task due on March 10 at 15:30 (this year or next year if date has passed)
            later.py add 明日 "明日のタスク" ... task due tomorrow morning
            later.py add 明日10時 "明日10時のタスク" ... task due tomorrow at 10:00
            later.py add 明後日 "明後日のタスク" ... task due the morning of the day after tomorrow
            later.py add 来週 "来週のタスク" ... task due next Monday morning
            later.py add 今 "今すぐやるタスク" ... task due immediately
            later.py add 20時 "今日の20時のタスク" ... task due today at 20:00
            later.py add 来週月曜 "レポート提出" ... task due next Monday morning
            later.py add 水曜日" "ゴミ出し" ... task due next Wednesday morning
            later.py add 来月第二月曜 "月次報告" ... task due on the second Monday of next month
    """
    tasks = load_tasks()
    notify_at = calc_due_date(due)
    notify_at_s = notify_at.strftime("%Y-%m-%d %H:%M:%S")
    tasks.append({"date": notify_at_s, "task": task, "status": "todo"})
    save_tasks(tasks)

    # Find the inserted task position after sorting
    sorted_tasks = load_tasks()
    added_idx = len(sorted_tasks)
    for idx, t in enumerate(sorted_tasks, start=1):
        if t["date"] == notify_at_s and t["task"] == task:
            added_idx = idx
            break

    # Build a table showing the successfully added task
    added_table = Table(
        title=get_msg("added_title"),
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    added_table.add_column(get_msg("col_pos"), justify="center")
    added_table.add_column(get_msg("col_task"), style="cyan")
    added_table.add_column(get_msg("col_due"), style="green")

    added_table.add_row(f"[bold green]{added_idx}[/]", task, notify_at_s)
    console.print(added_table)


@app.command("a")
def add_short(due: str, task: str):
    """alias for `add` command"""
    add(due, task)


def get_countdown_str(date_str: str) -> str:
    """Return a human-readable countdown string until the due date."""
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
    """Display the task list in a table."""
    if len(tasks) == 0:
        # Show message and return when there are no tasks
        console.print(get_msg("no_tasks"))
        return
    table = Table(title=title, show_lines=False, box=box.ROUNDED)
    table.add_column(get_msg("col_no"), justify="right")
    table.add_column(get_msg("col_task"), style="red")
    table.add_column(get_msg("col_due"), style="green")
    table.add_column(get_msg("col_remaining"), style="cyan")
    table.add_column(get_msg("col_status"), justify="center")
    for idx, task in enumerate(tasks, start=1):
        countdown = get_countdown_str(task["date"])
        status_key = "status_done" if task.get("status") == "done" else "status_todo"
        status_str = get_msg(status_key)
        table.add_row(f"{idx}", task["task"], task["date"], countdown, status_str)
    console.print(table)


@app.command("list")
def show_alias():
    """Show the task list."""
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
    """Delete a task by number (e.g. later.py delete 1)."""
    tasks = load_tasks()
    if number < 1 or number > len(tasks):
        raise typer.BadParameter(get_msg("err_idx_range", len(tasks)))
    deleted_task = tasks.pop(number - 1)
    save_tasks(tasks)
    print(get_msg("deleted_task", deleted_task["task"]))
    show()


@app.command("del")
def delelete_alias(number: int):
    """alias for `delete` command"""
    delete(number)


@app.command()
def clear(target: CLEAR_TARGETS = "overdue"):
    """Bulk-delete tasks based on the selected target."""
    tasks = load_tasks()
    now = datetime.now()
    if target == "overdue":
        if not typer.confirm(get_msg("clear_confirm"), default=True):
            print(get_msg("cancelled"))
            return
        tasks_due = []
        for task in tasks:
            notify_at = datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S")
            remove_date = notify_at - timedelta(days=1)  # Remove tasks overdue by at least one day
            if remove_date > now:
                tasks_due.append(task)
        save_tasks(tasks_due)
        print(get_msg("clear_done", len(tasks_due)))
    elif target == "done":
        if not typer.confirm(get_msg("clear_confirm_done"), default=True):
            print(get_msg("cancelled"))
            return
        tasks_remaining = [t for t in tasks if t.get("status") != "done"]
        save_tasks(tasks_remaining)
        print(get_msg("clear_done", len(tasks_remaining)))
    elif target == "all":
        if not typer.confirm(get_msg("clear_confirm_all"), default=True):
            print(get_msg("cancelled"))
            return
        save_tasks([])
        print(get_msg("clear_done", 0))
    # Show tasks after update
    show()


@app.command()
def check():
    """Show tasks whose due time has arrived."""
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
    """Display scheduled tasks in calendar format."""
    title = (
        get_msg("cal_title_weekly") if days == 7 else get_msg("cal_title_days", days)
    )
    tasks = load_tasks()
    now = datetime.now()

    # Map tasks by date
    from collections import defaultdict

    day_tasks = defaultdict(list)
    for task in tasks:
        try:
            t_date = datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S").date()
            day_tasks[t_date].append(task["task"])
        except ValueError:
            continue

    # Build table columns with headers and borders
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
    """Show calendar view; use cal --d 10 to specify a custom range."""
    show_cal(d)


@app.command("cal30")
def cal30():
    """Show a 30-day calendar view (same as cal --d 30)."""
    show_cal(30)


@app.command("info")
def info():
    """Show information."""
    print(get_msg("info_saved_in"))
    print(get_data_file())


@app.command("language")
def language_cmd(lang: str):
    """
    Change display language (en / ja).
    """
    normalized = lang.strip().lower()
    if normalized not in ("en", "ja"):
        raise typer.BadParameter(
            "Language must be 'en' or 'ja'. (言語は 'en' または 'ja' を指定してください。)"
        )

    from storage import set_language

    set_language(normalized)

    if normalized == "ja":
        console.print("[green]表示言語を日本語(ja)に設定しました。[/green]")
    else:
        console.print("[green]Display language has been set to English(en).[/green]")


@app.command()
def done(number: int):
    """
    Mark a task as done (e.g. later.py done 1).
    """
    tasks = load_tasks()
    if number < 1 or number > len(tasks):
        raise typer.BadParameter(get_msg("err_idx_range", len(tasks)))

    tasks[number - 1]["status"] = "done"
    save_tasks(tasks)
    console.print(get_msg("marked_done", tasks[number - 1]["task"]))
    show()


@app.command()
def todo(number: int):
    """
    Mark a task as todo (e.g. later.py todo 1).
    """
    tasks = load_tasks()
    if number < 1 or number > len(tasks):
        raise typer.BadParameter(get_msg("err_idx_range", len(tasks)))

    tasks[number - 1]["status"] = "todo"
    save_tasks(tasks)
    console.print(get_msg("marked_todo", tasks[number - 1]["task"]))
    show()


if __name__ == "__main__":
    app()
