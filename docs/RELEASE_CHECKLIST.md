# StudioNet release checklist

This checklist is StudioNet-only. It does not authorize Portal submission or
mainnet/Bradbury use.

1. Review the working tree, commit the exact contract/tests/docs candidate, and
   push it. Record the commit SHA and the normalized SHA-256 of
   `contracts/PolicyLifecycleResolver.py`.
2. Run `genvm-lint check`, `genvm-lint schema`, and the focused pytest commands.
3. Deploy each frozen snapshot with the complete constructor arguments. Capture
   the contract address and deployment transaction; poll until protocol status
   is `FINALIZED`, then record leader execution (`SUCCESS` or the exact returned
   status), protocol consensus result, and validator votes. Majority agreement
   is not unanimity.
4. Verify `genlayer code <address>` and `genlayer schema <address>` read-back.
   The normalized source read-back must equal the committed source hash.
5. After the frozen cutoff, call `resolve` once per snapshot. Poll each receipt
   to `FINALIZED`, record the real resolution transaction, execution result,
   consensus result, vote array, and the exact `get_state()` read-back. Accept a
   Portal claim only when the expected terminal `RESOLVED` state and all dates,
   clauses, identity fields, and rule IDs are present. `WAIT`, `CONTESTED`, or
   `VOID` is a real outcome, not a success substitute.
6. Verify each Explorer URL anonymously, update `deployments/studionet.json`,
   and keep older StudioNet/Bradbury manifests under an explicit historical
   label. Add only public source, test, audit, evidence, and receipt links to
   the Portal form.

Current release status: **YES for evidence preparation**. Commit
`4c2dec62d3b9bebd64ae6d7a3aedf47bed8e658e` is public, and both current
StudioNet contracts read back the normalized source hash
`885d0a2c4d80b0b3b72213dae426ed9f4b83995a4c467da689bc59e6d0e63914`.
The before-effective snapshot is `RESOLVED/PUBLISHED` at
`0xe93660c3d3FaF91444899A3E76A622B0e0A6E3dc`; the post-effective snapshot is
`RESOLVED/EFFECTIVE` at `0x21CD1989906e2418FDd7EfC0f3b4CE17FF2c90B4` after a
recorded retry from `CONTESTED`. The exact receipts and state read-backs are in
`deployments/studionet.json`. Portal submission remains a user action; no
Bradbury evidence is current.
