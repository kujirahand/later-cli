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

### Quick Start

A short tutorial is available below.

- [English guide](https://github.com/kujirahand/later-cli/tree/main/doc/README.md)
- [Japanese guide](https://github.com/kujirahand/later-cli/tree/main/doc/README-ja.md)

Basic usage:

```sh
# Adds a task for 3 days later at 8:00 AM
later add 3d "Submit report"  
# Check tasks
later list
# Mark the first task as done
later done 1
# Delete all completed tasks
later clear --target=done
# Check the task list again
later list
# Delete the first task
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
# Customize date display format
later set datetime_format "%Y/%m/%d %H:%M"
```

### Date Display Format Customization (`datetime_format`)


By default, notification timestamps in the task list (`later list`) omit the year and are displayed in a format like `MM/DD(weekday) HH:MM` (e.g., `03/01Wed03:33`).
If you want to change the display format, use `later set datetime_format (format)` to set your preferred format string.

You can use Python's [strftime](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) format specifiers.

| Format Example | Display Example |
| --- | --- |
| `%Y/%m/%d %H:%M` | `2026/06/01 10:30` |
| `%d/%m %H:%M` | `01/06 10:30` (European style) |
| `%b %d, %Y %I:%M %p` | `Jun 01, 2026 10:30 AM` (US style) |
| `%m/%d(%a) %H:%M` | `06/01(Mon) 10:30` (Japanese style) |

### Date Input Format Customization (`datetime_in_format`)

You can also customize the date input format when adding or editing tasks. By default, formats like `MM/DD HH` are supported, but you can change this by setting a custom format string to the `datetime_in_format` key.

```sh
# Change the date input format
later set datetime_in_format "%Y.%m.%d %H:%M"
```

For the format string, use Python's [strptime](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) format specifiers. For example, if you set `%Y.%m.%d %H:%M`, you can enter dates like `2026.06.01 10:30` when adding or editing tasks.

| Format Example | Input Example |
| --- | --- |
| `%Y.%m.%d %H:%M` | `2026.06.01 10:30` |
| `%d/%m %H:%M` | `01/06 10:30` (European style) |
| `%b %d, %Y %I:%M %p` | `Jun 01, 2026 10:30 AM` (US style) |
| `%m/%d(%a) %H:%M` | `06/01(Mon) 10:30` (Japanese style) |

### Date-Only Input Format Customization (`date_in_format`)

Likewise, by setting a custom format for the `date_in_format` key, you can customize the format used to input date-only values when adding or editing tasks. By default, formats like `MM/DD` are supported.

```sh
# Change the date-only input format (MM.DD)
later set date_in_format "%m.%d"
```

If the input is date-only and contains no time information, the notification time is automatically set to the app default: **`08:00:00` (8:00 AM)**. Also, when the year is omitted, the current year (or next year if that date has already passed) is automatically complemented.

| Format Example | Input Example | Stored Notification Datetime (when run in 2026) |
| --- | --- | --- |
| `%Y.%m.%d` | `2026.07.15` | `2026-07-15 08:00:00` |
| `%d/%m` | `15/06` (European style) | `2026-06-15 08:00:00` |
| `%m/%d` | `06/15` (Japanese style) | `2026-06-15 08:00:00` |

### Deadline Renewal and Direct Date Input (`renew` command)

The `later renew` command supports not only extending deadlines by relative offsets, but also updating a deadline by directly specifying a date or datetime.

```sh
# Extend task 1 by 7 days (relative offset)
later renew 1 "7d"

# Change task 1 deadline directly to 6/1 08:00:00 (direct date input)
later renew 1 "6/1"
```

When specifying a date directly, you can also use the custom formats configured above for `datetime_in_format` and `date_in_format`.

## More Detailed Guide

The following Mynavi series introduces the program and basic usage:

- https://news.mynavi.jp/techplus/article/zeropython-138/

## GitHub Repository

- [GitHub > later-cli](https://github.com/kujirahand/later-cli)
- [PyPI > later-cli](https://pypi.org/project/later-cli/)
