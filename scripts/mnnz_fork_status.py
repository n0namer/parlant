from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass


CORE_PREFIX = "src/parlant/core/"
UPSTREAM_SOURCE_PREFIX = "src/parlant/"


@dataclass(frozen=True)
class ForkStatus:
    branch: str
    upstream_develop_sha: str
    fork_main_sha: str
    fork_dev_sha: str
    head_sha: str
    upstream_push_url: str
    overlay_files: list[str]
    upstream_source_modified_files: list[str]
    upstream_core_modified_files: list[str]
    core_delta_alarm: bool


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        check=True,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.rstrip()


def classify_overlay_files(paths: list[str]) -> tuple[list[str], list[str]]:
    source = sorted(path for path in paths if path.startswith(UPSTREAM_SOURCE_PREFIX))
    core = sorted(path for path in source if path.startswith(CORE_PREFIX))
    return source, core


def parse_porcelain_paths(status_text: str) -> list[str]:
    paths: set[str] = set()
    for line in status_text.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path.replace("\\", "/"))
    return sorted(paths)


def working_tree_paths() -> list[str]:
    return parse_porcelain_paths(git("status", "--porcelain=v1", "-uall"))


def collect_status() -> ForkStatus:
    branch = git("branch", "--show-current")
    committed_paths = [
        line for line in git("diff", "--name-only", "main...HEAD").splitlines() if line
    ]
    paths = sorted(set(committed_paths) | set(working_tree_paths()))
    upstream_source, upstream_core = classify_overlay_files(paths)
    return ForkStatus(
        branch=branch,
        upstream_develop_sha=git("rev-parse", "upstream/develop"),
        fork_main_sha=git("rev-parse", "fork/main"),
        fork_dev_sha=git("rev-parse", "fork/dev"),
        head_sha=git("rev-parse", "HEAD"),
        upstream_push_url=git("remote", "get-url", "--push", "upstream"),
        overlay_files=sorted(paths),
        upstream_source_modified_files=upstream_source,
        upstream_core_modified_files=upstream_core,
        core_delta_alarm=len(upstream_core) > 5,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report MNNZ Parlant fork drift against mirror main"
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    status = collect_status()
    payload = asdict(status)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"branch={status.branch}")
        print(f"upstream/develop={status.upstream_develop_sha}")
        print(f"fork/main={status.fork_main_sha}")
        print(f"fork/dev={status.fork_dev_sha}")
        print(f"HEAD={status.head_sha}")
        print(f"upstream_push={status.upstream_push_url}")
        print(f"overlay_files={len(status.overlay_files)}")
        print(f"upstream_source_modified_files={len(status.upstream_source_modified_files)}")
        print(f"upstream_core_modified_files={len(status.upstream_core_modified_files)}")
        print(f"core_delta_alarm={str(status.core_delta_alarm).lower()}")

    if status.upstream_push_url != "DISABLED":
        return 3
    if status.core_delta_alarm:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
