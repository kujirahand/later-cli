# later-cli

 CLIでタスクを管理するプログラム。

```text
Usage:
  later.py <command> [<args>...]

Commands:
  add           Add a new task. Example: later.py add "3d" "Submit report"
  a             Alias for add (shorter command)
  show          Show all tasks
  clear         Remove overdue tasks
  check         Show due tasks
  data          Show the data file path
  --help        Show this help message

Examples:
  later.py add "3d" "レポート提出"                # 3日後のタスクを追加
  later.py add "10h" "打ち合わせ"               # 10時間後のタスクを追加
  later.py add "明日" "明日のタスク"              # 明日の午前8時のタスクを追加
  later.py add "明後日" "明後日のタスク"            # 明後日の午前8時のタスクを追加
  later.py add "来週" "来週のタスク"              # 来週の月曜日の午前8時のタスクを追加
  later.py show                         # 全タスク一覧を表示
  later.py clear                        # 期限切れタスクを削除
  later.py check                        # 期限切れタスクを表示
  later.py data                         # データの保存場所を表示
```
