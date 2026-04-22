# MWarfare Internal API

## Purpose

This is the detailed bot-consumer catalog for every MWarfare internal API
endpoint currently exposed to `m-bot`.

Use this doc when you need to:

- add or update an API client method
- understand signing and idempotency
- decide which endpoint a bot should call
- understand what each endpoint returns
- confirm what gameplay actions are currently supported

`m-bot` must use this API as its only gameplay-facing integration surface.

## Base URL

All routes are rooted at:

```text
/api/internal/v1
```

Example:

```text
https://<universe-host>/api/internal/v1/players/123/overview
```

## Access Model

This API is internal-only and uses signed service-account requests.

Bots do not use:

- browser cookies
- player sessions
- Cognito redirects
- direct backend shortcuts

The middleware only serves these routes on universe instances. Non-universe
roles return `404`.

## Required Headers

Every request must send:

- `X-Client-Id`
- `X-Internal-Timestamp`
- `X-Internal-Signature`

Every non-GET request must also send:

- `X-Idempotency-Key`

Recommended:

- `Accept: application/json`
- `Content-Type: application/json` for JSON requests

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

The final signature is:

```text
hex(hmac_sha256(signature_payload, client_secret))
```

Important details:

- timestamp freshness window is `300` seconds
- `PATH_INFO` must be only the path, not the full URL
- `QUERY_STRING` must be the raw query string or an empty string
- GET requests must use an empty idempotency line
- POST body hashing uses the exact JSON body sent over the wire

## Python Signing Example

```python
import hashlib
import hmac
import json
import time


def build_internal_api_headers(
    method: str,
    path: str,
    client_id: str,
    client_secret: str,
    query_string: str = "",
    payload: dict | None = None,
    idempotency_key: str | None = None,
) -> tuple[dict[str, str], str]:
    body = "" if payload is None else json.dumps(payload, separators=(",", ":"))
    timestamp = str(int(time.time()))
    idem = "" if method.upper() == "GET" else (idempotency_key or "")

    signature_payload = "\n".join([
        method.upper(),
        path,
        query_string,
        client_id,
        timestamp,
        idem,
        hashlib.sha256(body.encode("utf-8")).hexdigest(),
    ])

    signature = hmac.new(
        client_secret.encode("utf-8"),
        signature_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "Accept": "application/json",
        "X-Client-Id": client_id,
        "X-Internal-Timestamp": timestamp,
        "X-Internal-Signature": signature,
    }

    if method.upper() != "GET":
        headers["Content-Type"] = "application/json"
        headers["X-Idempotency-Key"] = idem

    return headers, body
```

## Scopes

Supported scopes:

- `read`
- `play`

Rules:

- `read` is required for query endpoints
- `play` is required for action endpoints
- missing scope returns `403` with code `missing_scope`

## Idempotency Rules

Non-GET requests are idempotent by header key.

Behavior:

- missing `X-Idempotency-Key` returns `422`
- if an identical request is already running, the API returns `409`
- if the same request already completed recently, the cached JSON response is
  returned directly
- default idempotency TTL is `300` seconds

Cache key is based on:

- client id
- method
- path
- idempotency key

It does not include the request body, so do not reuse an idempotency key across
different payloads for the same route.

## Rate Limiting

Current rate limit is `600` requests per minute per client id, with a floor of
`60` per minute if config is lowered too far.

## Response Envelope

### Success Envelope

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

### Failure Envelope

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

### Common Auth / Scope Failures

`invalid_signature`:

```json
{
  "status": "unauthorized",
  "code": "invalid_signature",
  "message": "Internal API request is not authorized.",
  "details": [],
  "retryable": false
}
```

`missing_scope`:

```json
{
  "status": "forbidden",
  "code": "missing_scope",
  "message": "Internal API client is missing the required scope.",
  "details": {
    "required_scope": "read"
  },
  "retryable": false
}
```

`missing_idempotency_key`:

