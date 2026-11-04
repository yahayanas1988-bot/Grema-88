"""Faux client Anthropic pour tester sans réseau ni clé API."""

from __future__ import annotations

import copy
import threading
from collections.abc import Callable
from contextlib import contextmanager
from types import SimpleNamespace


def _usage(entree: int, sortie: int) -> SimpleNamespace:
    return SimpleNamespace(
        input_tokens=entree, output_tokens=sortie,
        cache_read_input_tokens=0, cache_creation_input_tokens=None,
    )


def reponse_texte(texte: str, stop: str = "end_turn") -> SimpleNamespace:
    return SimpleNamespace(
        type="message",
        content=[SimpleNamespace(type="text", text=texte)],
        stop_reason=stop,
        usage=_usage(10, 5),
    )


def reponse_outil(nom: str, args: dict, id_outil: str = "tu_1") -> SimpleNamespace:
    return SimpleNamespace(
        type="message",
        content=[SimpleNamespace(type="tool_use", id=id_outil, name=nom, input=args)],
        stop_reason="tool_use",
        usage=_usage(8, 3),
    )


def reponse_repartition(taches: list[dict]) -> SimpleNamespace:
    """Réponse du Patron qui appelle l'outil `repartir`."""
    return reponse_outil("repartir", {"taches": taches}, id_outil="tu_plan")


def dernier_texte(params: dict) -> str:
    """Texte du dernier message envoyé (chaîne ou blocs)."""
    contenu = params["messages"][-1]["content"]
    if isinstance(contenu, str):
        return contenu
    return "".join(b.get("text", "") for b in contenu if isinstance(b, dict))


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
    def __init__(self, repondre: Callable[[dict], SimpleNamespace]):
        self._repondre = repondre
        self._verrou = threading.Lock()
        self.appels: list[dict] = []

    def _suivant(self, params):
        # copie profonde : l'agent modifie son historique après l'appel
        with self._verrou:
            self.appels.append(copy.deepcopy(params))
        return self._repondre(params)

    def create(self, **params):
        return self._suivant(params)

    @contextmanager
    def stream(self, **params):
        yield _Flux(self._suivant(params))


class FauxClient:
    """Renvoie les réponses dans l'ordre donné."""

    def __init__(self, reponses):
        file = list(reponses)
        self.messages = _Messages(lambda _params: file.pop(0))


class FauxClientFonction:
    """Choisit la réponse selon la requête : utile quand les appels sont parallèles."""

    def __init__(self, repondre: Callable[[dict], SimpleNamespace]):
        self.messages = _Messages(repondre)
