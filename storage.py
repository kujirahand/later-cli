import json
import os
import uuid

# Path to the JSON file used to store tasks --- (*1)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_FILE = os.path.join(ROOT_DIR, "tasks.json")
DATA_FILE = DEFAULT_DATA_FILE


def set_data_file(path):
    """Set the JSON file path used to store tasks."""
    global DATA_FILE
    DATA_FILE = os.fspath(path)


def reset_data_file():
    """Reset the task data file path to the default."""
    set_data_file(DEFAULT_DATA_FILE)


def get_data_file():
    """Return the current task data file path."""
    return DATA_FILE


def load_raw_data() -> dict:
    """Load raw JSON data and normalize it to dictionary format."""
    if not os.path.exists(DATA_FILE):
        return {"language": "en", "tasks": []}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {"language": "en", "tasks": []}

    # Keep backward compatibility for legacy list-only format
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
    """Write dictionary data to the JSON file."""
    if "tasks" in data:
        data["tasks"].sort(key=lambda x: x["date"])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_tasks(tasks):
    """Save tasks to the JSON file."""  # --- (*2)
    data = load_raw_data()

    # Automatically add a unique GUID to any new tasks that don't have one
    for task in tasks:
        if "guid" not in task:
            task["guid"] = str(uuid.uuid4())

    data["tasks"] = tasks
    save_raw_data(data)


def load_tasks():
    """Load tasks from the JSON file."""  # --- (*3)
    data = load_raw_data()
    tasks = data.get("tasks", [])

    # Backwards compatibility: add a unique GUID to legacy tasks that don't have one
    updated = False
    for task in tasks:
        if "guid" not in task:
            task["guid"] = str(uuid.uuid4())
            updated = True

    if updated:
        data["tasks"] = tasks
        save_raw_data(data)

    tasks.sort(key=lambda x: x["date"])
    return tasks


def get_language() -> str:
    """Return the configured language (e.g. ja/en). Default is 'en'."""
    data = load_raw_data()
    return data.get("language", "en")


def set_language(lang: str):
    """Save language setting (e.g. ja/en) to the JSON file."""
    data = load_raw_data()
    data["language"] = lang
    save_raw_data(data)