```json
{
  "status": "invalid_request",
  "code": "missing_idempotency_key",
  "message": "Missing internal API idempotency key.",
  "details": [],
  "retryable": false
}
```

### Normalized Command Success Shape

Action endpoints proxy older web-controller responses into a stable machine
shape:

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

Important normalization rules:

- web-only fields like `newAjaxToken`, `redirectUrl`, `components`, and `tab`
  are stripped
- remaining fields are surfaced under `data.result`
- proxied failures are converted into the internal failure envelope

## Body Context

Some endpoints accept:

- `body_id`

When present, it selects which owned planet or moon is the active body context
for the request.

If `body_id` does not belong to the player, the API returns:

- `422`
- code `body_not_owned`

## Endpoint Inventory

| Method | Path | Scope | Purpose |
| --- | --- | --- | --- |
| `GET` | `/players/{playerId}/overview` | `read` | current overview snapshot |
| `GET` | `/players/{playerId}/bodies` | `read` | body list plus empire snapshot |
| `GET` | `/players/{playerId}/queues` | `read` | building, research, and unit queues |
| `GET` | `/players/{playerId}/flights` | `read` | active fleet missions and slot usage |
| `GET` | `/players/{playerId}/galaxy/{galaxy}/systems/{system}` | `read` | system scan payload |
| `POST` | `/players/{playerId}/fleet/check-target` | `play` | mission availability and target checks |
| `POST` | `/players/{playerId}/fleet/calc` | `play` | duration, fuel, cargo, boost calculations |
| `POST` | `/players/{playerId}/fleet/dispatch` | `play` | live fleet launch |
| `POST` | `/players/{playerId}/fleet/{missionId}/recall` | `play` | recall outbound fleet |
| `GET` | `/players/{playerId}/exchange/state` | `read` | full exchange state |
| `GET` | `/players/{playerId}/messages` | `read` | recent message feed |
| `GET` | `/players/{playerId}/reports` | `read` | recent espionage and battle reports |
| `GET` | `/players/{playerId}/statistics` | `read` | focus statistics payload |
| `POST` | `/players/{playerId}/exchange/resource-listings` | `play` | create resource listing |
| `POST` | `/players/{playerId}/exchange/resource-listings/{listingId}/purchase` | `play` | buy a resource listing |
| `POST` | `/players/{playerId}/exchange/resource-listings/{listingId}/recall` | `play` | recall owned resource listing |
| `POST` | `/players/{playerId}/exchange/deliveries/retrieve` | `play` | retrieve pending deliveries |
| `POST` | `/players/{playerId}/exchange/deliveries/{deliveryId}/schedule` | `play` | schedule a delivery |

## Read Endpoints

### 1. Overview

```text
GET /players/{playerId}/overview
```

Query params:

- `body_id` optional

Returns:

- `player.id`
- `player.username`
- `player.language`
- `player.current_body_id`
- `player.bodies_count`
- `overview`

The `overview` payload comes from MWarfare's empire snapshot service and is the
closest API equivalent to the in-game overview page.

Use it for:

- top-level bot state refresh
- current body confirmation
- quick empire summary

Example:

```http
GET /api/internal/v1/players/123/overview?body_id=456
```

### 2. Bodies

```text
GET /players/{playerId}/bodies
```

Query params:

- `body_id` optional

Returns:

- `player`
- `bodies`
- `snapshot`

Body entries come from the empire snapshot payload and are the easiest way to:

- enumerate planets and moons
- see current body selection
- feed body selectors for later commands

### 3. Queues

```text
GET /players/{playerId}/queues
```

Query params:

- `body_id` optional

Returns:

- `current_body_id`
- `bodies[]`

Each `bodies[]` entry contains:

- `body.id`
- `body.name`
- `body.type`
- `body.coords`
- `queues.building[]`
- `queues.research[]`
- `queues.unit[]`

Queue item fields:

- `id`
- `title`
- `time_end`
- `time_total`
- `is_active`

