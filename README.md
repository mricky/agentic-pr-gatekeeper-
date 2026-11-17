# 🛡️ Agentic PR Gatekeeper
> **Autonomous AI-Powered Pull Request Review & Quality Gate via Model Context Protocol (MCP)**  
> **Author:** Mochamad Ricky Susanto  
> **License:** MIT  

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Architecture Gate](https://img.shields.io/badge/quality%20gate-MCP%20Enabled-success.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

`agentic-pr-gatekeeper` is an enterprise-grade autonomous pull request auditor that bridges **deterministic blast-radius metrics**, **Model Context Protocol (MCP)** AST analysis, and **frontier LLMs (Google Gemini 3.0 / Claude 3.5 Sonnet)** to answer the Principal Engineer mandate:
> *"Safely fast-track 30% of low-risk pull requests for automated approval while focusing human engineering hours on high-risk architectural regressions."*

---

## 🏛️ System Architecture

```
                       [ DEVELOPER OPENS PULL REQUEST ]
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼                                                   ▼
    [ CI/CD: GitHub Action ]                            [ Local CLI: 'pr-gatekeeper' ]
            │                                                   │
            └─────────────────────────┬─────────────────────────┘
                                      ▼
                   ┌───────────────────────────────────────┐
                   │   DETERMINISTIC BLAST RADIUS ENGINE   │
                   │   • Analyzes diff line counts & files │
                   │   • Detects critical paths & tests    │
                   └──────────────────┬────────────────────┘
                                      │
                                      ▼
                   ┌───────────────────────────────────────┐
                   │    MCP (MODEL CONTEXT PROTOCOL)       │
                   │    • Tool: get_ast_symbols()          │
                   │    • Tool: find_related_tests()       │
                   │    • Tool: get_arch_guidelines()      │
                   └──────────────────┬────────────────────┘
                                      │
                                      ▼
                   ┌───────────────────────────────────────┐
                   │       LLM SEMANTIC REVIEW ENGINE      │
                   │   (Google Gemini 3.0 Flash Preview)   │
                   │   • Concurrency & Race Conditions     │
                   │   • N+1 Database Query Detection      │
                   │   • Calculated Risk Score (1 to 5)    │
                   └──────────────────┬────────────────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       ▼                             ▼
              [ SCORE ≤ 2 (Low Risk) ]      [ SCORE > 2 (High Risk) ]
                       │                             │
                       ▼                             ▼
             🟢 AUTO-APPROVED              🟡 NEEDS HUMAN REVIEW / BLOCKED
             (Meets 30% Auto-Approval)     (Directs Human Peer Attention)
                       │                             │
                       └──────────────┬──────────────┘
                                      ▼
                   ┌───────────────────────────────────────┐
                   │        OUTPUT & REPORTING LAYER       │
                   │  • Rich Markdown Comment in GitHub PR │
                   │  • Commit Status: 'pr-agent/risk-gate'│
                   │  • Colored Terminal Dashboard         │
                   └───────────────────────────────────────┘
```

---

## ✨ Key Features

1. **Hybrid Risk-Scoring (1 to 5):**
   * **Score 1 - 2 (Low Risk):** Typo fixes, documentation, test additions, minor styling $\rightarrow$ **AUTO-APPROVED 🟢** (Achieving the 30% fast-track goal).
   * **Score 3 (Medium Risk):** Standard feature changes $\rightarrow$ **NEEDS HUMAN REVIEW 🟡**.
   * **Score 4 - 5 (Critical Risk):** Concurrency race conditions, unindexed queries, missing idempotency $\rightarrow$ **MERGE BLOCKED 🔴**.

2. **Model Context Protocol (MCP) Integration:**
   * Instead of reviewing diffs blindly, the reviewer invokes MCP tools to inspect:
     - `get_ast_symbols()`: Modified Python classes and function signatures.
     - `find_related_tests()`: Detects if tests were written for the modified code.
     - `get_arch_guidelines()`: Enforces company-wide rules (`ARCHITECTURE.md`).

3. **Deterministic Blast Radius:**
   * Automatically categorizes blast radius as `ISOLATED`, `MODULE`, or `SYSTEM_WIDE` based on files touched, critical infrastructure keyword matching, and diff volume.

4. **Multi-Channel Delivery:**
   * Rich interactive colored terminal output for developers pre-commit.
   * Automated sticky PR comments and Commit Status Checks in GitHub Actions.

---

## ⚖️ Why MCP? (Raw-Diff vs. Context-Aware Review)

Most AI code reviewers pass raw, truncated `git diff` text directly to an LLM. While fast, this blind approach fails for mission-critical engineering projects where context lives outside the diff lines.

| Architectural Dimension | ❌ Traditional Blind Review (Raw Diff) |  Agentic MCP Gatekeeper (`agentic-pr-gatekeeper`) |
| :--- | :--- | :--- |
| **Input to LLM** | Truncated `git diff` patch only. | `git diff` + AST Symbols + Discovered Unit Tests + `ARCHITECTURE.md`. |
| **Code Structure Insight** | Blind to modified classes, methods, or signatures. | **`get_ast_symbols()`**: Maps exact function ASTs, class scopes, and arguments. |
| **Test Verification** | Blind to whether test suites exist for changed files. | **`find_related_tests()`**: Auto-scans `tests/` to verify regression test coverage. |
| **Enterprise Governance** | Generic LLM prompt heuristics. | **`get_arch_guidelines()`**: Injects repo's real [`ARCHITECTURE.md`](file:///Users/hacaca/Projects/personal/public-repo/agentic-pr-gatekeeper/ARCHITECTURE.md) rules into review prompt. |
| **Blast Radius Calculation** | Guessed arbitrarily by LLM (hallucination-prone). | **Deterministic Engine**: Mathematical line diff count + critical infra pattern matching. |

### 🚌 Real-World Example: Shuttle Travel & Seat Booking System
In high-concurrency systems (such as a **Shuttle Travel Booking System**), subtle bugs can cause critical operational failures:
* **The Problem:** A developer modifies `book_seat()` in `booking.py` but forgets row-level locking (`SELECT FOR UPDATE`), creating a double-booking race condition. They also forget to add a unit test in `tests/test_booking.py`.
* **Traditional Raw Diff Reviewer:** Sees valid Python syntax $\rightarrow$ **False Approval 🟢** (Bypasses CI and causes production double-booking incidents).
* **Agentic MCP Gatekeeper:**
  1. AST extraction isolates `book_seat()` at line 45.
  2. Test discovery notes: `test_booking.py` missing accompanying regression tests.
  3. Architecture guidelines inject rule: *"Seat allocation must use row-level locking (`SELECT FOR UPDATE`)"*.
  4. **Verdict: 🔴 MERGE BLOCKED** with actionable architectural findings!

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/mricky/agentic-pr-gatekeeper.git
cd agentic-pr-gatekeeper

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### 2. Local CLI Usage

Run a pre-push review on your current branch against `main`:

```bash
export GEMINI_API_KEY="your-gemini-api-key"

# Review current branch changes
pr-gatekeeper review --target main

# Inspect MCP context symbols for a specific file
pr-gatekeeper context pr_gatekeeper/blast_radius.py
```

### 3. Running Test Suites

```bash
pytest tests/ -v
```

### 4. Auditing Other Repositories & Troubleshooting

#### A. Error: `zsh: command not found: pr-gatekeeper`
Ensure your virtual environment is activated:
```bash
# In the agentic-pr-gatekeeper folder:
source venv/bin/activate
pr-gatekeeper review --target main
```
Alternatively, call the binary directly:
```bash
./venv/bin/pr-gatekeeper review --target main
```

#### B. Using `pr-gatekeeper` to Audit Another Local Project (e.g. `llm-eval-arena` or your shuttle app)
To run `pr-gatekeeper` inside another project directory:
```bash
# 1. Navigate to target project
cd /path/to/your-target-repo

# 2. Activate its virtual environment
source venv/bin/activate

# 3. Install pr-gatekeeper in editable mode
pip install -e /path/to/agentic-pr-gatekeeper

# 4. Run the review against main
pr-gatekeeper review --target main
```

---

## 🤖 GitHub Actions Setup

Add this step to your repository's `.github/workflows/pr_review.yml`:

```yaml
name: 🛡️ Agentic PR Gatekeeper
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  audit:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      statuses: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install git+https://github.com/mricky/agentic-pr-gatekeeper-.git
      - name: Run Review Gatekeeper
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          COMMIT_SHA: ${{ github.event.pull_request.head.sha }}
        run: pr-gatekeeper review --target main --ci
```

---

## 📄 License
MIT License. Created by [Mochamad Ricky Susanto](https://github.com/mricky).

