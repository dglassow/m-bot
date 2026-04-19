# m-bot Design

## Purpose

`m-bot` is a locally hosted multi-bot control system for MWarfare.

It is intended to:

- run multiple bots concurrently across multiple MWarfare universes
- share persona behavior across universes
- give each persona a rich backstory that shapes its decisions
- use MWarfare's internal gameplay API as the only game-facing control surface
- use a locally hosted `gemma4-heretic` model for high-level reasoning
- maintain dossiers on observed players and rivals through LLM-assisted summaries
- provide a local web dashboard showing what each bot is doing in real time

This document is a living architecture note and should be updated as the design
evolves.

## Current Requirements

- Run about `25` bots concurrently.
- Support at least `3` different universes.
- Allow a single persona to operate across multiple universes.
- Allow bots to read state and take actions exclusively through the available
  internal API.
- Do not allow bots to access MWarfare backend internals, database state,
  private services, or privileged server-side execution paths directly.
- Give every persona its own nationality, timezone, life details, habits, and
  traits that influence play style.
- Allow personas to build and maintain opinions about other players and other
  bots through observation.
- Ensure bots treat every other entity in-universe as if it were a real player.
- Use a non-compiled language.
- Run locally on a Mac laptop.
- Use local system cores efficiently.
- Use the locally hosted `gemma4-heretic` model.
- Expose a locally hosted dashboard for monitoring and control.

## Recommended Stack

- Language: `Python 3.12+`
- HTTP client: `httpx`
- Validation / schemas: `pydantic`
- CLI: `typer`
- Dashboard backend: `FastAPI`
- HTML/UI: server-rendered templates with `Jinja2` plus optional `HTMX`
- Storage: `SQLite` in `WAL` mode
- Console UI: `rich`

## Jay-Gentic Instruction Framework

`m-bot` should include a dedicated Jay-Gentic instruction framework tuned for a
local `31B` model.

The canonical files are:

- `.jay-gentic.md`
- `docs/jay-gentic/system-prompt.md`
- `docs/jay-gentic/operating-rules.md`
- `docs/jay-gentic/task-routing.md`
- `docs/jay-gentic/project-map.md`
- `docs/jay-gentic/tuning-guide.md`

### Framework Goals

- keep default context small
- route tasks to the minimum required docs
- avoid overloading the local model with full architecture by default
- make prompt tuning modular and auditable

### Layering

The framework should follow Jay-Gentic's context model:

1. system prompt
2. tier-1 always-loaded rules
3. tier-2 expandable guidance
4. tier-3 deep references

### Operational Rule

Tier 1 should remain short and stable.

Deep architecture and reference material should stay in tier 2 or tier 3 unless
there is a repeated failure mode that justifies promoting a rule upward.

## Notifications

`m-bot` should send important operator alerts to Discord.

The current local webhook is provided through:

- `MBOT_DISCORD_IMPORTANT_WEBHOOK`

This secret should be stored locally in:

- `secrets/.env.local`

The raw webhook URL must not be copied into tracked docs or source files.

### Important Notification Types

Use this webhook for events such as:

- worker crash loops
- repeated MWarfare API failures
- universe-wide auth or signing failures
- prolonged local LLM outage
- bot stuck states
- safety-mode activation
- severe economic or military anomalies
- operator-required intervention

### Notification Format

Discord alerts should be:

- short
- severity-labeled
- grouped by universe and bot
- readable on desktop and mobile

Each alert should ideally include:

- severity
- universe
- bot id
- persona
- short issue summary
- timestamp
- recommended next step when relevant

## Core Design Principles

1. Keep game logic deterministic in Python.
2. Use the LLM for reasoning, not for mechanics.
3. Use processes, not threads, to take advantage of multiple CPU cores.
4. Keep shared state durable in a local database, not only in memory.
5. Separate persona identity from universe-specific runtime state.
6. Build observability in from the start.
7. Model social knowledge explicitly, not as loose prompt-only memory.
8. Never expose bot-only meta-knowledge to in-universe reasoning.
9. Treat the MWarfare internal API as the only allowed gameplay interface.

