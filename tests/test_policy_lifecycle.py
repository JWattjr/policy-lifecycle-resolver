import json

import pytest


DEFAULT_STAGES = [
    {"id": "INTRODUCED", "label": "Introduced", "kind": "INTRODUCED", "terminal": False},
    {"id": "PASSED", "label": "Passed or adopted", "kind": "PASSED", "terminal": False},
    {"id": "SIGNED", "label": "Signed", "kind": "SIGNED", "terminal": False},
    {"id": "PUBLISHED", "label": "Published", "kind": "PUBLISHED", "terminal": False},
    {"id": "EFFECTIVE", "label": "Effective", "kind": "EFFECTIVE", "terminal": False},
    {"id": "REJECTED", "label": "Rejected", "kind": "REJECTED", "terminal": True},
    {"id": "WITHDRAWN", "label": "Withdrawn", "kind": "WITHDRAWN", "terminal": True},
]
DEFAULT_CLAUSES = [
    {"id": "law_number", "text": "The official record identifies the measure as Public Law 117-58."},
    {"id": "approval_date", "text": "The official record gives an approval date of 2021-11-15."},
]
DEFAULT_RULES = {
    "id": "historical-snapshot-v1",
    "model": "HISTORICAL_SNAPSHOT",
    "event_date_policy": "EXPLICIT_EVENT_DATE_REQUIRED",
    "later_publication_policy": "ALLOW_IF_EXPLICIT_EVENT_DATE",
    "undated_policy": "UNRESOLVED",
    "future_effective_policy": "NOT_EFFECTIVE_AT_AS_OF",
    "complexity_policy": "UNSUPPORTED_UNRESOLVED",
    "conflict_policy": "CONTESTED",
}


def _args(
    stages=None,
    clauses=None,
    sources=None,
    as_of="2021-11-16T00:00:00Z",
    cutoff="2030-01-01T00:00:00Z",
    max_wait="2030-02-01T00:00:00Z",
    rules=None,
):
    return (
        "us-pl-117-58",
        "United States federal law",
        json.dumps(DEFAULT_STAGES if stages is None else stages),
        json.dumps(DEFAULT_CLAUSES if clauses is None else clauses),
        json.dumps(["https://official.example.org/policy"] if sources is None else sources),
        as_of,
        cutoff,
        max_wait,
        json.dumps(DEFAULT_RULES if rules is None else rules),
        "policy-lifecycle-pl117-58-v2",
    )


def _deploy(direct_deploy, **kwargs):
    return direct_deploy("contracts/PolicyLifecycleResolver.py", *_args(**kwargs))


def _observation(
    stage="SIGNED",
    clause_results=None,
    event_date="2021-11-15",
    effective_date="2021-12-01",
    event_date_supported=True,
    effective_date_supported=True,
    evidence_state="FINAL",
    complexity="NONE",
):
    return {
        "evidence_state": evidence_state,
        "stage_id": stage,
        "clause_results": {"law_number": "SATISFIED", "approval_date": "SATISFIED"}
        if clause_results is None
        else clause_results,
        "event_date": event_date,
        "effective_date": effective_date,
        "event_date_supported": event_date_supported,
        "effective_date_supported": effective_date_supported,
        "complexity": complexity,
    }


def _mock_final(direct_vm, result, body="official record explicitly dated 2021-11-15"):
    direct_vm.mock_web(r".*", {"status": 200, "body": body})
    direct_vm.mock_llm(r".*", json.dumps(result))


def test_historical_signed_snapshot_preserves_future_effective_date(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, _observation())
    result = contract.resolve()
    assert result["state"] == "RESOLVED"
    assert result["stage_id"] == "SIGNED"
    assert result["terminal"] is False
    assert result["event_date"] == "2021-11-15"
    assert result["effective_date"] == "2021-12-01"
    assert result["as_of"] == "2021-11-16T00:00:00+00:00"
    assert result["assessment_time"] == "2030-01-15T00:00:00+00:00"
    assert result["temporal_rule_id"] == "historical-snapshot-v1"
    assert direct_vm.run_validator()
    stored = json.loads(contract.get_state()["last_result"])
    assert set(stored) == {
        "state",
        "stage_id",
        "terminal",
        "clause_results",
        "event_date",
        "effective_date",
        "reason_code",
        "source_coverage",
        "policy_id",
        "jurisdiction",
        "spec_id",
        "temporal_rule_id",
        "as_of",
        "assessment_time",
    }


