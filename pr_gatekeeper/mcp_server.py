import os
import ast
import re
import glob
from typing import List, Dict, Any, Optional

DEFAULT_ARCH_GUIDELINES = """
# Enterprise Engineering Architecture Guidelines (Quality & Safety Gates)
1. Concurrency & Data Consistency:
   - All financial balance or inventory updates must use row-level locking (`SELECT FOR UPDATE`) or serializable transactions.
   - All mutating webhook/API endpoints must enforce idempotent request keys (UUID + payload hash).
2. Database Performance:
   - Zero N+1 queries allowed inside iteration loops.
   - All high-frequency WHERE filters must have supporting B-Tree composite indexes.
   - Zero external merge disk spills allowed on sorting large result sets.
3. Code Quality & Test Coverage:
   - Branch test coverage must stay >= 80%.
   - Every bug fix PR must include an automated regression unit test that would have failed prior to the fix.
4. Security:
   - Zero hardcoded secrets, credentials, or private API keys.
   - All SQL queries must be parameterized to prevent SQL Injection.
   - Webhook signature checks (HMAC-SHA256) must use timing-safe comparison (`compare_digest`).
"""

CODE_EXTENSIONS = (
    ".py", ".ts", ".tsx", ".js", ".jsx",
    ".go", ".rs", ".java", ".php", ".rb", ".cs"
)

class ContextMCPServer:
    """Local Context Provider providing AST/polyglot symbols, test discovery, and architecture rules."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)

    def get_ast_symbols(self, file_path: str) -> List[Dict[str, Any]]:
        """Parses source file symbols (AST for Python, regex for Go/TS/Rust/etc.)."""
        full_path = os.path.join(self.root_dir, file_path) if not os.path.isabs(file_path) else file_path
        if not os.path.exists(full_path):
            return []

        # 1. Native AST Parser for Python
        if file_path.endswith(".py"):
            symbols = []
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    tree = ast.parse(f.read(), filename=file_path)

                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.FunctionDef):
                        symbols.append({
                            "type": "function",
                            "name": node.name,
                            "line": node.lineno,
                            "args": [arg.arg for arg in node.args.args]
                        })
                    elif isinstance(node, ast.ClassDef):
                        methods = [
                            sub.name for sub in node.body if isinstance(sub, ast.FunctionDef)
                        ]
                        symbols.append({
                            "type": "class",
                            "name": node.name,
                            "line": node.lineno,
                            "methods": methods
                        })
            except Exception as e:
                symbols.append({"error": f"Failed to parse AST: {e}"})
            return symbols

        # 2. Universal Polyglot Symbol Extraction (Go, TS/JS, Rust, Java, PHP, etc.)
        symbols = []
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for idx, line in enumerate(lines, 1):
                clean_line = line.strip()
                # Go / Rust / Kotlin: func Name / fn name
                m_func = re.match(r'^(?:pub\s+)?(?:async\s+)?(?:def|func|fn|function)\s+([A-Za-z0-9_]+)', clean_line)
                if m_func:
                    symbols.append({"type": "function", "name": m_func.group(1), "line": idx})
                    continue

                # JS/TS exported arrow or const function
                m_js_func = re.match(r'^(?:export\s+)?(?:const|let|var)\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', clean_line)
                if m_js_func:
                    symbols.append({"type": "function", "name": m_js_func.group(1), "line": idx})
                    continue

                # Class / Struct / Interface / Type definition
                m_class = re.match(r'^(?:pub\s+)?(?:export\s+)?(?:class|interface|type|struct|enum)\s+([A-Za-z0-9_]+)', clean_line)
                if m_class:
                    symbols.append({"type": "type_definition", "name": m_class.group(1), "line": idx})
        except Exception as e:
            symbols.append({"error": f"Failed to extract symbols: {e}"})

        return symbols

    def find_related_tests(self, file_path: str) -> List[str]:
        """Discovers existing test files matching a given source file name across languages."""
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        patterns = [
            f"tests/**/test_{base_name}.py",
            f"tests/**/{base_name}_test.py",
            f"**/test_{base_name}.py",
            f"**/{base_name}.test.*",
            f"**/{base_name}.spec.*",
            f"**/{base_name}_test.go",
            f"tests/**/{base_name}Test.java",
            f"tests/**/{base_name}Test.php",
            f"**/{base_name}_spec.rb"
        ]

        found = []
        for pat in patterns:
            matches = glob.glob(os.path.join(self.root_dir, pat), recursive=True)
            for m in matches:
                rel = os.path.relpath(m, self.root_dir)
                if rel not in found:
                    found.append(rel)
        return found

    def get_arch_guidelines(self) -> str:
        """Retrieves internal ARCHITECTURE.md or returns enterprise defaults."""
        arch_candidates = [
            os.path.join(self.root_dir, "ARCHITECTURE.md"),
            os.path.join(self.root_dir, "docs", "ARCHITECTURE.md"),
            os.path.join(self.root_dir, ".github", "ARCHITECTURE.md"),
        ]
        for p in arch_candidates:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception:
                    pass
        return DEFAULT_ARCH_GUIDELINES.strip()

    def build_pr_context(self, changed_files: List[str]) -> Dict[str, Any]:
        """Aggregates all MCP tools into a unified context packet for the LLM."""
        ast_summary = {}
        related_tests = {}
        for f in changed_files:
            if f.endswith(CODE_EXTENSIONS):
                symbols = self.get_ast_symbols(f)
                if symbols:
                    ast_summary[f] = symbols
            tests = self.find_related_tests(f)
            if tests:
                related_tests[f] = tests

        return {
            "ast_symbols": ast_summary,
            "related_tests": related_tests,
            "architecture_guidelines": self.get_arch_guidelines()
        }

