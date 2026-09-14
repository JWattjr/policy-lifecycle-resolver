import json
import os
from pathlib import Path

import pytest


MANIFEST = Path("deployments/studionet.json")
EXPECTED_SNAPSHOTS = {
    "published_before_effective": {"state": "RESOLVED", "stage_id": "PUBLISHED"},
    "effective_after_cutoff": {"state": "RESOLVED", "stage_id": "EFFECTIVE"},
}


def test_studionet_manifest_records_current_hardened_snapshots():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["record_status"] == "CURRENT_HARDENED_STUDIONET"
    assert data["network"] == "studionet"
    assert data["runner"].startswith("py-genlayer:")
    assert data["source_commit"] != "REPLACE_WITH_RELEASE_COMMIT"
    assert data["source_identity_verified"] is True
    assert set(data["snapshots"]) == set(EXPECTED_SNAPSHOTS)
    for snapshot_name, expected in EXPECTED_SNAPSHOTS.items():
        snapshot = data["snapshots"][snapshot_name]
        assert snapshot["deployment_status"] == "FINALIZED"
        assert snapshot["deployment_execution"] in ("SUCCESS", "FINISHED_WITH_RETURN")
        assert snapshot["resolution_status"] == "FINALIZED"
        assert snapshot["resolution_execution"] in ("SUCCESS", "FINISHED_WITH_RETURN")
        assert snapshot["state_verified"] is True
        for field, value in expected.items():
            assert snapshot["resolution_state"][field] == value


@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("GENLAYER_INTEGRATION") != "1", reason="set GENLAYER_INTEGRATION=1 for a live StudioNet read")
def test_live_studionet_states_match_manifest():
    from genlayer_py import create_client
    from genlayer_py.chains import studionet

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    client = create_client(chain=studionet, endpoint=studionet.rpc_urls["default"]["http"][0])
    for snapshot_name, expected in EXPECTED_SNAPSHOTS.items():
        snapshot = data["snapshots"][snapshot_name]
        state = client.read_contract(address=snapshot["contract_address"], function_name="get_state", args=[])
        for field, value in expected.items():
            assert state[field] == value
