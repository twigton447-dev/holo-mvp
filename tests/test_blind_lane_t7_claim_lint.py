"""T7 - public claim-scope lint.

Falsifies: "no rate claim will be derived from the canary."
Passing validates nothing; this lint can only block premature claims.

NOTE: test_canary_spec_is_preregistered is EXPECTED RED until the blind-gate
spec gains a stopping rule and a pre-registered full-run size. Do not delete
or weaken it to get green - update the spec.
"""

from blind_lane_suite.claim_lint import lint_canary_spec, lint_public_surfaces, lint_text


def test_lint_detects_planted_violation():
    """Detector validation: a canary-scale ratio in a blind-lane sentence
    MUST error."""
    planted = "The blind-gate canary scored 19/20 on its first pass."
    result = lint_text(planted, source="planted")
    assert result["errors"], "claim lint failed to flag a planted canary-scale blind-lane ratio - lint broken"


def test_lint_ignores_unrelated_ratios():
    ok = "The governed lane completed 174/174 packets under the wave protocol."
    result = lint_text(ok, source="planted")
    assert not result["errors"]


def test_no_canary_scale_ratios_in_blind_context_on_public_surfaces():
    report = lint_public_surfaces()
    assert report["surfaces_scanned"], "no public surfaces found - nothing was linted"
    assert not report["errors"], (
        "PREMATURE CLAIM: canary-scale ratio in blind-lane sentence on a public surface: "
        f"{report['errors'][:5]}"
    )
    # Warnings are for human review, not failure; surface them in -rA output.
    if report["warnings"]:
        print(f"T7 WARNINGS (human review required): {report['warnings'][:10]}")


def test_canary_spec_is_preregistered():
    """EXPECTED RED until the spec adds: (a) a pre-registered stopping rule,
    (b) a pre-registered full-run size. Red here means the scope boundary
    exists only as intention."""
    result = lint_canary_spec()
    assert result["present"], "blind-gate replication spec file missing"
    assert not result["missing"], (
        f"CANARY SPEC NOT PRE-REGISTERED: missing {result['missing']} - "
        "add a stopping rule and full-run size to the spec (do not weaken this test)"
    )
