---
name: persona-dossier
description: Shape persona behavior, social memory, and player dossiers for m-bot
version: 1.0
tags: persona, dossier, llm, memory, social
---

# Persona And Dossier Work

## Use When

- designing persona schema or backstory structure
- updating dossier generation or summarization rules
- changing how bots observe, remember, or evaluate other players
- refining knowledge boundaries between personas and universes

## Default Flow

1. Start from the persona or dossier behavior to change.
2. Separate shared persona identity from universe-specific observations.
3. Keep dossier updates structured and grounded in observed events.
4. Make the LLM summarize and interpret, not invent unsupported facts.
5. Preserve the rule that bots treat all in-universe entities as players.

## Guardrails

- personas are persistent identities, not one-off prompts
- dossiers must be evidence-backed when possible
- bots do not know other bots are bots
- universe-specific tactics do not leak across universes unless explicitly summarized into persona memory
- deterministic systems remain the source of truth for actions

## Deliverables

- one schema, prompt, or document structure change
- one clear memory/dossier rule
- one targeted example or validation path
