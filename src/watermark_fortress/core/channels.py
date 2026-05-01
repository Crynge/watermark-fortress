from __future__ import annotations

import hashlib
import hmac
import re
from typing import Iterable

from .models import ChannelPlacement

ZERO_WIDTH = "\u2060"
THIN_SPACE = "\u2009"

LEXICAL_PAIRS = [
    ("because", "since"),
    ("however", "still"),
    ("therefore", "thus"),
    ("important", "critical"),
    ("improve", "strengthen"),
    ("detect", "identify"),
    ("robust", "resilient"),
]


def keyed_score(secret: str, label: str) -> int:
    digest = hmac.new(secret.encode("utf-8"), label.encode("utf-8"), hashlib.sha256).hexdigest()
    return int(digest[:8], 16)


def checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _select_budget(weight: float, ceiling: int) -> int:
    return max(1, min(ceiling, int(round(weight * ceiling))))


def _safe_window(text: str, start: int, end: int) -> str:
    left = max(0, start - 18)
    right = min(len(text), end + 18)
    return text[left:right]


def embed_lexical(text: str, secret: str, weight: float) -> tuple[str, list[ChannelPlacement]]:
    placements: list[ChannelPlacement] = []
    updated = text
    budget = _select_budget(weight, ceiling=6)

    for first, second in LEXICAL_PAIRS:
        if len(placements) >= budget:
            break
        pattern = re.compile(rf"\b({re.escape(first)}|{re.escape(second)})\b", flags=re.IGNORECASE)
        match = pattern.search(updated)
        if not match:
            continue
        use_first = keyed_score(secret, f"lexical:{first}:{match.start()}") % 2 == 0
        replacement = first if use_first else second
        fallback = second if use_first else first
        expected = replacement
        updated = updated[: match.start()] + replacement + updated[match.end() :]
        placements.append(
            ChannelPlacement(
                channel="lexical",
                anchor=checksum(updated[match.start() : match.start() + len(replacement)]),
                expected_surface=expected,
                fallback_surface=fallback,
                evidence_window=_safe_window(updated, match.start(), match.start() + len(replacement)),
                strength=weight,
            )
        )
    return updated, placements


def _candidate_words(text: str) -> Iterable[tuple[str, int, int]]:
    for match in re.finditer(r"\b[a-zA-Z]{5,}\b", text):
        yield match.group(0), match.start(), match.end()


def embed_zero_width(text: str, secret: str, weight: float) -> tuple[str, list[ChannelPlacement]]:
    placements: list[ChannelPlacement] = []
    chars = list(text)
    budget = _select_budget(weight, ceiling=8)
    offset = 0

    for word, start, end in _candidate_words(text):
        if len(placements) >= budget:
            break
        if keyed_score(secret, f"zero:{word}:{start}") % 3 != 0:
            continue
        insertion_point = start + min(2, len(word) - 2) + offset
        chars.insert(insertion_point, ZERO_WIDTH)
        inserted_word = word[: min(2, len(word) - 2)] + ZERO_WIDTH + word[min(2, len(word) - 2) :]
        window_source = "".join(chars)
        placements.append(
            ChannelPlacement(
                channel="zero_width",
                anchor=checksum(word),
                expected_surface=inserted_word,
                fallback_surface=word,
                evidence_window=_safe_window(window_source, insertion_point - 3, insertion_point + len(word)),
                strength=weight,
            )
        )
        offset += 1
    return "".join(chars), placements


def embed_punctuation(text: str, secret: str, weight: float) -> tuple[str, list[ChannelPlacement]]:
    placements: list[ChannelPlacement] = []
    updated = text
    budget = _select_budget(weight, ceiling=5)
    matches = list(re.finditer(r"([,;:])\s", updated))

    applied = 0
    shift = 0
    for match in matches:
        if applied >= budget:
            break
        token = match.group(1)
        if keyed_score(secret, f"punct:{token}:{match.start()}") % 2 != 0:
            continue
        start = match.start() + shift
        end = match.end() + shift
        replacement = f"{token}{THIN_SPACE}"
        updated = updated[:start] + replacement + updated[end - 1 :]
        placements.append(
            ChannelPlacement(
                channel="punctuation",
                anchor=checksum(token + str(start)),
                expected_surface=replacement,
                fallback_surface=f"{token} ",
                evidence_window=_safe_window(updated, start, start + len(replacement)),
                strength=weight,
            )
        )
        applied += 1
        shift += len(replacement) - (end - start)
    return updated, placements
