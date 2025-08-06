# PR Validator Script

This script validates open pull requests in the repository against a set of predefined rules to ensure code quality and security.

## Features

- Validates PR descriptions for minimum length and required sections
- Checks for required labels on PRs
- Validates file sizes and detects binary files
- Scans for potential security issues like hardcoded secrets
- Generates detailed validation reports

## Requirements

- Python 3.6+
- GitHub CLI (`gh`) installed and authenticated
- Access to the repository

## Configuration

Edit the following variables at the top of the script to match your repository:

```python
# Configuration
REPO_OWNER = "Sowrabh-B-S"  # Change to your GitHub username or organization
REPO_NAME = "bob-hackathon"  # Change to your repository name
GITHUB_HOST = "github.ibm.com"  # Change to "github.com" for public GitHub
```

You can also customize the validation rules:

```python
# Validation rules
MIN_DESCRIPTION_LENGTH = 10  # Minimum PR description length
MAX_FILE_SIZE_KB = 500  # Maximum file size in KB
REQUIRED_LABELS = []  # Add required labels if needed
FORBIDDEN_PATTERNS = [
    r"API_KEY\s*=\s*['\"]\w+['\"]",
    r"PASSWORD\s*=\s*['\"]\w+['\"]",
    # Add more patterns as needed
]
```

## Usage

Run the script from the command line:

```bash
python3 pr_validator.py
```

### Example Output

```
Validating PRs for Sowrabh-B-S/bob-hackathon on github.ibm.com
============================================================
Found 4 open pull requests

PR #4: Add PR validator script
Author: Sowrabh-B-S
Branch: feature/pr-validator
Created: 2025-08-06T06:03:27Z
Status: PASS

WARNINGS:
  - PR description should include a 'Changes' or 'Description' section

============================================================
PR #3: Add test PR file
Author: Sowrabh-B-S
Branch: feature/test-pr
Created: 2025-08-06T05:56:55Z
Status: PASS

WARNINGS:
  - PR description should include a 'Changes' or 'Description' section

============================================================
PR #1: Add calculator functionality
Author: Sowrabh-B-S
Branch: feature/calculator
Created: 2025-08-06T04:46:36Z
Status: PASS

WARNINGS:
  - PR description should include a 'Changes' or 'Description' section

============================================================

Validation complete: All PRs passed
```

## Integration with CI/CD

You can integrate this script into your CI/CD pipeline to automatically validate PRs. For example, in GitHub Actions:

```yaml
name: Validate PRs

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install GitHub CLI
        run: |
          curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
          echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
          sudo apt update
          sudo apt install gh
      - name: Authenticate GitHub CLI
        run: |
          echo "${{ secrets.GH_TOKEN }}" | gh auth login --with-token
      - name: Run PR validator
        run: python3 pr_validator.py
```

## Exit Codes

- `0`: All PRs passed validation
- `1`: One or more PRs failed validation

## Extending the Script

You can extend the script by adding more validation methods to the `PullRequest` class. For example:

```python
def _validate_commit_messages(self):
    """Validate commit messages in the PR."""
    try:
        # Get commits in this PR
        result = run_gh_command(
            f"api repos/{REPO_OWNER}/{REPO_NAME}/pulls/{self.number}/commits --hostname {GITHUB_HOST}"
        )
        commits = json.loads(result)
        
        for commit in commits:
            message = commit.get('commit', {}).get('message', '')
            if len(message) < 10:
                self.validation_warnings.append(
                    f"Commit {commit.get('sha')[:7]} has a short message"
                )
    except Exception as e:
        self.validation_warnings.append(f"Could not validate commit messages: {str(e)}")