## API-Only Access Rule

Bots in `m-bot` must operate through the MWarfare internal API only.

That means:

- all reads come from documented API endpoints
- all writes/actions go through documented API commands
- local logic may combine, cache, interpret, and schedule API usage
- LLM output may recommend actions, but execution still goes through the API

Bots must not:

- call private backend services directly
- access MWarfare database state directly
- rely on privileged in-process hooks
- assume hidden server-side state that is not visible through the API

This keeps the bot system realistic, portable, and aligned with the same
capabilities available to a well-designed external automation client.

## High-Level Architecture

The system should be split into four main parts:

1. Supervisor process
2. Worker processes
3. Shared local data store
4. Local dashboard and API

### 1. Supervisor Process

The supervisor is responsible for:

- loading configuration
- assigning bots to workers
- starting and monitoring worker processes
- restarting crashed workers
- tracking worker health
- exposing aggregate runtime health to the dashboard

The supervisor should not directly run bot logic.

### 2. Worker Processes

Workers should use:

- one OS process per worker
- one `asyncio` event loop inside each worker
- async HTTP clients for MWarfare API traffic
- async calls to the local LLM provider

Each worker manages a subset of bots.

Initial recommendation:

- `6` to `10` worker processes total
- each worker handles `2` to `5` bots

This is a better fit than running one process per bot.

### 3. Shared Local Data Store

Use SQLite in WAL mode as the first persistence layer.

The database should store:

- personas
- bot instances
- universe configuration
- bot runtime state
- social dossiers on observed entities
- persona memory summaries
- worker heartbeats
- action logs
- error logs
- LLM requests
- notification history
- scheduling metadata

### 4. Local Dashboard

A local web dashboard should provide:

- overall bot status
- per-bot visibility
- per-universe visibility
- persona inspection
- recent actions and errors
- limited operator controls

The dashboard should be local-only and operator-focused.

## Multiprocessing Strategy

Python should use multiple cores through multiprocessing, not threads.

### Why

- The GIL limits true CPU parallelism in threaded Python.
- Multiple processes can use multiple cores cleanly.
- Bot work is mostly I/O bound, but decision logic and model orchestration can
  still benefit from process isolation.

### Recommended Worker Count

Start with:

```text
worker_count = min(available_cores - 2, 10)
```

This leaves headroom for:

- the OS
- Glass
- the local LLM runtime
- the dashboard

Do not automatically map one bot to one process.

## Local LLM Integration

`gemma4-heretic` is locally hosted on the same machine and should be treated as
a shared local inference service.

### Rule

Do not load one model instance per bot.

Instead, `m-bot` should use a shared local provider adapter that connects to
the model through localhost.

### LLM Responsibilities

Use the model for:

- persona-consistent decision shaping
- high-level prioritization
- strategic summaries
- target evaluation summaries
- writing and updating dossiers on other players
- compressing long observation histories into usable memory
- chat or diplomacy generation
- compressed reasoning from structured state

Do not use the model for:

- HMAC signing
- polling loops
- timers
- resource arithmetic
- fleet math
- deterministic mission validation
- direct execution without rule validation

### LLM Safety Model

Every LLM-driven decision should follow this flow:

1. Python gathers structured game state.
2. Python builds a compact prompt.
3. The local model returns structured output, preferably JSON.
4. Python validates the output against hard rules.
5. Python executes only validated actions through MWarfare's internal API.

The same pattern should be used for social memory:

1. Python gathers structured observations.
2. The model proposes a dossier update or opinion summary.
3. Python stores the result in structured durable form.
4. Future decisions can read the stored dossier without needing to replay the
   full raw event history every time.

### LLM Provider Layer

The codebase should support an abstraction like:

- `LocalGemmaProvider`
- `OpenAIProvider`
- `MockProvider`

All bots should use a common interface, not a model-specific implementation.

### LLM Concurrency Controls

Because many bots may request reasoning at once, add:

