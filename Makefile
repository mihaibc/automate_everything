.PHONY: check lint test shellcheck py-compile bash-test perl-syntax perl-test powershell-test docs-check script-test

check: lint test shellcheck py-compile bash-test perl-syntax perl-test powershell-test docs-check script-test

lint:
	python3 -m ruff check Python scripts tests

test:
	python3 -m pytest

shellcheck:
	find Bash -name '*.sh' -type f -print0 | xargs -0 shellcheck

py-compile:
	python3 -m py_compile $$(find Python scripts -name '*.py' -type f)

bash-test:
	python3 -m pytest tests/test_bash_scripts.py

perl-syntax:
	find Perl -name '*.pl' -type f -print0 | xargs -0 -n1 perl -c

perl-test:
	REPO_ROOT=$$(pwd) prove -lr tests/perl

powershell-test:
	python3 -m pytest tests/test_powershell_scripts.py

docs-check:
	python3 scripts/check_markdown.py
	python3 scripts/check_no_markers.py
	git diff --check

script-test:
	python3 scripts/check_script_tests.py
