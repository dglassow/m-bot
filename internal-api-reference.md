# MWarfare Internal API Reference For m-bot

## Purpose

This document is the bot-facing reference for the currently available MWarfare
internal API.

`m-bot` must use this API as its only game-facing integration surface.

If MWarfare changes the internal API, this document must be updated at the same
time so `m-bot` stays aligned with the real contract.

## Base URL

All routes are rooted at:

```text
/api/internal/v1
```

Example full URL:

```text
https://<universe-host>/api/internal/v1/players/123/overview
```

## Access Model

This API is internal-only and uses signed service-account requests.

Bots do not use:

- player sessions
- Cognito redirects
- web cookies
- backend-only direct access

## Required Headers

Every request must send:

- `X-Client-Id`
- `X-Internal-Timestamp`
- `X-Internal-Signature`

Every non-GET request must also send:

- `X-Idempotency-Key`

Recommended:

- `Accept: application/json`
- `Content-Type: application/json` on JSON requests

## Signature Format

The signature payload is:

```text
<HTTP_METHOD>
<PATH_INFO>
<QUERY_STRING>
<CLIENT_ID>
<TIMESTAMP>
<IDEMPOTENCY_KEY_OR_EMPTY>
<SHA256_REQUEST_BODY>
```

The signature value is:

```text
hex(hmac_sha256(signature_payload, client_secret))
```

## Scopes

Current scopes:

- `read`
- `play`

`read` is required for query endpoints.  
`play` is required for action endpoints.

## Response Envelope

### Success

```json
{
  "status": "success",
  "data": {},
  "meta": {
    "client_id": "mwarfare-dev",
    "scopes": ["read", "play"]
  }
}
```

### Failure

```json
{
  "status": "failure",
  "code": "body_not_owned",
  "message": "Requested body is not owned by this player.",
  "details": {
    "body_id": 123
  },
  "retryable": false,
  "meta": {
    "client_id": "mwarfare-dev",
    "scopes": ["play"]
  }
}
```

### Command Success Shape

Command endpoints normalize older web-controller responses into a stable
machine-oriented result:

```json
{
  "status": "success",
  "data": {
    "action": "fleet.dispatch",
    "message": "Your fleet has been successfully sent.",
    "result": {}
  },
  "meta": {
    "client_id": "mwarfare-dev",
    "scopes": ["play"]
  }
}
```

## General Request Rules

### Player Context

Routes are scoped by explicit player id:

```text
/players/{playerId}/...
```

### Body Context

Some endpoints accept:

- `body_id`

When present, it selects which owned planet or moon should be used as the
current body context for that request.

### Limits

- messages endpoint max `limit` = `200`
- reports endpoint max `limit` = `100`

## Read Endpoints

### 1. Overview

```text
GET /players/{playerId}/overview
```

Optional query params:

- `body_id`

Returns:

- player id / username / language
- current body id
- body count
- overview snapshot payload

Example:

```http
GET /api/internal/v1/players/123/overview?body_id=456
```

### 2. Bodies

```text
GET /players/{playerId}/bodies
```

Optional query params:

- `body_id`

Returns:

- player identity
- `bodies`
- `snapshot`

Useful for:

- enumerating planets and moons
- selecting body context for later commands

### 3. Queues

```text
GET /players/{playerId}/queues
```

Optional query params:

- `body_id`

Returns queues across bodies:

- building queue
- research queue
- unit queue

Each queue item includes ids, target levels or amounts, timing, and whether the
item is active.

### 4. Flights

```text
GET /players/{playerId}/flights
```

Returns:

- used / max fleet slots
- active missions
- mission type / label
- origin / destination
- fleet composition
- carried resources
- recallability

### 5. Galaxy System

```text
GET /players/{playerId}/galaxy/{galaxy}/systems/{system}
```

Optional query params:

- `body_id`

Returns:

- current body info
- current-body capabilities
- system metadata
- raw galaxy rows for that system

Useful for:

- target discovery
- debris checks
- local launch capability checks

### 6. Exchange State

```text
GET /players/{playerId}/exchange/state
```

Returns:

- exchange coordinate
- exchange totals
- current ratios
- chart data
- player planets and cargo inventory
- active and pending resource listings
- active and pending ship listings
- player deliveries
- ship options

### 7. Messages

```text
GET /players/{playerId}/messages
```

Optional query params:

- `limit` default `50`, max `200`

Returns:

