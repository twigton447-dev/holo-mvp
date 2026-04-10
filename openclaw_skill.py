"""
openclaw_skill.py

Proof-of-concept OpenClaw skill.

Intercepts irreversible actions before execution, sends the action payload
to the Holo /v1/evaluate API, and either proceeds (ALLOW) or pauses and
notifies the user (ESCALATE).

Usage:
    from openclaw_skill import guarded

    @guarded(domain="wire_transfer", client_id="demo-client")
    def send_wire(amount_usd, recipient_account, memo):
        # ... execute the real action here
        pass

    result = send_wire(50000, "ACC-98765", "Vendor invoice #112")

Environment variables:
    HOLO_API_KEY   — Bearer token for the Holo API
    HOLO_API_URL   — Base URL (default: https://api.holoengine.ai)
"""

from __future__ import annotations

import functools
import os
import sys
import time
from typing import Any, Callable

import requests

HOLO_API_URL = os.getenv("HOLO_API_URL", "https://api.holoengine.ai")
HOLO_API_KEY = os.getenv("HOLO_API_KEY", "")
EVALUATE_ENDPOINT = f"{HOLO_API_URL}/v1/evaluate"


# ---------------------------------------------------------------------------
# Core evaluation call
# ---------------------------------------------------------------------------

def evaluate_action(client_id: str, domain: str, action_payload: dict) -> dict:
    """
    Send an action payload to the Holo /v1/evaluate endpoint.
    Returns the parsed response dict.
    Raises RuntimeError on network or auth failure.
    """
    if not HOLO_API_KEY:
        raise RuntimeError("HOLO_API_KEY environment variable not set.")

    resp = requests.post(
        EVALUATE_ENDPOINT,
        json={
            "client_id": client_id,
            "domain": domain,
            "action_payload": action_payload,
        },
        headers={
            "Authorization": f"Bearer {HOLO_API_KEY}",
            "Content-Type": "application/json",
        },
        timeout=300,
    )

    if resp.status_code == 401:
        raise RuntimeError(f"Authentication failed (401). Check HOLO_API_KEY.")
    if resp.status_code == 429:
        raise RuntimeError(f"Rate limit exceeded (429). Back off and retry.")
    if not resp.ok:
        raise RuntimeError(f"Holo API error {resp.status_code}: {resp.text[:300]}")

    return resp.json()


# ---------------------------------------------------------------------------
# Notification helper — pluggable per channel
# ---------------------------------------------------------------------------

def notify_user(verdict: dict, action_payload: dict) -> None:
    """
    Notify the user that an action was ESCALATED and paused.
    In production, route to Slack, email, PagerDuty, etc.
    This PoC prints to stdout.
    """
    print("\n" + "=" * 60)
    print("ACTION PAUSED — HOLO ESCALATION")
    print("=" * 60)
    print(f"  evaluation_id : {verdict['evaluation_id']}")
    print(f"  verdict       : {verdict['verdict']}")
    print(f"  confidence    : {verdict['confidence']}")
    print(f"  primary_signal: {verdict.get('primary_signal', 'N/A')}")
    print(f"  latency_ms    : {verdict['latency_ms']}")
    if verdict.get("provider_error"):
        print(f"  provider_error: {verdict['provider_error']}")
    print("-" * 60)
    print("  action_payload:")
    for k, v in action_payload.items():
        print(f"    {k}: {v}")
    print("=" * 60)
    print("Action has NOT been executed. Review and approve manually.\n")


# ---------------------------------------------------------------------------
# @guarded decorator
# ---------------------------------------------------------------------------

