# Project Map

This file should stay short. It exists to help the local model orient quickly.

## Canonical Docs

- `design.md`
  - full architecture and system intent
- `internal-api-reference.md`
  - fast entry point for MWarfare API work
- `docs/api/internal-api.md`
  - detailed MWarfare endpoint catalog, auth flow, and usage examples
- `docs/jay-gentic/*`
  - prompt/routing/tuning framework for Jay-Gentic

## Expected Code Areas

Planned major areas:

- `mbot/api_client/`
  - MWarfare internal API client
- `data/`
  - imported MWarfare source data and future local authored seed data
- `mbot/llm/`
  - local Gemma provider, prompt shaping, schemas
- `mbot/persona/`
  - persona definitions and behavior traits
- `mbot/storage/`
  - SQLite access and repositories
- `mbot/workers/`
  - bot runtime workers
- `mbot/supervisor/`
  - process orchestration
- `mbot/dashboard/`
  - local web dashboard
- `tests/`
  - unit/integration coverage
- `tools/`
  - importers, generators, and small maintenance utilities

## High-Level Data Concepts

- `persona_profile`
- `bot_instance`
- `universe_runtime_state`
- `social_dossier`
- `observation_event`
- `notification_event`

## Important Runtime Boundaries

- MWarfare gameplay state comes through the API.
- LLM output must be validated before execution.
- Personas are shared across universes.
- Tactical state is universe-specific.
- Operator knowledge must not leak into bot in-universe reasoning.
