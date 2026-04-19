# Dashboard Slice

Use this workflow when building one local dashboard page, widget, or operator control.

## Step 1: Gather Current Context

```bash
printf '=== Repo State ===\n'
git status --short --branch
printf '\n=== Design Dashboard Section ===\n'
rg -n "dashboard|operator|observability|control" design.md
printf '\n=== Jay-Gentic Dashboard Skill ===\n'
sed -n '1,220p' .jay-gentic/skills/dashboard-work/SKILL.md
printf '\n=== Dashboard-Related Files ===\n'
find . -maxdepth 3 \\( -path './mbot/dashboard*' -o -path './dashboard*' \\) | sort
```

## Step 2: Decompose The Slice

```prompt
You are implementing one operator-facing dashboard slice for m-bot.

Using the current repo context:
1. Identify the single operator question this slice should answer.
2. Choose the smallest page, widget, or control that delivers that answer.
3. Name the exact files that should change.
4. Give one validation step focused on operator readability and correctness.

Keep the scope narrow and avoid redesigning unrelated UI.
```

## Step 3: Produce An Execution Card

```prompt
Write a short execution card with these sections only:

- Operator Question
- Files
- Steps
- Validation
- Avoid

Keep it concise and action-oriented.
```
