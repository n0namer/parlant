from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

from .api import request_json
from .provision import provision

HERE = Path(__file__).resolve().parent


def wait_for_message(
    base_url: str,
    session_id: str,
    anchor: int,
    timeout_s: float,
) -> tuple[str, float, dict[str, Any]]:
    started = time.monotonic()
    while True:
        elapsed = time.monotonic() - started
        remaining = timeout_s - elapsed
        if remaining <= 0:
            break
        try:
            events = request_json(
                base_url,
                f"/sessions/{session_id}/events",
                timeout_s=min(10.0, remaining),
            )
        except (TimeoutError, OSError):
            time.sleep(min(1.0, max(0.0, remaining)))
            continue

        answers = [
            event
            for event in events
            if event.get("kind") == "message"
            and event.get("source") == "ai_agent"
            and isinstance(event.get("offset"), int)
            and event["offset"] > anchor
            and isinstance(event.get("data", {}).get("message"), str)
        ]
        if answers:
            answer = max(answers, key=lambda item: item["offset"])
            ready = [
                event
                for event in events
                if event.get("kind") == "status"
                and event.get("source") == "ai_agent"
                and isinstance(event.get("offset"), int)
                and event["offset"] > anchor
                and event.get("data", {}).get("status") == "ready"
            ]
            metadata = ready[-1].get("data", {}).get("data", {}) if ready else {}
            return (
                answer["data"]["message"],
                time.monotonic() - started,
                metadata,
            )
        time.sleep(1)
    raise TimeoutError(f"No AI message within {timeout_s:.1f}s")


def evaluate_response(text: str, turn: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    for pattern in turn.get("forbidden_regex", []):
        if re.search(pattern, text):
            violations.append(f"forbidden_regex:{pattern}")
    return violations


def recheck_captured_result(
    fixture: dict[str, Any],
    captured: dict[str, Any],
) -> dict[str, Any]:
    turns = {turn["id"]: turn for turn in fixture["turns"]}
    results: list[dict[str, Any]] = []
    all_violations: list[str] = []

    for original in captured.get("results", []):
        turn_id = original["id"]
        turn = turns[turn_id]
        violations = evaluate_response(original["message"], turn)
        all_violations.extend(f"{turn_id}:{value}" for value in violations)
        updated = dict(original)
        updated["violations"] = violations
        results.append(updated)

    return {
        **captured,
        "status": "PASS" if not all_violations else "FAIL",
        "violations": all_violations,
        "results": results,
        "rechecked": True,
    }


def run_replay(
    base_url: str,
    fixture: dict[str, Any],
    timeout_s: float,
) -> dict[str, Any]:
    profile = provision(
        base_url=base_url,
        offer_summary=fixture["offer_summary"],
        capabilities=list(fixture["capabilities"]),
        name_prefix="MNNZ replay",
    )
    session = request_json(
        base_url,
        "/sessions",
        {
            "agent_id": profile["agent_id"],
            "title": fixture["name"],
            "metadata": {
                "simulation": True,
                "source": "mnnz-sales-replay",
                "schema": fixture["schema"],
                "schema_version": fixture["schema_version"],
            },
        },
    )

    results: list[dict[str, Any]] = []
    all_violations: list[str] = []
    for turn in fixture["turns"]:
        event = request_json(
            base_url,
            f"/sessions/{session['id']}/events",
            {
                "kind": "message",
                "source": "customer",
                "message": turn["message"],
            },
            timeout_s=timeout_s,
        )
        message, latency_s, metadata = wait_for_message(
            base_url,
            session["id"],
            int(event["offset"]),
            timeout_s,
        )
        violations = evaluate_response(message, turn)
        all_violations.extend(f"{turn['id']}:{value}" for value in violations)
        results.append(
            {
                "id": turn["id"],
                "message": message,
                "latency_s": round(latency_s, 3),
                "violations": violations,
                "matched_guidelines": metadata.get("matched_guidelines", []),
                "matched_journeys": metadata.get("matched_journeys", []),
            }
        )

    return {
        "status": "PASS" if not all_violations else "FAIL",
        "fixture": fixture["name"],
        "profile": profile,
        "session_id": session["id"],
        "violations": all_violations,
        "results": results,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Run the cross-project MNNZ sales replay")
    parser.add_argument("--base-url", default="http://127.0.0.1:8800")
    parser.add_argument(
        "--fixture",
        default=str(HERE / "fixtures" / "ultra_vacancy_baseline.json"),
    )
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument(
        "--recheck-result",
        help="Re-evaluate a captured replay JSON with the current fixture rules without calling Parlant.",
    )
    args = parser.parse_args()

    fixture = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    if args.recheck_result:
        captured = json.loads(Path(args.recheck_result).read_text(encoding="utf-8"))
        result = recheck_captured_result(fixture, captured)
    else:
        result = run_replay(args.base_url, fixture, args.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
