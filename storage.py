import json
import os
import sqlite3
import uuid
from datetime import datetime

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


_suppress_logging = False


def get_db_file() -> str:
    """Return the absolute path of the events SQLite database file."""
    data_file = get_data_file()
    return os.path.join(os.path.dirname(data_file), "events.db")


def log_events_to_db(events: list[dict]):
    """Insert event log entries into the SQLite events.db file."""
    db_path = get_db_file()
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        # Initialize tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            json_str TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS events_logs (
            event_id INTEGER NOT NULL,
            task_id TEXT NOT NULL,
            json_str TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        for event in events:
            task_id = event["guid"]
            json_str = json.dumps(event, ensure_ascii=False)
            cursor.execute(
                "INSERT INTO events (task_id, json_str, timestamp) VALUES (?, ?, ?)",
                (task_id, json_str, event["timestamp"]),
            )
        conn.commit()
    finally:
        conn.close()


def save_tasks(tasks):
    """Save tasks to the JSON file."""  # --- (*2)
    global _suppress_logging
    data = load_raw_data()
    old_tasks = data.get("tasks", [])

    # Automatically add a unique GUID to any new tasks that don't have one
    for task in tasks:
        if "guid" not in task:
            task["guid"] = str(uuid.uuid4())

    # Detect modifications and log to SQLite database
    if not _suppress_logging:
        old_by_guid = {t["guid"]: t for t in old_tasks}
        new_by_guid = {t["guid"]: t for t in tasks}

        events_to_log = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Detect additions and updates
        for guid, new_task in new_by_guid.items():
            if guid not in old_by_guid:
                events_to_log.append(
                    {
                        "event": "add",
                        "guid": guid,
                        "timestamp": now_str,
                        "task": new_task["task"],
                        "status": new_task.get("status", "todo"),
                        "date": new_task["date"],
                    }
                )
            else:
                old_task = old_by_guid[guid]
                changed = False
                event_type = None

                if old_task.get("status") != new_task.get("status"):
                    changed = True
                    event_type = new_task.get("status", "todo")

                if old_task["date"] != new_task["date"]:
                    changed = True
                    if not event_type:
                        event_type = "renew"

                if old_task["task"] != new_task["task"]:
                    changed = True
                    if not event_type:
                        event_type = "update"

                if changed:
                    events_to_log.append(
                        {
                            "event": event_type or "update",
                            "guid": guid,
                            "timestamp": now_str,
                            "task": new_task["task"],
                            "status": new_task.get("status", "todo"),
                            "date": new_task["date"],
                        }
                    )

        # Detect deletions
        for guid, old_task in old_by_guid.items():
            if guid not in new_by_guid:
                events_to_log.append(
                    {
                        "event": "delete",
                        "guid": guid,
                        "timestamp": now_str,
                        "task": old_task["task"],
                        "status": old_task.get("status", "todo"),
                        "date": old_task["date"],
                    }
                )

        if events_to_log:
            log_events_to_db(events_to_log)

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


def restore_tasks_from_events(events: list[dict]):
    """Apply events from a synchronizing API to restore/update the task list."""
    global _suppress_logging
    _suppress_logging = True
    try:
        tasks = load_tasks()
        tasks_by_guid = {t["guid"]: t for t in tasks}

        # Apply events in chronological order
        events_sorted = sorted(events, key=lambda x: x.get("timestamp", ""))
        for event in events_sorted:
            guid = event.get("guid")
            if not guid:
                continue

            event_type = event.get("event")
            if event_type == "add":
                tasks_by_guid[guid] = {
                    "guid": guid,
                    "task": event["task"],
                    "date": event["date"],
                    "status": event.get("status", "todo"),
                }
            elif event_type in ("done", "todo", "renew", "update"):
                if guid not in tasks_by_guid:
                    # In case of synchronization gaps, create a skeleton task
                    tasks_by_guid[guid] = {"guid": guid}
                if "task" in event:
                    tasks_by_guid[guid]["task"] = event["task"]
                if "date" in event:
                    tasks_by_guid[guid]["date"] = event["date"]
                if "status" in event:
                    tasks_by_guid[guid]["status"] = event["status"]
                elif event_type in ("done", "todo"):
                    tasks_by_guid[guid]["status"] = event_type
            elif event_type == "delete":
                tasks_by_guid.pop(guid, None)

        save_tasks(list(tasks_by_guid.values()))
    finally:
        _suppress_logging = False


def get_language() -> str:
    """Return the configured language (e.g. ja/en). Default is 'en'."""
    data = load_raw_data()
    return data.get("language", "en")


def set_language(lang: str):
    """Save language setting (e.g. ja/en) to the JSON file."""
    data = load_raw_data()
    data["language"] = lang
    save_raw_data(data)
