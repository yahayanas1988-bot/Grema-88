"""Choix du domaine d'expertise pour une question.

Un petit modèle rapide répond par un seul identifiant. Si la réponse est
inexploitable ou si l'appel échoue, on se rabat sur les mots-clés : le routage
ne doit jamais bloquer la réponse.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from .domains import DOMAINS, DOMAINS_BY_ID, GENERAL_ID, Domain
from .usage import Usage

log = logging.getLogger(__name__)

ROUTER_SYSTEM = (
    "Tu es un aiguilleur. Tu choisis le domaine d'expertise qui convient le mieux "
    "à la demande. Réponds uniquement par l'identifiant du domaine, sans rien d'autre."
)


def _router_prompt(message: str) -> str:
    lignes = "\n".join(f"- {d.id} : {d.resume}" for d in DOMAINS)
    return f"Domaines :\n{lignes}\n\nDemande :\n<demande>\n{message[:1500]}\n</demande>"


def texte_de(response: Any) -> str:
    """Concatène les blocs texte d'une réponse de l'API."""
    morceaux = []
    for bloc in getattr(response, "content", []) or []:
        if getattr(bloc, "type", None) == "text":
            morceaux.append(bloc.text)
    return "".join(morceaux)


def parse_domain_id(texte: str) -> str | None:
    """Retourne le premier identifiant de domaine connu trouvé dans la réponse."""
    for mot in re.findall(r"[a-z\-]+", texte.lower()):
        if mot in DOMAINS_BY_ID:
            return mot
    return None


def keyword_domain(message: str) -> str:
    """Domaine dont les mots-clés apparaissent le plus dans la demande."""
    texte = message.lower()
    meilleur, score_max = GENERAL_ID, 0
    for domaine in DOMAINS:
        score = sum(
            1 for mot in domaine.mots_cles if re.search(rf"(?<!\w){re.escape(mot)}", texte)
        )
        if score > score_max:
            meilleur, score_max = domaine.id, score
    return meilleur


class Router:
    def __init__(self, client: Any, model: str, max_tokens: int, usage: Usage | None = None):
        self.client = client
        self.model = model
        self.max_tokens = max_tokens
        self.usage = usage or Usage()

    def choose(self, message: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=ROUTER_SYSTEM,
                messages=[{"role": "user", "content": _router_prompt(message)}],
            )
            self.usage.add(response)
            trouve = parse_domain_id(texte_de(response))
            if trouve:
                return trouve
            log.info("Réponse de routage inexploitable, repli sur les mots-clés.")
        except Exception:  # le routage ne doit jamais bloquer la réponse
            log.warning("Routage par le modèle en échec, repli sur les mots-clés.", exc_info=True)
        return keyword_domain(message)


def domaine_par_id(domain_id: str) -> Domain:
    return DOMAINS_BY_ID.get(domain_id, DOMAINS_BY_ID[GENERAL_ID])
