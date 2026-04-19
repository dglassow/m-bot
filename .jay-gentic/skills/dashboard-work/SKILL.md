---
name: dashboard-work
description: Build local operator dashboard slices for m-bot without UI sprawl
version: 1.0
tags: dashboard, ui, fastapi, observability
---

# Dashboard Work

## Use When

- adding a dashboard page, widget, or operator control
- exposing bot, worker, universe, or persona state
- improving local observability or operator workflows

## Default Flow

1. Start from the operator question the view must answer.
2. Keep the data source explicit: SQLite state, worker status, or aggregated bot events.
3. Prefer dense operator-first layout over decorative UI.
4. Add one visible interaction or insight per slice.
5. Validate that the page can be understood quickly during live bot operation.

## Guardrails

- This is a control plane, not a marketing site.
- Prefer server-rendered pages and simple partial updates.
- Keep views local-only and operator-focused.
- Do not bury important bot state behind excess navigation.
- Avoid broad visual rewrites while building core capabilities.

## Deliverables

- one clear page or widget change
- one supporting query or serialization change if needed
- one small operator note in docs when the workflow changes
