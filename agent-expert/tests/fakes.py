"""Faux client Anthropic pour tester sans réseau ni clé API."""

from __future__ import annotations

import copy
from contextlib import contextmanager
from types import SimpleNamespace


def reponse_texte(texte: str, stop: str = "end_turn") -> SimpleNamespace:
    return SimpleNamespace(
        type="message",
        content=[SimpleNamespace(type="text", text=texte)],
        stop_reason=stop,
        usage=SimpleNamespace(
            input_tokens=10, output_tokens=5,
            cache_read_input_tokens=0, cache_creation_input_tokens=0,
        ),
    )


def reponse_outil(nom: str, args: dict, id_outil: str = "tu_1") -> SimpleNamespace:
    return SimpleNamespace(
        type="message",
        content=[SimpleNamespace(type="tool_use", id=id_outil, name=nom, input=args)],
        stop_reason="tool_use",
        usage=SimpleNamespace(
            input_tokens=8, output_tokens=3,
            cache_read_input_tokens=None, cache_creation_input_tokens=None,
        ),
    )


class _Flux:
    def __init__(self, reponse):
        self._reponse = reponse

    @property
    def text_stream(self):
        for bloc in self._reponse.content:
            if bloc.type == "text":
                milieu = len(bloc.text) // 2
                yield bloc.text[:milieu]
                yield bloc.text[milieu:]

    def get_final_message(self):
        return self._reponse


class _Messages:
    def __init__(self, reponses):
        self.reponses = list(reponses)
        self.appels: list[dict] = []

    def _suivant(self, params):
        # copie profonde : l'agent modifie son historique après l'appel
        self.appels.append(copy.deepcopy(params))
        return self.reponses.pop(0)

    def create(self, **params):
        return self._suivant(params)

    @contextmanager
    def stream(self, **params):
        yield _Flux(self._suivant(params))


class FauxClient:
    def __init__(self, reponses):
        self.messages = _Messages(reponses)