def test_validator_rejects_every_consensus_field_mutation_and_extra_key(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, _observation())
    accepted = contract.resolve()
    mutations = [
        {**accepted, "state": "WAIT"},
        {**accepted, "stage_id": "PASSED"},
        {**accepted, "terminal": True},
        {**accepted, "clause_results": {"law_number": "UNSATISFIED", "approval_date": "SATISFIED"}},
        {**accepted, "event_date": "2021-11-16"},
        {**accepted, "effective_date": "2022-01-01"},
        {**accepted, "reason_code": "TEMPORAL_INSUFFICIENT"},
        {**accepted, "source_coverage": 0},
        {**accepted, "source_coverage": True},
        {**accepted, "policy_id": "other-policy"},
        {**accepted, "jurisdiction": "other-jurisdiction"},
        {**accepted, "spec_id": "other-spec"},
        {**accepted, "temporal_rule_id": "other-rules"},
        {**accepted, "as_of": "2021-11-17T00:00:00+00:00"},
        {**accepted, "assessment_time": "2030-01-16T00:00:00+00:00"},
        {**accepted, "unexpected": "not stored"},
        {key: value for key, value in accepted.items() if key != "reason_code"},
        ["not", "a", "result"],
    ]
    for mutation in mutations:
        assert direct_vm.run_validator(leader_result=mutation) is False


@pytest.mark.parametrize(
    "payload",
    [
        {**_observation(), "extra": True},
        {key: value for key, value in _observation().items() if key != "stage_id"},
        {**_observation(), "evidence_state": True},
        {**_observation(), "stage_id": "INVENTED"},
        {**_observation(), "clause_results": {"law_number": "SATISFIED"}},
        {**_observation(), "clause_results": {"law_number": True, "approval_date": "SATISFIED"}},
        {**_observation(), "event_date": "2021-11-15T00:00:00Z"},
        {**_observation(), "event_date_supported": 1},
        {**_observation(), "effective_date_supported": 0},
        {**_observation(), "complexity": "UNSUPPORTED"},
        [],
        "not-json",
    ],
)
def test_malformed_model_observations_fail_closed(direct_vm, direct_deploy, payload):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r".*", {"status": 200, "body": "evidence"})
    direct_vm.mock_llm(r".*", payload if isinstance(payload, str) else json.dumps(payload))
    with direct_vm.expect_revert():
        contract.resolve()
    assert contract.get_state()["attempts"] == 0


def test_validator_rejects_malformed_wrappers(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, _observation())
    accepted = contract.resolve()
    for wrapper in (None, [], "not-json", {"calldata": accepted}):
        assert direct_vm.run_validator(leader_result=wrapper) is False


@pytest.mark.parametrize(
    "kwargs,message",
    [
        ({"as_of": "2021-11-16T00:00:00"}, "timezone offset"),
        ({"cutoff": "2030-01-01T00:00:00"}, "timezone offset"),
        ({"max_wait": "2030-02-01T00:00:00"}, "timezone offset"),
        ({"cutoff": "2021-11-15T23:59:59Z"}, "at or after as_of"),
        ({"max_wait": "2030-01-01T00:00:00Z"}, "after cutoff"),
    ],
)
def test_constructor_rejects_temporal_timestamp_errors(direct_vm, direct_deploy, kwargs, message):
    with direct_vm.expect_revert(message):
        _deploy(direct_deploy, **kwargs)


@pytest.mark.parametrize(
    "stages,message",
    [
        ([{"id": "SIGNED", "label": "Signed", "terminal": False}], "exactly id, label, kind, terminal"),
        ([{"id": "SIGNED", "label": "Signed", "kind": "SIGNED", "terminal": 1}], "terminal must be boolean"),
        ([{"id": "SIGNED", "label": "Signed", "kind": "OTHER", "terminal": False}], "unsupported"),
        ([
            {"id": "A", "label": "One", "kind": "SIGNED", "terminal": False},
            {"id": "A", "label": "Two", "kind": "PASSED", "terminal": False},
        ], "stage IDs must be unique"),
        ([{"id": "WITHDRAWN", "label": "Withdrawn", "kind": "WITHDRAWN", "terminal": False}], "must be terminal"),
    ],
)
def test_constructor_rejects_unsafe_stage_shapes(direct_vm, direct_deploy, stages, message):
    with direct_vm.expect_revert(message):
        _deploy(direct_deploy, stages=stages)


