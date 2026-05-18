default:
    just --list

install:
    python -m pip install -r requirements.txt

test:
    python -m pytest
