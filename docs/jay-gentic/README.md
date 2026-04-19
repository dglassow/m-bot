# Jay-Gentic Instruction Framework For m-bot

This directory defines the instruction architecture for running `m-bot` through
Jay-Gentic on a local `31B` class model.

## Goal

Keep prompts:

- small
- explicit
- easy to tune
- easy to audit
- easy to evolve without rewriting one giant prompt

## Design Philosophy

The framework is intentionally split into layers:

1. `.jay-gentic.md`
2. `system-prompt.md`
3. tier-1 always-loaded operating docs
4. tier-2 on-demand tuning and project-map docs
5. tier-3 deep references

This follows Jay-Gentic's project-context model and progressive disclosure
approach so the local model only gets what it needs for the current task.

## Files

- `.jay-gentic.md`
  - project manifest for Jay-Gentic
- `system-prompt.md`
  - shortest possible high-priority system prompt
- `operating-rules.md`
  - hard constraints and execution rules
- `task-routing.md`
  - how to classify and route work
- `project-map.md`
  - repo layout and where major components live
- `tuning-guide.md`
  - how to keep prompts small and retune the framework safely

## Operating Rules For This Framework

- Keep tier 1 small and stable.
- Move detail into tier 2 or tier 3, not into the system prompt.
- Prefer short rules over narrative prose.
- Add examples only when the model actually needs them.
- If a rule is needed often, move it upward one tier.
- If a file becomes noisy or repetitive, split it.

## Update Policy

Whenever `m-bot` architecture changes materially:

- update `design.md`
- update `internal-api-reference.md` if the API contract changes
- update the Jay-Gentic framework files if the model would need new routing or
  operating guidance
