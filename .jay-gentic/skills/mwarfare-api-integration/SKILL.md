---
name: mwarfare-api-integration
description: Build and document MWarfare internal API client slices for m-bot
version: 1.0
tags: mwarfare, api, client, integration
---

# MWarfare API Integration

## Use When

- adding or changing an MWarfare API client method
- mapping a new endpoint into deterministic bot logic
- updating signing, headers, retries, or response parsing
- validating that a bot action uses documented API behavior only

## Default Flow

1. Read `internal-api-reference.md` first.
2. Confirm the exact request shape, required headers, and response envelope.
3. Model the request and response as typed local schemas.
4. Keep bot decision logic separate from transport and parsing code.
5. Add the narrowest useful test for the new slice.

## Guardrails

- Use only documented internal API capabilities.
- Do not assume hidden backend state.
- Keep the client deterministic and LLM-free.
- Add one endpoint family at a time.
- Prefer small request/response adapters over broad client rewrites.

## Deliverables

- typed request model if needed
- typed response model if needed
- one focused client method or action adapter
- one focused validation path or test
- doc update if the consumer contract changes
