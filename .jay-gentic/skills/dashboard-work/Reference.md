# Dashboard Work Reference

## Dashboard Priorities

The dashboard should answer:

- which bots are healthy
- what each bot is doing now
- what each bot will do next
- what requires operator attention
- which universe or worker is degraded

## Preferred Information Density

Lead with:

- severity
- universe
- bot id
- persona
- state
- last action
- next action
- last error or alert

## Operator Controls

Controls should be explicit and low-risk:

- pause bot
- resume bot
- force tick
- safe mode
- disable LLM for a bot
- inspect recent actions and errors

## Implementation Bias

- server-rendered templates first
- simple partial updates second
- full client-side app only if clearly needed later

## Small Slice Examples

- add a universe health card
- add a bot detail panel
- add a persona dossier summary card
- add an error timeline widget
- add a local notifications panel
