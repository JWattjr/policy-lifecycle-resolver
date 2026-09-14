# GenLayer Portal submission

**Contribution type:** Builder → Intelligent Contracts
**Title:** Policy Lifecycle Resolver
**Contribution date:** 2026-09-14
**Network:** StudioNet only

## Notes / Description (under 1,000 characters)

Policy Lifecycle Resolver is a reusable GenLayer Intelligent Contract for bills, regulations, proposals, and policies. It freezes lifecycle stages, required clauses, HTTPS sources, historical `as_of`, cutoff, maximum wait, and temporal rules. The leader and validators independently fetch evidence and compare an exact typed result; deterministic code stores only validated fields and protects terminal replay. Passage, signature, publication, and effectiveness stay distinct. Explicit dates are required; undated history, future effectiveness, unsupported complexity, unavailable/truncated evidence, and conflicts remain unresolved or contested. The OMB Federal Register Doc 2024-07496 constructor is a real public-evidence example. Two fresh StudioNet deployments and finalized resolve receipts are linked below; both stored `WAIT/EVIDENCE_PROVISIONAL`, so no terminal historical result is claimed. Mocked tests do not guarantee semantic prompt-injection resistance. No funds or legal advice.

## Evidence to add

1. GitHub repository (currently private; anonymous HTTP 404, so not yet Portal-ready) — https://github.com/JWattjr/policy-lifecycle-resolver
2. Published source commit `213ad01` (public URL unverified) — https://github.com/JWattjr/policy-lifecycle-resolver/commit/213ad01
   Deployed read-back SHA-256 (normalized source): `c622adbe196a7e3ee9e74ab5e1c0cbb2cefd68792420ef87bcd54e6542d93e2e`.
3. Contract source (public URL unverified) — https://github.com/JWattjr/policy-lifecycle-resolver/blob/main/contracts/PolicyLifecycleResolver.py
4. Focused tests (public URL unverified) — https://github.com/JWattjr/policy-lifecycle-resolver/blob/main/tests/test_policy_lifecycle.py
5. Security audit (public URL unverified) — https://github.com/JWattjr/policy-lifecycle-resolver/blob/main/docs/SECURITY_AUDIT.md
6. Test matrix (public URL unverified) — https://github.com/JWattjr/policy-lifecycle-resolver/blob/main/docs/TEST_MATRIX.md
7. Current local evidence manifest (publish before Portal use) — `deployments/studionet.json`
8. Published-before-effective contract — https://explorer-studio.genlayer.com/address/0xca2d559b98D7B8f9A5d2E33EA44Ae396854b67cE
9. Published-before-effective deployment (`FINALIZED`, leader `SUCCESS`) — https://explorer-studio.genlayer.com/transactions/0x2d29f1b1004915ab42b9cc110c59b1e65c5a1a3b16c1d3ee40d1f9302c5aa3b2
10. Published-before-effective resolve (`FINALIZED`, `MAJORITY_AGREE`, stored `WAIT/EVIDENCE_PROVISIONAL`) — https://explorer-studio.genlayer.com/transactions/0x0d341bdec867e4f04aae166bc8efa59171bd472e98acabd0481344399f5b32c1
11. Effective-after contract — https://explorer-studio.genlayer.com/address/0xcceCB3b68fb13Af8532fd9e767b29B4608109C4d
12. Effective-after deployment (`FINALIZED`, leader `SUCCESS`) — https://explorer-studio.genlayer.com/transactions/0x1a2a5e29b9c7ad173b255446896b0eb3c8e6a3952738209235edfe411249bdfd
13. Effective-after resolve (`FINALIZED`, `MAJORITY_AGREE`, stored `WAIT/EVIDENCE_PROVISIONAL`) — https://explorer-studio.genlayer.com/transactions/0x6b1a394cade4bfa8b1670ee478d22884c39b960f52de5d06df7efa2e688b4e41
14. Official Federal Register API evidence — https://www.federalregister.gov/api/v1/documents/2024-07496.json?fields%5B%5D=document_number&fields%5B%5D=effective_on&fields%5B%5D=publication_date&fields%5B%5D=title&fields%5B%5D=dates
15. Official GovInfo record — https://www.govinfo.gov/content/pkg/FR-2024-04-22/html/2024-07496.htm
16. Supplemental Federal Register rendition — https://www.federalregister.gov/documents/2024/04/22/2024-07496/guidance-for-federal-financial-assistance

The prior StudioNet and Bradbury manifests are historical pre-hardening records.
The current worktree has an uncommitted prompt clarification not present in the
deployed `213ad01` source. Submit only after intentionally publishing that
candidate and verifying a terminal live resolution; current status is **NO**.
