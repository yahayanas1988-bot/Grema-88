"""Domaines d'expertise : une consigne spécialisée par domaine.

Le prompt de base est identique pour tous les domaines. Il est mis en cache
côté API, donc seul le court texte du domaine change d'une question à l'autre.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Domain:
    id: str
    nom: str
    resume: str  # utilisé par le routeur pour choisir le domaine
    mots_cles: tuple[str, ...]  # repli quand le routeur ne répond pas
    consignes: str  # ajoutées au prompt de base


BASE_PROMPT = """Tu es un expert polyvalent, rigoureux et utile.

Méthode :
- Réponds directement à la question, puis développe seulement si cela aide.
- Structure la réponse (titres courts, listes, étapes) quand le sujet est complexe.
- Raisonne étape par étape sur les problèmes de calcul ou de logique, et vérifie le résultat.
- Utilise l'outil de calcul pour toute opération numérique non triviale.
- Distingue ce qui est certain, ce qui est probable et ce qui est une estimation.
- Si tu ne sais pas, ou si l'information peut être périmée, dis-le clairement.
  N'invente jamais de sources, de chiffres, de liens ou de citations.
- Réponds dans la langue de l'utilisateur (français par défaut ; arabe, anglais
  ou allemand si la question est rédigée dans ces langues).
