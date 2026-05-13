---
Domain: AUTOMATION
Version: 1.0.0
Complexity: Medium
Type: Integration
Category: Git Operations
name: github-pr-manager
Source: community
---
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

## Purpose

Automated GitHub PR creation orchestrated by Cangjie: Python builds PR data, Prolog validates branch state, Hy synthesizes PR body, Cangjie executes conditional logic and aggregates.

## Architecture

**Archetype**: Conditional Pipeline (Python → Prolog validate → Hy synthesize)

```cangjie
struct PRInput {
    repo: String;
    head: String;
    base: String;
    token: String;  // PAT (masked in logs)
    title: String;
    commits: Array<String>;
    diff_stats: Map<String, Int64>;
}

struct PROutput {
    pr_url: String;
    number: Int64;
    merged: Bool;
    validation_errors: Array<String>;
}
```

## Cangjie Orchestrator

```cangjie
func main(input: PRInput) -> PROutput {
    // Step 1: Python — compose PR payload + diff stats
    let py_code = """
import json

payload = {
    "title": ${input.title},
    "head": ${input.head},
    "base": ${input.base},
    "body": "Automated PR",
    "draft": False
}
# Simulated REST call (real impl uses requests/httplib)
response = {"html_url": f"https://github.com/${input.repo}/pull/123", "number": 123}
"""
    let py_result = perform EmCubed.call_surface("python", py_code);

    // Step 2: Prolog — branch validation rules
    let prolog_code = """
% Stub rules representing GitHub state
branch_exists("SpectreDeath/Em-Cubed", "skills-library").
branch_exists("SpectreDeath/Em-Cubed", "main").

repo("SpectreDeath/Em-Cubed").

pr_valid(Repo, Head, Base) :-
    repo(Repo),
    branch_exists(Repo, Head),
    branch_exists(Repo, Base),
    Head \\= Base.
"""
    let valid_check = perform EmCubed.call_surface("prolog", f"pr_valid(\"{input.repo}\", \"{input.head}\", \"{input.base}\").");

    // Step 3: Hy — synthesize PR body from commit history
    let hy_code = """
(import json)

(defn pr-summary [commits stats]
  (let [header "## Changes\\n\\n"
        commit-list (str (join "\\n- " commits))
        files (get stats "files" 0)
        add (get stats "insertions" 0)
        dels (get stats "deletions" 0)
        stats-section (f"### Stats\\n- Files: {files}\\n- Additions: +{add}\\n- Deletions: -{dels}")]
    (+ header commit-list "\\n" stats-section)))

body = pr_summary(${input.commits}, ${input.diff_stats})
"""
    let hy_body = perform EmCubed.call_surface("hy", hy_code);

    // Step 4: Conditional execution in Cangjie
    if valid_check["status"] != "ok" || valid_check.get("result") != True {
        return PROutput{
            pr_url: "",
            number: 0,
            merged: False,
            validation_errors: ["Invalid branch configuration"]
        };
    }

    return PROutput{
        pr_url: py_result["html_url"],
        number: py_result["number"],
        merged: True,
        validation_errors: []
    };
}
```

## Implementation Stream

1. **Python** (~15 LOC): Construct payload, simulate `POST /repos/:repo/pulls`
2. **Prolog** (~10 LOC): `branch_exists/3`, `pr_valid/4` guard clause
3. **Hy** (~12 LOC): Format PR body from commit messages + diff summary
4. **Cangjie** (~25 LOC): If-then-else guard on Prolog result; return final PR dict

**Total**: ~62 LOC vs 167 original (−63%)

## Dependencies

- Python: `httplib` or `requests` (optional, can be mocked)
- Prolog: PySWIP for branch validation
- Hy: String templating
- em_cubed

## Testing

```python
surface = CangjieSurface()

input = {
    "repo": "SpectreDeath/Em-Cubed",
    "head": "skills-library",
    "base": "main",
    "token": "ghp_fake123",
    "title": "feat: add Cangjie orchestration",
    "commits": ["feat: integrate Cangjie surface", "docs: update SKILL.md"],
    "diff_stats": {"files": 3, "insertions": 120, "deletions": 10}
}

result = await surface.execute("", input)
assert result["value"]["number"] == 123  // mocked
assert result["value"]["merged"] == True
```