- count
- recent messages
- message metadata
- params/body/view state

### 8. Reports

```text
GET /players/{playerId}/reports
```

Optional query params:

- `limit` default `25`, max `100`

Returns:

- espionage reports
- battle reports
- report message metadata

### 9. Statistics

```text
GET /players/{playerId}/statistics
```

Optional query params:

- `focus`

Returns:

- player id / username / focus
- statistics payload for the requested focus

## Action Endpoints

All action endpoints require:

- `play` scope
- `X-Idempotency-Key`

### 1. Fleet Check Target

```text
POST /players/{playerId}/fleet/check-target
```

Primary inputs:

- `body_id`
- `galaxy`
- `system`
- `position`
- `type`
- optional `mission`

Use this before fleet dispatch to discover:

- whether the target is valid
- what orders are available
- whether the target is reachable/usable

### 2. Fleet Calculate

```text
POST /players/{playerId}/fleet/calc
```

Use this before dispatch to calculate launch parameters.

Typical inputs include:

- `body_id`
- target coordinates and `type`
- unit amounts via launch-pad style fields
- resource payload
- `mission`
- `speed`
- `hold_time`
- `fuel_cell_boost`

The request shape follows the current MWarfare fleet launch conventions.

### 3. Fleet Dispatch

```text
POST /players/{playerId}/fleet/dispatch
```

Typical inputs:

- `body_id`
- `galaxy`
- `system`
- `position`
- `type`
- `mission`
- unit counts in launch-pad style fields like `am202`
- `metal`
- `crystal`
- `deuterium`
- `fuel_cell`
- `speed`
- `hold_time`
- optional mission-specific fields
- optional `fuel_cell_boost`

Important notes:

- This is the live gameplay dispatch surface.
- Use `check-target` and usually `calc` before dispatch.
- Validation errors come back in the normalized failure envelope.

### 4. Fleet Recall

```text
POST /players/{playerId}/fleet/{missionId}/recall
```

Recalls an active outbound mission when allowed.

Optional:

- `body_id`

### 5. Create Resource Listing

```text
POST /players/{playerId}/exchange/resource-listings
```

Required JSON/body fields:

- `planet_id`
- `sell_resource`
- `sell_amount`
- `want_resource`

Optional:

- `prefer_fast`

Example:

```json
{
  "planet_id": 456,
  "sell_resource": "metal",
  "sell_amount": 10000,
  "want_resource": "crystal",
  "prefer_fast": true
}
```

### 6. Purchase Resource Listing

```text
POST /players/{playerId}/exchange/resource-listings/{listingId}/purchase
```

Optional fields:

- `planet_id`
- `destination_planet_id`
- `deliver_at`

Use when accepting an existing exchange listing.

### 7. Recall Resource Listing

```text
POST /players/{playerId}/exchange/resource-listings/{listingId}/recall
```

Recalls one of the player’s resource listings.

### 8. Retrieve Deliveries

```text
POST /players/{playerId}/exchange/deliveries/retrieve
```

Retrieves eligible exchange deliveries to owned worlds.

### 9. Schedule Delivery

```text
POST /players/{playerId}/exchange/deliveries/{deliveryId}/schedule
```

Schedules a delivery for later.

The exact request body should follow the live exchange delivery scheduling
requirements from MWarfare.

## Example Signing Pattern

The current MWarfare tests build signatures like this:

```text
METHOD
PATH
QUERY
CLIENT_ID
TIMESTAMP
IDEMPOTENCY_KEY
SHA256(BODY)
```

Then:

```text
signature = HMAC_SHA256_HEX(payload, secret)
```

## Bot Usage Rules

`m-bot` should always:

1. read state from documented endpoints only
2. validate targets before action
3. calculate before dispatch when relevant
4. treat MWarfare API responses as source of truth
5. avoid any direct backend-only integration path

## Current Gaps

The current API does not yet fully cover all game systems.

Notable missing categories today:

- building queue mutations
- research queue mutations
- shipyard / defense queue mutations
- alliance/chat/admin action surfaces
- event/webhook subscriptions

Those gaps should be handled as unsupported features until MWarfare exposes
stable API routes for them.

## Source Of Truth

When this file needs to be refreshed, verify against:

- `routes/api.php` in MWarfare
- `docs/internal-api.md` in MWarfare
- internal API controllers and payload services in MWarfare

This document is a bot-consumer mirror of the live MWarfare internal API
contract, not an independent API design.
