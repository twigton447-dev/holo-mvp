from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "scripts" / "holochat_reconcile_capsules.py").read_text(encoding="utf-8")


def test_reconciliation_tool_defaults_to_metadata_only_dry_run():
    assert '"mode": "dry_run"' in SCRIPT
    assert 'parser.add_argument("--apply", action="store_true"' in SCRIPT
    assert 'expected_confirmation = f"MERGE:{args.source}:{args.target}"' in SCRIPT
    assert 'holo_preflight_capsule_identity_reconciliation' in SCRIPT
    assert 'client.rpc(' in SCRIPT
    assert 'holo_reconcile_capsule_identity' in SCRIPT
    assert 'target must be the original email-only HoloBrain' in SCRIPT
    assert 'move all eligible source records atomically into the target HoloBrain' in SCRIPT
    assert 'no message, memory, artifact, or connector content is printed by this tool' in SCRIPT
    assert 'no user data is deleted' in SCRIPT


def test_reconciliation_tool_requires_explicit_auth_maintenance_controls():
    assert '--begin-maintenance' in SCRIPT
    assert '--end-maintenance' in SCRIPT
    assert 'PAUSE_SIGNINS' in SCRIPT
    assert 'RESUME_SIGNINS' in SCRIPT
    assert 'holo_set_identity_maintenance' in SCRIPT
