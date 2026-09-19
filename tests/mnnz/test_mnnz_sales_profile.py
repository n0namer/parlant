from __future__ import annotations

import json
from pathlib import Path

from mnnz.sales.profile import GUIDELINES, JOURNEY, build_agent_description
from mnnz.sales import replay as replay_module
from mnnz.sales.replay import evaluate_response


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "mnnz" / "sales" / "fixtures" / "ultra_vacancy_baseline.json"
ADVERSARIAL_FIXTURE = ROOT / "mnnz" / "sales" / "fixtures" / "p0_adversarial_dialogues.json"


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
    assert (
        evaluate_response(
            "Мы не можем делать холодные звонки за вас и не можем обучать ваших менеджеров продавать.",
            turn,
        )
        == []
    )


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


def test_that_problem_first_fixture_rejects_invented_timeline() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    turn = next(item for item in fixture["turns"] if item["id"] == "problem_first")
    assert evaluate_response("Это делается за 15–20 минут.", turn)
    assert evaluate_response("Срок зависит от текущей настройки amoCRM.", turn) == []


def test_that_p0_adversarial_fixture_has_independent_risk_scenarios() -> None:
    fixture = json.loads(ADVERSARIAL_FIXTURE.read_text(encoding="utf-8"))
    assert fixture["schema"] == "mnnz.parlant.dialogue-suite"
    assert fixture["schema_version"] == "1.0.0"
    scenarios = {item["id"]: item for item in fixture["scenarios"]}
    assert {
        "post_stop_factual_question",
        "customer_correction_replaces_stale_fact",
        "no_call_preference_persists",
        "unsupported_guarantee",
    }.issubset(scenarios)
    assert all(item["priority"] == "P0" for item in scenarios.values())
    assert all(item["turns"] for item in scenarios.values())


def test_that_guarantee_evaluator_distinguishes_refusal_from_promise() -> None:
    fixture = json.loads(ADVERSARIAL_FIXTURE.read_text(encoding="utf-8"))
    scenario = next(item for item in fixture["scenarios"] if item["id"] == "unsupported_guarantee")
    turn = scenario["turns"][0]
    from mnnz.sales.dialogue_suite import evaluate_turn

    assert (
        evaluate_turn(
            "Я не могу гарантировать, что продажи вырастут в два раза.",
            turn,
        )
        == []
    )
    assert evaluate_turn(
        "Мы гарантируем, что продажи вырастут в два раза.",
        turn,
    )


def test_that_adversarial_suite_recheck_recomputes_false_positive() -> None:
    fixture = json.loads(ADVERSARIAL_FIXTURE.read_text(encoding="utf-8"))
    from mnnz.sales.dialogue_suite import recheck_captured_suite

    captured = {
        "status": "FAIL",
        "violations": ["stale"],
        "scenarios": [
            {
                "id": "unsupported_guarantee",
                "status": "FAIL",
                "turns": [
                    {
                        "turn": 1,
                        "message": "Я не могу гарантировать, что продажи вырастут минимум в два раза.",
                        "violations": ["stale"],
                    }
                ],
            }
        ],
    }
    rechecked = recheck_captured_suite(fixture, captured)
    assert rechecked["status"] == "PASS"
    assert rechecked["violations"] == []
    assert rechecked["scenarios"][0]["status"] == "PASS"


def test_that_unsupported_capability_turn_requires_explicit_declines() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    turn = next(
        item for item in fixture["turns"] if item["id"] == "unsupported_capability_and_no_call"
    )
    evasive = (
        "Да, мы можем помочь с интеграцией amoCRM, автоматизацией процессов, "
        "аналитикой и AI-ассистентами для продаж."
    )
    explicit = (
        "Холодные звонки за вас мы не делаем и обучение менеджеров продажам "
        "не предоставляем. Можем помочь с CRM, автоматизацией, аналитикой и AI-ассистентами."
    )
    assert any(
        value.startswith("missing_required_regex:") for value in evaluate_response(evasive, turn)
    )
    assert evaluate_response(explicit, turn) == []


def test_that_capability_guideline_requires_direct_negative_before_alternatives() -> None:
    guideline = next(item for item in GUIDELINES if item.key == "capability_grounding")
    action = guideline.action.lower()
    assert "directly" in action
    assert "do not provide/do it" in action
    assert "do not dodge" in action


def test_that_problem_first_fixture_rejects_invented_effort_or_complexity() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    turn = next(item for item in fixture["turns"] if item["id"] == "problem_first")
    assert evaluate_response(
        "Это не потребует больших изменений — только настройка отчёта.",
        turn,
    )
    assert (
        evaluate_response(
            "Первым шагом можно проверить маршрутизацию заявок и отчёт по обработке.",
            turn,
        )
        == []
    )


def test_that_profile_forbids_invented_effort_complexity_estimates() -> None:
    guideline = next(item for item in GUIDELINES if item.key == "no_invented_business_facts")
    condition = guideline.condition.lower()
    assert "effort" in condition
    assert "complexity" in condition
    assert "implementation scope" in condition


def test_that_problem_first_fixture_rejects_invented_platform_feature_and_guaranteed_fix() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    turn = next(item for item in fixture["turns"] if item["id"] == "problem_first")
    assert evaluate_response(
        "Дубли можно убрать правилом автоматического объединения по email или телефону.",
        turn,
    )
    assert evaluate_response(
        "Это минимальный шаг, который решит вашу проблему с потерями и дублями.",
        turn,
    )
    assert (
        evaluate_response(
            "Первым шагом проверьте маршрутизацию, источник и ответственного по потерянным заявкам.",
            turn,
        )
        == []
    )


def test_that_profile_has_external_platform_grounding_guideline() -> None:
    guideline = next(item for item in GUIDELINES if item.key == "external_platform_grounding")
    text = f"{guideline.condition} {guideline.action}".lower()
    assert "third-party platform" in text
    assert "do not assert" in text
    assert "conditional wording" in text


def test_that_provision_uses_current_journey_triggers_api() -> None:
    from mnnz.sales import provision as provision_module

    calls: list[tuple[str, dict[str, object] | None]] = []
    original_request_json = provision_module.request_json

    def fake_request_json(base_url, path, payload=None, timeout_s=30.0):
        assert base_url == "http://test"
        calls.append((path, payload))
        if path == "/tags":
            return {"id": "tag-1"}
        if path == "/agents":
            return {"id": "agent-1"}
        if path == "/guidelines":
            return {"id": f"guideline-{len(calls)}"}
        if path == "/journeys":
            return {"id": "journey-1"}
        raise AssertionError(path)

    try:
        provision_module.request_json = fake_request_json
        result = provision_module.provision(
            "http://test",
            "CRM integration only",
            ["CRM integration"],
            "Test",
        )
    finally:
        provision_module.request_json = original_request_json

    journey_payload = next(payload for path, payload in calls if path == "/journeys")
    assert journey_payload is not None
    assert journey_payload["triggers"] == list(JOURNEY.triggers)
    assert "conditions" not in journey_payload
    assert result["journey_id"] == "journey-1"


def test_that_journey_uses_public_triggers_contract() -> None:
    assert JOURNEY.triggers
    assert "interest" in JOURNEY.triggers[0].lower()
