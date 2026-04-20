# MWarfare `s2` AI Persona Import

This directory stores the imported MWarfare NPC roster and fallback persona
data copied from the live `s2` branch.

## Source

- repo: `../MWarfare`
- ref: `s2`
- profile source: `config/npc_profiles.php`
- persona source: `config/npc_personas.php`

## Files

- `npc_profiles.json`
  - normalized NPC profile roster
- `persona_archetypes.json`
  - source archetype used by each NPC fallback persona
- `personas_manifest.json`
  - compact summary of every NPC roster entry
- `personas/NPCxxx.json`
  - one full merged record per NPC, including profile metadata and fallback persona

## Notes

- These files are generated for `m-bot` consumption and reference.
- `NPC019` is included in the profile roster but currently has no fallback
  persona payload in the `s2` source, matching the live config state.
- Re-run the importer after MWarfare `s2` persona changes so `m-bot` stays
  aligned with the live source roster.
