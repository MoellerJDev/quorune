---
title: "Compiler coverage status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "75fb6f80e1b071a12be3e3fb88cd46ca33e5eff9b0f54b13981ac8e13a9ca275"
audience: "compiler and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Compiler coverage status

Source fingerprint: `75fb6f80e1b071a12be3e3fb88cd46ca33e5eff9b0f54b13981ac8e13a9ca275`

## Current top-level state

- Compiler version: `oracle-ir-v83`
- Runtime IR: `OracleCardIR lowered to canonical CardProgram V2 with a derived SemanticProgram compatibility index`
- CardProgram schema version: `2`
- Commander Oracle objects: `31623`
- Exact fraction: `0.118679`
- Capability records: `161`
- Assured fixed-target compiler nodes/shapes: `575` / `109`

## Top blockers

- The pinned Commander Oracle snapshot is not capability-complete.
- Material compiler residuals remain: `43178`.
- Blocked capability records remain: `4`.
- Configured evidence is incomplete for: `lexing`, `binding`.

Complete corpus, residual, stage, capability, and CardProgram inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json). The corpus-derived fixed-target grammar shapes and representative identities are in the [Commander Oracle census](../coverage/oracle-coverage-commander.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
