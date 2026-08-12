# Security and consensus audit: PolicyLifecycleResolver

Audit date: 2026-08-12
Scope: `contracts/PolicyLifecycleResolver.py`
Method: manual review, full GenVM lint and pinned-runner schema validation, direct-mode adversarial tests, explicit independent-validator execution, and finalized StudioNet/Bradbury receipt and state inspection.

## Result

No unresolved critical or high-severity code issue was found after remediation. The contract does not custody or transfer value.

## Remediated findings

| ID | Severity | Finding | Remediation |
| --- | --- | --- | --- |
| PL-01 | Medium | Free-form stages could permit invented outcomes. | Freeze unique stage IDs and reject any extracted stage outside the allowlist. |
| PL-02 | Medium | A source outage could pressure a terminal guess. | Return deterministic WAIT before prompting when all sources are unavailable. |
| PL-03 | Medium | Replay or indefinite delay could create unsafe settlement behavior. | Lock terminal states and force deterministic VOID at maximum wait. |

## Verification

- Exact runner pin: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`.
- `genvm-lint check` passes AST and SDK schema validation.
- Direct tests exercise lifecycle, failure, and independent-validator paths.
- AST regression proves nondeterministic closures do not reference `self`.
- StudioNet deployment and consensus transaction are finalized with successful leader execution; exact evidence is in `deployments/studionet.json`.
- Bradbury deployment and smoke-write receipts are finalized after successful execution and state reads; exact evidence is in `deployments/bradbury.json`.

Bradbury finalized smoke resolution reached `AGREE` with three `AGREE`, one timeout, and one deterministic-violation vote; the transaction executed `FINISHED_WITH_RETURN` and stored `RESOLVED / ENACTED`. Receipt stderr was empty.

## Residual risk

See `SECURITY.md`. This is an engineering assessment, not formal verification, a financial guarantee, or legal advice.
