import re
from typing import List, Tuple
from pr_gatekeeper.models import (
    BlastRadiusLevel,
    FileChange,
    DeterministicMetrics
)

CRITICAL_PATHS = [
    "migration", "schema", "auth", "security", "billing", "payment",
    "ledger", "dockerfile", "k8s", "kubernetes", "workflow", "ci"
]

TEST_PATTERNS = [
    r"test_", r"_test\.", r"\.spec\.", r"\.test\.", r"/tests?/", r"/__tests__/"
]

DOC_AND_ASSET_EXTS = [
    ".md", ".markdown", ".txt", ".rst", ".json", ".yaml", ".yml",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".css"
]

def is_doc_or_asset(file_path: str) -> bool:
    return any(file_path.lower().endswith(ext) for ext in DOC_AND_ASSET_EXTS)

def is_test_file(file_path: str) -> bool:
    path_lower = file_path.lower()
    return any(re.search(pattern, path_lower) for pattern in TEST_PATTERNS)

def touches_critical_path(file_path: str) -> bool:
    path_lower = file_path.lower()
    return any(keyword in path_lower for keyword in CRITICAL_PATHS)

def parse_numstat(numstat_output: str) -> List[FileChange]:
    changes: List[FileChange] = []
    for line in numstat_output.strip().splitlines():
        parts = line.strip().split(maxsplit=2)
        if len(parts) < 3:
            continue
        add_str, del_str, file_path = parts
        additions = int(add_str) if add_str.isdigit() else 0
        deletions = int(del_str) if del_str.isdigit() else 0
        
        changes.append(FileChange(
            file_path=file_path,
            additions=additions,
            deletions=deletions,
            is_test=is_test_file(file_path),
            is_critical_path=touches_critical_path(file_path)
        ))
    return changes

def calculate_deterministic_metrics(changes: List[FileChange], linter_passed: bool = True) -> DeterministicMetrics:
    total_files = len(changes)
    total_additions = sum(c.additions for c in changes)
    total_deletions = sum(c.deletions for c in changes)
    net_lines = total_additions - total_deletions

    # True source code excludes docs, assets, and tests
    has_source_code = any(not c.is_test and not is_doc_or_asset(c.file_path) for c in changes)
    has_tests = any(c.is_test for c in changes)
    has_accompanying_tests = has_tests or (not has_source_code)
    
    touches_critical = any(c.is_critical_path for c in changes)

    # Determine Blast Radius
    total_diff_volume = total_additions + total_deletions
    if touches_critical or total_diff_volume > 400 or total_files > 8:
        blast_radius = BlastRadiusLevel.SYSTEM_WIDE
    elif total_diff_volume > 100 or total_files > 3 or (has_source_code and not has_tests):
        blast_radius = BlastRadiusLevel.MODULE
    else:
        blast_radius = BlastRadiusLevel.ISOLATED

    return DeterministicMetrics(
        total_files=total_files,
        total_additions=total_additions,
        total_deletions=total_deletions,
        net_lines=net_lines,
        has_accompanying_tests=has_accompanying_tests,
        touches_critical_infrastructure=touches_critical,
        linter_passed=linter_passed,
        deterministic_blast_radius=blast_radius
    )