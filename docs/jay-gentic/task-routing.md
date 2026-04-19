# Task Routing

Use this file to decide what context to load next.

## Default Rule

Do not load `design.md` by default unless the task is architectural,
cross-cutting, or blocked without it.

Tier 1 should stay enough for small implementation work.

## Task Types

### 1. Architecture / Planning

Open:

- `design.md`
- `docs/jay-gentic/tuning-guide.md`

Use when:

- adding systems
- changing process model
- changing persona/social memory structure
- changing dashboard scope

### 2. MWarfare API Integration

Open:

- `internal-api-reference.md`
- `design.md` only if the integration changes architecture

Use when:

- adding a new API client method
- wiring a new bot action
- changing auth/signing behavior
- updating endpoint assumptions

### 3. Runtime / Worker Implementation

Open:

- `docs/jay-gentic/project-map.md`
- `design.md` only if worker behavior is unclear

Use when:

- editing worker loops
- scheduling
- supervisor logic
- multiprocessing design

### 4. Persona / Dossier / LLM Work

Open:

- `design.md`
- `docs/jay-gentic/tuning-guide.md`

Use when:

- persona schema changes
- prompt design changes
- dossier update flow changes
- memory summarization changes

### 5. Dashboard / Observability

Open:

- `docs/jay-gentic/project-map.md`
- `design.md` if UI scope or operator workflow changes

Use when:

- adding dashboard pages
- adding bot health views
- adding alerts/logging/notification flows

## If Unsure

Load:

- `docs/jay-gentic/project-map.md`

Then decide whether deep architecture context is actually needed.
