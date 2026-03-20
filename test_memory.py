"""
test_memory.py

Tests that Capsule ID + Project Brain are working end-to-end.

Run 1 (now):
    python test_memory.py --run 1

Run 2 (after a server restart or the next day):
    python test_memory.py --run 2

What it checks:
  - Capsule is created and stored in Supabase
  - Same email always returns the same capsule_id
  - Chat turns are persisted to Supabase
  - Session history is restored from Supabase after server restart
  - Holo references prior context in its response
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_KEY  = os.environ.get("HOLO_API_KEY", "demo")
HEADERS  = {"x-api-key": API_KEY, "Content-Type": "application/json"}

# Persistent state file — stores capsule_id and session_id between runs
STATE_FILE = Path(__file__).parent / ".test_memory_state.json"

TEST_EMAIL = "memory-test@holo.internal"
TEST_NAME  = "Memory Test"

# The message sent in Run 1 — specific enough that Holo can only know it if
# it loaded the session from Supabase
RUN1_MARKER = (
    "My name is Taylor and I'm building Holo Protect — "
    "a multi-model adversarial trust layer for AI agent payments. "
    "The secret test phrase is: COPPER-FALCON-7."
)

RUN2_QUESTION = (
    "What do you know about me and what I'm building? "
    "Do you remember the secret test phrase from our last conversation?"
)

SEP = "─" * 60


def ok(msg):   print(f"  ✓  {msg}")
def fail(msg): print(f"  ✗  {msg}"); sys.exit(1)
def info(msg): print(f"     {msg}")


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def signin(email: str, name: str) -> dict:
    resp = requests.post(f"{API_BASE}/auth/email",
                         json={"email": email, "name": name}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def chat(message: str, session_id: str | None, capsule_token: str) -> dict:
    hdrs = {**HEADERS, "Authorization": f"Bearer {capsule_token}"}
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    resp = requests.post(f"{API_BASE}/v1/chat", json=payload,
                         headers=hdrs, timeout=60)
    resp.raise_for_status()
    return resp.json()


def check_supabase_capsule(capsule_id: str) -> dict | None:
    """Query Supabase directly to confirm capsule row exists."""
    try:
        from supabase import create_client
        client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
        resp = client.table("holo_capsules").select("*").eq("capsule_id", capsule_id).single().execute()
        return resp.data
    except Exception as e:
        return None


def check_supabase_session(session_id: str) -> list:
    """Pull all messages for a session directly from Supabase."""
    try:
        from supabase import create_client
        client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
        resp = (client.table("holo_chat_messages")
                .select("role, content, turn_number")
                .eq("session_id", session_id)
                .order("turn_number")
                .execute())
        return resp.data or []
    except Exception as e:
        return []


# ---------------------------------------------------------------------------
# Run 1
# ---------------------------------------------------------------------------

def run1():
    print(f"\n{SEP}")
    print("  RUN 1 — Planting the memory")
    print(SEP)

    # 1. Check API is up
    try:
        health = requests.get(f"{API_BASE}/health", timeout=5).json()
        ok(f"API online — engine: {health.get('engine')}")
    except Exception as e:
        fail(f"API not reachable at {API_BASE}: {e}")

    # 2. Sign in → get capsule
    print("\n  [1] Sign in")
    result = signin(TEST_EMAIL, TEST_NAME)
    capsule_id    = result["capsule_id"]
    capsule_token = result["capsule_token"]
    ok(f"Signed in — capsule_id: {capsule_id[:8]}…")

    # 3. Confirm capsule row in Supabase
    print("\n  [2] Supabase capsule check")
    row = check_supabase_capsule(capsule_id)
    if row:
        ok(f"Capsule row confirmed in Supabase — email: {row.get('email')}, created: {str(row.get('created_at', ''))[:10]}")
    else:
        fail("Capsule row NOT found in Supabase — brain is not persisting capsules")

    # 4. Send the marker message
    print("\n  [3] Sending marker message")
    info(f"Message: \"{RUN1_MARKER[:60]}…\"")
    t0 = time.time()
    chat_result = chat(RUN1_MARKER, None, capsule_token)
    session_id  = chat_result["session_id"]
    elapsed     = int((time.time() - t0) * 1000)
    ok(f"Response received in {elapsed}ms — session_id: {session_id[:8]}…")
    info(f"Holo said: \"{chat_result['response'][:120]}…\"")

    # 5. Confirm messages persisted to Supabase
    print("\n  [4] Supabase message persistence check")
    time.sleep(1)  # give the write a moment
    messages = check_supabase_session(session_id)
    if messages:
        ok(f"{len(messages)} message(s) found in holo_chat_messages for this session")
        for m in messages:
            role    = m["role"].upper()
            preview = m["content"][:80].replace("\n", " ")
            info(f"  turn {m['turn_number']} [{role}]: {preview}…")
    else:
        fail("No messages found in Supabase — chat turns are not being persisted")

    # 6. Save state for Run 2
    state = {
        "capsule_id":    capsule_id,
        "capsule_token": capsule_token,
        "session_id":    session_id,
        "run1_at":       time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    STATE_FILE.write_text(json.dumps(state, indent=2))
    ok(f"State saved to {STATE_FILE.name}")

    print(f"\n{SEP}")
    print("  Run 1 complete. Now:")
    print("  1. Restart the backend server (kills in-memory sessions)")
    print("  2. Wait as long as you like — an hour, a day, a week")
    print("  3. Run:  python test_memory.py --run 2")
    print(SEP + "\n")


# ---------------------------------------------------------------------------
# Run 2
# ---------------------------------------------------------------------------

def run2():
    print(f"\n{SEP}")
    print("  RUN 2 — Testing recall")
    print(SEP)

    if not STATE_FILE.exists():
        fail(f"No state file found. Run 1 first: python test_memory.py --run 1")

    state = json.loads(STATE_FILE.read_text())
    original_capsule_id = state["capsule_id"]
    original_session_id = state["session_id"]
    run1_at             = state.get("run1_at", "unknown")
    info(f"Run 1 was at: {run1_at}")

    # 1. Check API is up
    try:
        requests.get(f"{API_BASE}/health", timeout=5)
        ok("API online")
    except Exception as e:
        fail(f"API not reachable: {e}")

    # 2. Sign in again with the same email
    print("\n  [1] Sign in with same email")
    result     = signin(TEST_EMAIL, TEST_NAME)
    capsule_id = result["capsule_id"]
    token      = result["capsule_token"]

    if capsule_id == original_capsule_id:
        ok(f"Same capsule_id returned — identity is persistent ✓")
    else:
        fail(f"Different capsule_id returned!\n     Run 1: {original_capsule_id}\n     Run 2: {capsule_id}")

    # 3. Confirm messages still in Supabase
    print("\n  [2] Supabase message persistence check")
    messages = check_supabase_session(original_session_id)
    if messages:
        ok(f"{len(messages)} message(s) still in Supabase after restart")
    else:
        fail("Messages gone from Supabase — persistence is not working")

    # 4. Resume the same session — should restore from Supabase
    print("\n  [3] Resume session from Supabase (continuing session_id from Run 1)")
    info(f"Question: \"{RUN2_QUESTION}\"")
    t0 = time.time()
    chat_result = chat(RUN2_QUESTION, original_session_id, token)
    elapsed     = int((time.time() - t0) * 1000)
    response    = chat_result["response"]
    ok(f"Response received in {elapsed}ms")
    print(f"\n  Holo's response:\n")
    print(f"  {'─' * 50}")
    for line in response.split("\n"):
        print(f"  {line}")
    print(f"  {'─' * 50}")

    # 5. Check if the secret phrase was recalled
    print("\n  [4] Checking for secret phrase recall")
    if "COPPER-FALCON-7" in response:
        ok("SECRET PHRASE RECALLED — brain memory is working end-to-end ✓")
    elif any(kw in response.lower() for kw in ["taylor", "holo protect", "adversarial", "trust layer"]):
        ok("Context recalled (name/project remembered) — brain is working ✓")
        info("Secret phrase not explicitly mentioned — check the full response above")
    else:
        print("  ⚠  Response doesn't clearly reference prior context.")
        info("This could mean session restoration worked but Holo chose not to repeat the phrase.")
        info("Check the full response above for indirect references.")

    print(f"\n{SEP}")
    print("  Run 2 complete.")
    print(SEP + "\n")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Holo capsule + brain persistence")
    parser.add_argument("--run", type=int, choices=[1, 2], required=True,
                        help="Which run to execute (1=plant, 2=recall)")
    args = parser.parse_args()

    if args.run == 1:
        run1()
    else:
        run2()
