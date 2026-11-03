# Agent IA expert polyvalent

Un agent en Python qui répond à tous les sujets. Une question est d'abord
envoyée à un petit modèle rapide qui choisit le **domaine d'expertise**
(droit, santé, informatique, finance…). La réponse est ensuite donnée par le
modèle le plus capable, avec la consigne spécialisée de ce domaine.

```
question ──► routeur (petit modèle, 1 mot) ──► domaine ──┐
                                 └─ repli : mots-clés    │
                                                         ▼
historique ◄── boucle d'outils ◄── expert (modèle principal, en flux)
                  calculer, date_heure
```

## Installation

```bash
cd agent-expert
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="votre-clé"
```

## Utilisation

```bash
# Une question
python -m agent_expert "Mon employeur peut-il me licencier pendant un arrêt maladie ?"

# Conversation (commandes : /aide)
python -m agent_expert

# Imposer un domaine, lister les domaines
python -m agent_expert --domaine tech "Pourquoi ma requête SQL renvoie des doublons ?"
python -m agent_expert --domaines
```

Commandes dans la conversation : `/domaine <id>`, `/domaine auto`, `/domaines`,
`/reset`, `/cout` (tokens consommés), `/quitter`.

## Réglages (variables d'environnement)

| Variable | Défaut | Rôle |
|---|---|---|
| `ANTHROPIC_API_KEY` | (obligatoire) | clé de l'API |
| `AGENT_MODEL` | `claude-opus-5-5` | modèle qui répond |
| `AGENT_ROUTER_MODEL` | `claude-haiku-5-5` | modèle qui choisit le domaine |
| `AGENT_MAX_TOKENS` | `4096` | longueur maximale d'une réponse |
| `AGENT_HISTORIQUE` | `40` | nombre de messages gardés dans la conversation |
| `AGENT_DOMAINE` | (vide) | imposer un domaine pour toutes les questions |

Pour un coût plus bas, `AGENT_MODEL=claude-sonnet-5-5` garde une bonne qualité.

## Domaines

Les domaines sont dans `agent_expert/domains.py`. Chacun a une consigne propre,
une description pour le routeur, et des mots-clés de secours.

`general`, `tech`, `droit`, `finance`, `sante`, `sciences`, `education`,
`business`, `redaction`, `histoire`, `agriculture`, `vie-pratique`.

Pour en ajouter un, ajoutez un `Domain(...)` à `DOMAINS`.

## Efficacité

- **Routage à bas coût** : un petit modèle ne renvoie qu'un identifiant (16 tokens au plus).
- **Prompt mis en cache** : le prompt de base et la consigne du domaine sont marqués
  pour le cache, et le dernier message aussi, donc chaque tour relit l'historique à tarif réduit.
  Le cache ne s'active qu'au-delà d'une certaine taille de préfixe (environ 1 000 tokens
  selon le modèle) : pour les questions très courtes, il n'y a pas d'économie.
- **Réponse en flux** : le texte s'affiche au fur et à mesure.
- **Historique borné** : les anciens messages sont retirés sans couper un appel d'outil.
- **Réessais** : le SDK réessaie automatiquement en cas d'erreur réseau, de surcharge ou de délai dépassé (3 fois).
- **Compteur de tokens** : `/cout` affiche la consommation réelle, y compris les lectures de cache.

## Outils

Outils fournis : `calculer` (arithmétique exacte, sans `eval`) et `date_heure`.
Pour en ajouter un, créez un `Tool` dans `agent_expert/tools.py` et ajoutez-le à
`default_toolbox()`. Une recherche web, par exemple, s'ajoute de la même façon :
sans outil de recherche, l'agent ne connaît que ce que contient son entraînement.

## Limites

- Les connaissances du modèle ont une date limite. Pour l'actualité, branchez un outil de recherche.
- Les domaines santé, droit et finance donnent une information générale, pas un avis professionnel.
  L'agent le signale quand c'est nécessaire.
- Le routage peut se tromper. Imposez le domaine avec `--domaine` ou `/domaine` si besoin.

## Tests

Les tests utilisent un faux client : pas de clé API ni de réseau nécessaires.

```bash
python -m unittest -v
```

## Structure

```
agent_expert/
  cli.py        interface en ligne de commande (une question ou conversation)
  agent.py      boucle de l'agent : routage, flux, outils, historique, cache
  router.py     choix du domaine (modèle, puis mots-clés)
  domains.py    domaines d'expertise et prompt de base
  tools.py      outils et calculatrice sécurisée
  usage.py      compteur de tokens
  config.py     réglages lus dans l'environnement
tests/          tests unitaires
```
