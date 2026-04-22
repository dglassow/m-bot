# MWarfare API Integration Reference

## What Good Looks Like

- one clear client method per endpoint or action
- explicit request serialization
- explicit response normalization
- deterministic error handling
- no reliance on undocumented server behavior

## Common Checklist

1. Identify the endpoint family.
2. Confirm whether it is read-only or a write/action.
3. Check required headers and signing inputs.
4. Confirm whether `body_id`, `planet_id`, or `playerId` is required.
5. Normalize the response envelope into a local model.
6. Add one success path and one failure path test when practical.

## Local Client Rules

- Keep HTTP concerns in the API layer.
- Keep scheduling and retries in runtime/workers.
- Keep strategic selection in persona or planning layers.
- Keep transport methods small and composable.

## Contract Rules

- Treat `internal-api-reference.md` as the bot-consumer source of truth.
- Treat `docs/api/internal-api.md` as the detailed endpoint catalog.
- If MWarfare changes the API contract, update both docs before using the new behavior.
- When the contract is unclear, prefer documenting the gap over guessing.

## Typical Small Slice

- add one request schema
- add one response schema
- add one client method
- add one targeted test
- update one doc paragraph if needed
