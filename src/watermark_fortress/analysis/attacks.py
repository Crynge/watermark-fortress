from __future__ import annotations

import random
import re
from typing import Callable

from watermark_fortress.core.channels import THIN_SPACE, ZERO_WIDTH

SYNONYM_ATTACK_MAP = {
    "because": "as",
    "since": "because",
    "critical": "important",
    "important": "major",
    "resilient": "strong",
    "robust": "strong",
    "detect": "spot",
    "identify": "spot",
    "therefore": "so",
    "thus": "so",
}


def typo_noise(text: str) -> str:
    chars = list(text)
    for index, char in enumerate(chars):
        if char.isalpha() and index % 31 == 0:
            chars[index] = char * 2
        elif char.isalpha() and index % 41 == 0:
            chars[index] = char.lower()
    return "".join(chars)


def unicode_scrub(text: str) -> str:
    return text.replace(ZERO_WIDTH, "").replace(THIN_SPACE, " ")


def punctuation_flatten(text: str) -> str:
    return re.sub(r"[;:]+", ",", text).replace(THIN_SPACE, " ")


def whitespace_crush(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def lexical_rewrite(text: str) -> str:
    updated = text
    for source, target in SYNONYM_ATTACK_MAP.items():
        updated = re.sub(rf"\b{re.escape(source)}\b", target, updated, flags=re.IGNORECASE)
    return updated


def mixed_pressure(text: str) -> str:
    random.seed(7)
    updated = whitespace_crush(punctuation_flatten(unicode_scrub(text)))
    return lexical_rewrite(typo_noise(updated))


ATTACKS: dict[str, Callable[[str], str]] = {
    "typo_noise": typo_noise,
    "unicode_scrub": unicode_scrub,
    "punctuation_flatten": punctuation_flatten,
    "whitespace_crush": whitespace_crush,
    "lexical_rewrite": lexical_rewrite,
    "mixed_pressure": mixed_pressure,
}


def run_attack(name: str, text: str) -> str:
    if name not in ATTACKS:
        raise KeyError(f"Unknown attack '{name}'.")
    return ATTACKS[name](text)
