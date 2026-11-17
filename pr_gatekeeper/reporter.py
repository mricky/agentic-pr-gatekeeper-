import os
import requests
from pr_gatekeeper.models import GatekeeperReport, Verdict, Severity

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAVE_RICH = True
    console = Console()
except ImportError:
    HAVE_RICH = False
    console = None

def print_rich_terminal_report(report: GatekeeperReport):
    """Prints a beautiful colored summary table to the developer's terminal."""
    badge_style = {
        Verdict.AUTO_APPROVED: "🟢 AUTO-APPROVED (Low Risk)",
        Verdict.NEEDS_HUMAN_REVIEW: "🟡 NEEDS HUMAN REVIEW (Medium Risk)",
        Verdict.REJECTED_BLOCKED: "🔴 REJECTED / BLOCKED (High Risk)",
    }
    verdict_badge = badge_style.get(report.verdict, str(report.verdict.value))

    if HAVE_RICH and console:
        rich_badge_style = {
            Verdict.AUTO_APPROVED: "[bold green]🟢 AUTO-APPROVED (Low Risk)[/bold green]",
            Verdict.NEEDS_HUMAN_REVIEW: "[bold yellow]🟡 NEEDS HUMAN REVIEW (Medium Risk)[/bold yellow]",
            Verdict.REJECTED_BLOCKED: "[bold red]🔴 REJECTED / BLOCKED (High Risk)[/bold red]",
        }
        r_verdict = rich_badge_style.get(report.verdict, str(report.verdict.value))
        console.print()
        console.print(Panel(
            f"[bold cyan]🛡️ AGENTIC PR GATEKEEPER EVALUATION REPORT[/bold cyan]\n"
            f"Verdict: {r_verdict}  |  Risk Score: [bold]{report.overall_risk_score} / 5[/bold] ({report.normalized_score_100}/100)  |  Blast Radius: [bold]{report.blast_radius.value}[/bold]\n\n"
            f"[italic]{report.summary}[/italic]",
            border_style="cyan"
        ))

        if report.deterministic_metrics:
            dm = report.deterministic_metrics
            console.print(f"[dim]Stats: {dm.total_files} files changed (+{dm.total_additions}/-{dm.total_deletions}) | Tests present: {dm.has_accompanying_tests} | Touches critical infra: {dm.touches_critical_infrastructure}[/dim]")

        if report.findings:
            table = Table(title="Semantic Audit Findings", show_header=True, header_style="bold magenta")
            table.add_column("Location", style="dim", width=25)
            table.add_column("Severity", width=12)
            table.add_column("Issue Detected", width=35)
            table.add_column("Actionable Suggestion")

            for f in report.findings:
                sev_color = {
                    Severity.CRITICAL: "[bold red]CRITICAL[/bold red]",
                    Severity.HIGH: "[red]HIGH[/red]",
                    Severity.MEDIUM: "[yellow]MEDIUM[/yellow]",
                    Severity.LOW: "[green]LOW[/green]",
                }.get(f.severity, str(f.severity.value))

                loc = f"{f.file_path}:{f.line_number}" if f.line_number else f.file_path
                table.add_row(loc, sev_color, f.issue, f.suggestion)

            console.print(table)
        else:
            console.print("[green]✨ No security or architectural violations detected.[/green]")
        console.print()
    else:
        # Fallback Plain ASCII Console
        print("\n" + "=" * 70)
        print("🛡️ AGENTIC PR GATEKEEPER EVALUATION REPORT")
        print("=" * 70)
        print(f"Verdict:     {verdict_badge}")
        print(f"Risk Score:  {report.overall_risk_score} / 5 (Normalized: {report.normalized_score_100}/100)")
        print(f"Blast Radius:{report.blast_radius.value}")
        print(f"Summary:     {report.summary}")
        if report.deterministic_metrics:
            dm = report.deterministic_metrics
            print(f"Files:       {dm.total_files} files (+{dm.total_additions}/-{dm.total_deletions}) | Tests: {dm.has_accompanying_tests}")
        print("-" * 70)
        if report.findings:
            print("FINDINGS:")
            for idx, f in enumerate(report.findings, 1):
                loc = f"{f.file_path}:{f.line_number}" if f.line_number else f.file_path
                print(f"  {idx}. [{f.severity.value}] {loc}: {f.issue}")
                print(f"     Suggestion: {f.suggestion}")
        else:
            print("✨ No architectural or security violations detected.")
        print("=" * 70 + "\n")

