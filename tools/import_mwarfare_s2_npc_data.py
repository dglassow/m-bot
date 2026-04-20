#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MWARFARE_REPO = PROJECT_ROOT.parent / "MWarfare"
DEFAULT_REF = "s2"
PROFILES_PATH = "config/npc_profiles.php"
PERSONAS_PATH = "config/npc_personas.php"


TOKEN_RE = re.compile(
    r"""
    (?P<WS>\s+)
  | (?P<PHP><\?php)
  | (?P<ARROW>=\>)
  | (?P<LBRACK>\[)
  | (?P<RBRACK>\])
  | (?P<LPAREN>\()
  | (?P<RPAREN>\))
  | (?P<COMMA>,)
  | (?P<SEMI>;)
  | (?P<EQUAL>=)
  | (?P<VAR>\$[A-Za-z_][A-Za-z0-9_]*)
  | (?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<STRING>'(?:\\.|[^'\\])*')
  | (?P<NUMBER>-?\d+)
    """,
    re.VERBOSE | re.MULTILINE,
)


class ParseError(RuntimeError):
    pass


@dataclass
class Token:
    kind: str
    value: str


def tokenise(source: str) -> list[Token]:
    tokens: list[Token] = []
    index = 0
    while index < len(source):
        match = TOKEN_RE.match(source, index)
        if not match:
            snippet = source[index : index + 40]
            raise ParseError(f"Unparsed PHP near: {snippet!r}")
        kind = match.lastgroup
        assert kind is not None
        value = match.group(kind)
        index = match.end()
        if kind in {"WS", "PHP"}:
            continue
        tokens.append(Token(kind, value))
    return tokens