- maximum concurrent LLM requests
- request queueing
- timeout handling
- retries with backoff
- decision caching where appropriate
- deterministic fallback behavior if the model is unavailable

## Persona Model

Personas should be shared across universes.

That means persona data must be independent from any one bot instance.

### Separate These Concepts

- `persona_profile`: stable shared behavioral identity
- `bot_instance`: one runtime bot tied to one player in one universe
- `universe_runtime_state`: tactical and economic state for that universe only
- `social_dossier`: structured memory about another entity, scoped to a
  persona and universe

### Persona Backstory Requirements

Each persona should have a rich backstory document and structured profile that
includes at least:

- name
- nationality
- home timezone
- age range or life stage
- work/life routine
- sleep schedule assumptions
- emotional temperament
- strategic temperament
- risk tolerance
- social style
- economic bias
- military bias
- exploration bias
- grudge/forgiveness tendencies
- diplomacy tendencies
- preferred play windows
- notable quirks or habits

This backstory is not decorative. It should influence:

- when the bot tends to play
- how aggressively it expands
- how quickly it retaliates
- how suspicious it is of other players
- how it values alliances, trade, revenge, and risk
- how it writes messages and logs

### Persona Representation

Each persona should exist in two forms:

1. Structured fields used directly by deterministic Python logic.
2. A narrative backstory document used by the LLM for consistent tone and
   decision framing.

The structured fields are the source of truth for anything operational.
Narrative text exists to improve consistency and richness, not to replace hard
behavioral parameters.

### Result

A single persona can behave consistently across universes while still keeping
universe-specific tactical state separated.

## Social Modeling And Dossiers

Each persona should maintain documents on other entities it observes or
interacts with.

These documents should be treated as durable social memory.

### Core Rule

Bots are not aware that other bots are bots.

Inside the simulation, every other entity is treated as a player or alliance
actor. This includes:

- human players
- other local bots
- shared persona-linked bots in other universes where relevant records exist

No prompt, memory, dashboard field, or decision API given to a bot should tell
it that another in-universe entity is an automation system.

### Dossier Scope

Dossiers should be stored per:

- persona
- universe
- observed entity

This keeps a persona's opinion about a player in Universe A separate from its
opinion about a similarly named or linked entity in Universe B.

### What A Dossier Should Capture

Each dossier should contain structured and summarized fields like:

- target player id or stable entity id
- username / alliance tag history
- first seen time
- last seen time
- threat level
- trust level
- aggression estimate
- activity-window estimate
- raidability estimate
- economic strength estimate
- military strength estimate
- history of attacks, trades, chats, scans, and betrayals
- inferred habits
- current stance
- open questions / uncertainty
- narrative summary

### How Dossiers Are Updated

Dossiers should be updated from:

- galaxy observations
- espionage reports
- combat reports
- exchange interactions
- message interactions
- alliance interactions
- repeated timing/activity patterns

The update pipeline should be:

1. deterministic observation event captured
2. event normalized into structured form
3. LLM asked to summarize or revise opinion
4. structured dossier fields updated
5. summary text refreshed

### Opinion Model

Each persona should be able to form opinions such as:

- trustworthy trader
- inactive farm
- dangerous raider
- revenge target
- useful ally
- likely trapper
- unpredictable wildcard

These opinions should affect future behavior, but never bypass hard game rules.

## Bot Knowledge Boundaries

The system needs a strict separation between:

- operator knowledge
- system knowledge
- in-universe bot knowledge

### Operator Knowledge

This includes anything the dashboard knows, such as:

- which entities are local bots
- worker assignments
- model usage
- internal failures

### Bot Knowledge

Bots may only reason from:

- their own persona
- persistent dossier state
- information gathered through allowed in-game observations
- configured universe context

Bots must not receive:

- "this user is one of our bots"
- "this player is controlled by persona X"
- out-of-band privileged knowledge from the dashboard
- system-internal execution details

This rule is essential for believable behavior.

## Dashboard Requirements

The dashboard should be locally hosted and provide the following views.

### Global Overview

