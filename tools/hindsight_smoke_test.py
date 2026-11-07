#!/usr/bin/env python3
"""Standalone Hindsight Cloud smoke test for LotLens.

The API key is read from .env/environment variables and is never printed.
This script is an isolated integration spike; it does not decide the final app stack.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv
from hindsight_client import Hindsight


DEMO_CASES = [
    (
        "LOT-POC-001",
        "Synthetic case LOT-POC-001: Supplier A, BMS connector, batch A101. "
        "Symptom: intermittent open-circuit readings during vibration testing. "
        "Investigation found insufficient crimp height. Corrective action: recalibrate "
        "the crimp tool and add a crimp-height sampling check. QA verified the action "
        "effective across the defined follow-up sample. This is synthetic demonstration data."
    ),
    (
        "LOT-POC-002",
        "Synthetic case LOT-POC-002: Supplier A, BMS connector, batch A115. "
        "Symptom: intermittent open-circuit readings resembling LOT-POC-001. "
        "A connector reseating/rework action was attempted but QA found the failure "
        "recurred; outcome: ineffective. Root cause remains unconfirmed. Do not treat "
        "this case as proof that the crimp-height issue is the cause. This is synthetic data."
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test LotLens connectivity to Hindsight Cloud.")
    parser.add_argument(
        "--create-bank",
        action="store_true",
        help="Create the configured bank. Use only if it does not already exist.",
    )
    parser.add_argument(
        "--seed-demo",
        action="store_true",
        help="Retain two clearly synthetic cases (may create billable memory operations).",
    )
    parser.add_argument(
        "--reflect",
        action="store_true",
        help="Run one Reflect call after Recall (may incur usage charges).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv()
    api_key = os.getenv("HINDSIGHT_API_KEY")
    base_url = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
    bank_id = os.getenv("HINDSIGHT_BANK_ID", "lotlens-dev")

    if not api_key:
        print("ERROR: HINDSIGHT_API_KEY is missing. Add it to your local .env file.")
        return 2
    if not bank_id:
        print("ERROR: HINDSIGHT_BANK_ID is missing.")
        return 2

    client = Hindsight(base_url=base_url, api_key=api_key, timeout=60.0)
    try:
        if args.create_bank:
            bank = client.create_bank(
                bank_id=bank_id,
                name="LotLens Development",
                background=(
                    "Development memory bank for synthetic manufacturing defect "
                    "investigations, corrective actions and QA-verified outcomes."
                ),
            )
            print(f"Created memory bank: {bank.bank_id}")
        else:
            print(f"Using configured bank: {bank_id}")

        if args.seed_demo:
            for case_id, content in DEMO_CASES:
                client.retain(
                    bank_id=bank_id,
                    content=content,
                    context="LotLens synthetic manufacturing investigation proof of concept",
                    metadata={"case_id": case_id, "dataset": "synthetic", "project": "lotlens"},
                )
                print(f"Retained synthetic experience: {case_id}")

        query = (
            "Find BMS connector intermittent open-circuit failures. "
            "Compare relevant supplier batches, corrective actions and whether QA "
            "verified each action as effective or ineffective. Distinguish similar "
            "symptoms from confirmed common causes."
        )
        recalled = client.recall(bank_id=bank_id, query=query, budget="low")
        print(f"Recall completed. Results returned: {len(recalled.results)}")
        for index, item in enumerate(recalled.results[:5], start=1):
            print(f"  {index}. [{getattr(item, 'type', 'memory')}] {item.text[:500]}")

        if args.reflect:
            response: Any = client.reflect(
                bank_id=bank_id,
                query=(
                    "Based only on the memories available, compare the BMS connector "
                    "investigations. Identify supporting and disconfirming evidence, "
                    "distinguish verified outcomes from unconfirmed causes, and state "
                    "what a quality engineer should investigate next. Apply these strict "
                    "evidence rules: (1) LOT-POC-002 has an explicitly unconfirmed root "
                    "cause; (2) the failure of connector reseating/rework proves only that "
                    "that attempted action was ineffective, not that the underlying cause "
                    "differs from LOT-POC-001; (3) do not claim crimp height is ruled out; "
                    "(4) do not claim the LOT-POC-001 crimp corrective action was applied "
                    "to batch A115 because no such fact is recorded; (5) state what is "
                    "known, unknown, and what evidence would resolve the uncertainty. "
                    "Never promote a hypothesis to a confirmed root cause."
                ),
                budget="low",
            )
            print("\nReflect response:")
            print(response.text)

        print("\nHindsight connection test completed.")
        return 0
    except Exception as exc:  # SDK exceptions include useful HTTP status/details.
        message = str(exc)
        print(f"ERROR: Hindsight request failed: {message}")
        if "401" in message:
            print("Check that the API key is active and copied correctly.")
        elif "402" in message:
            print("The Hindsight account may need credits before memory operations.")
        elif "404" in message:
            print("Check that the bank exists and HINDSIGHT_BANK_ID matches its exact ID.")
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