def array_replace_recursive(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        merged = dict(base)
        for key, value in override.items():
            if key in merged:
                merged[key] = array_replace_recursive(merged[key], value)
            else:
                merged[key] = value
        return merged
    return override


class PhpSubsetParser:
    def __init__(self, source: str) -> None:
        self.tokens = tokenise(source)
        self.index = 0
        self.env: dict[str, Any] = {}

    def parse(self) -> Any:
        returned: Any = None
        while not self.at_end():
            token = self.peek()
            if token.kind == "VAR":
                name = self.consume("VAR").value[1:]
                self.consume("EQUAL")
                self.env[name] = self.parse_expr()
                self.consume("SEMI")
                continue
            if token.kind == "IDENT" and token.value == "return":
                self.consume("IDENT")
                returned = self.parse_expr()
                self.consume("SEMI")
                continue
            raise ParseError(f"Unexpected token {token.kind}:{token.value}")
        return returned

    def parse_expr(self) -> Any:
        token = self.peek()
        if token.kind == "LBRACK":
            return self.parse_array()
        if token.kind == "STRING":
            raw = self.consume("STRING").value
            return bytes(raw[1:-1], "utf-8").decode("unicode_escape")
        if token.kind == "NUMBER":
            return int(self.consume("NUMBER").value)
        if token.kind == "VAR":
            name = self.consume("VAR").value[1:]
            if name not in self.env:
                raise ParseError(f"Unknown variable ${name}")
            return self.env[name]
        if token.kind == "IDENT":
            ident = self.consume("IDENT").value
            if ident == "true":
                return True
            if ident == "false":
                return False
            if ident == "null":
                return None
            if ident == "array_replace_recursive":
                self.consume("LPAREN")
                base = self.parse_expr()
                self.consume("COMMA")
                override = self.parse_expr()
                self.consume("RPAREN")
                return array_replace_recursive(base, override)
            raise ParseError(f"Unsupported identifier: {ident}")
        raise ParseError(f"Unexpected expression token {token.kind}:{token.value}")

    def parse_array(self) -> Any:
        self.consume("LBRACK")
        if self.check("RBRACK"):
            self.consume("RBRACK")
            return []

        values: list[Any] = []
        pairs: list[tuple[Any, Any]] = []
        associative = False

        while not self.check("RBRACK"):
            item = self.parse_expr()
            if self.check("ARROW"):
                associative = True
                self.consume("ARROW")
                pairs.append((item, self.parse_expr()))
            else:
                values.append(item)
            if self.check("COMMA"):
                self.consume("COMMA")
                if self.check("RBRACK"):
                    break
            else:
                break

        self.consume("RBRACK")
        if associative:
            if values:
                raise ParseError("Mixed keyed and non-keyed PHP arrays are unsupported.")
            return {key: value for key, value in pairs}
        return values

    def at_end(self) -> bool:
        return self.index >= len(self.tokens)

    def peek(self) -> Token:
        if self.at_end():
            raise ParseError("Unexpected end of input.")
        return self.tokens[self.index]

    def check(self, kind: str) -> bool:
        return not self.at_end() and self.tokens[self.index].kind == kind

    def consume(self, kind: str) -> Token:
        token = self.peek()
        if token.kind != kind:
            raise ParseError(f"Expected {kind}, got {token.kind}:{token.value}")
        self.index += 1
        return token


def git_show(repo: Path, ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{ref}:{path}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def git_rev_parse(repo: Path, ref: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", ref],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def archetype_map(personas_source: str) -> dict[str, str]:
    matches = re.findall(
        r"'(NPC\d+)'\s*=>\s*array_replace_recursive\(\$([A-Za-z_][A-Za-z0-9_]*)\s*,",
        personas_source,
    )
    return {npc_key: base for npc_key, base in matches}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    repo = DEFAULT_MWARFARE_REPO
    ref = DEFAULT_REF
    commit = git_rev_parse(repo, ref)

    profiles_source = git_show(repo, ref, PROFILES_PATH)
    personas_source = git_show(repo, ref, PERSONAS_PATH)

    profiles_payload = PhpSubsetParser(profiles_source).parse()
    personas_payload = PhpSubsetParser(personas_source).parse()

    defaults: list[dict[str, Any]] = profiles_payload["defaults"]
    fallbacks: dict[str, dict[str, Any]] = personas_payload["fallbacks"]
    archetypes = archetype_map(personas_source)

    output_root = PROJECT_ROOT / "data" / "mwarfare-s2"
    personas_root = output_root / "personas"

    profiles_manifest: list[dict[str, Any]] = []
    personas_manifest: list[dict[str, Any]] = []

    for profile in defaults:
        npc_key = str(profile["npc_key"])
        normalized_profile = dict(profile)
        normalized_profile.setdefault("is_enabled", True)
        profiles_manifest.append(normalized_profile)

        persona = fallbacks.get(npc_key)
        persona_record = {
            "npc_key": npc_key,
            "profile": normalized_profile,
            "archetype": archetypes.get(npc_key),
            "persona": persona,
            "source": {
                "project": "MWarfare",
                "ref": ref,
                "commit": commit,
                "profiles_path": PROFILES_PATH,
                "personas_path": PERSONAS_PATH,
            },
        }
        write_json(personas_root / f"{npc_key}.json", persona_record)

        personas_manifest.append(
            {
                "npc_key": npc_key,
                "default_username": normalized_profile["default_username"],
                "default_email": normalized_profile["default_email"],
                "legacy_aid": normalized_profile["legacy_aid"],
                "is_enabled": normalized_profile["is_enabled"],
                "persona_s3_key": normalized_profile["persona_s3_key"],
                "archetype": archetypes.get(npc_key),
                "has_persona": persona is not None,
                "display_name": persona["identity"]["display_name"] if persona else None,
                "home_timezone": persona["background"]["home_timezone"] if persona else None,
                "region": persona["background"]["region"] if persona else None,
                "alliance_tag": (
                    persona.get("social", {})
                    .get("alliance_identity", {})
                    .get("tag")
                    if persona
                    else None
                ),
                "alliance_name": (
                    persona.get("social", {})
                    .get("alliance_identity", {})
                    .get("name")
                    if persona
                    else None
                ),
            }
        )

    write_json(
        output_root / "npc_profiles.json",
        {
            "source": {"project": "MWarfare", "ref": ref, "commit": commit, "path": PROFILES_PATH},
            "profiles": profiles_manifest,
        },
    )
    write_json(
        output_root / "persona_archetypes.json",
        {
            "source": {"project": "MWarfare", "ref": ref, "commit": commit, "path": PERSONAS_PATH},
            "archetypes": archetypes,
        },
    )
    write_json(
        output_root / "personas_manifest.json",
        {
            "source": {"project": "MWarfare", "ref": ref, "commit": commit, "path": PERSONAS_PATH},
            "personas": personas_manifest,
        },
    )


if __name__ == "__main__":
    main()
