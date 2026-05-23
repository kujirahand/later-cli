# later-cli

 CLIでタスクを管理するプログラム。

## インストール

### GitHubリポジトリからインストール

```sh
# リポジトリを取ってくる
git clone https://github.com/kujirahand/later-cli.git
cd later-cli
# 依存をインストール
python -m pip install -r requirements.txt
```

### macOS/Linuxの場合

本リポジトリをcloneした後、パスに追加します。すると、`later args...`の形で利用できます。
`~/.zshrc`や`~/.bashrc`に以下のコマンドを記述すると良いでしょう。

```sh
LATER_PATH=/path/to/later-cli
PATH=$LATER_PATH:$PATH
source '$HOME/.bash_completions/later.py.sh'
$LATER_SCRIPT check
```

## 使い方

```text
Usage:
  later.py <command> [<args>...]

Commands:
  add           Add a new task. Example: later.py add "3d" "Submit report"
  a             Alias for add (shorter command)
  show          Show all tasks
  delete        Delete a task by number. Example: later.py delete 1
  clear         Remove overdue tasks
  check         Show due tasks
  info          Show the data file path
  --file FILE   Use FILE as the task JSON file
  --help        Show this help message

Examples:
  later.py add "3d" "レポート提出"                # 3日後のタスクを追加
  later.py add "10h" "打ち合わせ"               # 10時間後のタスクを追加
  later.py add "明日" "明日のタスク"              # 明日の午前8時のタスクを追加
  later.py add "明後日" "明後日のタスク"            # 明後日の午前8時のタスクを追加
  later.py add "来週" "来週のタスク"              # 来週の月曜日の午前8時のタスクを追加
  later.py show                         # 全タスク一覧を表示
  later.py delete 1                     # 番号1のタスクを削除
  later.py clear                        # 期限切れタスクを削除
  later.py check                        # 期限切れタスクを表示
  later.py info                         # データの保存場所を表示
  later.py --file /tmp/tasks.json add now "テスト" # 指定したファイルにタスクを追加
```

## 詳しい使い方

以下のマイナビ様の連載で、プログラムの使い方や、プログラムの詳しい解説を掲載しています。

- https://news.mynavi.jp/techplus/article/zeropython-138/
