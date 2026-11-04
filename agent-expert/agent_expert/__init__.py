"""Agent IA expert polyvalent : une équipe de spécialistes dirigée par un Patron."""

from .agent import Answer, ExpertAgent
from .config import Settings
from .domains import DOMAINS, DOMAINS_BY_ID
from .equipe import Equipe, TeamAnswer
from .tools import ToolBox, default_toolbox

__all__ = [
    "Answer",
    "DOMAINS",
    "DOMAINS_BY_ID",
    "Equipe",
    "ExpertAgent",
    "Settings",
    "TeamAnswer",
    "ToolBox",
    "default_toolbox",
]
