# MWarfare Internal API Reference For m-bot

## Purpose

This file is the fast entry point for MWarfare API work in `m-bot`.

The full endpoint catalog, signing details, request examples, and action
payload notes now live in:

- [docs/api/internal-api.md](docs/api/internal-api.md)

Use this file first, then open the detailed catalog when you need to implement
or document a real endpoint flow.

## Quick Summary

- Base path: `/api/internal/v1`
- Auth model: signed service-account requests
- Read scope: `read`
- Action scope: `play`
- Non-GET requests require `X-Idempotency-Key`
- Bots must use this API as their only gameplay integration surface

## Current Endpoint Families

- overview
- bodies
- queues
- flights
- galaxy system lookup
- fleet target checks
- fleet calculation
- fleet dispatch
- fleet recall
- exchange state
- messages
- reports
- statistics
- exchange resource listing actions
- exchange delivery actions

## Canonical Detailed Doc

For full usage details, open:

- [docs/api/internal-api.md](docs/api/internal-api.md)

## Source Of Truth

When refreshing the docs, verify against:

- `routes/api.php` in MWarfare
- internal API controllers and payload services in MWarfare
- internal API middleware in MWarfare

This document is a routing pointer. The detailed contract lives in the docs
path above so it is easier to discover from the main `docs/` tree.
