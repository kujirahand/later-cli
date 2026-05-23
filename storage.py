import json
import os

# タスクを保存する JSON ファイルのパス --- (*1)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_FILE = os.path.join(ROOT_DIR, "tasks.json")
DATA_FILE = DEFAULT_DATA_FILE


def set_data_file(path):
    """タスクを保存する JSON ファイルのパスを変更する"""
    global DATA_FILE
    DATA_FILE = os.fspath(path)


def reset_data_file():
    """タスクを保存する JSON ファイルのパスを標準に戻す"""
    set_data_file(DEFAULT_DATA_FILE)


def get_data_file():
    """現在のタスク保存ファイルのパスを返す"""
    return DATA_FILE


def save_tasks(tasks):
    """ "タスクを JSON ファイルに保存する"""  # --- (*2)
    tasks.sort(key=lambda x: x["date"])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)


def load_tasks():
    """タスクを JSON ファイルから読み込む"""  # --- (*3)
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        tasks = json.load(f)
        tasks.sort(key=lambda x: x["date"])
        return tasks
