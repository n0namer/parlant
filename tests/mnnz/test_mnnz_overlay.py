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


def test_that_fcm_runner_avoids_reserved_powershell_home_variable() -> None:
    runner = (ROOT / "mnnz" / "fcm" / "run.ps1").read_text(encoding="utf-8")
    assert "[string]$ParlantHome" in runner
    assert "[string]$Home" not in runner
    assert "$env:PARLANT_HOME = $ParlantHome" in runner
    assert "--migrate" in runner


def test_that_fcm_readme_uses_non_reserved_runner_parameter() -> None:
    readme = (ROOT / "mnnz" / "fcm" / "README.md").read_text(encoding="utf-8")
    assert "-ParlantHome" in readme
    assert "-Home " not in readme
