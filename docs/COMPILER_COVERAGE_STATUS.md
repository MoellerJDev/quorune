---
title: "Compiler coverage status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "21167c835c4caa5e680bf08cd8943c50233c9a1d063b8c8faae3a2ca2693d41e"
audience: "compiler and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Compiler coverage status

Source fingerprint: `21167c835c4caa5e680bf08cd8943c50233c9a1d063b8c8faae3a2ca2693d41e`

## Current top-level state

- Compiler version: `oracle-ir-v88`
- Runtime IR: `OracleCardIR lowered to canonical CardProgram V2 with a derived SemanticProgram compatibility index`
- CardProgram schema version: `2`
- Commander Oracle objects: `31623`
- Exact fraction: `0.123897`
- Capability records: `171`
- Assured fixed-target compiler nodes/shapes: `578` / `112`

## Top blockers

- The pinned Commander Oracle snapshot is not capability-complete.
- Material compiler residuals remain: `42713`.
- Blocked capability records remain: `4`.
- Configured evidence is incomplete for: `lexing`, `binding`.

Complete corpus, residual, stage, capability, and CardProgram inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json). The corpus-derived fixed-target grammar shapes and representative identities are in the [Commander Oracle census](../coverage/oracle-coverage-commander.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
