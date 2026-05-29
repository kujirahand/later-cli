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
# APIエンドポイントとAPIキーの設定
later set api_endpoint "https://example.com"
later set api_key "laterapi::your::key"

# 日時の表示フォーマットをカスタマイズ
later set datetime_format "%Y/%m/%d %H:%M"
```

### 日時表示フォーマットのカスタマイズ (`datetime_format`)

デフォルトでは、タスク一覧 (`later list`) の通知日時は年が省かれ、`m/d 曜日 H:i` のような形式で表示されます（例: `03/01水03:33` または `03/01Wed03:33`）。
表示形式を変更したい場合は、`tasks.json` の `datetime_format` キーにフォーマット文字列を設定します。

Pythonの `strftime` フォーマット指定子を使用できます。
- **`%Y/%m/%d %H:%M`**: `2026/06/01 10:30`
- **`%d/%m %H:%M`**: `01/06 10:30` (欧州スタイル)
- **`%b %d, %Y %I:%M %p`**: `Jun 01, 2026 10:30 AM` (米国スタイル)

## Web APIとの同期機能 (sync)

`later-cli` は、複数のデバイス間での双方向タスク同期や、リモートのWeb APIサーバーへのタスクデータのバックアップに対応しています。同期を実行すると、ローカルで行った変更履歴（タスクの追加、削除、完了/未完了状態の変更イベント）がリモートサーバーに送信され、同時にサーバー上の最新イベントを受信してローカルのデータベースに適用します。

### 同期の設定

同期を行うには、`set` コマンドを使用して、APIのエンドポイントURLとAPIキーを `tasks.json` に設定します。

```bash
# リモートAPIのベースエンドポイントURLを設定
later set api_endpoint "https://example.com"

# APIキーを設定 (形式: laterapi::xxx::xxxx)
later set api_key "laterapi::your_api_key_here"
```

### 接続・認証テスト (sync hello)

設定したAPIエンドポイントとAPIキーが正しく機能しているかを確認するために、`sync hello` 疎通テストコマンドを実行できます。

```bash
later sync hello
```

疎通に成功すると、接続成功の旨とサーバーからの応答メッセージが表示されます。APIキーが無効である場合や、通信エラーが発生した場合は、エラーの詳細な原因（Bearerトークンが無効であるか欠落しているか、あるいはネットワークエラーかなど）が表示されます。

### タスクの同期 (sync)

実際に双方向のタスク同期を行うには、`sync` コマンドを実行します。

```bash
later sync
```

このコマンドを実行すると、未同期のローカルイベントが自動的にサーバーに送信（プッシュ）され、サーバー側の最新の変更イベントが取得（プル）されてローカルタスクに適用されます。また、同期成功時のタイムスタンプ (`api_updated_at`) が更新されます。

## より詳細なガイド

マイナビニュースの以下の連載記事で、このプログラムの紹介と基本的な使い方が紹介されています。

- https://news.mynavi.jp/techplus/article/zeropython-138/

## GitHubリポジトリ

- [GitHub > later-cli](https://github.com/kujirahand/later-cli)
- [PyPI > later-cli](https://pypi.org/project/later-cli/)
