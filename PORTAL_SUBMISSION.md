# GenLayer Portal submission

**Contribution type:** Builder → Intelligent Contracts
**Title:** Policy Lifecycle Resolver
**Contribution date:** August 12, 2026

## Notes / Description

Built and deployed an MIT-licensed Policy Lifecycle Resolver, a standalone GenLayer Intelligent Contract for bills, regulations, governance proposals, and public policies. Deployment freezes an allowlisted lifecycle taxonomy, required-clause tests, official HTTPS sources, cutoff, maximum wait, and spec ID. The leader fetches official records; validators independently re-fetch them and require exact agreement on stage, terminal flag, clause vector, effective date, coverage, and reason code. Source outages remain WAIT, contradictions become CONTESTED, cancellation/max-wait become VOID, and terminal settlement is replay-safe. Includes a pinned GenVM runner, direct/adversarial tests, full schema validation, security audit, test matrix, and finalized StudioNet deployment plus consensus evidence. It does not custody funds or provide legal advice.

## Evidence to add

1. GitHub Repository — https://github.com/JWattjr/policy-lifecycle-resolver
2. GitHub File — https://github.com/JWattjr/policy-lifecycle-resolver/blob/main/contracts/PolicyLifecycleResolver.py
3. GitHub File — https://github.com/JWattjr/policy-lifecycle-resolver/blob/main/tests/test_policy_lifecycle.py
4. GitHub File — https://github.com/JWattjr/policy-lifecycle-resolver/blob/main/docs/SECURITY_AUDIT.md
5. GitHub File — https://github.com/JWattjr/policy-lifecycle-resolver/blob/main/docs/TEST_MATRIX.md
6. GitHub File — https://github.com/JWattjr/policy-lifecycle-resolver/blob/main/deployments/studionet.json
7. GitHub File — https://github.com/JWattjr/policy-lifecycle-resolver/blob/main/deployments/bradbury.json
8. GenLayer Explorer Contract — https://explorer-bradbury.genlayer.com/address/0x368b4583979221C2CA9F85ad20f15fEdfA17A39F

The repository is private. Grant Portal reviewers repository access before submission.
