import os
import json
import requests
from typing import Dict, Any, Optional
from pr_gatekeeper.models import (
    GatekeeperReport,
    BlastRadiusLevel,
    Verdict,
    Severity,
    ReviewFinding,
    DeterministicMetrics
)

def evaluate_with_llm(
    diff_text: str,
    deterministic_metrics: DeterministicMetrics,
    mcp_context: Dict[str, Any],
    api_key: Optional[str] = None
) -> GatekeeperReport:
    """Evaluates PR using Gemini 3.0 / LLM, enforcing structured schema output."""
    api_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()

    # Baseline deterministic fallback if no API key or empty diff
    if not diff_text.strip():
        return GatekeeperReport(
            overall_risk_score=1,
            normalized_score_100=0,
            blast_radius=BlastRadiusLevel.ISOLATED,
            verdict=Verdict.AUTO_APPROVED,
            summary="No functional source code changes detected in this Pull Request.",
            findings=[],
            deterministic_metrics=deterministic_metrics,
            mcp_context_used=mcp_context
        )

    if not api_key:
        # Deterministic fallback based purely on blast radius & tests
        score = 2 if deterministic_metrics.has_accompanying_tests and not deterministic_metrics.touches_critical_infrastructure else 4
        verdict = Verdict.AUTO_APPROVED if score <= 2 else Verdict.NEEDS_HUMAN_REVIEW
        return GatekeeperReport(
            overall_risk_score=score,
            normalized_score_100=score * 20,
            blast_radius=deterministic_metrics.deterministic_blast_radius,
            verdict=verdict,
            summary=f"Evaluated via deterministic baseline (GEMINI_API_KEY not configured). Blast radius is {deterministic_metrics.deterministic_blast_radius.value}.",
            findings=[],
            deterministic_metrics=deterministic_metrics,
            mcp_context_used=mcp_context
        )

    # Gemini 3.0 Prompt with MCP context injection
    arch_rules = mcp_context.get("architecture_guidelines", "")
    ast_summary = json.dumps(mcp_context.get("ast_symbols", {}), indent=2)
    tests_summary = json.dumps(mcp_context.get("related_tests", {}), indent=2)

    prompt = f"""
You are an elite Principal Software Architect and Autonomous CI/CD Gatekeeper auditing a Pull Request.

Context from MCP Tools:
---
[ARCHITECTURE GUIDELINES]:
{arch_rules}

[AST SYMBOLS MODIFIED]:
{ast_summary}

[RELATED TESTS DETECTED]:
{tests_summary}

[DETERMINISTIC METRICS]:
- Total Files Changed: {deterministic_metrics.total_files}
- Additions: {deterministic_metrics.total_additions}, Deletions: {deterministic_metrics.total_deletions}
- Touches Critical Infrastructure: {deterministic_metrics.touches_critical_infrastructure}
- Has Accompanying Tests: {deterministic_metrics.has_accompanying_tests}
---

Your Task:
Analyze the Git Diff below and produce an authoritative review report.
1. Evaluate Blast Radius: 'ISOLATED' (docs/minor style), 'MODULE' (single component/logic), or 'SYSTEM_WIDE' (auth/db/billing).
2. Calculate an Overall Risk Score (Integer from 1 to 5):
   - 1: Trivial / Zero Risk (Typo fixes, documentation, test additions) -> ELIGIBLE FOR AUTO-APPROVAL
   - 2: Low Risk (Minor isolated bugfix with accompanying unit tests) -> ELIGIBLE FOR AUTO-APPROVAL
   - 3: Medium Risk (Standard feature, refactor, or logic change requiring human peer review) -> NEEDS HUMAN REVIEW
   - 4: High Risk (Significant architectural change, unindexed queries, missing tests on critical paths) -> REJECTED / BLOCKED
   - 5: Critical Risk (SQL Injection, race conditions, floating point money drift, data corruption risk) -> REJECTED / BLOCKED
3. Set Verdict:
   - If Score <= 2: 'AUTO_APPROVED' (fulfilling the 30% auto-approval target)
   - If Score == 3: 'NEEDS_HUMAN_REVIEW'
   - If Score >= 4: 'REJECTED_BLOCKED'

CRITICAL: Return output ONLY as pure JSON adhering to this schema:
{{
    "overall_risk_score": <1-5>,
    "normalized_score_100": <0-100>,
    "blast_radius": "<ISOLATED|MODULE|SYSTEM_WIDE>",
    "verdict": "<AUTO_APPROVED|NEEDS_HUMAN_REVIEW|REJECTED_BLOCKED>",
    "summary": "<Concise 2-3 sentence executive evaluation summary>",
    "findings": [
        {{
            "file_path": "<file>",
            "line_number": <int>,
            "severity": "<LOW|MEDIUM|HIGH|CRITICAL>",
            "issue": "<concise issue description>",
            "suggestion": "<actionable fix>"
        }}
    ]
}}

Git Diff:
```diff
{diff_text[:35000]}
```
"""

    model_name = "gemini-3-flash-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    }

    try:
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=45)
        if res.status_code != 200:
            url_fallback = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            res = requests.post(url_fallback, json=payload, headers={"Content-Type": "application/json"}, timeout=45)
        res.raise_for_status()
        data = res.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(raw_text)

        score = int(parsed.get("overall_risk_score", 3))
        norm_score = int(parsed.get("normalized_score_100", score * 20))
        blast = BlastRadiusLevel(parsed.get("blast_radius", deterministic_metrics.deterministic_blast_radius.value))
        verdict = Verdict(parsed.get("verdict", "NEEDS_HUMAN_REVIEW"))

        findings = [
            ReviewFinding(
                file_path=f.get("file_path", "unknown"),
                line_number=f.get("line_number", 0),
                severity=Severity(f.get("severity", "MEDIUM")),
                issue=f.get("issue", ""),
                suggestion=f.get("suggestion", "")
            )
            for f in parsed.get("findings", [])
        ]

        return GatekeeperReport(
            overall_risk_score=score,
            normalized_score_100=norm_score,
            blast_radius=blast,
            verdict=verdict,
            summary=parsed.get("summary", "Automated evaluation completed."),
            findings=findings,
            deterministic_metrics=deterministic_metrics,
            mcp_context_used=mcp_context
        )

    except Exception as e:
        # Graceful fallback to deterministic analysis
        return GatekeeperReport(
            overall_risk_score=3,
            normalized_score_100=60,
            blast_radius=deterministic_metrics.deterministic_blast_radius,
            verdict=Verdict.NEEDS_HUMAN_REVIEW,
            summary=f"Automated AI review fallback (API error: {e}). Manual peer review required.",
            findings=[],
            deterministic_metrics=deterministic_metrics,
            mcp_context_used=mcp_context
        )
