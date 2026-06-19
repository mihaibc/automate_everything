.PHONY: check lint test shellcheck py-compile

check: lint test shellcheck py-compile

lint:
	python3 -m ruff check Python tests

test:
	python3 -m pytest

shellcheck:
	shellcheck Bash/**/*.sh

py-compile:
	python3 -m py_compile $$(find Python -name '*.py' -type f)
