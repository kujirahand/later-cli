# later-cli

[![PyPI version](https://img.shields.io/pypi/v/later-cli.svg)](https://pypi.org/project/later-cli/)

A CLI task management tool. It is a simple program for managing tasks from the command line.

![A simple task management tool for the terminal: later](https://raw.githubusercontent.com/kujirahand/later-cli/refs/heads/main/doc/preview.png)

- [日本語はこちら](https://github.com/kujirahand/later-cli/blob/main/README-ja.md)

## Installation

Requires Python 3.10 or later.

### Install from PyPI

You can install `later-cli` using pip:

```sh
pip install later-cli
```

Then you can run the `later` command in your terminal.

### Install from GitHub Repository

Use the package manager [uv](https://github.com/astral-sh/uv) for setup. Running the commands below automatically creates a virtual environment (`.venv`) and syncs dependencies. First, install `uv`:

```sh
# Install uv
pip install uv
# OR
# brew install uv
# cargo install --git https://github.com/astral-sh/uv uv
```

And then, clone the repository and set up the environment:

```sh
# Clone the repository
git clone https://github.com/kujirahand/later-cli.git
cd later-cli

# Install dependencies and set up the environment
uv sync
```

### Quick Usage

A short tutorial is available below.

- [English guide](https://github.com/kujirahand/later-cli/tree/main/doc/README.md)
- [Japanese guide](https://github.com/kujirahand/later-cli/tree/main/doc/README-ja.md)

Basic usage:

```sh
# Adds a task for 3 days later at 8:00 AM
later add 3d "Submit report"  
# Check tasks
later list
# Done the first task
later done 1
# Clear the done task
later clear --target=done
# Delete the done task
later list
later delete 1
```

## Setup to Check Tasks at Shell Startup

### For macOS/Linux

After cloning this repository, add the script directory to your `PATH`. Then you can run `later args...` from anywhere.
The wrapper script `later` automatically runs via `uv run` when `.venv` exists.

It is convenient to add the following settings to `~/.zshrc` or `~/.bashrc`:

```sh
LATER_CLI_PATH="/path/to/later-cli"  # replace with your later-cli path
PATH="$LATER_CLI_PATH:$PATH"
# Check due tasks at startup
later check
```

### For Windows

When using Windows PowerShell, open `~\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1` (the value of `$PROFILE`) in a text editor and add the following lines. If the file or folder does not exist, create it first.

```powershell
cd /path/to/later-cli  # replace with your later-cli path
uv run later check
```

## How to Use later-cli

Please type `later --help` to see the available commands and options.

## Configuration Customization

You can change values in `tasks.json` with the `set` command.

```bash
# Configure API endpoint and API key
later set api_endpoint "https://example.com"
later set api_key "laterapi::your::key"

# Customize date display format
later set datetime_format "%Y/%m/%d %H:%M"
```

### Date Display Format Customization (`datetime_format`)

By default, notification timestamps in the task list (`later list`) omit the year and use an `m/d weekday H:i` style format (for example: `03/01Wed03:33`).
If you want to change the display format, set the `datetime_format` key in `tasks.json`.

You can use Python `strftime` format specifiers:
- **`%Y/%m/%d %H:%M`**: `2026/06/01 10:30`
- **`%d/%m %H:%M`**: `01/06 10:30` (European style)
- **`%b %d, %Y %I:%M %p`**: `Jun 01, 2026 10:30 AM` (US style)

## Synchronization with Web API (sync)

`later-cli` supports bi-directional task synchronization between multiple devices or with a remote Web API server. Running the synchronization will push your local event history (task addition, deletion, and status changes) to the remote server and pull the latest events to keep your local database fully up to date.

- [later-api repository](https://github.com/kujirahand/later-api)

### Synchronization Configuration

To set up synchronization, you must configure the API endpoint URL and your API key in `tasks.json` using the `set` command:

```bash
# Set the remote API base endpoint URL
later set api_endpoint "https://example.com"

# Set your API key (must follow format: laterapi::xxx::xxxx)
later set api_key "laterapi::your_api_key_here"
```

### Connection & Authentication Test (sync hello)

You can verify that your remote endpoint and API key are configured correctly by executing the `sync hello` connection test command:

```bash
later sync hello
```

If successful, it will display a connection success message along with the response message from the server. If authentication fails, or if a connection error occurs, the detailed error reasons (such as missing/invalid Bearer tokens or network errors) will be clearly displayed.

### Running Synchronization (sync)

To perform actual bi-directional synchronization, execute the `sync` command:

```bash
later sync
```

This will automatically push any unsynced local events, pull remote events, apply those remote changes to your local tasks, and update your synchronization timestamp (`api_updated_at`).

## More Detailed Guide

The following Mynavi series introduces the program and basic usage:

- https://news.mynavi.jp/techplus/article/zeropython-138/

## GitHub Repository

- [GitHub > later-cli](https://github.com/kujirahand/later-cli)
- [PyPI > later-cli](https://pypi.org/project/later-cli/)