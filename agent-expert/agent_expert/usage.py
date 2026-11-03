"""Compteur de tokens, pour suivre le coût réel d'une session."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Usage:
    requetes: int = 0
    tokens_entree: int = 0
    tokens_sortie: int = 0
    tokens_lus_en_cache: int = 0
    tokens_ecrits_en_cache: int = 0

    def add(self, response: Any) -> None:
        self.requetes += 1
        u = getattr(response, "usage", None)
        if u is None:
            return
        self.tokens_entree += getattr(u, "input_tokens", 0) or 0
        self.tokens_sortie += getattr(u, "output_tokens", 0) or 0
        self.tokens_lus_en_cache += getattr(u, "cache_read_input_tokens", 0) or 0
        self.tokens_ecrits_en_cache += getattr(u, "cache_creation_input_tokens", 0) or 0

    def resume(self) -> str:
        return (
            f"{self.requetes} requête(s) · {self.tokens_entree} tokens d'entrée "
            f"({self.tokens_lus_en_cache} lus depuis le cache, "
            f"{self.tokens_ecrits_en_cache} écrits dans le cache) · "
            f"{self.tokens_sortie} tokens de sortie"
        )
