from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class BlastRadiusLevel(str, Enum):
    ISOLATED = "ISOLATED"         # Minor docs, styling, static assets
    MODULE = "MODULE"             # Isolated component, single service logic
    SYSTEM_WIDE = "SYSTEM_WIDE"   # Database schema, auth, billing, payment, routing

class Verdict(str, Enum):
    AUTO_APPROVED = "AUTO_APPROVED"           # Low risk (Score 1-2): eligible for 30% auto-approval target
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW" # Medium risk (Score 3): requires peer review
    REJECTED_BLOCKED = "REJECTED_BLOCKED"     # High risk (Score 4-5): architectural or security violation

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class FileChange(BaseModel):
    file_path: str
    additions: int = 0
    deletions: int = 0
    change_type: str = "MODIFIED" # ADDED, MODIFIED, DELETED
    is_test: bool = False
    is_critical_path: bool = False # touching auth, migrations, billing, etc.

class DeterministicMetrics(BaseModel):
    total_files: int = 0
    total_additions: int = 0
    total_deletions: int = 0
    net_lines: int = 0
    has_accompanying_tests: bool = False
    touches_critical_infrastructure: bool = False
    linter_passed: bool = True
    deterministic_blast_radius: BlastRadiusLevel = BlastRadiusLevel.ISOLATED

class ReviewFinding(BaseModel):
    file_path: str
    line_number: int = 0
    severity: Severity = Severity.MEDIUM
    issue: str
    suggestion: str

class GatekeeperReport(BaseModel):
    overall_risk_score: int = Field(ge=1, le=5, description="Risk Score from 1 (lowest risk) to 5 (critical risk)")
    normalized_score_100: int = Field(ge=0, le=100, description="Normalized score 0-100 for enterprise dashboards")
    blast_radius: BlastRadiusLevel
    verdict: Verdict
    summary: str
    findings: List[ReviewFinding] = Field(default_factory=list)
    deterministic_metrics: Optional[DeterministicMetrics] = None
    mcp_context_used: Optional[Dict[str, Any]] = None

