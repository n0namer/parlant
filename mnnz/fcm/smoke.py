from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from typing import Any


def request_json(base_url: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body[:500]}") from exc


def wait_for_message(
    base_url: str, session_id: str, anchor: int, timeout_s: float
) -> tuple[str, float]:
    started = time.monotonic()
    while time.monotonic() - started < timeout_s:
        events = request_json(base_url, f"/sessions/{session_id}/events")
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
            return answer["data"]["message"], time.monotonic() - started
        time.sleep(1)
    raise TimeoutError(f"No AI message within {timeout_s:.1f}s")


def main() -> int:
    parser = argparse.ArgumentParser(description="Parlant -> FCM live compatibility smoke")
    parser.add_argument("--base-url", default="http://127.0.0.1:8800")
    parser.add_argument("--timeout", type=float, default=180.0)
    args = parser.parse_args()

    agent = request_json(
        args.base_url,
        "/agents",
        {
            "name": f"MNNZ FCM smoke {int(time.time())}",
            "description": (
                "Compatibility smoke agent. Reply in Russian. "
                "Do not invent pricing or capabilities. No external side effects."
            ),
        },
    )
    session = request_json(
        args.base_url,
        "/sessions",
        {
            "agent_id": agent["id"],
            "title": "MNNZ FCM compatibility smoke",
            "metadata": {"simulation": True, "source": "mnnz-fcm-smoke"},
        },
    )
    customer_event = request_json(
        args.base_url,
        f"/sessions/{session['id']}/events",
        {
            "kind": "message",
            "source": "customer",
            "message": (
                "У нас уже есть CRM, часть входящих заявок теряется. "
                "Какой минимальный первый шаг вы бы предложили? Не придумывайте цену."
            ),
        },
    )
    message, latency_s = wait_for_message(
        args.base_url,
        session["id"],
        int(customer_event["offset"]),
        args.timeout,
    )

    result = {
        "status": "PASS",
        "agent_id": agent["id"],
        "session_id": session["id"],
        "latency_s": round(latency_s, 3),
        "message": message,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
