from __future__ import annotations

import argparse
import json
import time

from .api import request_json
from .profile import GUIDELINES, JOURNEY, build_agent_description


def provision(
    base_url: str,
    offer_summary: str,
    capabilities: list[str],
    name_prefix: str,
) -> dict[str, object]:
    nonce = int(time.time())
    tag = request_json(base_url, "/tags", {"name": f"mnnz-sales-{nonce}"})
    tag_id = tag["id"]

    agent = request_json(
        base_url,
        "/agents",
        {
            "name": f"{name_prefix} {nonce}",
            "description": build_agent_description(offer_summary, capabilities),
            "tags": [tag_id],
        },
    )

    guideline_ids: list[str] = []
    for spec in GUIDELINES:
        guideline = request_json(
            base_url,
            "/guidelines",
            {
                "condition": spec.condition,
                "action": spec.action,
                "description": f"MNNZ:{spec.key}",
                "criticality": spec.criticality,
                "enabled": True,
                "tags": [tag_id],
                "priority": spec.priority,
            },
            timeout_s=120.0,
        )
        guideline_ids.append(guideline["id"])

    journey = request_json(
        base_url,
        "/journeys",
        {
            "title": JOURNEY.title,
            "triggers": list(JOURNEY.triggers),
            "description": JOURNEY.description,
            "tags": [tag_id],
            "priority": JOURNEY.priority,
        },
        timeout_s=120.0,
    )

    return {
        "agent_id": agent["id"],
        "tag_id": tag_id,
        "guideline_ids": guideline_ids,
        "journey_id": journey["id"],
        "guideline_count": len(guideline_ids),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Provision the MNNZ bounded-sales profile")
    parser.add_argument("--base-url", default="http://127.0.0.1:8800")
    parser.add_argument("--offer-summary", required=True)
    parser.add_argument("--capability", action="append", default=[])
    parser.add_argument("--name-prefix", default="MNNZ bounded sales")
    args = parser.parse_args()

    result = provision(args.base_url, args.offer_summary, args.capability, args.name_prefix)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
