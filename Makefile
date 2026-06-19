.PHONY: check lint test shellcheck py-compile perl-syntax perl-test docs-check

check: lint test shellcheck py-compile perl-syntax perl-test docs-check

lint:
	python3 -m ruff check Python tests

test:
	python3 -m pytest

shellcheck:
	find Bash -name '*.sh' -type f -print0 | xargs -0 shellcheck

py-compile:
	python3 -m py_compile $$(find Python -name '*.py' -type f)

perl-syntax:
	find Perl -name '*.pl' -type f -print0 | xargs -0 -n1 perl -c

perl-test:
	REPO_ROOT=$$(pwd) prove -lr tests/perl

docs-check:
	python3 scripts/check_markdown.py
	python3 scripts/check_no_markers.py
	git diff --check
