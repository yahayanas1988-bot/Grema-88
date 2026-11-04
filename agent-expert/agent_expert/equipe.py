"""Travail en équipe : le Patron répartit la demande entre les spécialistes.

1. Le Patron (petit modèle rapide) découpe la demande en tâches, une par domaine.
2. Une seule tâche : le spécialiste répond directement, en flux. C'est le cas
   le plus fréquent, et il ne coûte pas plus cher qu'un agent seul.
3. Plusieurs tâches : les spécialistes travaillent en parallèle, puis le Patron
   (modèle principal) assemble leurs rapports en une seule réponse, en flux.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from .agent import ExpertAgent, OnText
from .config import Settings
from .domains import DOMAINS, DOMAINS_BY_ID, GENERAL_ID
from .router import domaine_par_id, keyword_domain
from .tools import ToolBox

log = logging.getLogger(__name__)

# Appelé avec ("plan", [Domain]), ("rapport", Domain, réussi) puis ("synthese",).
OnEvent = Callable[..., None]


@dataclass(frozen=True)
class Tache:
    domaine: str
    consigne: str


@dataclass(frozen=True)
class Rapport:
    domaine: str
    texte: str
    erreur: str | None = None


@dataclass(frozen=True)
class TeamAnswer:
    text: str
    stop_reason: str | None
    taches: tuple[Tache, ...]
    rapports: tuple[Rapport, ...]


PATRON_SYSTEM = """Tu es le Patron d'une équipe d'experts. Tu répartis la demande entre les spécialistes avec l'outil `repartir`.

Règles :
- Une seule tâche quand un seul domaine suffit : c'est le cas le plus fréquent.
- Plusieurs tâches seulement si la demande couvre vraiment plusieurs domaines, {maxi} au maximum, jamais deux fois le même domaine.
- Chaque consigne doit se suffire à elle-même : le spécialiste ne voit que sa consigne et la demande d'origine."""


def outil_repartir(maxi: int) -> dict[str, Any]:
    return {
        "name": "repartir",
        "description": "Répartit la demande entre les spécialistes de l'équipe.",
        "input_schema": {
            "type": "object",
            "properties": {
                "taches": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": maxi,
                    "items": {
                        "type": "object",
                        "properties": {
                            "domaine": {"type": "string", "enum": [d.id for d in DOMAINS]},
                            "consigne": {
                                "type": "string",
                                "description": "Ce que ce spécialiste doit traiter, formulé pour lui.",
                            },
                        },
                        "required": ["domaine", "consigne"],
                    },
                }
            },
            "required": ["taches"],
        },
    }


def lire_taches(response: Any, question: str, maxi: int) -> list[Tache]:
    """Extrait les tâches de l'appel à `repartir`, en écartant ce qui est invalide."""
    brut: list[Any] = []
    for bloc in getattr(response, "content", []) or []:
        if getattr(bloc, "type", None) == "tool_use" and getattr(bloc, "name", None) == "repartir":
            brut = (getattr(bloc, "input", None) or {}).get("taches") or []
            break
    taches: list[Tache] = []
    vus: set[str] = set()
    for item in brut:
        if not isinstance(item, dict):
            continue
        domaine = item.get("domaine") if item.get("domaine") in DOMAINS_BY_ID else GENERAL_ID
        if domaine in vus:
            continue
        vus.add(domaine)
        taches.append(Tache(domaine, str(item.get("consigne") or "").strip() or question))
        if len(taches) == maxi:
            break
    return taches


def _contexte_recent(messages: list[dict[str, Any]], limite: int = 800) -> str:
    """Dernier échange de la conversation, pour que le Patron comprenne les suites."""
    question = reponse = ""
    for message in reversed(messages):
        if message["role"] == "assistant" and not reponse:
            reponse = "".join(
                b.get("text", "") for b in message["content"] if b.get("type") == "text"
            )
        elif message["role"] == "user" and isinstance(message["content"], str):
            question = message["content"]
            break
    if not question:
        return ""
    return f"Échange précédent :\nUtilisateur : {question[:limite]}\nRéponse : {reponse[:limite]}\n\n"


def _consigne_specialiste(question: str, tache: Tache) -> str:
    return (
        "Tu fais partie d'une équipe. Le chef d'équipe assemblera ta contribution avec "
        "celles des autres spécialistes.\n\n"
        f"Demande d'origine (pour le contexte) :\n<demande>\n{question}\n</demande>\n\n"
        f"Ta partie : {tache.consigne}\n\n"
        "Traite seulement ta partie, de façon complète et concise."
    )


