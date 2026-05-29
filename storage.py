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


def load_raw_data() -> dict:
    """JSONファイルから生データを読み込み、辞書形式に統一して返す"""
    if not os.path.exists(DATA_FILE):
        return {"language": "en", "tasks": []}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {"language": "en", "tasks": []}

    # 従来のリスト形式だった場合の互換性維持
    if isinstance(data, list):
        return {"language": "en", "tasks": data}
    elif isinstance(data, dict):
        if "language" not in data:
            data["language"] = "en"
        if "tasks" not in data:
            data["tasks"] = []
        return data
    else:
        return {"language": "en", "tasks": []}


def save_raw_data(data: dict):
    """辞書データを JSON ファイルに書き込む"""
    if "tasks" in data:
        data["tasks"].sort(key=lambda x: x["date"])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_tasks(tasks):
    """タスクを JSON ファイルに保存する"""  # --- (*2)
    data = load_raw_data()
    data["tasks"] = tasks
    save_raw_data(data)


def load_tasks():
    """タスクを JSON ファイルから読み込む"""  # --- (*3)
    data = load_raw_data()
    tasks = data.get("tasks", [])
    tasks.sort(key=lambda x: x["date"])
    return tasks


def get_language() -> str:
    """設定されている言語（ja/enなど）を返す。デフォルトは 'en'"""
    data = load_raw_data()
    return data.get("language", "en")


def set_language(lang: str):
    """言語（ja/enなど）をJSONファイルに保存する"""
    data = load_raw_data()
    data["language"] = lang
    save_raw_data(data)
