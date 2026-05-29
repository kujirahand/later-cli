# later-cli

 CLIでタスクを管理するプログラム。

## インストール

### GitHubリポジトリからインストール

パッケージマネージャーである [uv](https://github.com/astral-sh/uv) を使用してセットアップを行います。以下のコマンドを実行するだけで自動的に仮想環境（`.venv`）が構築され、依存関係の同期が完了します。

以下はuvをインストールするためのコマンドです。

```sh
# uvのインストール
pip install uv
# OR
# brew install uv
# cargo install --git https://github.com/astral-sh/uv uv
```

次いで、本プロジェクトのリポジトリをクローンして、依存関係をインストールします。

```sh
# リポジトリを取ってくる
git clone https://github.com/kujirahand/later-cli.git
cd later-cli

# 依存関係をインストールして同期
uv sync
```

### macOS/Linuxの場合

本リポジトリをcloneした後、パスにスクリプトのディレクトリを追加します。すると、`later args...` の形でどこからでも利用できます。
ラッパースクリプト `later` は、`.venv` が存在すれば自動的に `uv run` を経由して実行されます。

`~/.zshrc` や `~/.bashrc` に以下の設定を追加すると便利です。

```sh
LATER_CLI_PATH="/path/to/later-cli"  # later-cliのパスに置き換える
pushd $LATER_CLI_PATH >/dev/null
# 起動時に期限の来たタスクをチェックする
uv run later.py check
popd >/dev/null
```

### Windowsの場合

WindowsのPowerShellであれば、ユーザーフォルダにある `~\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1` というファイル（`$PROFILE` の値）をテキストエディタで開いて、下記のような内容を追加します。なお、ファイルやフォルダがない場合は作成して追加する必要があります。

`uv run` を介して実行するように設定します。

```powershell
$script = Join-Path (Split-Path $PROFILE) "later.py"
uv run $script check
```

そして、このファイルと同じフォルダに、先ほど作成した「later.py」と「storage.py」を保存します。そうすると、新規PowerShellウィンドウを開いたときに、このスクリプトが自動的に実行され、期限が来たタスクが表示されるようになります。

## later の使い方

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
  later.py add "3d" "レポート提出"        # 3日後のタスクを追加
  later.py add "10h" "打ち合わせ"         # 10時間後のタスクを追加
  later.py add "明日" "明日のタスク"        # 明日の午前8時のタスクを追加
  later.py add "明後日" "明後日のタスク"    # 明後日の午前8時のタスクを追加
  later.py add "来週" "来週のタスク"       # 来週の月曜日の午前8時のタスクを追加
  later.py show                         # 全タスク一覧を表示
  later.py delete 1                     # 番号1のタスクを削除
  later.py clear                        # 期限切れタスクを削除
  later.py check                        # 期限切れタスクを表示
  later.py info                         # データの保存場所を表示
  later.py --file /tmp/tasks.json add now "テスト" # 指定したファイルにタスクを追加
```

## 開発者向け (just)

本プロジェクトではタスクランナーとして [just](https://github.com/casey/just) を導入しています。開発時のテストやコード品質の管理（Lint/Format）に利用できます。インストール方法は [justのGitHubリポジトリ](https://github.com/casey/just#installation) をご参照ください。

### justのコマンド一覧

プロジェクトのルートディレクトリで以下のコマンドを実行できます。

- **`just`** または **`just --list`**: 利用可能なコマンドの一覧を表示します。
- **`just install`**: 依存関係パッケージ（pytest, black, ruff 等）をインストールします。
- **`just test`**: `pytest` を使用してテストを実行します。
- **`just lint`**: `ruff` を使用してコードの静的解析（Linter）を実行します。
- **`just format`**: `black` および `ruff` を使用してコードを自動整形（Formatter）します。

## 詳しい使い方

以下のマイナビ様の連載で、プログラムの使い方や、プログラムの詳しい解説を掲載しています。

- https://news.mynavi.jp/techplus/article/zeropython-138/
