"""
billing.py

Stripe billing integration for Holo.

Plans:
  free     — 1 free loop, no card required
  starter  — $49/mo, 500 calls
  pro      — $199/mo, 3000 calls
  enterprise — custom

Flow:
  1. User signs up → free tier, 1 call quota
  2. User hits limit → directed to upgrade
  3. User subscribes via Stripe Checkout
  4. Webhook confirms payment → quota updated in Supabase
"""

from __future__ import annotations

import logging
import os

import stripe

logger = logging.getLogger("holo.billing")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

PLANS = {
    "free":    {"calls_per_month": 1,    "price_id": None,                                    "amount_usd": 0},
    "starter": {"calls_per_month": 500,  "price_id": os.getenv("STRIPE_STARTER_PRICE_ID"),    "amount_usd": 49},
    "pro":     {"calls_per_month": 3000, "price_id": os.getenv("STRIPE_PRO_PRICE_ID"),        "amount_usd": 199},
}

OVERAGE_RATE = {
    "starter": 0.15,  # $ per call over quota
    "pro":     0.10,
}


def create_checkout_session(plan: str, customer_email: str, success_url: str, cancel_url: str) -> str:
    """
    Create a Stripe Checkout session for the given plan.
    Returns the checkout URL to redirect the user to.
    """
    price_id = PLANS[plan]["price_id"]
    if not price_id:
        raise ValueError(f"No price ID configured for plan: {plan}")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        customer_email=customer_email,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"plan": plan},
    )
    return session.url


def create_customer_portal_session(stripe_customer_id: str, return_url: str) -> str:
    """
    Create a Stripe Customer Portal session so users can manage/cancel their subscription.
    Returns the portal URL.
    """
    session = stripe.billing_portal.Session.create(
        customer=stripe_customer_id,
        return_url=return_url,
    )
    return session.url


def get_subscription(stripe_customer_id: str) -> dict | None:
    """Fetch the active subscription for a customer. Returns None if none found."""
    try:
        subs = stripe.Subscription.list(customer=stripe_customer_id, status="active", limit=1)
        if subs.data:
            return subs.data[0]
    except Exception as e:
        logger.warning(f"Failed to fetch subscription: {e}")
    return None


def construct_webhook_event(payload: bytes, sig_header: str) -> stripe.Event:
    """Parse and verify a Stripe webhook event."""
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    return stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