def _prompt_synthese(question: str, rapports: list[Rapport]) -> str:
    blocs = []
    for rapport in rapports:
        corps = rapport.texte if rapport.erreur is None else f"(rapport indisponible : {rapport.erreur})"
        blocs.append(f'<rapport domaine="{domaine_par_id(rapport.domaine).nom}">\n{corps}\n</rapport>')
    return (
        f"Question de l'utilisateur :\n<question>\n{question}\n</question>\n\n"
        "Rapports de tes spécialistes :\n" + "\n\n".join(blocs) + "\n\n"
        "Tu es le chef d'équipe. Écris la réponse finale à l'utilisateur : une seule réponse "
        "cohérente, qui reprend l'essentiel de chaque rapport sans le recopier, signale les "
        "contradictions et les parties manquantes, et ne présente pas les rapports un par un."
    )


def _rien(*_: Any) -> None:
    pass


class Equipe:
    """Le Patron et ses spécialistes. La conversation est tenue par `self.agent`."""

    def __init__(self, client: Any, settings: Settings | None = None, tools: ToolBox | None = None):
        self.client = client
        self.settings = settings or Settings()
        self.agent = ExpertAgent(client, self.settings, tools)
        self.usage = self.agent.usage

    def reset(self) -> None:
        self.agent.reset()

    def planifier(self, question: str) -> list[Tache]:
        maxi = max(1, self.settings.max_specialistes)
        domaines = "\n".join(f"- {d.id} : {d.resume}" for d in DOMAINS)
        contenu = (
            f"Domaines :\n{domaines}\n\n{_contexte_recent(self.agent.messages)}"
            f"Demande :\n<demande>\n{question[:4000]}\n</demande>"
        )
        try:
            response = self.client.messages.create(
                model=self.settings.router_model,
                max_tokens=self.settings.planner_max_tokens,
                system=PATRON_SYSTEM.format(maxi=maxi),
                tools=[outil_repartir(maxi)],
                tool_choice={"type": "tool", "name": "repartir"},
                messages=[{"role": "user", "content": contenu}],
            )
            self.usage.add(response)
            taches = lire_taches(response, question, maxi)
            if taches:
                return taches
            log.info("Répartition inexploitable, repli sur les mots-clés.")
        except Exception:  # la répartition ne doit jamais bloquer la réponse
            log.warning("Répartition par le Patron en échec, repli sur les mots-clés.", exc_info=True)
        return [Tache(keyword_domain(question), question)]

    def ask(
        self,
        question: str,
        *,
        domain: str | None = None,
        on_text: OnText | None = None,
        on_event: OnEvent | None = None,
    ) -> TeamAnswer:
        evenement = on_event or _rien
        impose = domain or self.settings.forced_domain
        taches = [Tache(impose, question)] if impose else self.planifier(question)
        evenement("plan", [domaine_par_id(t.domaine) for t in taches])

        if len(taches) == 1:
            reponse = self.agent.ask(question, domain=taches[0].domaine, on_text=on_text)
            return TeamAnswer(reponse.text, reponse.stop_reason, tuple(taches), ())

        rapports = self._consulter(taches, question, evenement)
        evenement("synthese")
        reponse = self.agent.ask(
            _prompt_synthese(question, rapports), domain=GENERAL_ID, on_text=on_text
        )
        return TeamAnswer(reponse.text, reponse.stop_reason, tuple(taches), tuple(rapports))

    def _consulter(self, taches: list[Tache], question: str, evenement: OnEvent) -> list[Rapport]:
        """Fait travailler les spécialistes en parallèle ; un échec n'arrête pas les autres."""
        specialistes = [ExpertAgent(self.client, self.settings, self.agent.tools) for _ in taches]
        rapports: dict[int, Rapport] = {}
        erreurs: list[Exception] = []
        pool = ThreadPoolExecutor(max_workers=len(taches))
        try:
            futurs = {
                pool.submit(s.ask, _consigne_specialiste(question, t), domain=t.domaine): i
                for i, (s, t) in enumerate(zip(specialistes, taches))
            }
            for futur in as_completed(futurs):
                i = futurs[futur]
                tache = taches[i]
                try:
                    rapports[i] = Rapport(tache.domaine, futur.result().text)
                except Exception as exc:
                    log.warning("Le spécialiste %s n'a pas pu répondre : %s", tache.domaine, exc)
                    erreurs.append(exc)
                    rapports[i] = Rapport(tache.domaine, "", erreur=str(exc))
                evenement("rapport", domaine_par_id(tache.domaine), rapports[i].erreur is None)
        finally:
            pool.shutdown(wait=False, cancel_futures=True)
            for specialiste in specialistes:
                self.usage.fusionner(specialiste.usage)
        if len(erreurs) == len(taches):
            raise erreurs[0]
        return [rapports[i] for i in range(len(taches))]
