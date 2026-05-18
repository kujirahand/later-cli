#!/usr/bin/env python
""" CLIでタスクを管理するプログラム """

from datetime import datetime, timedelta
from pathlib import Path
import re
import typer
import rich
from rich.console import Console
from rich.table import Table
from storage import load_tasks, save_tasks, get_data_file, reset_data_file, set_data_file

# TyperやConsoleのインスタンスを作成
app = typer.Typer(no_args_is_help=True,add_completion=False)
console = Console()

@app.callback()
def main(
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

def calc_due_date(due: str) -> datetime:
    """期限の表現を解析して、通知日時を計算する"""
    now = datetime.now()
    normalized = due.strip().lower()
    if normalized == "now" or normalized == "すぐ" or normalized == "今":
        return now
    if normalized == "明日" or normalized == "tomorrow":
        return (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    if normalized == "明後日":
        return (now + timedelta(days=2)).replace(hour=8, minute=0, second=0, microsecond=0)
    if normalized == "来週" or normalized == "nextweek":
        return (now + timedelta(days=7)).replace(hour=8, minute=0, second=0, microsecond=0)
    match = re.fullmatch(r"(\d+)([dh日])", normalized)
    if not match:
        raise typer.BadParameter("期限は '3d' / '2h' の形式で指定してください。")
    amount = int(match.group(1))
    unit = match.group(2)
    if unit == "d":
        return (now + timedelta(days=amount)).replace(hour=8, minute=0, second=0, microsecond=0)
    if unit == "h":
        return now + timedelta(hours=amount)
    return now


@app.command()
def add(due: str, task: str):
    """
    タスクを追加する

    指定例:
      later.py add "3d" "レポート提出" ... Add 3 days task
      later.py add "10h" "打ち合わせ" ... 10 hours task
      later.py add "明日" "明日のタスク" ... Add tomorrow 8am task
      later.py add "明後日" "明後日のタスク" ... Add the day after tomorrow 8am task
      later.py add "来週" "来週のタスク" ... Add next week 8am task
      later.py add now "今すぐやるタスク" ... Add now task
      later.py add 今 "今すぐやるタスク" ... Add now task
    """
    tasks = load_tasks()
    notify_at = calc_due_date(due)
    notify_at_s = notify_at.strftime("%Y-%m-%d %H:%M:%S")
    # 既存の date キーは維持しつつ、時刻付き情報を notify_at に保存
    tasks.append({"date": notify_at_s, "task": task})
    save_tasks(tasks)
    print(f"タスクを追加しました: {task} (通知日時: {notify_at_s})")


@app.command("a")
def add_short(due: str, task: str):
    """タスク追加の簡易コマンド (例: later.py a "3d" "レポート提出")"""
    add(due, task)


def show_tasks(tasks: list[dict], title: str):
    """タスクのリストを表形式で表示する"""
    if len(tasks) == 0:
        # タスクがない場合はメッセージを表示して終了
        console.print("- [bold green]later:[/bold green] [blue]タスクはありません。[/blue]")
        return
    table = Table(title=title, show_lines=False)
    table.add_column("番号", justify="right")
    table.add_column("タスク", style="red")
    table.add_column("期限", style="green")
    for idx, task in enumerate(tasks, start=1):
        table.add_row(f"{idx}", task["task"], task["date"])
    console.print(table)


@app.command()
def show():
    """保存されたタスクを表示する"""
    tasks = load_tasks()
    show_tasks(tasks, "■ 保存したタスク一覧")

@app.command()
def delete(number: int):
    """番号を指定してタスクを削除する (例: later.py delete 1)"""
    tasks = load_tasks()
    if number < 1 or number > len(tasks):
        raise typer.BadParameter(f"番号は 1 から {len(tasks)} の範囲で指定してください。")
    deleted_task = tasks.pop(number - 1)
    save_tasks(tasks)
    print(f"タスクを削除しました: {deleted_task['task']}")
    show()

@app.command()
def clear():
    """期限が過ぎたタスクを一括削除する"""
    tasks = load_tasks()
    now = datetime.now()
    tasks_due = []
    for task in tasks:
        notify_at = datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S")
        remove_date = notify_at - timedelta(days=1)  # 期限が1日以上過ぎたもの
        if remove_date > now:
            tasks_due.append(task)
    save_tasks(tasks_due)
    print(f"期限が過ぎたタスクを削除しました。残りのタスク数: {len(tasks_due)}")
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
    show_tasks(tasks_due, "■ 期限が来たタスク")

@app.command("info")
def info():
    """情報を表示"""
    print("タスクは以下のファイルに保存されています:")
    print(get_data_file())

if __name__ == "__main__":
    app()
