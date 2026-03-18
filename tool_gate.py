"""
tool_gate.py

The governor's external verification layer. Runs once at the start of each
evaluation, before any analyst turn.

Purpose:
  Convert INFERRED signals into SUBMITTED_DATA facts. Instead of asking models
  to speculate ("this routing number might be a consumer credit union"), the
  governor looks it up and hands the analysts the answer as verified data.

Four verifiers:
  1. routing_institution   — what bank does this routing number belong to?
  2. invoice_amount        — exact % deviation from the vendor's historical range
  3. acquisition_timing    — was a banking change requested before the acquisition closed?
  4. email_domain          — do all emails in the chain use the vendor's registered domain?

Failure policy:
  Every verifier is fault-tolerant. A failed lookup returns None and is logged.
  The evaluation continues without that fact — the system degrades gracefully.
"""

import logging
import re
from datetime import datetime
from statistics import mean, stdev
from typing import Optional

logger = logging.getLogger("holo.toolgate")

ROUTING_API = "https://www.routingnumbers.info/api/name.json"


class ToolGate:

    def verify(self, action: dict, context: dict) -> dict:
        """
        Run all applicable verifiers for this evaluation.
        Returns a dict of verified facts. Never raises.
        """
        facts = {}

        # 1. Routing number institution lookup
        routing = str(action.get("routing_number", "")).strip()
        if routing:
            result = self._lookup_routing(routing)
            if result:
                facts["routing_institution"] = result

        vendor_record = context.get("vendor_record", {})
        email_chain   = context.get("email_chain", [])

        # 2. Invoice amount vs. historical range
        amount = action.get("amount_usd")
        if amount and vendor_record:
            result = self._check_invoice_amount(float(amount), vendor_record)
            if result:
                facts["invoice_amount_analysis"] = result

        # 3. Acquisition timing — banking change before close?
        if vendor_record and email_chain:
            result = self._check_acquisition_timing(vendor_record, email_chain)
            if result:
                facts["acquisition_timing"] = result

        # 4. Email domain consistency
        if vendor_record and email_chain:
            result = self._check_domain_consistency(vendor_record, email_chain)
            if result:
                facts["email_domain_analysis"] = result

        if facts:
            logger.info(
                f"  ToolGate verified {len(facts)} fact(s): {list(facts.keys())}"
            )
        else:
            logger.info("  ToolGate: no verifiable facts extracted.")

        return facts

    # -------------------------------------------------------------------------
    # 1. Routing number lookup
    # -------------------------------------------------------------------------

    def _lookup_routing(self, routing_number: str) -> Optional[dict]:
        """
        Look up what financial institution a routing number belongs to.
        Uses the public routingnumbers.info API.
        """
        try:
            import httpx
            resp = httpx.get(
                ROUTING_API,
                params={"rn": routing_number},
                timeout=5.0,
            )
            data = resp.json()
            if data.get("code") == 200:
                institution = data.get("customer_name", "Unknown")
                logger.info(
                    f"  Routing {routing_number} → {institution}"
                )
                return {
                    "routing_number":   routing_number,
                    "institution_name": institution,
                    "source":           "routingnumbers.info",
                    "fact_type":        "SUBMITTED_DATA",
                }
            else:
                logger.warning(
                    f"  Routing lookup returned code {data.get('code')} "
                    f"for {routing_number}"
                )
        except Exception as e:
            logger.warning(f"  Routing lookup failed ({routing_number}): {e}")
        return None

    # -------------------------------------------------------------------------
    # 2. Invoice amount analysis
    # -------------------------------------------------------------------------

    def _check_invoice_amount(self, amount: float, vendor_record: dict) -> Optional[dict]:
        """
        Compute exact % deviation from the vendor's historical invoice range.
        Models currently estimate this; the governor computes it precisely.
        """
        try:
            history = vendor_record.get("invoice_history", [])
            known_range = vendor_record.get("typical_invoice_range", {})

            historical_amounts = [
                float(inv["amount"]) for inv in history
                if "amount" in inv
            ]

            if not historical_amounts and not known_range:
                return None

            result = {
                "submitted_amount": amount,
                "fact_type":        "SUBMITTED_DATA",
            }

            if historical_amounts:
                hist_mean = mean(historical_amounts)
                hist_min  = min(historical_amounts)
                hist_max  = max(historical_amounts)
                pct_vs_mean = ((amount - hist_mean) / hist_mean) * 100

                result.update({
                    "historical_mean":    round(hist_mean, 2),
                    "historical_min":     hist_min,
                    "historical_max":     hist_max,
                    "pct_deviation_mean": round(pct_vs_mean, 1),
                    "above_historical_max": amount > hist_max,
                    "sample_size":        len(historical_amounts),
                })

                if len(historical_amounts) >= 3:
                    hist_stdev = stdev(historical_amounts)
                    z_score    = (amount - hist_mean) / hist_stdev if hist_stdev else 0
                    result["z_score"] = round(z_score, 2)

            elif known_range:
                range_min = float(known_range.get("min", 0))
                range_max = float(known_range.get("max", 0))
                if range_max > 0:
                    pct_vs_max = ((amount - range_max) / range_max) * 100
                    result.update({
                        "stated_range_min":   range_min,
                        "stated_range_max":   range_max,
                        "pct_above_max":      round(pct_vs_max, 1),
                        "above_stated_range": amount > range_max,
                    })

            logger.info(
                f"  Invoice ${amount:,.2f} | "
                f"deviation={result.get('pct_deviation_mean', result.get('pct_above_max', 'N/A'))}%"
            )
            return result

        except Exception as e:
            logger.warning(f"  Invoice amount analysis failed: {e}")
        return None

    # -------------------------------------------------------------------------
    # 3. Acquisition timing check
    # -------------------------------------------------------------------------

    def _check_acquisition_timing(
        self, vendor_record: dict, email_chain: list
    ) -> Optional[dict]:
        """
        Determine whether a banking change request was made before the
        acquisition legally closed.

        If a vendor requests routing/account changes while their acquirer
        hasn't yet taken legal ownership, that is a process violation.
        Pre-close banking migrations are prohibited by most transaction agreements.
        """
        try:
            close_expected = vendor_record.get("acquisition_close_expected", "")
            acquirer       = vendor_record.get("acquirer_name", "")
            if not close_expected or not acquirer:
                return None

            # Parse "2026-Q2" → approximate close date (start of Q2 = April 1)
            close_date = self._parse_quarter(close_expected)
            if not close_date:
                return None

            # Find emails that mention banking changes
            banking_change_emails = []
            banking_keywords = [
                "routing", "account number", "remit", "banking", "wire",
                "payment details", "bank account", "treasury"
            ]
            for email in email_chain:
                body = email.get("body", "").lower()
                timestamp = email.get("timestamp", "")
                if any(kw in body for kw in banking_keywords) and timestamp:
                    try:
                        email_date = datetime.fromisoformat(
                            timestamp.replace("Z", "+00:00")
                        )
                        if email_date < close_date:
                            banking_change_emails.append({
                                "from":      email.get("from", ""),
                                "timestamp": timestamp,
                                "days_before_close": (close_date - email_date).days,
                            })
                    except ValueError:
                        pass

            result = {
                "acquirer":               acquirer,
                "acquisition_close_expected": close_expected,
                "close_date_parsed":      close_date.strftime("%Y-%m-%d"),
                "banking_change_before_close": len(banking_change_emails) > 0,
                "pre_close_banking_emails": banking_change_emails,
                "fact_type":              "SUBMITTED_DATA",
            }

            if banking_change_emails:
                logger.info(
                    f"  Acquisition timing: {len(banking_change_emails)} banking "
                    f"change email(s) sent before {close_expected} close"
                )
            else:
                logger.info(
                    f"  Acquisition timing: no pre-close banking changes detected"
                )

            return result

        except Exception as e:
            logger.warning(f"  Acquisition timing check failed: {e}")
        return None

    def _parse_quarter(self, s: str) -> Optional[datetime]:
        """
        Parse quarter strings like '2026-Q2' or 'Q2 2026' into the first
        day of that quarter (conservative: assumes close happens at start of Q).
        """
        m = re.search(r"(\d{4})[^\d]*[Qq](\d)", s)
        if not m:
            m = re.search(r"[Qq](\d)[^\d]*(\d{4})", s)
            if m:
                quarter, year = int(m.group(1)), int(m.group(2))
            else:
                return None
        else:
            year, quarter = int(m.group(1)), int(m.group(2))

        quarter_start_month = (quarter - 1) * 3 + 1
        try:
            return datetime(year, quarter_start_month, 1)
        except ValueError:
            return None

    # -------------------------------------------------------------------------
    # 4. Email domain consistency
    # -------------------------------------------------------------------------

    def _check_domain_consistency(
        self, vendor_record: dict, email_chain: list
    ) -> Optional[dict]:
        """
        Verify that every email in the chain originates from the vendor's
        registered domain. A domain switch mid-chain is a BEC red flag.
        """
        try:
            vendor_email = vendor_record.get("vendor_email", "")
            if not vendor_email or "@" not in vendor_email:
                return None

            vendor_domain = vendor_email.split("@")[-1].lower()
            analysis      = []
            inconsistent  = []

            for email in email_chain:
                from_addr = email.get("from", "")
                if "@" not in from_addr:
                    continue
                from_domain = from_addr.split("@")[-1].lower()
                match       = (from_domain == vendor_domain)
                entry = {
                    "from":          from_addr,
                    "domain":        from_domain,
                    "matches_vendor": match,
                    "timestamp":     email.get("timestamp", ""),
                }
                analysis.append(entry)
                if not match:
                    inconsistent.append(entry)

            result = {
                "vendor_domain":         vendor_domain,
                "emails_analyzed":       len(analysis),
                "all_domains_match":     len(inconsistent) == 0,
                "domain_inconsistencies": inconsistent,
                "fact_type":             "SUBMITTED_DATA",
            }

            if inconsistent:
                logger.info(
                    f"  Domain check: {len(inconsistent)} email(s) from "
                    f"unexpected domain (expected {vendor_domain})"
                )
            else:
                logger.info(
                    f"  Domain check: all {len(analysis)} emails from {vendor_domain}"
                )

            return result

        except Exception as e:
            logger.warning(f"  Domain consistency check failed: {e}")
        return None
