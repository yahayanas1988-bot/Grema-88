"""Boucle de l'agent : routage, réponse en flux, outils, historique.

Points d'efficacité :
- le prompt de base et la consigne du domaine sont mis en cache côté API ;
- le dernier message est marqué pour le cache, donc chaque tour relit
  l'historique déjà traité à tarif réduit ;
- le routage se fait avec un petit modèle, et la réponse est streamée ;
- l'historique est borné, et la dernière étape d'outils se fait sans outils.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .config import Settings
from .domains import BASE_PROMPT, Domain
from .router import Router, domaine_par_id
from .tools import ToolBox, default_toolbox
from .usage import Usage

OnText = Callable[[str], None]
CACHE = {"type": "ephemeral"}


@dataclass(frozen=True)
class Answer:
    text: str
    domain: str
    stop_reason: str | None


def system_blocks(domain: Domain) -> list[dict[str, Any]]:
    return [
        {"type": "text", "text": BASE_PROMPT, "cache_control": CACHE},
        {
            "type": "text",
            "text": f"Spécialité active : {domain.nom}.\n{domain.consignes}",
            "cache_control": CACHE,
        },
    ]


def bloc_vers_param(bloc: Any) -> dict[str, Any]:
    """Convertit un bloc de réponse (objet SDK, dict ou autre) en bloc renvoyable à l'API."""
    if isinstance(bloc, dict):
        return {k: v for k, v in bloc.items() if v is not None}
    if hasattr(bloc, "model_dump"):
        return bloc.model_dump(exclude_none=True)
    return {k: v for k, v in vars(bloc).items() if v is not None}


def _message_utilisateur_simple(message: dict[str, Any]) -> bool:
    return message["role"] == "user" and isinstance(message["content"], str)


class ExpertAgent:
    def __init__(
        self,
        client: Any,
        settings: Settings | None = None,
        tools: ToolBox | None = None,
    ):
        self.client = client
        self.settings = settings or Settings()
        self.tools = tools if tools is not None else default_toolbox()
        self.usage = Usage()
        self.router = Router(
            client, self.settings.router_model, self.settings.router_max_tokens, self.usage
        )
        self.messages: list[dict[str, Any]] = []

    def reset(self) -> None:
        self.messages = []

    def route(self, question: str) -> str:
        """Domaine à utiliser pour cette question (imposé ou choisi automatiquement)."""
        if self.settings.forced_domain:
            return self.settings.forced_domain
        return self.router.choose(question)

    def ask(
        self,
        question: str,
        *,
        domain: str | None = None,
        on_text: OnText | None = None,
    ) -> Answer:
        expert = domaine_par_id(domain or self.route(question))
        debut = len(self.messages)
        self.messages.append({"role": "user", "content": question})
        try:
            texte, stop = self._boucle(expert, on_text)
        except BaseException:  # y compris Ctrl-C : pas de question sans réponse dans l'historique
            del self.messages[debut:]
            raise
        self._tailler_historique()
        return Answer(texte, expert.id, stop)

    def _boucle(self, expert: Domain, on_text: OnText | None) -> tuple[str, str | None]:
        system = system_blocks(expert)
        outils = self.tools.schemas()
        for etape in range(self.settings.max_tool_steps + 1):
            # Dernière étape sans outils : le modèle doit répondre en texte.
            avec_outils = outils if etape < self.settings.max_tool_steps else []
            reponse = self._appeler(system, avec_outils, on_text)
            self.usage.add(reponse)
            contenu = [bloc_vers_param(b) for b in reponse.content]
            self.messages.append({"role": "assistant", "content": contenu})

            if reponse.stop_reason != "tool_use":
                texte = "".join(b.get("text", "") for b in contenu if b.get("type") == "text")
                return texte, reponse.stop_reason

            resultats = []
            for bloc in contenu:
                if bloc.get("type") == "tool_use":
                    texte, erreur = self.tools.run(bloc["name"], bloc.get("input") or {})
                    resultats.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": bloc["id"],
                            "content": texte,
                            "is_error": erreur,
                        }
                    )
            if not resultats:
                return "", reponse.stop_reason
            self.messages.append({"role": "user", "content": resultats})
        raise RuntimeError("Boucle d'outils sans réponse finale.")

    def _appeler(self, system: list[dict[str, Any]], outils: list[dict[str, Any]], on_text: OnText | None):
        params: dict[str, Any] = {
            "model": self.settings.model,
            "max_tokens": self.settings.max_tokens,
            "system": system,
            "messages": self._messages_avec_cache(),
        }
        if outils:
            params["tools"] = outils
        if on_text is None:
            return self.client.messages.create(**params)
        with self.client.messages.stream(**params) as flux:
            for morceau in flux.text_stream:
                on_text(morceau)
            return flux.get_final_message()

    def _messages_avec_cache(self) -> list[dict[str, Any]]:
        """Copie de l'historique où le dernier bloc porte le point de cache."""
        if not self.messages:
            return []
        *avant, dernier = self.messages
        contenu = dernier["content"]
        blocs = [{"type": "text", "text": contenu}] if isinstance(contenu, str) else [dict(b) for b in contenu]
        if blocs:
            blocs[-1] = {**blocs[-1], "cache_control": CACHE}
        return [*avant, {"role": dernier["role"], "content": blocs}]

    def _tailler_historique(self) -> None:
        """Garde environ `max_history_messages` messages, en repartant d'une vraie question."""
        limite = self.settings.max_history_messages
        if len(self.messages) <= limite:
            return
        ancres = [i for i, m in enumerate(self.messages) if _message_utilisateur_simple(m)]
        if not ancres:
            return
        debut = len(self.messages) - limite
        candidats = [i for i in ancres if i >= debut]
        self.messages = self.messages[candidats[0] if candidats else ancres[-1]:]
