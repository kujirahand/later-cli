import json
import os

# タスクを保存する JSON ファイルのパス --- (*1)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT_DIR, "tasks.json")

def save_tasks(tasks):
    """"タスクを JSON ファイルに保存する""" # --- (*2)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)

def load_tasks():
    """タスクを JSON ファイルから読み込む""" # --- (*3)
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        tasks = json.load(f)
        tasks.sort(key=lambda x: x["date"])
        return tasks
