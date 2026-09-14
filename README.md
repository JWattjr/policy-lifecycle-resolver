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

The exact StudioNet publication, deployment, finality, source-identity, and
read-back procedure is in [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md).

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

Structured official records may expose explicit dates as `publication_date`,
`effective_on`, or `effective_date`; the prompt maps those fields to the frozen
publication/effective stage kinds. That mapping is an interpretation aid, not a
publisher-authentication claim.

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
  "policy_id": "omb-guidance-2024-07496-before-effective-v2",
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
    "https://www.federalregister.gov/api/v1/documents/2024-07496.json?fields%5B%5D=document_number&fields%5B%5D=effective_on&fields%5B%5D=publication_date&fields%5B%5D=title&fields%5B%5D=dates",
    "https://www.federalregister.gov/api/v1/documents/2024-07496.json?fields%5B%5D=document_number&fields%5B%5D=effective_on&fields%5B%5D=publication_date&fields%5B%5D=title&fields%5B%5D=dates&fields%5B%5D=abstract"
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
  "spec_id": "omb-guidance-2024-07496-before-effective-v2"
}
~~~

The companion post-effective snapshot uses the same sources and rules with
`policy_id=omb-guidance-2024-07496-effective-after-v2`,
`as_of=2024-10-02T00:00:00Z`, and the `EFFECTIVE` stage. The live StudioNet
attempts below conservatively returned `WAIT/EVIDENCE_PROVISIONAL`; they do not
prove a terminal two-snapshot demonstration. The direct tests cover the
successful canonical paths with mocks, while the public records remain available
for an independently reviewed retry.

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

## Current StudioNet evidence (2026-09-14)

The deployed source commit used by the two corrected deployments is
`213ad01` (the configured remote's `main` ref resolves to this commit).
Read-back with `genlayer code` matched the normalized source SHA-256
`c622adbe196a7e3ee9e74ab5e1c0cbb2cefd68792420ef87bcd54e6542d93e2e`.
The GitHub web repository and commit URLs currently return anonymous HTTP 404,
so public source hosting is not yet verified for Portal use.

- Published-before-effective snapshot: [contract](https://explorer-studio.genlayer.com/address/0xca2d559b98D7B8f9A5d2E33EA44Ae396854b67cE), [deployment receipt](https://explorer-studio.genlayer.com/transactions/0x2d29f1b1004915ab42b9cc110c59b1e65c5a1a3b16c1d3ee40d1f9302c5aa3b2), and [resolve receipt](https://explorer-studio.genlayer.com/transactions/0x0d341bdec867e4f04aae166bc8efa59171bd472e98acabd0481344399f5b32c1). Both receipts are `FINALIZED` with leader `SUCCESS`; protocol consensus is `MAJORITY_AGREE`. `get_state()` is `WAIT/EVIDENCE_PROVISIONAL`, `attempts=1`, not terminal.
- Effective-after snapshot: [contract](https://explorer-studio.genlayer.com/address/0xcceCB3b68fb13Af8532fd9e767b29B4608109C4d), [deployment receipt](https://explorer-studio.genlayer.com/transactions/0x1a2a5e29b9c7ad173b255446896b0eb3c8e6a3952738209235edfe411249bdfd), and [resolve receipt](https://explorer-studio.genlayer.com/transactions/0x6b1a394cade4bfa8b1670ee478d22884c39b960f52de5d06df7efa2e688b4e41). Both receipts are `FINALIZED` with leader `SUCCESS`; protocol consensus is `MAJORITY_AGREE`. `get_state()` is `WAIT/EVIDENCE_PROVISIONAL`, `attempts=1`, not terminal.

The exact constructor arguments, vote arrays, state read-backs, source sizes,
and the initial disagreement probe are in `deployments/studionet.json`. The
older pre-hardening StudioNet record is preserved as
`deployments/studionet-historical-2026-08-12.json`; `deployments/bradbury.json`
is historical and is not current submission evidence. The working tree has an
uncommitted prompt clarification (not included in the deployed source), so this
candidate is not submit-ready until that change is intentionally published and
deployed, and a terminal live resolution is verified.
