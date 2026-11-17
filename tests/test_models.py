import pytest
from pr_gatekeeper.models import (
    BlastRadiusLevel,
    Verdict,
    Severity,
    ReviewFinding,
    GatekeeperReport,
    DeterministicMetrics
)

def test_models_validation():
    report = GatekeeperReport(
        overall_risk_score=2,
        normalized_score_100=40,
        blast_radius=BlastRadiusLevel.ISOLATED,
        verdict=Verdict.AUTO_APPROVED,
        summary="Test typo fix and documentation update.",
        findings=[
            ReviewFinding(
                file_path="README.md",
                line_number=10,
                severity=Severity.LOW,
                issue="Minor grammatical typo",
                suggestion="Fix spelling"
            )
        ]
    )

    assert report.overall_risk_score == 2
    assert report.verdict == Verdict.AUTO_APPROVED
    assert len(report.findings) == 1
    assert report.findings[0].severity == Severity.LOW

def test_models_risk_score_bounds():
    with pytest.raises(ValueError):
        GatekeeperReport(
            overall_risk_score=6, # Must be <= 5
            normalized_score_100=120,
            blast_radius=BlastRadiusLevel.SYSTEM_WIDE,
            verdict=Verdict.REJECTED_BLOCKED,
            summary="Invalid score test"
        )
