# Policy Lifecycle Resolver

A standalone GenLayer Intelligent Contract that resolves a bill, regulation, governance proposal, or public policy to a frozen lifecycle stage and required-clause vector from official public records.

## GenLayer-native decision

Validators independently fetch the frozen sources and agree exactly on lifecycle state, allowlisted stage, terminal flag, ordered clause map, effective date, source coverage, and deterministic reason code.

## Lifecycle and API

`OPEN → WAIT/CONTESTED/RESOLVED/VOID`; `WAIT` and `CONTESTED` are retryable, while `RESOLVED` and `VOID` are terminal. A frozen maximum-wait timestamp forces `VOID` without an LLM call.

Constructor: `policy_id, jurisdiction, stages, clauses, sources, cutoff, max_wait, spec_id`. Public methods: `resolve()` and `get_state()`.

Every evidence URL is frozen, bounded, public HTTPS. Fetched text is untrusted input; prompts instruct validators to ignore embedded commands. Leader and validator closures snapshot ordinary values and independently re-fetch evidence.

## Live evidence

- [StudioNet contract](https://explorer-studio.genlayer.com/address/0xBC1Ae52C008692b1FA8Ae1D572365451bcD23978)
- [Bradbury contract](https://explorer-bradbury.genlayer.com/address/0x368b4583979221C2CA9F85ad20f15fEdfA17A39F)
- Exact StudioNet transaction hashes, constructor arguments, state, and execution results are in `deployments/studionet.json`.

## Verify

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/PolicyLifecycleResolver.py
python -m pytest tests -q
```

The contract uses a concrete pinned GenVM runner. See `docs/SECURITY_AUDIT.md`, `docs/TEST_MATRIX.md`, and `PORTAL_SUBMISSION.md` for reviewer evidence. This primitive does not custody funds; consumers must wait for GenLayer finality and remain idempotent.