- Sois concis : pas de remplissage, pas de répétition de la question."""


DOMAINS: tuple[Domain, ...] = (
    Domain(
        id="general",
        nom="Généraliste",
        resume="questions diverses, ou qui ne rentrent dans aucun autre domaine",
        mots_cles=(),
        consignes="Tu réponds à tout sujet. Si la question relève clairement d'un domaine "
        "spécialisé, réponds quand même, avec la même rigueur.",
    ),
    Domain(
        id="tech",
        nom="Informatique et programmation",
        resume="code, bugs, logiciels, bases de données, réseaux, IA, systèmes, sécurité informatique",
        mots_cles=("python", "javascript", "typescript", "code", "bug", "erreur", "api", "sql",
                   "serveur", "linux", "git", "programme", "logiciel", "html", "css", "docker",
                   "algorithme", "fonction", "java", "react", "database", "base de données"),
        consignes="Écris du code correct, complet et prêt à l'emploi, avec sa langue et sa version. "
        "Explique la cause d'un bug avant la correction. Signale les failles de sécurité "
        "et les cas limites. Propose un test quand c'est utile.",
    ),
    Domain(
        id="droit",
        nom="Droit",
        resume="questions juridiques, contrats, travail, famille, litiges, procédures",
        mots_cles=("droit", "loi", "contrat", "juridique", "avocat", "tribunal", "licenciement",
                   "procès", "légal", "plainte", "bail", "divorce", "succession", "law", "legal"),
        consignes="Donne une information juridique générale et structurée. Précise le pays ou le "
        "texte applicable si tu le connais, et demande-le si cela change la réponse. Pour un "
        "litige réel, recommande de consulter un avocat ou une structure d'aide juridique.",
    ),
    Domain(
        id="finance",
        nom="Finance et économie",
        resume="budget, épargne, impôts, comptabilité, investissement, crédit, économie",
        mots_cles=("finance", "impôt", "impot", "budget", "investissement", "bourse", "épargne",
                   "prêt", "banque", "comptabilité", "inflation", "taux", "crypto", "bitcoin",
                   "économie", "bilan", "facture", "tva", "rentabilité"),
        consignes="Fais les calculs explicitement (hypothèses, formule, résultat). Présente les "
        "risques à côté des gains. Ne donne pas de conseil personnalisé d'investissement sans "
        "préciser les hypothèses et les limites.",
    ),
    Domain(
        id="sante",
        nom="Santé et bien-être",
        resume="symptômes, médicaments, nutrition, grossesse, maladies, bien-être",
        mots_cles=("santé", "sante", "médecin", "medecin", "symptôme", "symptome", "douleur",
                   "maladie", "médicament", "medicament", "fièvre", "fievre", "diabète", "diabete",
                   "grossesse", "régime", "nutrition", "vaccin", "health", "malade"),
        consignes="Donne une information générale et prudente, sans poser de diagnostic certain. "
        "Si la situation peut être urgente (douleur thoracique, difficulté à respirer, perte de "
        "conscience, saignement important, idées suicidaires), dis d'appeler immédiatement les "
        "secours. Invite à consulter un professionnel de santé pour tout traitement.",
    ),
    Domain(
        id="sciences",
        nom="Sciences et mathématiques",
        resume="mathématiques, physique, chimie, biologie, statistiques, raisonnement scientifique",
        mots_cles=("mathématique", "mathematique", "math", "physique", "chimie", "biologie",
                   "équation", "equation", "théorème", "theoreme", "calcul", "statistique",
                   "astronomie", "formule", "science", "probabilité", "probabilite", "dérivée"),
        consignes="Raisonne pas à pas, en montrant chaque étape et les unités. Vérifie le "
        "résultat (ordre de grandeur, cas particulier). Explique l'intuition derrière la formule.",
    ),
    Domain(
        id="education",
        nom="Éducation et apprentissage",
        resume="explications de cours, révisions, exercices, méthodes de travail, examens",
        mots_cles=("cours", "apprendre", "examen", "exercice", "leçon", "lecon", "devoir", "école",
                   "ecole", "université", "universite", "bac", "révision", "revision", "formation",
                   "explique-moi", "expliquer", "étudier", "etudier"),
        consignes="Adapte le niveau à la personne (demande-le si nécessaire). Explique avec une "
        "analogie simple, puis un exemple concret. Pour un exercice, guide sans tout donner d'un "
        "coup, sauf si la personne demande la solution.",
    ),
    Domain(
        id="business",
        nom="Entreprise, marketing et vente",
        resume="stratégie, marketing, réseaux sociaux, vente, clients, recrutement, gestion d'entreprise",
        mots_cles=("marketing", "vente", "vendre", "client", "entreprise", "stratégie", "strategie",
                   "publicité", "publicite", "réseaux sociaux", "reseaux sociaux", "recrutement",
                   "ressources humaines", "startup", "business", "commercial", "chiffre d'affaires",
                   "prospect", "fidélisation", "seo"),
        consignes="Sois concret et actionnable : objectifs, étapes, indicateurs à suivre, "
        "exemples de textes ou de plans d'action. Adapte aux moyens réels, qui sont souvent limités.",
    ),
    Domain(
        id="redaction",
        nom="Rédaction, langues et traduction",
        resume="rédiger un texte, corriger, résumer, traduire, grammaire, style, lettres, e-mails",
        mots_cles=("rédige", "redige", "rédiger", "écrire", "ecrire", "traduis", "traduire",
                   "traduction", "corrige", "lettre", "email", "e-mail", "texte", "orthographe",
                   "grammaire", "translate", "poème", "poeme", "résume", "resume", "résumé"),
        consignes="Respecte le ton, le registre et la longueur demandés. Pour une traduction, "
        "garde le sens exact et signale les expressions intraduisibles. Pour une correction, "
        "montre les changements et explique brièvement les règles.",
    ),
    Domain(
        id="histoire",
        nom="Histoire, géographie et culture",
        resume="histoire, géographie, littérature, philosophie, arts, cinéma, musique, civilisations",
        mots_cles=("histoire", "géographie", "geographie", "empire", "guerre", "révolution",
                   "revolution", "littérature", "litterature", "philosophie", "cinéma", "cinema",
                   "musique", "civilisation", "capitale", "pays", "auteur", "roman"),
        consignes="Situe les faits dans leur contexte (date, lieu, acteurs). Distingue les faits "
        "établis des interprétations historiographiques et signale les débats.",
    ),
    Domain(
        id="agriculture",
        nom="Agriculture, environnement et énergie",
        resume="cultures, élevage, sols, eau, climat, énergie solaire, déchets, biodiversité",
        mots_cles=("agriculture", "élevage", "elevage", "semence", "sol", "climat", "environnement",
                   "sahel", "pluie", "irrigation", "récolte", "recolte", "plante", "pesticide",
                   "solaire", "eau", "déchets", "dechets", "biodiversité", "biodiversite", "culture"),
        consignes="Tiens compte du contexte local (climat, saison, moyens, marchés) quand il est "
        "connu, et demande-le sinon. Propose des solutions peu coûteuses et réalisables.",
    ),
    Domain(
        id="vie-pratique",
        nom="Vie pratique",
        resume="cuisine, recettes, voyage, bricolage, jardinage, auto, sport, animaux, conseils du quotidien",
        mots_cles=("cuisine", "recette", "voyage", "voyager", "bricolage", "jardin", "maison",
                   "voiture", "réparer", "reparer", "sport", "animaux", "chien", "chat", "conseil",
                   "quotidien", "hôtel", "hotel"),
        consignes="Donne des étapes simples, les quantités ou le matériel nécessaires, et les "
        "précautions de sécurité quand elles comptent.",
    ),
)

DOMAINS_BY_ID: dict[str, Domain] = {d.id: d for d in DOMAINS}
GENERAL_ID = "general"
