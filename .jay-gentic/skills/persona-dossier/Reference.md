# Persona And Dossier Reference

## Persona Layers

Keep persona data split into:

- stable backstory and traits
- long-lived preferences
- cross-universe memory summaries
- universe-specific observations
- tactical runtime state

## Dossier Goals

Each dossier should help the bot answer:

- who is this player
- what patterns have they shown
- how dangerous are they
- how trustworthy are they
- how should this persona react to them

## Dossier Content Types

- observed facts
- inferred tendencies
- relationship status
- recent incidents
- confidence level
- next recommended posture

## Knowledge Boundary

The bot should reason as if every observed entity is a player.

It may notice:

- predictable behavior
- unusual timing
- repetitive patterns

It may not conclude:

- this is another bot
- this is an admin-controlled agent
- this entity has out-of-band coordination

unless the game-visible evidence justifies a player-like interpretation.

## Small Slice Examples

- add timezone-aware persona activity windows
- add dossier confidence scoring
- add relationship stance summaries
- improve observation-to-summary pipeline
