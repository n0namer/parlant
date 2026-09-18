from __future__ import annotations

import json
from pathlib import Path

from mnnz.sales.profile import GUIDELINES, JOURNEY, build_agent_description
from mnnz.sales import replay as replay_module
from mnnz.sales.replay import evaluate_response


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "mnnz" / "sales" / "fixtures" / "ultra_vacancy_baseline.json"


def test_that_sales_profile_has_unique_stable_guideline_keys() -> None:
    keys = [item.key for item in GUIDELINES]
    assert len(keys) == len(set(keys))
    assert {
        "language_continuity",
        "capability_grounding",
        "no_invented_business_facts",
        "unknown_pricing",
        "respect_channel_preference",
        "problem_first",
        "terminal_stop",
    }.issubset(set(keys))


def test_that_agent_description_is_bounded_by_explicit_offer_truth() -> None:
    description = build_agent_description(
        "CRM integration only",
        ["CRM integration", "workflow automation"],
    )
    assert "CRM integration only" in description
    assert "CRM integration, workflow automation" in description
    assert "Never invent pricing" in description


def test_that_journey_contains_terminal_stop_instruction() -> None:
    assert "stop selling" in JOURNEY.description.lower()
    assert JOURNEY.priority == 100


def test_that_shared_fixture_is_versioned_and_has_four_cross_project_turns() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert fixture["schema"] == "mnnz.parlant.sales-replay"
    assert fixture["schema_version"] == "1.0.0"
    assert [turn["id"] for turn in fixture["turns"]] == [
        "price_without_canonical_price",
        "unsupported_capability_and_no_call",
        "problem_first",
        "terminal_stop",
    ]


def test_that_replay_evaluator_distinguishes_claim_from_explicit_denial() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    turn = fixture["turns"][1]
    assert evaluate_response("Да, можем взять холодный обзвон на себя.", turn)
    assert evaluate_response("Мы не можем делать холодные звонки за вас.", turn) == []
    assert evaluate_response("Мы не можем обучать ваших менеджеров продавать.", turn) == []


def test_that_fixture_rejects_invented_sales_department_handoff() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    first_turn = fixture["turns"][0]
    violations = evaluate_response(
        "Для стоимости свяжитесь с нашим отделом продаж.",
        first_turn,
    )
    assert violations


def test_that_recheck_captured_result_recomputes_stale_false_positive() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    captured = {
        "status": "FAIL",
        "violations": ["stale"],
        "results": [
            {
                "id": "unsupported_capability_and_no_call",
                "message": "Мы не можем делать холодные звонки за вас или обучать ваших менеджеров продавать.",
                "violations": ["stale"],
            }
        ],
    }
    rechecked = replay_module.recheck_captured_result(fixture, captured)
    assert rechecked["status"] == "PASS"
    assert rechecked["violations"] == []
    assert rechecked["results"][0]["violations"] == []
    assert rechecked["rechecked"] is True


def test_that_wait_for_message_retries_transient_poll_timeout() -> None:
    calls = 0
    original_request_json = replay_module.request_json
    original_sleep = replay_module.time.sleep

    def fake_request_json(base_url, path, payload=None, timeout_s=30.0):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise TimeoutError("transient poll timeout")
        return [
            {
                "offset": 2,
                "source": "ai_agent",
                "kind": "message",
                "data": {"message": "safe reply"},
            },
            {
                "offset": 3,
                "source": "ai_agent",
                "kind": "status",
                "data": {
                    "status": "ready",
                    "data": {"stage": "completed", "matched_guidelines": []},
                },
            },
        ]

    try:
        replay_module.request_json = fake_request_json
        replay_module.time.sleep = lambda _: None
        message, latency_s, metadata = replay_module.wait_for_message(
            "http://test",
            "session-1",
            anchor=1,
            timeout_s=5.0,
        )
    finally:
        replay_module.request_json = original_request_json
        replay_module.time.sleep = original_sleep

    assert message == "safe reply"
    assert latency_s >= 0
    assert metadata["stage"] == "completed"
    assert calls == 2


def test_that_replay_uses_cli_timeout_for_customer_event_post() -> None:
    seen_timeouts: list[float] = []
    original_provision = replay_module.provision
    original_request_json = replay_module.request_json
    original_wait_for_message = replay_module.wait_for_message

    def fake_request_json(base_url, path, payload=None, timeout_s=30.0):
        assert base_url == "http://test"
        if path == "/sessions":
            return {"id": "session-1"}
        if path.endswith("/events") and payload is not None:
            seen_timeouts.append(timeout_s)
            return {"offset": 1}
        raise AssertionError((path, payload, timeout_s))

    fixture = {
        "schema": "mnnz.parlant.sales-replay",
        "schema_version": "1.0.0",
        "name": "timeout-proof",
        "offer_summary": "CRM",
        "capabilities": ["CRM"],
        "turns": [{"id": "t1", "message": "hello", "forbidden_regex": []}],
    }

    try:
        replay_module.provision = lambda **_: {
            "agent_id": "agent-1",
            "guideline_count": 0,
            "journey_id": "journey-1",
        }
        replay_module.request_json = fake_request_json
        replay_module.wait_for_message = lambda *args, **kwargs: ("safe response", 0.1, {})

        result = replay_module.run_replay("http://test", fixture, timeout_s=91.0)
    finally:
        replay_module.provision = original_provision
        replay_module.request_json = original_request_json
        replay_module.wait_for_message = original_wait_for_message

    assert result["status"] == "PASS"
    assert seen_timeouts == [91.0]
