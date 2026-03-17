#!/usr/bin/env python3
"""Holo V1 MVP -- API Key Generator.

Usage:
    python generate_key.py "demo-key"
    python generate_key.py "test-key" --rpm 20
"""

import hashlib
import os
import secrets
import sys

from dotenv import load_dotenv

load_dotenv()


def generate_key(name: str, max_rpm: int = 10):
    """Generate a new API key and insert it into Supabase."""

    from db import Database

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        sys.exit(1)

    db = Database(url=url, key=key)

    # Generate the key
    raw_key = f"holo_sk_{secrets.token_hex(16)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:15]

    # Insert into Supabase
    record = db.insert_api_key(
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=name,
        max_rpm=max_rpm,
    )

    print()
    print("=" * 60)
    print("  Holo API Key Generated")
    print("=" * 60)
    print()
    print(f"  Name:    {name}")
    print(f"  Key:     {raw_key}")
    print(f"  Prefix:  {key_prefix}")
    print(f"  RPM:     {max_rpm}")
    print(f"  ID:      {record['id']}")
    print()
    print("  IMPORTANT: Copy the key now. It cannot be retrieved later.")
    print()
    print(f"  Paste into .env:  HOLO_API_KEY={raw_key}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_key.py <key-name> [--rpm <max>]")
        sys.exit(1)

    name = sys.argv[1]
    rpm = 10

    if "--rpm" in sys.argv:
        idx = sys.argv.index("--rpm")
        rpm = int(sys.argv[idx + 1])

    generate_key(name, rpm)