Building-only fields:

- `mode`
- `level_target`

Research-only fields:

- `level_target`

Unit-only fields:

- `amount`
- `amount_remaining`

### 4. Flights

```text
GET /players/{playerId}/flights
```

Returns:

- `slots.used`
- `slots.max`
- `missions[]`

Each mission contains:

- mission ids and parent linkage
- mission type and label
- recallability flags
- departure and arrival timestamps
- forward duration and hold time
- origin and destination coordinates
- fleet unit count and unit list
- carried resources

Use it for:

- outgoing mission tracking
- return timers
- current fleet slot pressure
- choosing recallable actions

### 5. Galaxy System

```text
GET /players/{playerId}/galaxy/{galaxy}/systems/{system}
```

Query params:

- `body_id` optional

Returns:

- `player`
- `current_body`
- `system`
- `capabilities`
- `rows`

`capabilities` currently includes:

- `espionage_probe_count`
- `recycler_count`
- `interplanetary_missiles_count`
- `can_colonize`
- `phalanx_icon`

`rows` is the raw MWarfare galaxy-system payload used by the UI. It is the
endpoint to use for:

- target scanning
- debris discovery
- moon and player presence checks
- deciding whether recon, harvest, attack, or colonize is worth attempting

### 6. Exchange State

```text
GET /players/{playerId}/exchange/state
```

Returns:

- `player`
- `exchange`
- `planets`
- `resource_listings`
- `ship_listings`
- `my_deliveries`
- `ship_options`

`exchange` contains:

- exchange coordinate
- live totals
- live ratios
- chart data
- max galaxies
- fleet speed

Each planet entry contains:

- id, name, coords, galaxy/system/position, type
- current resources
- cargo inventory

Listings are normalized into bot-safe keys such as:

- `listing_id`
- `listing_type`
- `status`
- `sell_resource`
- `sell_amount`
- `want_resource`
- `ship_type`
- `ship_quantity`
- `price_resource`
- `price_per_ship`
- `available_at`
- `expires_at`
- `deliver_by`

Deliveries are normalized into:

- `delivery_id`
- `listing_type`
- `listing_id`
- `resource_type`
- `resource_amount`
- `base_resource_amount`
- `bonus_amount`
- `ship_type`
- `ship_quantity`
- `status`
- `destination_planet_id`
- `mission_id`
- `deliver_by`
- `scheduled_for`
- `created_at`

This is the main exchange planning endpoint.

### 7. Messages

```text
GET /players/{playerId}/messages
```

Query params:

- `limit` optional, default `50`, max `200`

Returns:

- `count`
- `messages[]`

Each message includes:

- `id`
- `type`
- `subject`
- `key`
- `params`
- `body`
- `viewed`
- `action_planet_id`
- `sender_user_id`
- `espionage_report_id`
- `battle_report_id`
- `alliance_shared`
- `created_at`
- `updated_at`

Use this for:

- inbox polling
- system notification detection
- report cross-link discovery

### 8. Reports

```text
GET /players/{playerId}/reports
```

Query params:

- `limit` optional, default `25`, max `100`

Returns:

- `count`
- `reports[]`

Each entry includes message metadata plus either:

- `espionage_report`
- `battle_report`

Espionage report fields include:

- coordinates
- owner ids
- activity minutes
- player info
- resources
- debris
- buildings
- research
- ships
- defense

Battle report fields include:

- coordinates
- general summary
- attacker payload
- defender payload
- rounds
- loot
- debris
- repaired defenses
- wreckage

Use this for:

- espionage intelligence
- combat outcome ingestion
- dossier updates

### 9. Statistics

```text
GET /players/{playerId}/statistics
```

Query params:

- `focus` optional

Returns:

- `player.id`
- `player.username`
- `player.focus`
- `statistics`

This endpoint is a pass-through to MWarfare's focus statistics payload. Use it
for:

- specialization tracking
- long-horizon performance summaries
- dashboard and tuning views

