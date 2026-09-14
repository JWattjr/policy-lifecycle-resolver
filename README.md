# Policy Lifecycle Resolver

Policy Lifecycle Resolver is a standalone GenLayer Intelligent Contract for
resolving a bill, regulation, governance proposal, or public policy against a
frozen lifecycle taxonomy and required-clause vector. The reusable primitive
stores a compact, auditable observation; it is not a legal-advice service and
does not custody funds.

## Why GenLayer is needed

The evidence is external, public, and potentially incomplete or contradictory.
The leader and validators independently fetch the same frozen HTTPS sources and
interpret them into a bounded observation. GenLayer consensus accepts the
canonical result only when the independent assessments agree. A conventional
contract could store a caller-supplied stage, but it could not independently
interpret public records at the state transition.

## Frozen historical-snapshot model

This release intentionally implements one historical snapshot, not continuous
tracking. The constructor freezes:

- lifecycle stages with explicit semantic kinds: `INTRODUCED`, `PASSED`,
  `SIGNED`, `PUBLISHED`, `EFFECTIVE`, `REJECTED`, or `WITHDRAWN`;
- required clauses and their IDs;
- public HTTPS source URLs;
- `as_of`, the historical observation timestamp;
- `cutoff`, the earliest assessment timestamp; and
- `max_wait`, the deterministic timeout, plus an exact temporal-rule object.

`as_of` is passed unchanged to every leader and validator prompt. A stage event
must have an explicitly supported calendar date no later than `as_of`. A later
publication may report an earlier event only when its content explicitly gives
that event date. An undated current-status page is insufficient. A future
effective date does not make an `EFFECTIVE` snapshot; the contract can instead
resolve a `SIGNED` or `PUBLISHED` stage while retaining the future date. Passage,
signature, publication, and effectiveness are distinct kinds; no country’s
legislative sequence is treated as universal. Amendments, partial commencement,
multiple versions, and conflicting records are left unresolved or contested by
the frozen rules.

The contract lifecycle is `OPEN → WAIT/CONTESTED/RESOLVED/VOID`. `WAIT` and
`CONTESTED` are retryable. `RESOLVED` and `VOID` are terminal contract states;
the stored stage’s `terminal` flag describes the policy stage and may be false
for a terminal resolved snapshot. Terminal calls are idempotent and do not
increase `attempts`. Assessment is permissionless.

## Consensus and evidence boundary

The model observation must contain exactly eight keys:
`evidence_state`, `stage_id`, `clause_results`, `event_date`,
`effective_date`, `event_date_supported`, `effective_date_supported`, and
`complexity`. The stored result has exactly fourteen bounded, typed fields,
including policy identity, specification, temporal rule ID, `as_of`, and the
assessment time. Extra or missing keys, invalid stages or clause IDs, malformed
dates, bool/int confusion, unsupported dates, and out-of-range coverage are
rejected. Both leader and validator results are canonicalized and validated
again before storage; every state-affecting field is compared.

Non-200, empty, malformed, or transport-failed sources are marked unavailable;
all unusable sources deterministically produce `WAIT / SOURCE_UNAVAILABLE`.
Bodies over 6,000 bytes are marked `SOURCE_TRUNCATED` in the prompt. Partial or
truncated material is not automatically a negative fact: it may resolve only if
validators agree that the remaining content supports every required claim;
otherwise clauses remain `UNKNOWN` and the result stays `WAIT`.

Source text is untrusted data and prompts explicitly reject embedded commands.
That is a boundary and audit aid, not a guarantee of real-model prompt-injection
resistance. HTTPS and hostname checks do not prove publisher authority or remove
all network attacks.

## Constructor and public API

Constructor parameters are `policy_id, jurisdiction, stages, clauses, sources,
as_of, cutoff, max_wait, temporal_rules, spec_id`. Public methods are
`resolve()` and `get_state()`.

The following real-source example freezes OMB’s final Guidance for Federal
Financial Assistance (Federal Register Doc. 2024-07496):

~~~json
{
  "policy_id": "omb-guidance-2024-07496",
  "jurisdiction": "United States federal administrative guidance",
  "stages": [
    {"id":"PUBLISHED","label":"Published","kind":"PUBLISHED","terminal":false},
    {"id":"EFFECTIVE","label":"Effective","kind":"EFFECTIVE","terminal":false}
  ],
  "clauses": [
    {"id":"document","text":"The official record identifies Federal Register Doc No. 2024-07496."},
    {"id":"publication_date","text":"The official record states publication on 2024-04-22."},
    {"id":"effective_date","text":"The official record states an effective date of 2024-10-01."}
  ],
  "sources": [
    "https://www.govinfo.gov/content/pkg/FR-2024-04-22/html/2024-07496.htm",
    "https://www.federalregister.gov/documents/2024/04/22/2024-07496/guidance-for-federal-financial-assistance"
  ],
  "as_of": "2024-06-01T00:00:00Z",
  "cutoff": "2026-01-01T00:00:00Z",
  "max_wait": "2030-01-01T00:00:00Z",
  "temporal_rules": {
    "id":"historical-snapshot-v1",
    "model":"HISTORICAL_SNAPSHOT",
    "event_date_policy":"EXPLICIT_EVENT_DATE_REQUIRED",
    "later_publication_policy":"ALLOW_IF_EXPLICIT_EVENT_DATE",
    "undated_policy":"UNRESOLVED",
    "future_effective_policy":"NOT_EFFECTIVE_AT_AS_OF",
    "complexity_policy":"UNSUPPORTED_UNRESOLVED",
    "conflict_policy":"CONTESTED"
  },
  "spec_id": "omb-guidance-2024-07496-v1"
}
~~~

The companion post-effective snapshot uses the same sources and rules with
`as_of=2024-10-02T00:00:00Z` and the `EFFECTIVE` stage. The two snapshots are
the intended temporal demonstration; the model supplies dates from the public
records rather than from contract storage.

## Checks and release evidence

~~~powershell
$env:PYTHONIOENCODING = "utf-8"
genvm-lint check contracts/PolicyLifecycleResolver.py
genvm-lint schema contracts/PolicyLifecycleResolver.py
python -m pytest tests/test_policy_lifecycle.py tests/test_nondet_storage.py -q
~~~

The direct suite is offline and deterministic; it cannot prove real-model
prompt-injection resistance or every live network outcome. The current
StudioNet release manifest and receipts are recorded in
`deployments/studionet.json` after fresh deployment. The earlier StudioNet and
Bradbury records are retained as explicitly historical pre-hardening evidence.
