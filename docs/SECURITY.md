# Security model
The contract is permissionless to assess and holds no funds. It does not provide
legal advice, authenticate publishers, implement jurisdiction-specific legal
advice, or pay downstream consumers. Payout, caller authorization, appeals, and
finality handling remain downstream responsibilities.
## Threats addressed

- **Malicious leader:** validators independently fetch the frozen source list,
  inspect the same frozen historical context, and recompute every consequential
  result field.
- **Schema and type confusion:** exact model and accepted-result schemas reject
  extra/missing fields, invented stages or clause IDs, malformed dates, and
  Python bool/int equality traps.
- **Premature resolution:** `as_of`, `cutoff`, and `max_wait` are normalized
  timezone-aware UTC values. Before `cutoff` no nondeterministic assessment is
  attempted; at or after `max_wait` the result is deterministic `VOID`.
- **Replay/double settlement:** terminal contract states (`RESOLVED` and
  `VOID`) return the stored state without another assessment or attempt count.
- **Unsafe evidence URLs:** HTTPS, userinfo, private/internal hosts, literal
  private IPs, whitespace, and non-default ports are rejected at construction.
- **Evidence transport errors:** non-200, empty, malformed, failed, and
  truncated responses are explicitly marked incomplete. All unusable sources
  force `WAIT / SOURCE_UNAVAILABLE`; missing facts never become
  `UNSATISFIED`.

## Temporal semantics

The release freezes one `HISTORICAL_SNAPSHOT` at `as_of`; it is not a continuous
monitor. Every leader and validator receives the exact `as_of`, assessment time,
policy identity, jurisdiction, specification, and temporal-rule ID. Event dates
must be explicitly supported and no later than `as_of`. A later publication can
describe an earlier event only when its content gives that event date. An
undated current-status page cannot establish a historical stage. An
`EFFECTIVE` stage requires an explicitly supported effective date no later than
`as_of`; a future effective date may remain attached to a resolved `SIGNED` or
`PUBLISHED` snapshot. Passage, signature, publication, and effectiveness are
distinct stage kinds. Amendments, partial commencement, multiple versions, and
conflicting records become an explicit unresolved/contested outcome under the
frozen rules.

## Prompt-injection and publisher limitations

Source text is bounded and labeled as data, and the prompt tells the model to
ignore embedded commands. These are mechanical transport/content safeguards;
mocked tests do **not** guarantee semantic prompt-injection resistance against
real models. HTTPS reachability is not proof of publisher authority, DNS
integrity, or legal authenticity. Consumers must choose authoritative URLs and
wait for GenLayer finality before using a result.

## Scope

The contract is permissionless to assess and holds no funds. It does not provide
legal advice, authenticate publishers, implement jurisdiction-specific legal
advice, or pay downstream consumers. Payout, caller authorization, appeals, and
finality handling remain downstream responsibilities.
