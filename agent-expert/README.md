# Agent IA expert polyvalent, qui travaille en équipe

Un agent en Python qui répond à tous les sujets en travaillant **en équipe**.
Un chef d'équipe, le **Patron**, lit la demande et la répartit entre des
spécialistes (droit, santé, informatique, finance…). Les spécialistes
travaillent **en parallèle**, puis le Patron assemble leurs rapports en une
seule réponse.

```
                         ┌─► spécialiste Droit    ─┐
question ──► Patron ─────┼─► spécialiste Finance  ─┼─► Patron : synthèse (en flux)
          (petit modèle, │   (en parallèle,        │
           outil         └─► …  outils compris)   ─┘
           « repartir »)
                │
                └─ un seul domaine suffit ? ─► le spécialiste répond directement (en flux)
```

- **Un seul domaine** (le cas le plus fréquent) : le spécialiste répond directement.
  Cela coûte autant qu'un agent seul : un petit appel de répartition, puis la réponse.
- **Plusieurs domaines** (« ouvrir une boutique : statut et impôts ? ») : chaque
  spécialiste traite sa partie, puis le Patron rédige la réponse finale. Si un
  spécialiste échoue, les autres continuent et la synthèse le signale.
- **Mode solo** (`--solo`) : un seul spécialiste par question, choisi par un routeur.

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

# Une question qui touche plusieurs domaines : l'équipe se répartit le travail
python -m agent_expert "Je veux ouvrir une boutique à Niamey : quel statut et quels impôts ?"

# Conversation (commandes : /aide)
python -m agent_expert

# Un seul spécialiste par question ; imposer un domaine ; lister les domaines
python -m agent_expert --solo "Explique-moi les fractions"
python -m agent_expert --domaine tech "Pourquoi ma requête SQL renvoie des doublons ?"
python -m agent_expert --domaines
```

Exemple d'affichage en équipe :

```
[Équipe : Droit, Finance et économie]
  ✓ Droit
  ✓ Finance et économie
[Synthèse du Patron]
…réponse finale, affichée au fur et à mesure…
```

Commandes dans la conversation : `/equipe`, `/solo`, `/domaine <id>`,
`/domaine auto`, `/domaines`, `/reset`, `/cout` (tokens consommés, équipe
comprise), `/quitter`.

## Réglages (variables d'environnement)

| Variable | Défaut | Rôle |
|---|---|---|
| `ANTHROPIC_API_KEY` | (obligatoire) | clé de l'API |
| `AGENT_MODEL` | `claude-opus-5-5` | modèle des spécialistes et de la synthèse |
| `AGENT_ROUTER_MODEL` | `claude-haiku-5-5` | modèle du Patron pour la répartition (et du routeur en solo) |
| `AGENT_SPECIALISTES` | `4` | nombre maximal de spécialistes par demande |
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

- **Équipe seulement quand c'est utile** : une demande à un seul domaine ne coûte pas plus
  qu'un agent seul. Une demande à N domaines coûte N réponses de spécialistes plus une
  synthèse, mais les spécialistes travaillent en même temps, donc l'attente reste celle
  d'un seul spécialiste plus la synthèse.
- **Répartition à bas coût** : le Patron répartit avec un petit modèle rapide, par un appel
  d'outil forcé qui renvoie une liste de tâches structurée (pas de texte à interpréter).
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
- La répartition peut se tromper. Imposez le domaine avec `--domaine` ou `/domaine` si besoin.

## Tests

Les tests utilisent un faux client : pas de clé API ni de réseau nécessaires.

```bash
python -m unittest -v
```

## Structure

```
agent_expert/
  cli.py        interface en ligne de commande (une question ou conversation)
  equipe.py     le Patron : répartition, spécialistes en parallèle, synthèse
  agent.py      un spécialiste : flux, outils, historique, cache
  router.py     choix du domaine en mode solo (modèle, puis mots-clés)
  domains.py    domaines d'expertise et prompt de base
  tools.py      outils et calculatrice sécurisée
  usage.py      compteur de tokens
  config.py     réglages lus dans l'environnement
tests/          tests unitaires
```
