# later-cli (Japanese)

[![PyPI version](https://img.shields.io/pypi/v/later-cli.svg)](https://pypi.org/project/later-cli/)

later-cliは、ターミナルで簡単にタスクを管理できるシンプルなCLIツールです。

![A simple task management tool for the terminal: later](https://raw.githubusercontent.com/kujirahand/later-cli/refs/heads/main/doc/preview.png)

- [English here](https://github.com/kujirahand/later-cli/blob/main/README.md)

## インストール方法

Python 3.10以降が必要です。

### PyPIからインストール

pipを使って簡単に `later-cli` をインストールできます。

```sh
pip install later-cli
```

インストール後、ターミナルから `later` コマンドを実行できるようになります。

### GitHubリポジトリからインストール

セットアップにはパッケージマネージャーの [uv](https://github.com/astral-sh/uv) を使用します。以下のコマンドを実行すると、仮想環境 (`.venv`) が自動的に作成され、依存関係が同期されます。まず、`uv` をインストールします。

```sh
# uvのインストール
pip install uv
# または
# brew install uv
# cargo install --git https://github.com/astral-sh/uv uv
```

次に、リポジトリをクローンして環境をセットアップします。

```sh
# リポジトリのクローン
git clone https://github.com/kujirahand/later-cli.git
cd later-cli

# 依存関係のインストールと環境セットアップ
uv sync
```

### クイックスタート

簡単なチュートリアルは以下からご覧いただけます。

- [英語ガイド (English guide)](https://github.com/kujirahand/later-cli/tree/main/doc/README.md)
- [日本語ガイド (Japanese guide)](https://github.com/kujirahand/later-cli/tree/main/doc/README-ja.md)

基本的な使い方:

```sh
# 3日後の午前8時のタスクを追加
later add 3d "レポート提出"  
# タスクの一覧を確認
later list
# 1番目のタスクを完了にする
later done 1
# 完了したタスクを一括削除
later clear --target=done
# タスクの一覧を再確認
later list
# 1番目のタスクを削除する
later delete 1
```

## シェル起動時にタスクを自動チェックする設定

### macOS/Linux の場合

このリポジトリをクローンした後、スクリプトがあるディレクトリを環境変数 `PATH` に追加してください。これで、どこからでも `later` コマンドを実行できるようになります。
`.venv` が存在する場合、ラッパースクリプト `later` は自動的に `uv run` 経由で実行されます。

`~/.zshrc` または `~/.bashrc` に以下の設定を追加しておくと便利です。

```sh
LATER_CLI_PATH="/path/to/later-cli"  # 実際のlater-cliのパスに置き換えてください
PATH="$LATER_CLI_PATH:$PATH"
# シェル起動時に期限切れ・期限当日のタスクをチェック
later check
```

### Windows の場合

Windows PowerShellを使用している場合は、`~\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1` (`$PROFILE` 変数の値) をテキストエディタで開き、以下の行を追加します。ファイルやフォルダが存在しない場合は、まず新規作成してください。

```powershell
cd /path/to/later-cli  # 実際のlater-cliのパスに置き換えてください
uv run later check
```

## 使い方詳細

利用可能なコマンドやオプションを確認するには、`later --help` を実行してください。

## 設定のカスタマイズ

`set` コマンドを使って `tasks.json` の設定値を変更できます。

```bash
# 日時の表示フォーマットをカスタマイズ
later set datetime_format "%Y/%m/%d %H:%M"
```

### 日時表示フォーマットのカスタマイズ (`datetime_format`)

デフォルトでは、タスク一覧 (`later list`) の通知日時は年が省かれ、`月/日 曜日 時:分` のような形式で表示されます（例: `03/01水03:33` または `03/01Wed03:33`）。
表示形式を変更したい場合は、`later set datetime_format (形式)`で、フォーマット文字列を設定します。

フォーマット文字列の設定には、Pythonの[strftime](https://docs.python.org/ja/3.14/library/datetime.html#strftime-and-strptime-format-codes)フォーマット指定子を使用できます。

| フォーマット例 | 表示例 |
| --- | --- |
| `%Y/%m/%d %H:%M` | `2026/06/01 10:30` |
| `%d/%m %H:%M` | `01/06 10:30` (欧州スタイル) |
| `%b %d, %Y %I:%M %p` | `Jun 01, 2026 10:30 AM` (米国スタイル) |
| `%m/%d(%a) %H:%M` | `06/01(月) 10:30` (日本スタイル) |

### 入力日時指定のカスタマイズ (`datetime_in_format`)

タスクの追加や編集の際に、日付を入力するためのフォーマットもカスタマイズできます。デフォルトでは、`月/日 時`のような形式がサポートされていますが、これを変更したい場合は、`datetime_in_format` キーにカスタムフォーマットを設定してください。

```sh
# 日付入力フォーマットを変更
later set datetime_in_format "%Y.%m.%d %H:%M"
```

フォーマットの部分には、Pythonの[strptime](https://docs.python.org/ja/3.14/library/datetime.html#strftime-and-strptime-format-codes)フォーマット指定子を使用できます。例えば、`%Y.%m.%d %H:%M` と設定すると、タスクの追加や編集の際に `2026.06.01 10:30` のような形式で日付を入力できるようになります。

| フォーマット例 | 入力例 |
| --- | --- |
| `%Y.%m.%d %H:%M` | `2026.06.01 10:30` |
| `%d/%m %H:%M` | `01/06 10:30` (欧州スタイル) |
| `%b %d, %Y %I:%M %p` | `Jun 01, 2026 10:30 AM` (米国スタイル) |
| `%m/%d(%a) %H:%M` | `06/01(月) 10:30` (日本スタイル) |

### 入力日付指定のカスタマイズ (`date_in_format`)

同様に、`date_in_format` キーにカスタムフォーマットを設定することで、タスクの追加や編集の際に日付のみを入力するためのフォーマットもカスタマイズできます。デフォルトでは、`月/日` のような形式がサポートされています。

```sh
# 日付入力フォーマット(月.日)を変更
later set date_in_format "%m.%d"
```

時刻情報を含まない日付のみのフォーマットで入力された場合、通知時刻はアプリのデフォルトである **`08:00:00` (午前8時)** が自動的に設定されます。また、年が省略されている場合は、今年（または日付がすでに過ぎている場合は来年）が自動的に補完されます。

| フォーマット例 | 入力例 | 登録される通知日時 (2026年実行時) |
| --- | --- | --- |
| `%Y.%m.%d` | `2026.07.15` | `2026-07-15 08:00:00` |
| `%d/%m` | `15/06` (欧州スタイル) | `2026-06-15 08:00:00` |
| `%m/%d` | `06/15` (日本スタイル) | `2026-06-15 08:00:00` |

### 期限の更新と直接日付指定 (`renew` コマンド)

`later renew` コマンドは、タスクの期限を相対的に延長するだけでなく、特定の日時や日付を直接指定して更新することもサポートしています。

```sh
# タスク1の期限を7日延長する (相対オフセット)
later renew 1 "7d"

# タスク1の期限を 6/1 08:00:00 に直接変更する (日付直接指定)
later renew 1 "6/1"
```

日付を直接指定する場合、上記で設定した `datetime_in_format` や `date_in_format` のカスタム形式もそのまま使用できます。

## より詳細なガイド

マイナビニュースの以下の連載記事で、このプログラムの紹介と基本的な使い方が紹介されています。

- https://news.mynavi.jp/techplus/article/zeropython-138/

## GitHubリポジトリ

- [GitHub > later-cli](https://github.com/kujirahand/later-cli)
- [PyPI > later-cli](https://pypi.org/project/later-cli/)