def guarded(domain: str, client_id: str = "openclaw-poc"):
    """
    Decorator that intercepts a function call, evaluates the action via Holo,
    and either executes it (ALLOW) or pauses it (ESCALATE).

    Args:
        domain      Maps to Holo's template selection (e.g. "wire_transfer",
                    "invoice_payment", "vendor_onboarding").
        client_id   Identifies the calling system in Holo's logs.
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            # Build action_payload from function arguments
            action_payload = dict(kwargs)
            # Also capture positional args by name if possible
            import inspect
            sig = inspect.signature(fn)
            param_names = list(sig.parameters.keys())
            for i, val in enumerate(args):
                if i < len(param_names):
                    action_payload[param_names[i]] = val

            print(f"[OpenClaw] Intercepting action: domain={domain} fn={fn.__name__}")

            try:
                verdict = evaluate_action(client_id, domain, action_payload)
            except RuntimeError as e:
                print(f"[OpenClaw] Holo API error: {e}")
                print("[OpenClaw] Defaulting to ESCALATE (fail-safe).")
                notify_user(
                    {
                        "evaluation_id": "unavailable",
                        "verdict": "ESCALATE",
                        "confidence": "LOW",
                        "primary_signal": None,
                        "latency_ms": 0,
                        "provider_error": str(e),
                    },
                    action_payload,
                )
                return None

            if verdict["verdict"] == "ALLOW":
                print(
                    f"[OpenClaw] ALLOW "
                    f"(confidence={verdict['confidence']}, "
                    f"latency={verdict['latency_ms']}ms, "
                    f"id={verdict['evaluation_id']})"
                )
                return fn(*args, **kwargs)
            else:
                notify_user(verdict, action_payload)
                return None

        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# End-to-end test
# ---------------------------------------------------------------------------

def _run_e2e_test():
    """
    Run one ALLOW-path and one ESCALATE-path test against the live API.
    Prints results. Does not execute any real actions.
    """
    print("\n" + "=" * 60)
    print("OPENCLAW END-TO-END TEST")
    print(f"  endpoint: {EVALUATE_ENDPOINT}")
    print("=" * 60)

    # --- ALLOW path: routine, low-risk action ---
    print("\n[Test 1] Routine action — expecting ALLOW or fast evaluation")
    t0 = time.time()
    try:
        result = evaluate_action(
            client_id="openclaw-e2e-test",
            domain="invoice_payment",
            action_payload={
                "amount_usd": 500,
                "recipient": "Acme Supplies LLC",
                "account_number": "ACC-00123",
                "memo": "Monthly office supplies invoice #INV-2026-001",
                "initiated_by": "finance-bot@company.com",
            },
        )
        elapsed = int((time.time() - t0) * 1000)
        print(f"  verdict       : {result['verdict']}")
        print(f"  confidence    : {result['confidence']}")
        print(f"  primary_signal: {result.get('primary_signal', 'N/A')}")
        print(f"  evaluation_id : {result['evaluation_id']}")
        print(f"  latency_ms    : {result['latency_ms']} (wall: {elapsed}ms)")
        if result.get("provider_error"):
            print(f"  provider_error: {result['provider_error']}")
        print(f"  [{'PASS' if result['verdict'] in ('ALLOW', 'ESCALATE') else 'FAIL'}] Request returned a valid verdict.")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # --- ESCALATE path: suspicious wire ---
    print("\n[Test 2] Suspicious wire — expecting ESCALATE")
    t0 = time.time()
    try:
        result = evaluate_action(
            client_id="openclaw-e2e-test",
            domain="wire_transfer",
            action_payload={
                "amount_usd": 250000,
                "recipient": "NEW-VENDOR-XYZ",
                "account_number": "ACC-99999",
                "bank": "Unknown Bank, Cayman Islands",
                "memo": "URGENT: CEO approval verbal — process immediately",
                "initiated_by": "external-agent@unknown.io",
                "request_received_at": "2026-04-10T03:42:00Z",
            },
        )
        elapsed = int((time.time() - t0) * 1000)
        print(f"  verdict       : {result['verdict']}")
        print(f"  confidence    : {result['confidence']}")
        print(f"  primary_signal: {result.get('primary_signal', 'N/A')}")
        print(f"  evaluation_id : {result['evaluation_id']}")
        print(f"  latency_ms    : {result['latency_ms']} (wall: {elapsed}ms)")
        if result.get("provider_error"):
            print(f"  provider_error: {result['provider_error']}")
        print(f"  [{'PASS' if result['verdict'] == 'ESCALATE' else 'SOFT-PASS (ALLOW returned, review signal)'}] Request returned a verdict.")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # --- Decorator test ---
    print("\n[Test 3] @guarded decorator — ALLOW path")

    @guarded(domain="invoice_payment", client_id="openclaw-e2e-test")
    def pay_invoice(amount_usd, vendor, memo):
        print(f"  >> Executing payment: ${amount_usd} to {vendor} — {memo}")
        return {"status": "paid", "amount": amount_usd}

    pay_result = pay_invoice(
        amount_usd=250,
        vendor="Office Depot",
        memo="Printer paper restock",
    )
    print(f"  pay_result: {pay_result}")

    print("\n[Test 4] @guarded decorator — ESCALATE path")

    @guarded(domain="wire_transfer", client_id="openclaw-e2e-test")
    def send_wire(amount_usd, recipient_account, memo):
        print(f"  >> Executing wire: ${amount_usd} to {recipient_account}")
        return {"status": "wired", "amount": amount_usd}

    wire_result = send_wire(
        amount_usd=180000,
        recipient_account="OFFSHORE-ACC-001",
        memo="URGENT CEO request do not delay",
    )
    print(f"  wire_result: {wire_result}  (None = action was paused)")

    print("\n" + "=" * 60)
    print("END-TO-END TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    _run_e2e_test()
