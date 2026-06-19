# Contributing to Automate Everything

Thank you for your interest in contributing to **Automate Everything**. The goal is to keep the repository practical, safe to run, and easy for developers to inspect before they trust a script on their machine.

## How to Contribute

### 1. Fork the Repository

- Start by [forking the repository](https://github.com/mihaibc/automate_everything/fork) to your GitHub account.

### 2. Clone Your Fork

- Clone your forked repository to your local machine:
  ```bash
  git clone https://github.com/mihaibc/automate_everything.git
  cd automate_everything
  ```

### 3. Create a New Branch

- Create a new branch for your contribution:
  ```bash
  git checkout -b feature-branch-name
  ```
  - Replace `feature-branch-name` with a descriptive name for your branch.

### 4. Make Your Changes

- Navigate to the appropriate directory for the language or task you're working on (e.g., `Python/file_management/`).
- Add your new script or modify an existing one.
- Ensure your code follows the project's coding standards and conventions.
- Add any necessary documentation or comments to your code.
- If your script requires dependencies, update `pyproject.toml`, a relevant `requirements.txt`, or the closest README.

### 5. Test Your Changes

- Run your script to make sure it works as expected.
- Add or update tests for reusable Python behavior.
- Add a small example when the script expects structured input.
- Check that new or changed commands work from the repository root.
- Run the local quality gate:

  ```bash
  make check
  ```

### 6. Commit Your Changes

- Commit your changes with a clear and concise commit message:
  ```bash
  git add .
  git commit -m "Add feature: description of your feature"
  ```
  - Ensure your commit message clearly describes what your changes do.

### 7. Push to Your Fork

- Push your branch to your forked repository on GitHub:
  ```bash
  git push origin feature-branch-name
  ```

### 8. Submit a Pull Request

- Go to the original repository on GitHub and you should see a prompt to submit a Pull Request (PR).
- Click on "Compare & pull request".
- Provide a detailed description of the change: what problem it solves, how to use it, and any dependencies required.
- Submit the pull request.

### 9. Review Process

- Your pull request will be reviewed by the repository maintainers.
- You may be asked to make additional changes or clarify certain aspects of your contribution.
- Once your pull request is approved, it will be merged into the main repository.

## Coding Guidelines

- **Readability**: Write clear and understandable code. Use meaningful variable and function names.
- **Documentation**: Include a short script description, README entry, and at least one realistic command.
- **Consistency**: Follow the coding style used in the repository. For Python, this typically means adhering to PEP 8 standards.
- **Modularity**: If possible, structure your scripts so they can be reused or easily adapted to other tasks.

## Script Quality Checklist

Every new script should aim for:

- A `--help` path or clear usage block.
- Safe defaults. Destructive scripts should support `--dry-run`.
- Clear error messages and non-zero exit codes on failure.
- No hard-coded secrets, personal paths, or machine-specific assumptions.
- README documentation with at least one realistic command.
- Tests for Python functions that transform data, handle paths, parse files, or call reusable logic.
- Dependency notes in `pyproject.toml`, `requirements.txt`, or the relevant README.

For Bash:

- Use `set -euo pipefail`.
- Quote variables.
- Validate required external commands before using them.
- Prefer building JSON through a real JSON tool or Python when prompts can contain quotes or newlines.

For PowerShell:

- Use `[CmdletBinding()]` when helpful.
- Prefer parameters over editing variables in the script body.
- Avoid changing execution policy inside scripts.
- Return clear errors with `Write-Error` and meaningful exit codes.

## Additional Notes

- Please do not include sensitive information (like API keys or passwords) in your scripts.
- Ensure that your contributions are your original work and that you have the right to share them.
- Contributions that add significant value are especially encouraged, but small improvements are appreciated.
- All contributors are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
- Please read [SECURITY.md](SECURITY.md) before submitting scripts that install tools, move files, or call network endpoints.
- Use the [bug report](.github/ISSUE_TEMPLATE/bug_report.md) or [feature request](.github/ISSUE_TEMPLATE/feature_request.md) templates when opening issues.

## License

By contributing to this repository, you agree that your contributions will be licensed under the MIT License.

Thank you for helping keep the repository useful, careful, and easy to trust.
