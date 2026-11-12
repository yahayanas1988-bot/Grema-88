# Agent Grema sur n8n : guide d'installation

Tout tient dans **un seul workflow** (un seul écran dans n8n) et **un seul tableau de bord** que n8n affiche lui-même.

## Ce que fait le workflow

```
 Entrées                    Tri                       Équipe                          Réponse
 📱 WhatsApp ─┐                                   ┌─ 💬 Agent WhatsApp ─┐
 🌐 Tableau ──┤                                   ├─ 📣 Agent Réseaux  ─┤
 💬 Chat test ┼─ ⚙️ Réglages ─ C'est GREMA ? ─ 🧭 Patron ─┼─ 🛍️ Agent Ventes   ─┼─ 📝 Préparer ─ 🗒️ Journal ─ 🔀 WhatsApp / Tableau / Chat
 ⏰ 7 h, 20 h ┘        │                          ├─ 🔎 Agent Recherche ─┤
                       └─ client ──────────────────► 💬 Agent WhatsApp    ├─ 📋 Agent Rapports ─┤
                                                  ├─ 🎬 Agent Créatif  ─┤
                                                  ├─ 💰 Agent Finances ─┤
                                                  └─ 👑 Agent Patron   ─┘
```

- **Agent Patron (🧭)** lit chaque demande de GREMA et la confie au bon agent parmi 7 :

| Agent | Son travail | Ses outils |
|---|---|---|
| 💬 WhatsApp | Répond aux clients, prend les commandes | mémoire |
| 📣 Réseaux | Légendes, hashtags, plans TikTok / YouTube / Facebook | Internet |
| 🛍️ Ventes | Boutique, vendeurs, offres (RDV Pro) | calculatrice |
| 🔎 Recherche | Prix, concurrents, actualité du Niger, analyse produit /10 | Internet, Wikipédia, calculatrice |
| 📋 Rapports | ☀️ Ma journée (7 h), résumé du soir (20 h) | mémoire |
| 🎬 Créatif | Scénarios vidéo FR/EN, livres, dessin animé, affiches | Wikipédia |
| 💰 Finances | Caisse, marges, devis, FCFA ↔ euro, mobile money | calculatrice, Internet |
| 👑 Patron | Discussion, conseils, demandes qui touchent plusieurs agents | les trois |

- **Tout passe par Claude** : le même compte Claude (API Anthropic) fait réfléchir les 8 agents et fait aussi la recherche Internet (outil « Recherche Internet (Claude) »).
- **Les clients** qui écrivent sur WhatsApp parlent seulement à l'Agent WhatsApp (ils ne voient rien d'interne).
- **7 h** : « ☀️ Ma journée » ; **20 h** : résumé du soir. Les deux arrivent sur le WhatsApp de GREMA.
- **Solide** : si Claude ne répond pas, l'agent envoie « 😔 Petit souci technique… » au lieu de rester muet ; si le tri échoue, c'est le Patron qui répond ; un échec d'envoi WhatsApp ne bloque pas le reste.
- **Une mémoire par conversation** (20 derniers messages), partagée par tous les agents.
- **Règle d'or** écrite dans chaque agent : ils préparent, ils ne publient, ne paient et n'envoient rien à un tiers sans ton « oui ».

## 1. Importer (2 minutes)

1. Ouvre ton n8n (n8n.cloud ou ton propre serveur, version 1.80 ou plus récente).
2. **Workflows → ➕ → ⋯ (en haut à droite) → Import from File** et choisis `workflow-agent-grema.json`.
3. Tout apparaît sur un seul écran, rangé en 4 zones de couleur.

## 2. Créer les 3 identifiants