## Action Endpoints

All action endpoints require:

- `play` scope
- `X-Idempotency-Key`

Recommended action flow:

1. read current state
2. validate target if relevant
3. calculate if relevant
4. dispatch action
5. re-read state to confirm the result

### 1. Fleet Check Target

```text
POST /players/{playerId}/fleet/check-target
```

Primary inputs:

- `body_id` optional
- `galaxy` required
- `system` required
- `position` required
- `type` required
- `mission` optional
- launch-pad unit fields like `am202` optional but strongly recommended when
  mission legality depends on fleet composition

Use it to discover:

- whether a target is valid
- which mission orders are enabled
- target-specific errors
- ship performance context

The underlying web payload includes:

- `targetOk`
- `orders`
- `errors`
- ship data for the current body

Because this endpoint is proxied, the normalized internal response will keep
those machine-useful fields under `data.result`.

Example body:

```json
{
  "body_id": 456,
  "galaxy": 0,
  "system": 0,
  "position": 6,
  "type": 1,
  "mission": 8,
  "am209": 20
}
```

### 2. Fleet Calculate

```text
POST /players/{playerId}/fleet/calc
```

Primary inputs:

- `body_id` optional
- `galaxy`
- `system`
- `position`
- `type`
- `mission`
- `speed`
- `hold_time` optional
- `fuel_cell_boost` optional
- launch-pad unit fields like `am202`, `am203`, `am209`

Returns:

- `duration`
- `fuelConsumption`
- `cargoCapacity`
- `availableCargo`
- `canReach`
- fuel-cell boost details

This endpoint is the authoritative pre-flight calculator for:

- duration
- fuel cost
- cargo headroom
- range legality
- fuel-cell speed/reward boost information

Example body:

```json
{
  "body_id": 456,
  "galaxy": 0,
  "system": 0,
  "position": 6,
  "type": 1,
  "mission": 8,
  "speed": 10,
  "hold_time": 0,
  "fuel_cell_boost": 0,
  "am209": 20
}
```

### 3. Fleet Dispatch

```text
POST /players/{playerId}/fleet/dispatch
```

Primary inputs:

- `body_id` optional
- `galaxy`
- `system`
- `position`
- `type`
- `mission`
- `speed`
- `hold_time` optional
- `fuel_cell_boost` optional
- ship and missile amounts via launch-pad style fields like `am202`
- carried resources:
  - `metal`
  - `crystal`
  - `deuterium`

Mission-specific optional fields may also be required, for example:

- `missile_target`

Behavior notes verified from source:

- exchange coordinates cannot be targeted
- deep-space missions normalize to slot 16 debris targeting internally
- some deep-space missions require specific research at level 1+
- missile attacks must contain only interplanetary missiles
- regular fleet missions cannot include interplanetary missiles

Successful response usually contains:

- `data.action = fleet.dispatch`
- `data.message`
- `data.result` if the web payload included machine-useful leftovers

Failure response contains the normalized internal failure envelope.

Example body:

```json
{
  "body_id": 456,
  "galaxy": 0,
  "system": 0,
  "position": 6,
  "type": 1,
  "mission": 8,
  "speed": 10,
  "hold_time": 0,
  "fuel_cell_boost": 0,
  "metal": 0,
  "crystal": 0,
  "deuterium": 0,
  "am209": 20
}
```

### 4. Fleet Recall

```text
POST /players/{playerId}/fleet/{missionId}/recall
```

Path params:

- `missionId` required

Body:

- `body_id` optional

Use it to cancel a recallable outbound mission.

Behavior notes:

- returns `404` if mission not found
- authorization is enforced by MWarfare policy checks
- successful normalized response may only contain `action` and `message`

### 5. Create Resource Listing

```text
POST /players/{playerId}/exchange/resource-listings
```

Required fields:

- `planet_id`
- `sell_resource`
- `sell_amount`
- `want_resource`

Optional fields:

