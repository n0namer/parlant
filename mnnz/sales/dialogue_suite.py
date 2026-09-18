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


def evaluate_turn(text: str, turn: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    for pattern in turn.get("forbidden_regex", []):
        if re.search(pattern, text):
            violations.append(f"forbidden_regex:{pattern}")
    return violations


def wait_for_message(
    base_url: str,
    session_id: str,
    anchor: int,
    timeout_s: float,
) -> tuple[str, float, dict[str, Any]]:
    started = time.monotonic()
    while True:
        remaining = timeout_s - (time.monotonic() - started)
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


def recheck_captured_suite(
    fixture: dict[str, Any],
    captured: dict[str, Any],
) -> dict[str, Any]:
    scenarios = {scenario["id"]: scenario for scenario in fixture["scenarios"]}
    all_violations: list[str] = []
    scenario_results: list[dict[str, Any]] = []

    for original_scenario in captured.get("scenarios", []):
        scenario_id = original_scenario["id"]
        scenario = scenarios[scenario_id]
        turn_results: list[dict[str, Any]] = []
        for index, original_turn in enumerate(original_scenario.get("turns", [])):
            turn = scenario["turns"][index]
            violations = evaluate_turn(original_turn["message"], turn)
            all_violations.extend(f"{scenario_id}:turn-{index + 1}:{value}" for value in violations)
            updated_turn = dict(original_turn)
            updated_turn["violations"] = violations
            turn_results.append(updated_turn)
        updated_scenario = dict(original_scenario)
        updated_scenario["turns"] = turn_results
        updated_scenario["status"] = (
            "PASS" if all(not turn["violations"] for turn in turn_results) else "FAIL"
        )
        scenario_results.append(updated_scenario)

    return {
        **captured,
        "status": "PASS" if not all_violations else "FAIL",
        "violations": all_violations,
        "scenarios": scenario_results,
        "rechecked": True,
    }


def run_suite(base_url: str, fixture: dict[str, Any], timeout_s: float) -> dict[str, Any]:
    profile = provision(
        base_url=base_url,
        offer_summary=fixture["offer_summary"],
        capabilities=list(fixture["capabilities"]),
        name_prefix="MNNZ adversarial suite",
    )

    scenario_results: list[dict[str, Any]] = []
    all_violations: list[str] = []

    for scenario in fixture["scenarios"]:
        session = request_json(
            base_url,
            "/sessions",
            {
                "agent_id": profile["agent_id"],
                "title": f"{fixture['name']}::{scenario['id']}",
                "metadata": {
                    "simulation": True,
                    "source": "mnnz-sales-adversarial-suite",
                    "schema": fixture["schema"],
                    "schema_version": fixture["schema_version"],
                    "scenario_id": scenario["id"],
                },
            },
        )
        turn_results: list[dict[str, Any]] = []
        for turn_index, turn in enumerate(scenario["turns"], start=1):
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
            violations = evaluate_turn(message, turn)
            all_violations.extend(
                f"{scenario['id']}:turn-{turn_index}:{value}" for value in violations
            )
            turn_results.append(
                {
                    "turn": turn_index,
                    "customer": turn["message"],
                    "message": message,
                    "latency_s": round(latency_s, 3),
                    "violations": violations,
                    "manual_expectations": turn.get("manual_expectations", []),
                    "matched_guidelines": metadata.get("matched_guidelines", []),
                    "matched_journeys": metadata.get("matched_journeys", []),
                }
            )
        scenario_results.append(
            {
                "id": scenario["id"],
                "priority": scenario["priority"],
                "risk_ids": scenario.get("risk_ids", []),
                "title": scenario["title"],
                "session_id": session["id"],
                "status": "PASS"
                if all(not turn["violations"] for turn in turn_results)
                else "FAIL",
                "turns": turn_results,
            }
        )

    return {
        "status": "PASS" if not all_violations else "FAIL",
        "fixture": fixture["name"],
        "profile": profile,
        "violations": all_violations,
        "scenarios": scenario_results,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Run the MNNZ adversarial dialogue suite")
    parser.add_argument("--base-url", default="http://127.0.0.1:8800")
    parser.add_argument(
        "--fixture",
        default=str(HERE / "fixtures" / "p0_adversarial_dialogues.json"),
    )
    parser.add_argument("--timeout", type=float, default=240.0)
    parser.add_argument(
        "--recheck-result",
        help="Re-evaluate a captured suite JSON with current fixture rules without calling Parlant.",
    )
    args = parser.parse_args()

    fixture = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    if args.recheck_result:
        captured = json.loads(Path(args.recheck_result).read_text(encoding="utf-8"))
        result = recheck_captured_suite(fixture, captured)
    else:
        result = run_suite(args.base_url, fixture, args.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