| Identifiant | Où le trouver | Nœuds concernés |
|---|---|---|
| **Claude (Anthropic API)** | console.anthropic.com → API Keys → Create Key. Attention : c'est payé à l'usage, à part de ton abonnement Claude (quelques centimes par message, environ 1 centime de plus par recherche Internet). | 🧠 Claude (le cerveau) **et** Recherche Internet (Claude) |
| **WhatsApp** (2 identifiants) | developers.facebook.com → ton app → WhatsApp → API Setup. **WhatsApp API** : jeton d'accès permanent + ID du compte WhatsApp Business. **WhatsApp OAuth API** (pour recevoir) : ID et clé secrète de l'app (App settings → Basic). | 📱 WhatsApp : message reçu, 📤 Répondre sur WhatsApp |
| **Clé du tableau de bord** | Type **Header Auth**. Nom : `X-Grema-Cle`. Valeur : un mot de passe long que tu inventes. Nomme-le « Clé tableau de bord Grema ». | 🌐 Tableau de bord : demande |

Pour chaque nœud listé : double-clic → champ **Credential** → choisis l'identifiant.

Modèle : le nœud 🧠 et l'outil Recherche Internet utilisent `claude-sonnet-5-5`. Si ta clé ne le propose pas, choisis un autre modèle Claude dans la liste du nœud 🧠 et change le nom dans l'outil Recherche Internet.

## 3. Remplir ⚙️ Réglages

Double-clic sur **⚙️ Réglages** :
- `numeroGrema` : ton numéro WhatsApp **sans + ni espaces**, ex. `4917612345678`.
- `idNumeroWhatsApp` : le « Phone number ID » de la page API Setup de Meta.

## 4. Tester sans rien risquer

1. Clique sur **💬 Chat de test** → **Open chat** et écris « Salam aleykoum patron » puis « prépare 3 légendes TikTok pour RDV Pro ».
2. Regarde quel agent a répondu (le chemin s'allume en vert).

## 5. Activer

Clique sur **Activate / Publish** en haut. Ensuite :
- **Tableau de bord** : ouvre le lien de production du nœud **🖥️ Ouvrir le tableau de bord** en ajoutant ta clé à la fin :
  `https://ton-n8n/webhook/grema-tableau#cle=TA_CLE`
  Garde ce lien en favori ou sur l'écran d'accueil du téléphone (ne le partage pas : il contient ta clé). Sans `#cle=…`, la page te demande la clé avec 🔑.
- Sur le tableau de bord : à gauche les 6 agents (touche-en un pour lui parler directement, sinon le Patron choisit), au centre le chat et les raccourcis, à droite le journal du jour (échanges, messages WhatsApp, clients).
- Sur Meta, l'abonnement aux messages se fait tout seul à l'activation.

## Bon à savoir

- **Un numéro WhatsApp = un seul robot.** Si le numéro est déjà relié à MyChatBot, il faut choisir : MyChatBot **ou** n8n.
- **Règle des 24 h de WhatsApp** : le message de 7 h / 20 h n'arrive que si tu as écrit au numéro du robot dans les dernières 24 h (sinon il faut un modèle de message validé par Meta).
- **La mémoire de conversation** se vide si n8n redémarre (pour une mémoire durable : remplacer le nœud 🗂️ par une mémoire Postgres ou Redis).
- **Le journal** du tableau de bord garde les 200 derniers échanges. Il se remplit seulement quand le workflow est activé (pas en test).
- **Ajouter un agent** : copie un agent, change sa consigne, ajoute une catégorie du même nom dans 🧭 Agent Patron et relie la nouvelle sortie.
- **Changer les heures** : nœud ⏰, expression `0 7,20 * * *` (heure d'Allemagne).

## Ce qui a été vérifié

Le workflow a été importé et activé dans un vrai n8n (version 2.47), avec un faux Claude (simulé) pour les tests :
- le tableau de bord s'ouvre, refuse une mauvaise clé et répond avec la bonne ;
- le Patron envoie bien chaque demande au bon agent (Réseaux, Ventes, Recherche, Créatif, Finances, Patron) ;
- l'Agent Recherche utilise bien la recherche Internet via Claude et reprend le résultat dans sa réponse ;
- un client WhatsApp va seulement à l'Agent WhatsApp, et la réponse part vers son numéro ;
- les accusés de lecture WhatsApp sont ignorés ;
- quand Claude est en panne (simulée), l'agent répond quand même avec un message d'excuse ;
- le journal se remplit et la page tient sur un écran de téléphone.

Pas encore testé pour de vrai : l'envoi chez Meta (WhatsApp) et les réponses de Claude, car il faut tes propres clés.
