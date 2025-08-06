#!/usr/bin/env python3
"""
Script to post a validation comment on a specific PR
"""

import os
import sys
import json
import re
import subprocess
import shlex

# Configuration
PR_NUMBER = "5"  # The PR to validate and comment on
REPO_OWNER = "sowrabhbs"
REPO_NAME = "bob-hackathon-pr-validator"
GITHUB_HOST = "github.com"

def run_gh_command(command):
    """Run a GitHub CLI command and return the output."""
    import shlex
    
    # Use shlex to properly handle command arguments with spaces and quotes
    cmd_parts = ["gh"] + shlex.split(command)
    
    result = subprocess.run(cmd_parts, shell=False, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    
    return result.stdout

def get_pull_request():
    """Fetch the pull request data."""
    try:
        result = run_gh_command(
            f"api repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER} --hostname {GITHUB_HOST}"
        )
        return json.loads(result)
    except Exception as e:
        print(f"Error fetching pull request: {str(e)}")
        sys.exit(1)

def post_comment(comment):
    """Post a comment on the pull request."""
    try:
        # Escape single quotes in the comment
        escaped_comment = comment.replace("'", "'\\''")
        cmd = f"api repos/{REPO_OWNER}/{REPO_NAME}/issues/{PR_NUMBER}/comments --hostname {GITHUB_HOST} -f body='{escaped_comment}'"
        run_gh_command(cmd)
        print(f"Comment posted on PR #{PR_NUMBER}")
    except Exception as e:
        print(f"Error posting comment: {str(e)}")
        sys.exit(1)

def main():
    """Main function to validate PR and post comment."""
    print(f"Validating PR #{PR_NUMBER} for {REPO_OWNER}/{REPO_NAME}")
    
    # Get PR data
    pr_data = get_pull_request()
    
    # Generate validation report
    title = pr_data.get('title')
    author = pr_data.get('user', {}).get('login')
    body = pr_data.get('body') or ""
    
    # Simple validation
    status = "PASS"
    errors = []
    warnings = []
    
    # Check description length
    if len(body) < 10:
        status = "FAIL"
        errors.append("PR description is too short (min 10 chars required)")
    
    # Check for description sections
    if not re.search(r'## Changes|## Description', body, re.IGNORECASE):
        warnings.append("PR description should include a 'Changes' or 'Description' section")
    
    # Generate report
    report = [
        "## PR Validation Report",
        "",
        f"### PR #{PR_NUMBER}: {title}",
        f"- **Author**: {author}",
        f"- **Status**: {status}",
        ""
    ]
    
    if errors:
        report.append("### ❌ ERRORS:")
        for error in errors:
            report.append(f"- {error}")
        report.append("")
    
    if warnings:
        report.append("### ⚠️ WARNINGS:")
        for warning in warnings:
            report.append(f"- {warning}")
        report.append("")
    
    if not errors and not warnings:
        report.append("### ✅ No issues found.")
    
    report_text = "\n".join(report)
    print(report_text)
    
    # Post comment
    post_comment(report_text)
    
    return 0 if status == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
