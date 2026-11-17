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
      - run: pip install agentic-pr-gatekeeper
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
