# Operating Rules

## Primary Objective

Build `m-bot` as a reliable local bot orchestration system for MWarfare.

## Hard Constraints

- Bots must use the MWarfare internal API only.
- Do not design direct backend hooks as bot runtime dependencies.
- Keep core gameplay math and legality checks deterministic in Python.
- Treat the local LLM as advisory, not authoritative.
- Preserve the rule that bots do not know other bots are bots.
- Keep operator-only secrets out of tracked files.
- Keep the dashboard local-first and operator-focused.

## Local-Model Constraints

The main build assistant is a local `31B` model. Optimize the framework for:

- short prompts
- crisp rules
- explicit routing
- low ambiguity
- minimal context fan-out

Avoid:

- giant all-in-one instruction files
- long repetitive prose
- broad open-ended requests when a tighter task can be given

## Execution Style

- inspect first
- edit narrowly
- verify quickly
- document decisions when they affect architecture

## Documentation Rules

When behavior or architecture changes, update the relevant docs in the same
task:

- `design.md` for architecture
- `internal-api-reference.md` for MWarfare API usage
- Jay-Gentic framework docs if prompt/routing behavior should change
