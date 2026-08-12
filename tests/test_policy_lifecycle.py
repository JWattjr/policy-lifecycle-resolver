import json


def _deploy(direct_deploy):
    return direct_deploy(
        "contracts/PolicyLifecycleResolver.py",
        "bill-42",
        "Example Legislature",
        json.dumps([
            {"id": "INTRODUCED", "label": "Introduced", "terminal": False},
            {"id": "ENACTED", "label": "Enacted", "terminal": True},
        ]),
        json.dumps([{"id": "budget", "text": "The final law contains the budget clause"}]),
        json.dumps(["https://official.example.org/bill-42"]),
        "2030-01-01T00:00:00Z",
        "2030-02-01T00:00:00Z",
        "policy-v1",
    )


def _mock_page(vm):
    vm.mock_web(r".*", {"status": 200, "body": "official record"})


def test_resolves_allowlisted_stage_and_clause_vector(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_page(direct_vm)
    direct_vm.mock_llm(r".*", json.dumps({
        "evidence_state": "FINAL", "stage_id": "ENACTED",
        "clause_results": {"budget": "SATISFIED"}, "effective_date": "2030-01-10",
    }))
    result = contract.resolve()
    assert result["state"] == "RESOLVED"
    assert result["stage_id"] == "ENACTED"
    assert direct_vm.run_validator()
    assert not direct_vm.run_validator(leader_result={
        "state": "RESOLVED", "stage_id": "INTRODUCED", "terminal": False,
        "clause_results": {"budget": "SATISFIED"}, "effective_date": "2030-01-10",
        "reason_code": "EVIDENCE_FINAL", "source_coverage": 1,
    })


def test_source_outage_stays_retryable(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r".*", {"status": 503, "body": "offline"})
    assert contract.resolve()["state"] == "WAIT"


def test_max_wait_voids_without_evidence(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-02-01T00:00:00Z")
    assert contract.resolve()["reason_code"] == "MAX_WAIT_EXPIRED"
