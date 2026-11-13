"""Outils que le modèle peut appeler pendant une réponse.

Ajouter un outil : créer un `Tool` (nom, description, schéma JSON, fonction)
et l'ajouter à `default_toolbox()`. La fonction reçoit les arguments en dict
et renvoie du texte. Une exception devient un résultat d'erreur pour le modèle.
"""

from __future__ import annotations

import ast
import math
import operator
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    schema: dict[str, Any]
    fn: Callable[[dict[str, Any]], str]


class ToolBox:
    def __init__(self, tools: Iterable[Tool] = ()):
        self._tools: dict[str, Tool] = {t.name: t for t in tools}

    def schemas(self) -> list[dict[str, Any]]:
        return [
            {"name": t.name, "description": t.description, "input_schema": t.schema}
            for t in self._tools.values()
        ]

    def run(self, name: str, args: dict[str, Any]) -> tuple[str, bool]:
        """Exécute un outil. Retourne (texte, est_une_erreur)."""
        outil = self._tools.get(name)
        if outil is None:
            return f"Outil inconnu : {name}", True
        try:
            return str(outil.fn(args)), False
        except Exception as exc:  # l'erreur est renvoyée au modèle, pas à l'utilisateur
            return f"Erreur : {exc}", True


# --- Calculatrice -----------------------------------------------------------
# Évaluation par arbre syntaxique, sans eval(), avec une liste blanche d'opérations.

_OPERATEURS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_FONCTIONS: dict[str, Callable[..., float]] = {
    "sqrt": math.sqrt,
    "log": math.log,
    "exp": math.exp,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
}
_EXPOSANT_MAX = 1000
_LONGUEUR_MAX = 200


def evaluer(expression: str) -> float:
    if len(expression) > _LONGUEUR_MAX:
        raise ValueError("expression trop longue")
    arbre = ast.parse(expression.strip(), mode="eval")
    return _eval(arbre.body)


def _eval(noeud: ast.AST) -> float:
    if isinstance(noeud, ast.Constant) and type(noeud.value) in (int, float):
        return noeud.value
    if isinstance(noeud, ast.BinOp) and type(noeud.op) in _OPERATEURS:
        gauche, droite = _eval(noeud.left), _eval(noeud.right)
        if isinstance(noeud.op, ast.Pow) and abs(droite) > _EXPOSANT_MAX:
            raise ValueError("exposant trop grand")
        return _OPERATEURS[type(noeud.op)](gauche, droite)
    if isinstance(noeud, ast.UnaryOp) and isinstance(noeud.op, (ast.UAdd, ast.USub)):
        valeur = _eval(noeud.operand)
        return +valeur if isinstance(noeud.op, ast.UAdd) else -valeur
    if (
        isinstance(noeud, ast.Call)
        and isinstance(noeud.func, ast.Name)
        and noeud.func.id in _FONCTIONS
        and not noeud.keywords
    ):
        return _FONCTIONS[noeud.func.id](*[_eval(a) for a in noeud.args])
    raise ValueError("expression non autorisée")


def _calculer(args: dict[str, Any]) -> str:
    resultat = evaluer(str(args["expression"]))
    if isinstance(resultat, float) and resultat.is_integer() and abs(resultat) < 1e15:
        resultat = int(resultat)
    return str(resultat)


def _date_heure(_: dict[str, Any]) -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


CALCULATRICE = Tool(
    name="calculer",
    description=(
        "Calcule une expression mathématique exacte. Opérateurs + - * / // % **, "
        "parenthèses, et fonctions sqrt, log, exp, abs, round, min, max."
    ),
    schema={
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Ex. (12.5*4)+sqrt(9)"},
        },
        "required": ["expression"],
    },
    fn=_calculer,
)

DATE_HEURE = Tool(
    name="date_heure",
    description="Donne la date et l'heure actuelles (UTC). À utiliser pour toute question sur 'aujourd'hui'.",
    schema={"type": "object", "properties": {}},
    fn=_date_heure,
)


def default_toolbox() -> ToolBox:
    return ToolBox([CALCULATRICE, DATE_HEURE])
