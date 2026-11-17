---
name: agentic-pr-gatekeeper
description: Autonomous AI Pull Request review and architectural quality gatekeeper via Model Context Protocol (MCP). Use this skill when evaluating a Pull Request, checking a git diff for blast radius, detecting concurrency bugs (race conditions, missing row-level locks), verifying accompanying unit tests, or auditing code against enterprise architecture guidelines.
license: MIT
compatibility: Python >= 3.9, git
metadata:
  author: Mochamad Ricky Susanto
  version: "1.0.0"
  homepage: "https://github.com/mricky/agentic-pr-gatekeeper-.git"
---

# Agentic PR Gatekeeper: Quality & Safety Review Skill

This skill guides an AI Agent (Claude Code, Cursor, Copilot, or Antigravity) to perform an enterprise-grade Pull Request review using **Deterministic Blast Radius**, **MCP Context Extraction (AST & Tests)**, and **Structured Architectural Auditing**.

---

## 🎯 When to Use This Skill
Trigger this skill whenever:
- The user asks to **review a Pull Request / branch diff** against `main` or another target branch.
- The user wants to **audit code safety** for race conditions, N+1 queries, unhandled nulls, or security risks.
- The user asks: *"Is this PR safe to merge?"* or *"Check blast radius of my changes"*.
- Enforcing the **30% Auto-Approval mandate**: Fast-tracking low-risk changes (docs, typo, tests, styling) while flagging high-risk architectural regressions.

---

## 🛠️ Step-by-Step Workflow

### Step 1: Extract Git Diff & Statistics
Run the CLI tool or git diff against the target branch:
```bash
pr-gatekeeper review --target main
```
Alternatively, extract the modified files and AST symbols directly:
```bash
# Inspect MCP AST symbols for a modified file
pr-gatekeeper context <file_path>
```

### Step 2: Deterministic Blast Radius Assessment
Analyze the blast radius objectively before evaluating semantics:
1. **Line counts:** Total additions + deletions.
2. **Critical Infrastructure Paths:** Does the diff touch sensitive directories?
   - `migrations/`, `schema/`, `sql/` (Database mutations)
   - `auth/`, `security/`, `billing/`, `payment/` (Zero-trust modules)
   - `config/`, `infra/`, `.github/` (Pipeline configurations)
3. **Accompanying Tests:** Verify if modified source code has corresponding test updates in `tests/`.

### Step 3: MCP Semantic Audit Checklist
Evaluate the code changes against the 4 core pillars defined in `references/ARCHITECTURE_GUIDELINES.md`:

1. **Concurrency & Data Consistency:**
   - Are monetary or inventory balance updates protected with row-level locks (`SELECT FOR UPDATE`) or serializable transactions?
   - Are mutating webhook and API endpoints idempotent (UUID + request payload hash)?
2. **Database Performance:**
   - Are there N+1 queries executed inside loops?
   - Are new high-frequency WHERE filters supported by composite B-Tree indexes?
3. **Test Coverage & Regression:**
   - Does every bug fix include an automated regression test that would have failed prior to the fix?
   - Is test coverage preserved?
4. **Security Standards:**
   - Zero hardcoded secrets, private keys, or API tokens.
   - All SQL statements must be parameterized.
   - Webhook signatures (HMAC-SHA256) must use timing-safe comparison (`compare_digest`).

---

## 📊 Verdict & Scoring Scale

Categorize the Pull Request into one of three standard verdicts:

| Score | Verdict | Criteria | Action |
| :---: | :--- | :--- | :--- |
| **1 - 2** | 🟢 **AUTO_APPROVED** | Low Risk: Pure documentation, typo fixes, new test cases, minor isolated UI styling. | Eligible for the 30% fast-track automated merge. |
| **3** | 🟡 **NEEDS_HUMAN_REVIEW** | Medium Risk: Standard feature development, non-critical service logic modifications with accompanying tests. | Requires peer code review approval. |
| **4 - 5** | 🔴 **REJECTED_BLOCKED** | High / Critical Risk: Architectural safety violation, missing row-level locks on balance updates, unindexed loop queries, or security vulnerabilities. | Blocks merge until resolved. |

---

## 📋 Reporting Format

When presenting the review to the developer, follow this structured format:

```markdown
### 🛡️ Agentic PR Gatekeeper Report
**Evaluation Verdict:** [🟢 AUTO_APPROVED | 🟡 NEEDS_HUMAN_REVIEW | 🔴 REJECTED_BLOCKED]
**Overall Risk Score:** [1 to 5] / 5 (Normalized: [0-100]/100)
**Blast Radius:** [ISOLATED | MODULE | SYSTEM_WIDE]

> [Concise 2-sentence executive summary of the evaluation]

### 📊 Deterministic Metrics:
- **Files Changed:** `X` (+Y / -Z)
- **Accompanying Tests:** [Yes ✅ | No ⚠️]
- **Critical Infrastructure Path:** [Yes ⚠️ | No ✅]

### 📋 Findings:
| Location | Severity | Issue Detected | Actionable Suggestion |
| :--- | :---: | :--- | :--- |
| `path/to/file.py:line` | `[CRITICAL/HIGH/MEDIUM/LOW]` | Issue description | Concrete recommendation |
```
