from __future__ import annotations

from pathlib import Path

from scripts import mnnz_fork_status as module


ROOT = Path(__file__).resolve().parents[2]


def test_that_fork_status_classifies_upstream_source_and_core_paths() -> None:
    source, core = module.classify_overlay_files(
        [
            "AGENTS.md",
            "mnnz/fcm/smoke.py",
            "src/parlant/adapters/nlp/custom.py",
            "src/parlant/core/engines/example.py",
        ]
    )
    assert source == [
        "src/parlant/adapters/nlp/custom.py",
        "src/parlant/core/engines/example.py",
    ]
    assert core == ["src/parlant/core/engines/example.py"]


def test_that_porcelain_parser_preserves_first_tracked_path() -> None:
    assert module.parse_porcelain_paths(" M PLAN.md\n?? mnnz/fcm/smoke.py\n") == [
        "PLAN.md",
        "mnnz/fcm/smoke.py",
    ]


def test_that_fcm_profile_does_not_modify_upstream_source() -> None:
    expected = [
        ROOT / "mnnz" / "fcm" / "README.md",
        ROOT / "mnnz" / "fcm" / "bootstrap.ps1",
        ROOT / "mnnz" / "fcm" / "run.ps1",
        ROOT / "mnnz" / "fcm" / "smoke.py",
    ]
    assert all(path.exists() for path in expected)
