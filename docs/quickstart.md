# Holo API — Developer Quickstart

## What it does

You have an AI agent about to take an irreversible action — send a wire, approve a vendor, modify permissions. Before it executes, you send the action to Holo. Holo runs a multi-model adversarial evaluation and returns `ALLOW` or `ESCALATE` with a reason.

Your agent proceeds or pauses based on the verdict.

---

## Get an API key

Email taylor@holoengine.ai with your use case. You'll receive a `holo_sk_...` key.

---

## Make your first call

```bash
curl -X POST https://api.holoengine.ai/v1/evaluate \
  -H "Authorization: Bearer holo_sk_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "your-system-name",
    "domain": "wire_transfer",
    "action_payload": {
      "amount_usd": 50000,
      "recipient": "Acme Supplies LLC",
      "memo": "Invoice #INV-2026-112",
      "initiated_by": "finance-agent@yourcompany.com"
    }
  }'
```

**Response:**
```json
{
  "evaluation_id": "holo_a1b2c3d4",
  "verdict": "ALLOW",
  "confidence": "HIGH",
  "primary_signal": null,
  "latency_ms": 18400
}
```

---

## Verdict reference

| verdict | confidence | meaning |
|---------|-----------|---------|
| `ALLOW` | `HIGH` | Clean. Proceed. |
| `ALLOW` | `MEDIUM` | Likely clean. Models didn't fully converge. |
| `ESCALATE` | `HIGH` | Confirmed risk. Do not execute. Route to human. |
| `ESCALATE` | `MEDIUM` | Suspicious but inconclusive. Human review recommended. |
| `ESCALATE` | `LOW` | Provider error — Holo couldn't complete evaluation. Fail-safe triggered. |

---

## Domains

Pass the action type in the `domain` field. Supported values:

| domain | use case |
|--------|----------|
| `wire_transfer` | Outbound payments, wires, ACH |
| `invoice_payment` | Vendor invoice approvals |
| `vendor_onboarding` | New vendor or supplier registration |
| `permission_change` | Access control modifications |
| `data_export` | Bulk data exports or transfers |

Unknown domains fall back to `invoice_payment` template.

---

## Python — `@guarded` decorator

Install:
```bash
pip install requests
```

Copy [`openclaw_skill.py`](../openclaw_skill.py) into your project.

```python
import os
from openclaw_skill import guarded

os.environ["HOLO_API_KEY"] = "holo_sk_YOUR_KEY"
os.environ["HOLO_API_URL"] = "https://api.holoengine.ai"

@guarded(domain="wire_transfer", client_id="my-agent")
def send_wire(amount_usd, recipient, memo):
    # only runs if Holo returns ALLOW
    your_payment_api.send(amount_usd, recipient, memo)

# Holo evaluates before executing
send_wire(50000, "Acme LLC", "Invoice #112")
```

If verdict is `ESCALATE`, the function does not execute and the user is notified.

---

## What to put in `action_payload`

The more context you provide, the tighter the evaluation. Sparse payloads escalate by default (fail-safe).

**Good payload:**
```json
{
  "amount_usd": 50000,
  "recipient": "Acme Supplies LLC",
  "recipient_account": "ACC-00123",
  "memo": "Monthly supplies invoice #INV-2026-112",
  "initiated_by": "finance-agent@company.com",
  "vendor_known": true,
  "prior_payments_to_vendor": 8,
  "request_received_via": "email",
  "request_time_utc": "2026-04-10T14:30:00Z"
}
```

**Minimum viable payload:**
```json
{
  "amount_usd": 50000,
  "recipient": "Acme Supplies LLC",
  "memo": "Invoice #112"
}
```

---

## Error handling

Holo never crashes your agent. On provider failure:

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

Always handle `verdict == "ESCALATE"` — including the `LOW` confidence / provider error case.

---

## Latency

Full evaluation runs 2–3 minutes. Set your client timeout to at least 300 seconds.

This is intentional: Holo runs multiple independent model turns with adversarial pressure. Speed is not the product. Accuracy at the action boundary is.

---

## Limits

| | Free tier |
|--|--|
| Evaluations | 10/month |
| Payload size | 32KB |
| Timeout | 300s |

Need more? Contact taylor@holoengine.ai.