@pytest.mark.parametrize(
    "kwargs,message",
    [
        ({"clauses": [{"id": "x", "text": "x", "extra": True}]}, "exactly id and text"),
        ({"clauses": [{"id": "x", "text": "x"}, {"id": "x", "text": "y"}]}, "clause IDs must be unique"),
        ({"rules": {**DEFAULT_RULES, "extra": "x"}}, "exactly the frozen rule schema"),
        ({"rules": {**DEFAULT_RULES, "model": "CURRENT_STATE"}}, "unsupported temporal rule"),
    ],
)
def test_constructor_rejects_unsafe_clause_and_rule_shapes(direct_vm, direct_deploy, kwargs, message):
    with direct_vm.expect_revert(message):
        _deploy(direct_deploy, **kwargs)


@pytest.mark.parametrize(
    "sources,message",
    [
        (["http://official.example.org/policy"], "HTTPS"),
        (["https://127.0.0.1/policy"], "publicly reachable"),
        (["https://official.example.org:8443/policy"], "default HTTPS port"),
        (["https://official.example.org/policy", "https://official.example.org/policy"], "source URLs must be unique"),
    ],
)
def test_constructor_rejects_unsafe_or_duplicate_sources(direct_vm, direct_deploy, sources, message):
    with direct_vm.expect_revert(message):
        _deploy(direct_deploy, sources=sources)


def test_signed_stage_is_distinct_from_effective_stage_at_snapshot(direct_vm, direct_deploy):
    stages = [
        {"id": "SIGNED", "label": "Signed", "kind": "SIGNED", "terminal": False},
        {"id": "EFFECTIVE", "label": "Effective", "kind": "EFFECTIVE", "terminal": False},
    ]
    signed = _deploy(direct_deploy, stages=stages)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, _observation(stage="SIGNED"))
    assert signed.resolve()["state"] == "RESOLVED"
    assert signed.get_state()["stage_id"] == "SIGNED"


def test_effective_stage_resolves_only_after_effective_date(direct_vm, direct_deploy):
    stages = [{"id": "EFFECTIVE", "label": "Effective", "kind": "EFFECTIVE", "terminal": False}]
    contract = _deploy(direct_deploy, stages=stages, as_of="2022-01-01T00:00:00Z")
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, _observation(stage="EFFECTIVE"))
    result = contract.resolve()
    assert result["state"] == "RESOLVED"
    assert result["stage_id"] == "EFFECTIVE"
    assert result["effective_date"] == "2021-12-01"


def test_future_effectiveness_cannot_resolve_effective_stage(direct_vm, direct_deploy):
    stages = [{"id": "EFFECTIVE", "label": "Effective", "kind": "EFFECTIVE", "terminal": False}]
    contract = _deploy(direct_deploy, stages=stages)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, _observation(stage="EFFECTIVE", effective_date="2021-12-01"))
    result = contract.resolve()
    assert result["state"] == "WAIT"
    assert result["reason_code"] == "TEMPORAL_INSUFFICIENT"
    assert result["stage_id"] == ""


def test_event_after_as_of_is_unresolved(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, _observation(event_date="2021-11-17"))
    result = contract.resolve()
    assert result["state"] == "WAIT"
    assert result["reason_code"] == "TEMPORAL_INSUFFICIENT"


def test_later_publication_can_support_explicit_earlier_event_date(direct_vm, direct_deploy):
    stages = [{"id": "PUBLISHED", "label": "Published", "kind": "PUBLISHED", "terminal": False}]
    contract = _deploy(direct_deploy, stages=stages)
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(
        r".*",
        {"status": 200, "body": "Published 2022-01-10; this official page expressly records the event on 2021-11-15."},
    )
    direct_vm.mock_llm(r"ALLOW_IF_EXPLICIT_EVENT_DATE", json.dumps(_observation(stage="PUBLISHED")))
    result = contract.resolve()
    assert result["state"] == "RESOLVED"
    assert result["event_date"] == "2021-11-15"


