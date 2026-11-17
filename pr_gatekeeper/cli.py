import sys
import argparse
import subprocess
from typing import Optional, Tuple, List
from pr_gatekeeper import __version__
from pr_gatekeeper.blast_radius import parse_numstat, calculate_deterministic_metrics
from pr_gatekeeper.mcp_server import ContextMCPServer
from pr_gatekeeper.reviewer import evaluate_with_llm
from pr_gatekeeper.reporter import (
    print_rich_terminal_report,
    post_github_status_and_comment
)

SUPPORTED_EXTENSIONS = [
    "*.py", "*.ts", "*.tsx", "*.js", "*.jsx",
    "*.go", "*.rs", "*.java", "*.php", "*.rb",
    "*.cs", "*.cpp", "*.c", "*.sql", "*.html",
    "*.yaml", "*.yml"
]

def get_git_diff_and_stats(target_branch: str = "main") -> Tuple[str, str, List[str]]:
    """Extracts git diff, numstat, and changed file paths across polyglot languages."""
    cmd_stat = ["git", "diff", f"origin/{target_branch}...HEAD", "--numstat"]
    cmd_diff = ["git", "diff", f"origin/{target_branch}...HEAD", "--"] + SUPPORTED_EXTENSIONS

    try:
        numstat = subprocess.check_output(cmd_stat).decode("utf-8", errors="ignore")
        diff = subprocess.check_output(cmd_diff).decode("utf-8", errors="ignore")
    except Exception:
        try:
            cmd_stat = ["git", "diff", "HEAD~1...HEAD", "--numstat"]
            cmd_diff = ["git", "diff", "HEAD~1...HEAD", "--"] + SUPPORTED_EXTENSIONS
            numstat = subprocess.check_output(cmd_stat).decode("utf-8", errors="ignore")
            diff = subprocess.check_output(cmd_diff).decode("utf-8", errors="ignore")
        except Exception:
            numstat = ""
            diff = ""

    changed_files = [
        line.split()[-1] for line in numstat.strip().splitlines() if line.strip()
    ]
    return diff, numstat, changed_files

def run_review(target: str = "main", ci_mode: bool = False, api_key: Optional[str] = None):
    """Core review execution."""
    diff_text, numstat_text, changed_files = get_git_diff_and_stats(target)

    # 1. Deterministic Blast Radius
    file_changes = parse_numstat(numstat_text)
    deterministic_metrics = calculate_deterministic_metrics(file_changes)

    # 2. MCP Codebase Context
    mcp_server = ContextMCPServer(root_dir=".")
    mcp_context = mcp_server.build_pr_context(changed_files)

    # 3. LLM Semantic Review
    report = evaluate_with_llm(
        diff_text=diff_text,
        deterministic_metrics=deterministic_metrics,
        mcp_context=mcp_context,
        api_key=api_key
    )

    # 4. Multi-Channel Reporting
    print_rich_terminal_report(report)

    if ci_mode:
        post_github_status_and_comment(report)

    if report.verdict.value == "REJECTED_BLOCKED":
        sys.exit(1)
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        prog="pr-gatekeeper",
        description="🛡️ AI-Powered Autonomous Pull Request Review & Quality Gate via MCP"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: review
    p_review = subparsers.add_parser("review", help="Audit branch diff using MCP context and Gemini 3.0")
    p_review.add_argument("--target", "-t", default="main", help="Target branch to compare against (default: main)")
    p_review.add_argument("--ci", action="store_true", help="CI mode (posts comment & status check to GitHub)")
    p_review.add_argument("--api-key", help="Google Gemini API Key (or set GEMINI_API_KEY env variable)")

    # Command: context
    p_context = subparsers.add_parser("context", help="Inspect MCP context tools for a source file")
    p_context.add_argument("file_path", help="File path to inspect")

    # Command: version
    subparsers.add_parser("version", help="Show version information")

    args = parser.parse_args()

    if args.command == "review":
        run_review(target=args.target, ci_mode=args.ci, api_key=args.api_key)
    elif args.command == "context":
        mcp = ContextMCPServer(root_dir=".")
        symbols = mcp.get_ast_symbols(args.file_path)
        tests = mcp.find_related_tests(args.file_path)
        print(f"🔍 MCP Context for: {args.file_path}")
        print(f"• AST Symbols: {len(symbols)} found")
        for s in symbols:
            print(f"  - {s.get('type')}: {s.get('name')} (line {s.get('line')})")
        print(f"• Related Tests: {tests if tests else 'None detected'}")
    elif args.command == "version":
        print(f"Agentic PR Gatekeeper v{__version__}")
    else:
        parser.print_help()

app = main

if __name__ == "__main__":
    main()
