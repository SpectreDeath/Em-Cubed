---
Domain: AUTOMATION
surfaces:
  - python
  - prolog
  - hy
Version: 1.0.0
Complexity: Medium
Type: Integration
Category: Git Operations
Estimated Execution Time: 1-3 minutes
name: github-pr-manager
Source: community
origin: manual
triggers:
  - pull_request
  - github_api
  - git_ops
quality:
  applied_count: 1
  success_count: 1
  completion_rate: 1.0
  token_savings_avg: 0.0
created_at: "2026-05-03T15:40:00Z"
updated_at: "2026-05-03T15:40:00Z"
---

## Purpose

Automated GitHub Pull Request management using Python for API interaction, Prolog for branch validation, and Hy for intelligent PR description synthesis.

## Description

This skill automates the creation and management of GitHub Pull Requests by:
- Python for robust interaction with the GitHub REST API (v3) using Personal Access Tokens.
- Prolog for validating branch relationships, ensuring non-identical head/base, and checking repository state.
- Hy for adaptive synthesis of PR titles and bodies based on commit history and diff statistics.

## Examples

### Creating a PR for a feature branch

```
Input: head="feature-x", base="main", token="ghp_***", repo="owner/repo"
Output: Pull Request #123 created at https://github.com/owner/repo/pull/123
```

## Implementation

### Python GitHub API Client

```python
import json
import http.client
from typing import Dict, Any, Optional

class GitHubPRManager:
    """Manages GitHub Pull Requests via REST API."""
    
    def __init__(self, token: str, repo_full_name: str):
        self._token = token  # Store privately to prevent accidental exposure
        self.repo = repo_full_name
        self.host = "api.github.com"
        self.headers = {
            "Authorization": f"token {self._token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Em-Cubed-PR-Manager"
        }
    
    def __repr__(self):
        """Safe representation that doesn't expose the token."""
        return f"GitHubPRManager(repo='{self.repo}', host='{self.host}')"
        
    def __str__(self):
        """Safe string representation that doesn't expose the token."""
        return self.__repr__()

    def create_pull_request(self, title: str, body: str, head: str, base: str) -> Dict[str, Any]:
        """Creates a pull request on GitHub."""
        conn = http.client.HTTPSConnection(self.host)
        payload = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        
        conn.request("POST", f"/repos/{self.repo}/pulls", json.dumps(payload), self.headers)
        response = conn.getresponse()
        data = response.read().decode()
        conn.close()
        
        if response.status not in (200, 201):
            raise Exception(f"Failed to create PR: {response.status} {data}")
            
        return json.loads(data)

    def get_pull_requests(self, state: str = "open") -> list:
        """Retrieves list of pull requests."""
        conn = http.client.HTTPSConnection(self.host)
        conn.request("GET", f"/repos/{self.repo}/pulls?state={state}", headers=self.headers)
        response = conn.getresponse()
        data = response.read().decode()
        conn.close()
        return json.loads(data)
```

### Prolog Branch Validation

```prolog
% Validate PR readiness
pr_ready(Repo, Head, Base) :-
    repo_exists(Repo),
    branch_exists(Repo, Head),
    branch_exists(Repo, Base),
    Head \= Base,
    \+ pr_exists(Repo, Head, Base, open).

% Repository and branch stubs (to be populated by context)
repo_exists("SpectreDeath/Em-Cubed").
branch_exists("SpectreDeath/Em-Cubed", "skills-library").
branch_exists("SpectreDeath/Em-Cubed", "master").

% Conflict detection
potential_conflict(File) :-
    modified_in(File, "skills-library"),
    modified_in(File, "master"),
    overlapping_changes(File).
```

### Hy Description Synthesis

```hy
(defn generate-pr-body [commits stats]
  "Synthesize a PR body from commit messages and diff stats"
  (let [header "## Automated PR Summary\n\n"
        commit-list (reduce (fn [acc c] (str acc "- " c "\n")) "" commits)
        stat-summary (str "\n### Statistics\n" 
                          "- Files changed: " (get stats "files") "\n"
                          "- Insertions: " (get stats "insertions") "\n"
                          "- Deletions: " (get stats "deletions"))]
    (str header commit-list stat-summary)))

(defn score-pr-title [title]
  "Score a PR title based on conventional commits"
  (cond
    [(.startswith title "feat:") 1.0]
    [(.startswith title "fix:") 0.9]
    [(.startswith title "docs:") 0.7]
    [True 0.5]))
```

## Testing

```python
import unittest
from unittest.mock import patch, MagicMock
# Assuming the above Python code is in a module named github_pr_manager
# from skills.AUTOMATION.github_pr_manager.implementation import GitHubPRManager

class TestGitHubPRManager(unittest.TestCase):
    @patch("http.client.HTTPSConnection")
    def test_create_pr_success(self, mock_conn):
        mock_response = MagicMock()
        mock_response.status = 201
        mock_response.read.return_value = json.dumps({"html_url": "http://github.com/pr/1"}).encode()
        
        mock_instance = mock_conn.return_value
        mock_instance.getresponse.return_value = mock_response
        
        # Use environment variable or test token instead of hardcoding
        import os
        test_token = os.getenv("TEST_GITHUB_TOKEN", "fake_token_for_testing")
        manager = GitHubPRManager(test_token, "owner/repo")
        result = manager.create_pull_request("title", "body", "head", "base")
        
        self.assertEqual(result["html_url"], "http://github.com/pr/1")
        mock_instance.request.assert_called_once()

if __name__ == "__main__":
    unittest.main()
```

````
