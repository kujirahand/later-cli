-- SQLiteにイベントを保存するためのテーブル定義
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL, -- タスクのID(GUID)を保存
    json_str TEXT NOT NULL, -- タスクの内容をJSON形式で保存
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- イベントがAPIと同期された後に移動されるテーブル
CREATE TABLE IF NOT EXISTS events_logs (
    event_id INTEGER NOT NULL, -- eventsテーブルのevent_idを参照
    task_id TEXT NOT NULL, -- タスクのID(GUID)を保存
    json_str TEXT NOT NULL, -- "add", "done", "delete"などの操作を保存
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
