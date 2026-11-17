from pr_gatekeeper.blast_radius import (
    is_test_file,
    touches_critical_path,
    parse_numstat,
    calculate_deterministic_metrics
)
from pr_gatekeeper.models import BlastRadiusLevel

def test_is_test_file_detection():
    assert is_test_file("tests/test_service.py") is True
    assert is_test_file("src/app.spec.ts") is True
    assert is_test_file("src/controllers/auth_controller.py") is False

def test_touches_critical_path():
    assert touches_critical_path("db/migrations/001_create_users.sql") is True
    assert touches_critical_path("src/services/billing_service.py") is True
    assert touches_critical_path("src/components/Button.tsx") is False

def test_calculate_deterministic_metrics_isolated():
    numstat_raw = "10\t2\tdocs/guide.md\n5\t1\tREADME.md\n"
    changes = parse_numstat(numstat_raw)
    metrics = calculate_deterministic_metrics(changes)

    assert metrics.total_files == 2
    assert metrics.total_additions == 15
    assert metrics.total_deletions == 3
    assert metrics.deterministic_blast_radius == BlastRadiusLevel.ISOLATED

def test_calculate_deterministic_metrics_system_wide():
    numstat_raw = "450\t120\tdb/migrations/002_add_ledger.sql\n"
    changes = parse_numstat(numstat_raw)
    metrics = calculate_deterministic_metrics(changes)

    assert metrics.touches_critical_infrastructure is True
    assert metrics.deterministic_blast_radius == BlastRadiusLevel.SYSTEM_WIDE

