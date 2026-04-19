# Tuning Guide For A Local 31B Model

This framework is designed for a capable but limited local model.

## Tuning Priorities

Optimize for:

- short context
- low ambiguity
- stable structure
- explicit decision boundaries
- modular docs

## What To Put In Which Layer

### System Prompt

Put only:

- mission of the repo
- hard rules
- execution style

Do not put:

- detailed architecture
- endpoint catalogs
- examples unless absolutely necessary

### Tier 1 Context

Put:

- operating rules
- routing rules
- short repo map

### Tier 2 Context

Put:

- tuning guidance
- expanded project map
- subsystem-specific constraints

### Tier 3 Context

Put:

- full architecture docs
- full API docs
- long references

## Prompting Rules

When giving Jay-Gentic tasks:

- ask for one concrete outcome
- specify the files to inspect
- say what success looks like
- avoid bundling unrelated work
- use the decomposition template for anything larger than a small slice

Prefer:

- "add X to file Y"
- "update the schema for Z"
- "document the endpoint shape for A"

Avoid:

- "build the whole system"
- "review everything and improve it"

## Default Decomposition Rule

For a local 31B model, treat these as separate tasks unless there is a clear
reason to combine them:

- API client work
- runtime worker logic
- dashboard work
- persona or dossier work
- documentation-only work

Use `docs/jay-gentic/small-task-decomposition.md` as the default format for
turning a broad ask into a safe slice.

## When The Model Struggles

Symptoms:

- repetitive output
- vague plans
- missed constraints
- over-broad edits

Corrective actions:

1. reduce the task scope
2. point it to exactly 1-3 files
3. move detail out of the prompt and into a referenced doc
4. ask for a plan before asking for edits
5. split architecture work from implementation work
6. route the task through one matching workflow template if available

## Change Management

When tuning the framework:

- change one layer at a time
- do not expand tier 1 casually
- record structural changes in `design.md` if they affect how the bot system is
  built or maintained
- keep auto-loaded skills concise and move detail into `Reference.md`

## Rule Of Thumb

If a task can be understood without loading `design.md`, it probably should be.
