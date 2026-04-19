# API Client Slice

Use this workflow when adding or changing one MWarfare internal API integration slice.

## Step 1: Gather Current Context

```bash
printf '=== Repo State ===\n'
git status --short --branch
printf '\n=== API Reference Heads ===\n'
sed -n '1,220p' internal-api-reference.md
printf '\n=== Jay-Gentic Framework Files ===\n'
find .jay-gentic -maxdepth 3 \\( -name 'SKILL.md' -o -name 'Reference.md' -o -path './.jay-gentic/workflows/*' \\) | sort
```

## Step 2: Decompose The Slice

```prompt
You are implementing one MWarfare internal API client slice for m-bot.

Using the current repo context:
1. Identify the single endpoint family or action that should be implemented next.
2. Break the work into the smallest safe sequence.
3. Name the exact files that should change first.
4. State one focused validation step.

Keep the plan small enough for a local 31B model to execute reliably.
```

## Step 3: Produce An Execution Card

```prompt
Write a short execution card with these sections only:

- Goal
- Files
- Steps
- Validation
- Stop Conditions

Keep it concise and implementation-ready.
```