def generate_markdown_pr_comment(report: GatekeeperReport) -> str:
    """Generates a structured GitHub Markdown PR comment."""
    verdict_badge = {
        Verdict.AUTO_APPROVED: "🟢 **AUTO-APPROVED** (30% Fast-Track Quality Gate)",
        Verdict.NEEDS_HUMAN_REVIEW: "🟡 **NEEDS HUMAN REVIEW** (Peer Review Required)",
        Verdict.REJECTED_BLOCKED: "🔴 **MERGE BLOCKED** (Architectural / Security Violation)",
    }.get(report.verdict, str(report.verdict.value))

    finding_rows = ""
    for f in report.findings:
        icon = "🔴" if f.severity in [Severity.CRITICAL, Severity.HIGH] else ("🟡" if f.severity == Severity.MEDIUM else "🟢")
        loc = f"`{f.file_path}:{f.line_number}`" if f.line_number else f"`{f.file_path}`"
        finding_rows += f"| {loc} | {icon} `{f.severity.value}` | {f.issue} | `{f.suggestion}` |\n"

    if not finding_rows:
        finding_rows = "| - | 🟢 `CLEAN` | No architectural regressions or vulnerabilities found. | Ready to merge. |\n"

    dm_summary = ""
    if report.deterministic_metrics:
        dm = report.deterministic_metrics
        dm_summary = f"- **Files Changed:** `{dm.total_files}` (+{dm.total_additions}/-{dm.total_deletions})\n" \
                     f"- **Accompanying Tests:** `{'Yes ✅' if dm.has_accompanying_tests else 'No ⚠️'}`\n" \
                     f"- **Critical Infrastructure Path:** `{'Yes ⚠️' if dm.touches_critical_infrastructure else 'No ✅'}`\n"

    return f"""### 🛡️ Agentic PR Gatekeeper Report
**Evaluation Verdict:** {verdict_badge}  
**Overall Risk Score:** `{report.overall_risk_score} / 5` (Normalized: `{report.normalized_score_100}/100`)  
**Blast Radius:** `{report.blast_radius.value}`  

> {report.summary}

---

### 📊 Deterministic Metrics:
{dm_summary}
---

### 📋 Semantic Audit Findings:
| Location | Severity | Issue Detected | Actionable Suggestion |
| :--- | :---: | :--- | :--- |
{finding_rows}

{"⚠️ **Action Required:** This PR violates architectural boundaries or security invariants. Resolve findings above or obtain an emergency break-glass approval." if report.verdict == Verdict.REJECTED_BLOCKED else ("✨ **Auto-Approval Eligible:** Code changes pass all safety thresholds and qualifies for the automated 30% approval target." if report.verdict == Verdict.AUTO_APPROVED else "👀 **Peer Review Required:** Please request review from a team member.")}

*Powered by Agentic PR Gatekeeper & Model Context Protocol (MCP)*
"""

def post_github_status_and_comment(report: GatekeeperReport):
    """Posts comment and status check to GitHub if running in GitHub Actions."""
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    pr_number = os.environ.get("PR_NUMBER", "").strip()
    commit_sha = os.environ.get("COMMIT_SHA", "").strip()

    if not token or not repo or not pr_number or not commit_sha:
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 1. Update Commit Status Check
    status_url = f"https://api.github.com/repos/{repo}/statuses/{commit_sha}"
    state = "success" if report.verdict in [Verdict.AUTO_APPROVED, Verdict.NEEDS_HUMAN_REVIEW] else "failure"
    payload = {
        "state": state,
        "description": f"Risk Score: {report.overall_risk_score}/5 ({report.verdict.value})",
        "context": "pr-agent/risk-gate",
        "target_url": f"https://github.com/{repo}/pull/{pr_number}"
    }
    try:
        requests.post(status_url, json=payload, headers=headers, timeout=15)
    except Exception as e:
        if console:
            console.print(f"[dim]Failed to update GitHub status check: {e}[/dim]")

    # 2. Post PR Comment
    comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    comment_body = generate_markdown_pr_comment(report)
    try:
        requests.post(comment_url, json={"body": comment_body}, headers=headers, timeout=15)
    except Exception as e:
        if console:
            console.print(f"[dim]Failed to post PR comment: {e}[/dim]")
