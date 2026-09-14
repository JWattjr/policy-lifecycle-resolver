# Policy Lifecycle Resolver test matrix

The focused suite uses offline GenLayer direct mode and captured validator
execution. It is intended to exercise actual contract and validator behavior;
it is not a substitute for live receipts or a guarantee of real-model
prompt-injection resistance.

| Requirement | Direct coverage | Live / integration evidence |
| --- | --- | --- |
| Exact model schema and canonical 14-field result | Extra/missing keys, wrong wrappers, invalid enums and types | Consensus receipt and source read-back |
| Bool/int and malformed date rejection | Bool flags/status/coverage, ISO-8601 and YYYY-MM-DD cases | Receipt execution result |
| Frozen identity and specification binding | Mutation of policy, jurisdiction, spec, rule ID, `as_of`, assessment time | `get_state()` and manifest constructor args |
| Frozen stage taxonomy | Duplicate/invented stage IDs, exact stage keys, unsupported kinds, rejected/withdrawn terminal rules | Constructor schema/read-back |
| Passage/signature/publication/effectiveness distinction | Signed snapshot, effective snapshot, future effective date | Current StudioNet snapshots resolve `PUBLISHED` before the effective date and `EFFECTIVE` after it |
| Historical temporal semantics | Event before/after `as_of`, later publication with explicit earlier event, undated page | Official GovInfo/Federal Register source links |
| Required clauses | Exact clause IDs, unknown vector remains `UNKNOWN`/`WAIT` | Canonical stored clause map |
| Source handling | Non-200, empty, malformed, truncated and partial evidence | Independent validator re-fetch |
| Conflict/provisional/complexity/cancellation | Explicit `CONTESTED`, `WAIT`, and `VOID` mappings | Consensus receipt if demonstrated |
| Assessment boundaries | Before cutoff, exact cutoff, exact max-wait | Deployment/resolution timestamps |
| Replay and snapshot semantics | Terminal idempotency, unchanged state after later warp | Repeated `get_state()` read-back |
| Nondeterministic storage safety | AST closure test and accepted-result storage invariant | Execution-success receipt |

## Commands

~~~powershell
$env:PYTHONIOENCODING = "utf-8"
genvm-lint check contracts/PolicyLifecycleResolver.py
genvm-lint schema contracts/PolicyLifecycleResolver.py
python -m pytest tests/test_policy_lifecycle.py tests/test_nondet_storage.py -q
~~~

The final live section is populated only from independently checked StudioNet
receipts in `deployments/studionet.json`. Both current deployments and the
terminal resolve receipts are `FINALIZED`; leader execution is `SUCCESS`, and
the protocol result is `MAJORITY_AGREE`. The before-effective state is
`RESOLVED/PUBLISHED`; the post-effective state is `RESOLVED/EFFECTIVE` after one
retry from a recorded `CONTESTED` result. Protocol `FINALIZED` and leader
execution `SUCCESS` are recorded separately; a finality label alone is not
evidence of successful execution.