- `prefer_fast`

Allowed resources:

- `metal`
- `crystal`
- `deuterium`
- `fuel_cell`

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

Success message:

- `Resource listing created. Transfer mission dispatched to the exchange.`

### 6. Purchase Resource Listing

```text
POST /players/{playerId}/exchange/resource-listings/{listingId}/purchase
```

Path params:

- `listingId` required

Optional fields:

- `planet_id`
- `destination_planet_id`
- `deliver_at`

Behavior:

- if `planet_id` is omitted, MWarfare uses the player's current body
- `deliver_at` is parsed as a date/time string
- successful purchase queues a delivery

Example:

```json
{
  "planet_id": 456,
  "destination_planet_id": 789,
  "deliver_at": "2026-04-22T18:30:00Z"
}
```

### 7. Recall Resource Listing

```text
POST /players/{playerId}/exchange/resource-listings/{listingId}/recall
```

Path params:

- `listingId` required

No request body is required.

Outcome:

- either the resources become immediately available in deliveries
- or the backing fleet begins returning

### 8. Retrieve Deliveries

```text
POST /players/{playerId}/exchange/deliveries/retrieve
```

Required fields:

- `planet_id`
- `delivery_ids` array

Optional fields:

- `pickup_amount`
- `resource_type`

Behavior notes:

- only deliveries owned by the player are considered
- only `pending_selection` deliveries are eligible
- if `pickup_amount` is set, MWarfare may split a delivery and create a
  leftover delivery row
- the action dispatches a retrieval mission to the exchange

Example:

```json
{
  "planet_id": 456,
  "delivery_ids": ["delivery-1", "delivery-2"],
  "pickup_amount": 5000,
  "resource_type": "metal"
}
```

### 9. Schedule Delivery

```text
POST /players/{playerId}/exchange/deliveries/{deliveryId}/schedule
```

Path params:

- `deliveryId` required

Required fields:

- `destination_planet_id`
- `deliver_at`

Behavior:

- delivery must exist
- delivery must belong to the player
- schedule time is parsed from the provided date string

Example:

```json
{
  "destination_planet_id": 789,
  "deliver_at": "2026-04-22T18:30:00Z"
}
```

## How m-bot Should Use This API

### Recommended Request Sequence

For scouting:

1. `GET /overview`
2. `GET /bodies`
3. `GET /galaxy/{galaxy}/systems/{system}`

For fleet launch:

1. `GET /flights`
2. `POST /fleet/check-target`
3. `POST /fleet/calc`
4. `POST /fleet/dispatch`
5. `GET /flights`

For exchange:

1. `GET /exchange/state`
2. choose listing or create listing
3. action endpoint
4. `GET /exchange/state` again

For intelligence:

1. `GET /messages`
2. `GET /reports`
3. update local state from the returned report payloads

### Client Rules

`m-bot` should always:

1. read state only from documented endpoints
2. treat API responses as source of truth
3. re-read state after actions
4. avoid guessing hidden server-side state
5. keep transport, parsing, and decision logic separate

## Current Gaps

These gameplay areas are not yet exposed through the internal API:

- building queue mutations
- research queue mutations
- shipyard / defense queue mutations
- alliance and chat actions
- admin/dev actions
- event subscriptions or webhooks
- ship listing create/update/purchase/recall actions

Those features should be treated as unsupported in `m-bot` until MWarfare
ships stable internal routes for them.

## Source Of Truth

When refreshing this file, verify against:

- `routes/api.php` in MWarfare
- `app/Http/Middleware/InternalApiSignature.php`
- `app/Http/Middleware/EnsureInternalApiScope.php`
- `app/Http/Controllers/InternalApi/*`
- `app/Services/InternalApi/*`
- `tests/Feature/InternalApiOverviewControllerTest.php`
- `tests/Unit/InternalApiControllerResponseTest.php`

This document is a bot-consumer mirror of the live MWarfare internal API
contract. It is not an independent API design.
