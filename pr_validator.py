#!/usr/bin/env python3
"""
PR Validator Script for GitHub Repositories

This script fetches all open pull requests from a GitHub repository and runs
various validations on them, such as checking for proper descriptions,
file size limits, and potential security issues.
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime

# Configuration
REPO_OWNER = "sowrabhbs"
REPO_NAME = "bob-hackathon-pr-validator"
GITHUB_HOST = "github.com"

# Validation rules
MIN_DESCRIPTION_LENGTH = 10
MAX_FILE_SIZE_KB = 500
REQUIRED_LABELS = []  # Add required labels if needed
FORBIDDEN_PATTERNS = [
    r"API_KEY\s*=\s*['\"]\w+['\"]",
    r"PASSWORD\s*=\s*['\"]\w+['\"]",
    r"SECRET\s*=\s*['\"]\w+['\"]",
    r"TOKEN\s*=\s*['\"]\w+['\"]"
]

class PullRequest:
    """Class representing a Pull Request with validation methods."""
    
    def __init__(self, pr_data):
        """Initialize with PR data from GitHub API."""
        self.number = pr_data.get('number')
        self.title = pr_data.get('title')
        self.body = pr_data.get('body') or ""
        self.author = pr_data.get('user', {}).get('login')
        self.branch = pr_data.get('head', {}).get('ref')
        self.created_at = pr_data.get('created_at')
        self.updated_at = pr_data.get('updated_at')
        self.labels = [label.get('name') for label in pr_data.get('labels', [])]
        self.validation_errors = []
        self.validation_warnings = []
        
    def validate(self):
        """Run all validations on this PR."""
        self._validate_description()
        self._validate_labels()
        self._validate_files()
        self._validate_security()
        return len(self.validation_errors) == 0
    
    def _validate_description(self):
        """Validate PR description length and content."""
        if len(self.body) < MIN_DESCRIPTION_LENGTH:
            self.validation_errors.append(
                f"PR description is too short (min {MIN_DESCRIPTION_LENGTH} chars required)"
            )
        
        if not re.search(r'## Changes|## Description', self.body, re.IGNORECASE):
            self.validation_warnings.append(
                "PR description should include a 'Changes' or 'Description' section"
            )
    
    def _validate_labels(self):
        """Validate that required labels are present."""
        for label in REQUIRED_LABELS:
            if label not in self.labels:
                self.validation_errors.append(f"Required label '{label}' is missing")
    
    def _validate_files(self):
        """Validate files in the PR for size and other constraints."""
        try:
            # Get files changed in this PR
            result = run_gh_command(
                f"api repos/{REPO_OWNER}/{REPO_NAME}/pulls/{self.number}/files --hostname {GITHUB_HOST}"
            )
            files = json.loads(result)
            
            for file_data in files:
                filename = file_data.get('filename')
                changes = file_data.get('changes', 0)
                additions = file_data.get('additions', 0)
                deletions = file_data.get('deletions', 0)
                
                # Check file size (if available)
                if file_data.get('size', 0) > MAX_FILE_SIZE_KB * 1024:
                    self.validation_errors.append(
                        f"File '{filename}' exceeds maximum size of {MAX_FILE_SIZE_KB}KB"
                    )
                
                # Check for large changes
                if changes > 500:
                    self.validation_warnings.append(
                        f"File '{filename}' has {changes} changes (>{additions} additions, {deletions} deletions)"
                    )
                
                # Check file extensions for binary files
                if re.search(r'\.(exe|bin|jar|war|zip|tar|gz|rar)$', filename, re.IGNORECASE):
                    self.validation_warnings.append(
                        f"Binary file '{filename}' detected in PR"
                    )
        except Exception as e:
            self.validation_warnings.append(f"Could not validate files: {str(e)}")
    
    def _validate_security(self):
        """Check for potential security issues in the PR."""
        try:
            # Get the PR diff
            result = run_gh_command(
                f"api repos/{REPO_OWNER}/{REPO_NAME}/pulls/{self.number} --hostname {GITHUB_HOST} -H 'Accept: application/vnd.github.v3.diff'"
            )
            
            # Check for forbidden patterns in the diff
            for pattern in FORBIDDEN_PATTERNS:
                if re.search(pattern, result, re.IGNORECASE):
                    self.validation_errors.append(
                        f"Potential security issue: Found pattern matching '{pattern}'"
                    )
        except Exception as e:
            self.validation_warnings.append(f"Could not perform security validation: {str(e)}")
    
    def get_report(self):
        """Generate a validation report for this PR."""
        status = "PASS" if len(self.validation_errors) == 0 else "FAIL"
        
        report = [
            f"PR #{self.number}: {self.title}",
            f"Author: {self.author}",
            f"Branch: {self.branch}",
            f"Created: {self.created_at}",
            f"Status: {status}",
            ""
        ]
        
        if self.validation_errors:
            report.append("ERRORS:")
            for error in self.validation_errors:
                report.append(f"  - {error}")
            report.append("")
        
        if self.validation_warnings:
            report.append("WARNINGS:")
            for warning in self.validation_warnings:
                report.append(f"  - {warning}")
            report.append("")
        
        if not self.validation_errors and not self.validation_warnings:
            report.append("No issues found.")
        
        return "\n".join(report)


def run_gh_command(command):
    """Run a GitHub CLI command and return the output."""
    import shlex
    
    # Use shlex to properly handle command arguments with spaces and quotes
    cmd_parts = ["gh"] + shlex.split(command)
    
    result = subprocess.run(cmd_parts, shell=False, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    
    return result.stdout


def get_open_pull_requests():
    """Fetch all open pull requests from the repository."""
    try:
        # First get the raw PR data without using jq
        result = run_gh_command(
            f"api repos/{REPO_OWNER}/{REPO_NAME}/pulls --hostname {GITHUB_HOST}"
        )
        prs_data = json.loads(result)
        
        # Extract only the fields we need
        simplified_prs = []
        for pr in prs_data:
            simplified_prs.append({
                "number": pr.get("number"),
                "title": pr.get("title"),
                "body": pr.get("body"),
                "user": pr.get("user"),
                "head": pr.get("head"),
                "created_at": pr.get("created_at"),
                "updated_at": pr.get("updated_at"),
                "labels": pr.get("labels", [])
            })
        
        return simplified_prs
    except Exception as e:
        print(f"Error fetching pull requests: {str(e)}")
        sys.exit(1)


def main():
    """Main function to run the PR validation."""
    print(f"Validating PRs for {REPO_OWNER}/{REPO_NAME} on {GITHUB_HOST}")
    print("=" * 60)
    
    # Get all open PRs
    prs_data = get_open_pull_requests()
    print(f"Found {len(prs_data)} open pull requests\n")
    
    # Validate each PR
    all_valid = True
    for pr_data in prs_data:
        pr = PullRequest(pr_data)
        is_valid = pr.validate()
        all_valid = all_valid and is_valid
        
        # Print validation report
        print(pr.get_report())
        print("=" * 60)
    
    # Final summary
    print(f"\nValidation complete: {'All PRs passed' if all_valid else 'Some PRs failed'}")
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