- total bots
- bots by universe
- running / paused / errored counts
- worker health
- model queue depth
- recent API errors

### Per Bot

- bot id
- persona id
- persona name
- universe
- player/account
- current body
- current status
- last action
- next scheduled action
- last API request
- last LLM decision summary
- top current dossiers / rivals
- health/errors

### Per Universe

- universe id / label
- base URL
- bot count
- rate-limit state
- recent errors
- recent activity

### Per Persona

- persona traits
- persona backstory
- timezone and activity assumptions
- linked bot instances
- universes active in
- shared memory summary
- recent reasoning summaries

### Social Intel Views

The dashboard should also expose:

- dossier list per persona
- dossier detail pages
- recent opinion changes
- observed hostility / diplomacy history
- inferred player activity windows
- trust / threat rankings

### Logs

- action log
- error log
- worker log
- LLM request log

### Operator Controls

- pause bot
- resume bot
- pause universe
- resume universe
- trigger immediate tick
- disable or enable LLM usage
- switch bot into safe mode

## MWarfare API Integration

The bot should use MWarfare's internal API, not the web session layer.

Current important API categories:

- overview
- bodies
- queues
- flights
- galaxy
- exchange
- messages
- reports
- statistics
- fleet actions

The current bot-facing reference for these endpoints should live in:

- `internal-api-reference.md`

### Integration Rules

1. Treat MWarfare as the source of truth.
2. Never let bot state drift from API-confirmed state.
3. Always validate target and launch data before dispatch.
4. Prefer stable internal API endpoints over scraping UI responses.
5. Do not use any non-API backend shortcut, even if it would be technically
   available locally.

## Persistence Model

Initial database tables should include at least:

- `persona_profiles`
- `persona_backstories`
- `persona_memory_summaries`
- `bot_instances`
- `bot_runtime_state`
- `observed_entities`
- `social_dossiers`
- `observation_events`
- `universe_sessions`
- `worker_processes`
- `bot_heartbeats`
- `bot_actions`
- `bot_errors`
- `llm_requests`
- `schedules`

## Suggested Project Layout

```text
m-bot/
  design.md
  config/
  plans/
  tests/
  mbot/
    api_client/
    cli/
    core/
    dashboard/
      templates/
      static/
    llm/
      prompts/
    persona/
    storage/
    supervisor/
    universe/
    workers/
```

## Phased Build Plan

### Phase 1

- project scaffold
- config loading
- SQLite setup
- MWarfare internal API client
- local Gemma provider adapter
- supervisor process
- worker process skeleton

### Phase 2

- bot registry
- persona system
- persona backstory ingestion
- basic polling loop
- overview / bodies / flights / galaxy reads
- dashboard skeleton

### Phase 3

- fleet decision engine
- exchange automation
- structured LLM decision prompts
- observation event pipeline
- dossier generation and updates
- action logs and error tracking
- dashboard controls

### Phase 4

- improved scheduling
- cross-universe persona memory handling
- richer social memory and rivalry modeling
- richer dashboards
- safe-mode automation
- operator tooling and replay/debug workflows

## Open Decisions

These are still open and should be revisited as we continue:

- exact worker count default for this Mac
- exact local endpoint format for `gemma4-heretic`
- whether the local dashboard should use WebSockets or polling first
- whether to start with raw `sqlite3`, `SQLAlchemy`, or `sqlmodel`
- how much long-term persona memory should be stored versus summarized
- whether dossier summaries should be refreshed on every new observation or in
  batched intervals
- what minimum structured fields are required before the LLM may write a social
  opinion update

## Current Recommendation Summary

The best current design is:

- Python
- multiprocessing workers
- async I/O within each worker
- shared SQLite state
- shared local `gemma4-heretic` provider
- rich persona backstories with structured behavioral traits
- per-persona, per-universe social dossiers on observed entities
- strict in-universe knowledge boundaries so bots treat all others as players
- deterministic Python execution layer
- local FastAPI dashboard

This gives the best balance of:

- low friction
- multi-core usage
- local observability
- maintainability
- future growth
