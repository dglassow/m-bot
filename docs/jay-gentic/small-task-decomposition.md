# Small-Task Decomposition Pattern

Use this pattern whenever a task touches more than one subsystem, feels vague,
or would otherwise invite broad edits.

## Default Rule

Reduce every task to:

- one outcome
- one subsystem
- one main change type
- one focused validation step

If you cannot state all four clearly, the task is still too large.

## Preferred Prompt Shape

Ask Jay-Gentic for:

1. one concrete goal
2. the exact files to inspect first
3. a 3-5 step execution sequence
4. one validation step
5. explicit stop conditions

## Canonical Template

```text
Goal:
Implement one concrete change: <goal>

Inspect first:
- <file 1>
- <file 2>
- <file 3>

Constraints:
- keep the change limited to <subsystem>
- do not redesign unrelated code
- use only documented interfaces

Deliver:
- smallest safe implementation
- any required doc update
- one focused validation step

Stop when:
- <done condition 1>
- <done condition 2>
```

## Good Example

```text
Goal:
Add one client method for the exchange state endpoint.

Inspect first:
- internal-api-reference.md
- design.md
- mbot/api/...

Constraints:
- API-only integration
- no backend assumptions
- no unrelated client refactor

Deliver:
- one typed client method
- one response model
- one focused test

Stop when:
- the exchange state call is represented locally
- the response shape is documented in code or tests
```

## Bad Example

```text
Build the whole bot API layer and make sure it is production-ready.
```

## Recovery Pattern

If the model starts to drift:

1. reduce the task to one endpoint, one page, or one memory rule
2. limit the initial file set to 1-3 files
3. ask for an execution card before asking for edits
4. run one workflow template instead of issuing a broad custom prompt
