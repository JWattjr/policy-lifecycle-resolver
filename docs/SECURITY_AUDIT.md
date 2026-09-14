# Security and consensus audit: PolicyLifecycleResolver

Audit scope: `contracts/PolicyLifecycleResolver.py`
Review date: 2026-09-14
Status: hardened release candidate; live proof is recorded only after the fresh
StudioNet deployment described in `deployments/studionet.json`.

## Decision boundary

The release uses one explicit `HISTORICAL_SNAPSHOT` model. `as_of` is the
historical observation time, `cutoff` is the earliest assessment time, and
`max_wait` is the deterministic void boundary. The exact `as_of`, assessment
time, policy ID, jurisdiction, spec ID, and temporal-rule ID are captured before
nondeterministic execution and are echoed into the canonical result.

The model observation has exactly eight keys:
`evidence_state`, `stage_id`, `clause_results`, `event_date`,
`effective_date`, `event_date_supported`, `effective_date_supported`, and
`complexity`. The stored consensus result has exactly fourteen keys. Exact key
sets, types, enum values, date syntax, clause IDs, stage IDs, coverage bounds,
stage/date relationships, and state/reason relationships are checked for the
leader, the independent validator, and the accepted value before any storage
write. Canonical dictionaries, not raw model objects, are compared.

Validators independently re-fetch the frozen URLs. A source outage, empty or
malformed body, non-200 response, and transport exception cannot be silently
converted into a negative fact. Bodies over 6,000 bytes are labeled
`SOURCE_TRUNCATED`; partial material can resolve only if the validators agree it
still supports every required claim. Unsupported amendments, partial
commencement, or multiple versions are `CONTESTED / UNSUPPORTED_COMPLEXITY`.

## Findings and remediations

| ID | Severity | Finding | Remediation |
| --- | --- | --- | --- |
| PL-01 | High | The prior contract called its earliest assessment cutoff a historical observation cutoff. | Added explicit frozen `as_of`, passed it into every assessment, and rejected unsupported or post-`as_of` event claims. |
| PL-02 | High | Leader output lacked an exact bounded schema and could carry bool/int or extra-key ambiguity. | Added exact eight-key model schema, exact fourteen-key canonical result, strict types, context binding, and pre-storage revalidation. |
| PL-03 | Medium | Passage, signature, publication, and effectiveness were not distinguished. | Frozen stages now carry semantic kinds; `EFFECTIVE` requires a supported date reached by `as_of`, while future effective dates remain visible on earlier stages. |
| PL-04 | Medium | Empty, malformed, and truncated evidence were not represented explicitly. | Added bounded evidence records and conservative `UNKNOWN`/`WAIT` handling. |
| PL-05 | Medium | Tests did not cover temporal sides of `as_of`, complex policy records, or every state field mutation. | Added targeted direct tests, captured-validator mutations, boundary tests, replay checks, and storage invariants. |
| PL-06 | Low | Documentation overstated prompt-injection protection and live deployment readiness. | Documentation now separates mechanical transport/content checks from unproven semantic prompt-injection resistance and labels all pre-release receipts historical. |

## Checks performed

- Pinned runner header: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`.
- `genvm-lint check contracts/PolicyLifecycleResolver.py` passes lint and SDK
  validation.
- `genvm-lint schema contracts/PolicyLifecycleResolver.py` reports a 10-parameter
  constructor and two public methods (`resolve` and `get_state`).
- The focused direct and AST suites cover 51 passing tests in this release
  candidate. Direct mocks exercise contract validation and captured validator
  behavior; they do not establish real-model prompt-injection resistance.
- Fresh StudioNet deployment, finality, execution-success receipts, validator
  votes, source identity, and read-back state are **pending until recorded in
  `deployments/studionet.json`**. No Bradbury or old StudioNet record is proof of
  this source revision.

## Residual risks

URL checks constrain shape and obvious private destinations; they do not prove
publisher authority, DNS integrity, or legal authenticity. The source and model
remain untrusted. Prompt instructions and bounded/truncated markers are useful
mechanical boundaries but cannot guarantee semantic prompt-injection resistance
in production; mocked tests cannot prove it. Ambiguous or insufficient history
stays unresolved, and live network drift can cause validator disagreement.
This contract holds no funds and does not implement legal advice, payouts,
appeals, or downstream authorization. Consumers must verify protocol finality
and execution success, then apply their own idempotency guard.