def test_undated_current_status_page_stays_unresolved(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(
        direct_vm,
        _observation(event_date="", effective_date="", event_date_supported=False, effective_date_supported=False),
        body="Current status: signed. No event date is shown.",
    )
    result = contract.resolve()
    assert result["state"] == "WAIT"
    assert result["reason_code"] == "TEMPORAL_INSUFFICIENT"


def test_unknown_clause_never_becomes_unsatisfied(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, _observation(clause_results={"law_number": "UNKNOWN", "approval_date": "SATISFIED"}))
    result = contract.resolve()
    assert result["state"] == "WAIT"
    assert result["reason_code"] == "CLAUSE_UNKNOWN"
    assert set(result["clause_results"].values()) == {"UNKNOWN"}


def test_all_source_outage_and_empty_source_are_retryable(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy, sources=["https://a.example.org/policy", "https://b.example.org/policy"])
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r"a\.example\.org", {"status": 503, "body": "offline"})
    direct_vm.mock_web(r"b\.example\.org", {"status": 200, "body": ""})
    result = contract.resolve()
    assert result["state"] == "WAIT"
    assert result["reason_code"] == "SOURCE_UNAVAILABLE"
    assert result["source_coverage"] == 0


def test_truncated_evidence_is_marked_and_can_only_resolve_if_model_has_support(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r".*", {"status": 200, "body": "x" * 6001})
    direct_vm.mock_llm(r"SOURCE_TRUNCATED", json.dumps(_observation(clause_results={"law_number": "UNKNOWN", "approval_date": "UNKNOWN"})))
    result = contract.resolve()
    assert result["state"] == "WAIT"
    assert result["reason_code"] == "CLAUSE_UNKNOWN"


@pytest.mark.parametrize(
    "evidence_state,expected_state,expected_reason",
    [
        ("PROVISIONAL", "WAIT", "EVIDENCE_PROVISIONAL"),
        ("CONFLICT", "CONTESTED", "AUTHORITATIVE_CONFLICT"),
        ("CANCELLED", "VOID", "EVENT_CANCELLED"),
    ],
)
def test_failure_dispositions_are_explicit_and_bounded(direct_vm, direct_deploy, evidence_state, expected_state, expected_reason):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, _observation(evidence_state=evidence_state))
    result = contract.resolve()
    assert result["state"] == expected_state
    assert result["reason_code"] == expected_reason
    assert result["stage_id"] == ""
    assert result["clause_results"] == {"approval_date": "UNKNOWN", "law_number": "UNKNOWN"}


def test_unsupported_complexity_is_contested_not_guessed(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, _observation(complexity="PARTIAL_COMMENCEMENT"))
    result = contract.resolve()
    assert result["state"] == "CONTESTED"
    assert result["reason_code"] == "UNSUPPORTED_COMPLEXITY"


def test_cutoff_and_max_wait_boundaries_are_deterministic(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy, cutoff="2030-01-15T00:00:00Z", max_wait="2030-02-01T00:00:00Z")
    direct_vm.warp("2030-01-14T23:59:59Z")
    before = contract.resolve()
    assert before["state"] == "WAIT"
    assert before["reason_code"] == "BEFORE_CUTOFF"
    assert set(before["clause_results"].values()) == {"UNKNOWN"}

    direct_vm.clear_mocks()
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, _observation())
    assert contract.resolve()["state"] == "RESOLVED"


def test_exact_max_wait_void_is_terminal_and_idempotent(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-02-01T00:00:00Z")
    expired = contract.resolve()
    assert expired["state"] == "VOID"
    assert expired["reason_code"] == "MAX_WAIT_EXPIRED"
    attempts = contract.get_state()["attempts"]
    state_before = contract.get_state()
    assert contract.resolve() == state_before
    assert contract.get_state()["attempts"] == attempts


def test_resolved_snapshot_is_terminal_and_replay_safe(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, _observation())
    first = contract.resolve()
    state_before = contract.get_state()
    direct_vm.clear_mocks()
    direct_vm.warp("2040-01-15T00:00:00Z")
    replay = contract.resolve()
    assert replay == state_before
    assert contract.get_state() == state_before
    assert first["as_of"] == "2021-11-16T00:00:00+00:00"


def test_nondeterministic_prompt_contains_frozen_temporal_context(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r".*", {"status": 200, "body": "dated official record"})
    direct_vm.mock_llm(r"(?s)as_of=2021-11-16T00:00:00\+00:00.*assessment_time=2030-01-15T00:00:00\+00:00", json.dumps(_observation()))
    assert contract.resolve()["state"] == "RESOLVED"
