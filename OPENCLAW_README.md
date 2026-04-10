# OpenClaw Dev Flow

## What's built

**`POST /v1/evaluate`** — production evaluation endpoint  
**`openclaw_skill.py`** — Python PoC skill with `@guarded` decorator  

---

## Endpoint

```
POST /v1/evaluate
Authorization: Bearer <holo_sk_...>
Content-Type: application/json
```

**Request:**
```json
{
  "client_id": "your-system-id",
  "domain": "wire_transfer",
  "action_payload": {
    "amount_usd": 50000,
    "recipient": "Vendor LLC",
    "memo": "Invoice #112"
  }
}
```

**Response:**
```json
{
  "evaluation_id": "holo_a1b2c3d4",
  "verdict": "ESCALATE",
  "confidence": "HIGH",
  "primary_signal": "Approval chain override + off-hours urgency flags",
  "latency_ms": 18400
}
```

**On provider failure** (never crashes):
```json
{
  "evaluation_id": "holo_...",
  "verdict": "ESCALATE",
  "confidence": "LOW",
  "primary_signal": null,
  "latency_ms": 200,
  "provider_error": "Connection timeout"
}
```

---

## Auth

Bearer token validated against the `api_keys` Supabase table (same keys issued via `/auth/keys`). Falls back to `HOLO_API_KEY` env var.

---

## OpenClaw skill

```python
from openclaw_skill import guarded

@guarded(domain="wire_transfer", client_id="my-agent")
def send_wire(amount_usd, recipient_account, memo):
    # only runs if Holo returns ALLOW
    execute_payment(amount_usd, recipient_account)

result = send_wire(50000, "ACC-99999", "URGENT CEO request")
# → ESCALATE: action paused, user notified, returns None
```

Set env vars:
```
HOLO_API_KEY=holo_sk_...
HOLO_API_URL=https://api.holoengine.ai   # or http://localhost:8000
```

---

## Deploy to Railway

Railway auto-deploys from `origin` (GitHub) if connected.

**Option A — push to trigger deploy:**
```bash
git push origin main
```

**Option B — manual deploy via Railway CLI:**
```bash
railway login
railway up
```

The `Procfile` is already correct:
```
web: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

---

## Supabase migration required

The `evaluation_logs` table needs new columns for `/v1/evaluate` logging.  
Run in the Supabase SQL editor:

```sql
ALTER TABLE evaluation_logs
  ADD COLUMN IF NOT EXISTS client_id     text,
  ADD COLUMN IF NOT EXISTS confidence    text,
  ADD COLUMN IF NOT EXISTS primary_signal text,
  ADD COLUMN IF NOT EXISTS latency_ms    integer,
  ADD COLUMN IF NOT EXISTS domain        text,
  ADD COLUMN IF NOT EXISTS provider_error text;
```

Until this runs, evaluations complete normally — logging silently fails with a warning.

---

## Test results (local, 2026-04-10)

| Test | Evaluation ID | Verdict | Turns | Status |
|------|--------------|---------|-------|--------|
| Routine invoice $500 | holo_33cc38f4 | ESCALATE | 4 | 200 OK |
| Suspicious wire $250k | holo_315c137e | ESCALATE | 5 | 200 OK |
| `@guarded` decorator | holo_195a8808 | ESCALATE | 4 | 200 OK |

HTTP 200 on all calls. Auth validated against Supabase `api_keys`. Findings written to `holo_findings`.
