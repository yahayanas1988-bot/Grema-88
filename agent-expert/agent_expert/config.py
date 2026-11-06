"""Réglages de l'agent, lus dans les variables d'environnement."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # Modèle qui répond aux questions : le plus capable par défaut.
    model: str = "claude-opus-5-5"
    # Petit modèle rapide et peu coûteux qui choisit le domaine d'expertise.
    router_model: str = "claude-haiku-5-5"
    max_tokens: int = 4096
    router_max_tokens: int = 16
    # Nombre maximal d'allers-retours avec les outils pour une même question.
    max_tool_steps: int = 5
    # Nombre maximal de messages gardés dans l'historique (coût et latence).
    max_history_messages: int = 40
    # Domaine imposé (ex. "droit") ; None = routage automatique.
    forced_domain: str | None = None
    # Travail en équipe : nombre maximal de spécialistes consultés en parallèle.
    max_specialistes: int = 4
    planner_max_tokens: int = 600

    @classmethod
    def from_env(cls) -> Settings:
        env = os.environ
        return cls(
            model=env.get("AGENT_MODEL", cls.model),
            router_model=env.get("AGENT_ROUTER_MODEL", cls.router_model),
            max_tokens=int(env.get("AGENT_MAX_TOKENS", cls.max_tokens)),
            max_history_messages=int(env.get("AGENT_HISTORIQUE", cls.max_history_messages)),
            forced_domain=env.get("AGENT_DOMAINE") or None,
            max_specialistes=int(env.get("AGENT_SPECIALISTES", cls.max_specialistes)),
        )
