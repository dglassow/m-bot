# Persona Dossier Slice

Use this workflow when refining persona backstory handling, social memory, or player dossier behavior.

## Step 1: Gather Current Context

```bash
printf '=== Repo State ===\n'
git status --short --branch
printf '\n=== Persona And Dossier References ===\n'
rg -n "persona|dossier|memory|backstory|universe-specific|bots are bots" design.md
printf '\n=== Persona Skill ===\n'
sed -n '1,240p' .jay-gentic/skills/persona-dossier/SKILL.md
printf '\n=== Decomposition Guide ===\n'
sed -n '1,240p' docs/jay-gentic/small-task-decomposition.md
```

## Step 2: Decompose The Slice

```prompt
You are implementing one persona or dossier slice for m-bot.

Using the current repo context:
1. Identify the one behavior or memory rule to change.
2. Separate shared persona logic from universe-specific state.
3. Name the exact files that should change.
4. Give one validation step that proves the knowledge boundary still holds.

Keep the scope small enough for a local 31B model to finish cleanly.
```

## Step 3: Produce An Execution Card

```prompt
Write a short execution card with these sections only:

- Behavior Change
- Files
- Steps
- Validation
- Boundary Check

Keep it concise and implementation-ready.
```
