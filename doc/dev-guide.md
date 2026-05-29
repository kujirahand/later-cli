# later-cli for Developers (`just`)

This project uses [just](https://github.com/casey/just) as a task runner. It is used for tests and code quality checks (lint/format) during development. See the [just GitHub repository](https://github.com/casey/just#installation) for installation instructions.

## `just` Command List

Run the following commands in the project root directory.

- **`just`** or **`just --list`**: Show the list of available commands.
- **`just install`**: Install dependency packages (e.g., `pytest`, `black`, `ruff`).
- **`just test`**: Run tests with `pytest`.
- **`just lint`**: Run static analysis (linter) with `ruff`.
- **`just format`**: Auto-format code with `black` and `ruff`.
