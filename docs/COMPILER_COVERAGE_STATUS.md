---
title: "Compiler coverage status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "e280c67b6456e6c1ae4f43c6b1147df7ed4e41e2539939bb97eeb7341bf65997"
audience: "compiler and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Compiler coverage status

Source fingerprint: `e280c67b6456e6c1ae4f43c6b1147df7ed4e41e2539939bb97eeb7341bf65997`

## Current top-level state

- Compiler version: `oracle-ir-v103`
- Runtime IR: `OracleCardIR lowered to canonical CardProgram V2 with a derived SemanticProgram compatibility index`
- CardProgram schema version: `2`
- Commander Oracle objects: `31623`
- Exact fraction: `0.171521`
- Capability records: `196`
- Assured fixed-target compiler nodes/shapes: `578` / `112`

## Top blockers

- The pinned Commander Oracle snapshot is not capability-complete.
- Material compiler residuals remain: `39147`.
- Blocked capability records remain: `4`.
- Configured evidence is incomplete for: `lexing`, `binding`.

Complete corpus, residual, stage, capability, and CardProgram inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json). The corpus-derived fixed-target grammar shapes and representative identities are in the [Commander Oracle census](../coverage/oracle-coverage-commander.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
