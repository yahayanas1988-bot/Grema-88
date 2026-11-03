"""Interface en ligne de commande : une question, ou une conversation."""

from __future__ import annotations

import argparse
import dataclasses
import logging
import os
import sys

import anthropic

from .agent import ExpertAgent
from .config import Settings
from .domains import DOMAINS, DOMAINS_BY_ID
from .router import domaine_par_id

AIDE = """Commandes :
  /domaine <id>   imposer un domaine (ex. /domaine droit)
  /domaine auto   revenir au choix automatique
  /domaines       lister les domaines
  /reset          effacer la conversation
  /cout           afficher la consommation de tokens
  /quitter        sortir"""


def _repondre(agent: ExpertAgent, question: str, domaine_force: str | None) -> None:
    domaine = domaine_par_id(domaine_force or agent.route(question))
    print(f"\n[{domaine.nom}]", flush=True)
    reponse = agent.ask(
        question,
        domain=domaine.id,
        on_text=lambda morceau: print(morceau, end="", flush=True),
    )
    print()
    if reponse.stop_reason == "max_tokens":
        print("(réponse coupée par la limite de longueur ; augmentez AGENT_MAX_TOKENS)")


def _lister_domaines() -> None:
    for d in DOMAINS:
        print(f"{d.id:<14} {d.nom} : {d.resume}")


def _interactif(agent: ExpertAgent, domaine_force: str | None) -> int:
    print("Agent expert prêt. Posez votre question, ou tapez /aide.")
    while True:
        try:
            ligne = input("vous > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not ligne:
            continue
        if ligne in ("/quitter", "/q"):
            return 0
        if ligne == "/aide":
            print(AIDE)
        elif ligne == "/reset":
            agent.reset()
            print("Conversation effacée.")
        elif ligne == "/cout":
            print(agent.usage.resume())
        elif ligne == "/domaines":
            _lister_domaines()
        elif ligne.startswith("/domaine"):
            arg = ligne[len("/domaine"):].strip()
            if arg in ("", "auto"):
                domaine_force = None
                print("Choix automatique du domaine.")
            elif arg in DOMAINS_BY_ID:
                domaine_force = arg
                print(f"Domaine imposé : {DOMAINS_BY_ID[arg].nom}")
            else:
                print(f"Domaine inconnu : {arg}. Voir /domaines.")
        else:
            try:
                _repondre(agent, ligne, domaine_force)
            except KeyboardInterrupt:
                print("\n(interrompu)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agent_expert",
        description="Agent IA polyvalent qui s'appuie sur des spécialistes par domaine.",
    )
    parser.add_argument(
        "question",
        nargs="*",
        help="question à poser ; sans question, lance une conversation interactive",
    )
    parser.add_argument("--domaine", choices=sorted(DOMAINS_BY_ID), help="imposer un domaine")
    parser.add_argument("--domaines", action="store_true", help="lister les domaines et quitter")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")

    if args.domaines:
        _lister_domaines()
        return 0
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Définissez la variable ANTHROPIC_API_KEY avant de lancer l'agent.", file=sys.stderr)
        return 2

    settings = Settings.from_env()
    if args.domaine:
        settings = dataclasses.replace(settings, forced_domain=args.domaine)
    # Réessais automatiques sur erreurs réseau, surcharge (429, 529) et délais dépassés.
    client = anthropic.Anthropic(max_retries=3, timeout=120.0)
    agent = ExpertAgent(client, settings)

    try:
        if args.question:
            _repondre(agent, " ".join(args.question), None)
            return 0
        return _interactif(agent, None)
    except anthropic.APIError as exc:
        print(f"Erreur de l'API : {exc}", file=sys.stderr)
        return 1
