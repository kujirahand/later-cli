# later-cli

[![PyPI version](https://img.shields.io/pypi/v/later-cli.svg)](https://pypi.org/project/later-cli/)

A CLI task management tool. It is a simple program for managing tasks from the command line.

![A simple task management tool for the terminal: later](https://raw.githubusercontent.com/kujirahand/later-cli/refs/heads/main/doc/preview.png)

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

```text
Usage:
  later <command> [<args>...]

Commands:
  add           Add a new task. Example: later add "3d" "Submit report"
  a             Alias for add (shorter command)
  list          Show all tasks
  ls            Alias for list (shorter command)
  show          Alias for list
  delete        Delete a task by number. Example: later delete 1
  del           Alias for delete (shorter command)
  clear         Remove overdue tasks
  check         Show due tasks
  cal           Show weekly schedule in calendar format
  info          Show the data file path
  version       Show version information
  language      Set display language (en / ja)
  done          Mark a task as done. Example: later done 1
  todo          Mark a task as todo. Example: later todo 1
  --file FILE   Use FILE as the task JSON file
  --help        Show this help message

Examples:
  later add "3d" "Submit report"        # add task due in 3 days
  later add "10h" "Meeting"             # add task due in 10 hours
  later add "today" "Today's task"       # add task for today at 8:00 AM
  later add "tomorrow" "Tomorrow's task" # add task for tomorrow at 8:00 AM
  later add "tomorrow 20:00" "Tomorrow 20:00" # add task for tomorrow at 8:00 PM
  later add "day after tomorrow" "Task"  # add task for the day after tomorrow at 8:00 AM
  later add "next week" "Next week's task" # add task for next Monday at 8:00 AM
  later add "next Monday" "Submit report" # add task for next Monday at 8:00 AM
  later add "Wednesday" "Take out trash" # add task for next Wednesday at 8:00 AM
  later add "next month second Monday" "Monthly report" # add task for second Monday next month at 8:00 AM
  later add "tomorrow 10:00" "Submit report" # add task for tomorrow at 10:00 AM
  later add "15:30" "Meeting"            # add task for 15:30 today (or tomorrow if already passed)
  later add "5/25" "Test task"           # add task for May 25 at 8:00 AM (next year if already passed)
  later add "Dec 3 15:30" "Monthly report" # add task for Dec 3 at 15:30
  later add "2026-05-25" "Test task"     # add task for May 25, 2026 at 8:00 AM
  later show                         # show all tasks
  later delete 1                     # delete task number 1
  later clear                        # remove overdue tasks
  later check                        # show overdue tasks
  later cal                          # show weekly schedule in calendar format
  later info                         # show data file location
  later version                      # show version information
  later language ja                  # set display language to Japanese (ja)
  later done 1                       # mark task number 1 as done
  later todo 1                       # mark task number 1 as todo
  later --file /tmp/tasks.json add now "Test" # add task to specified file
```

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

## For Developers (`just`)

This project uses [just](https://github.com/casey/just) as a task runner. It is used for tests and code quality checks (lint/format) during development. See the [just GitHub repository](https://github.com/casey/just#installation) for installation instructions.

### `just` Command List

Run the following commands in the project root directory.

- **`just`** or **`just --list`**: Show the list of available commands.
- **`just install`**: Install dependency packages (e.g., `pytest`, `black`, `ruff`).
- **`just test`**: Run tests with `pytest`.
- **`just lint`**: Run static analysis (linter) with `ruff`.
- **`just format`**: Auto-format code with `black` and `ruff`.

## More Detailed Guide

The following Mynavi series introduces the program and basic usage:

- https://news.mynavi.jp/techplus/article/zeropython-138/

## GitHub Repository

- [GitHub > later-cli](https://github.com/kujirahand/later-cli)
- [PyPI > later-cli](https://pypi.org/project/later-cli/)