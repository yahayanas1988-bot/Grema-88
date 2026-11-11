"""Génère le workflow n8n « Agent Grema » (un seul écran) dans workflow-agent-grema.json."""
import json, uuid, sys, pathlib

ICI = pathlib.Path(__file__).parent
SORTIE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ICI / "workflow-agent-grema.json"
HTML = (ICI / "tableau.html").read_text(encoding="utf-8")

V = {  # versions de nœuds (vérifiées contre n8n installé)
    "agent": 2.2, "classifier": 1.1, "anthropic": 1.3, "memory": 1.3, "wiki": 1, "calc": 1,
    "chat": 1.1, "webhook": 2, "respond": 1.1, "set": 3.4, "if": 2.2, "switch": 3.2,
    "schedule": 1.2, "wa": 1, "watrigger": 1, "code": 2, "sticky": 1, "filter": 2.2,
}

nodes, conns = [], {}

def nid():
    return str(uuid.uuid4())

def node(name, typ, ver, pos, params, **extra):
    n = {"parameters": params, "id": nid(), "name": name, "type": typ, "typeVersion": ver, "position": list(pos)}
    n.update(extra)
    nodes.append(n)
    return name

def lien(src, dst, out=0, kind="main", idx=0):
    c = conns.setdefault(src, {}).setdefault(kind, [])
    while len(c) <= out:
        c.append([])
    c[out].append({"node": dst, "type": kind, "index": idx})

def sset(name, pos, champs, inclure=False):
    p = {"mode": "manual", "assignments": {"assignments": [
        {"id": nid(), "name": k, "value": v, "type": t} for k, v, t in champs]}, "options": {}}
    if inclure:
        p["includeOtherFields"] = True
    return node(name, "n8n-nodes-base.set", V["set"], pos, p)

def note(texte, pos, l, h, couleur=None):
    p = {"content": texte, "height": h, "width": l}
    if couleur:
        p["color"] = couleur
    node(f"Note {len(nodes)}", "n8n-nodes-base.stickyNote", V["sticky"], pos, p)

def cond_str(gauche, op, droite=""):
    c = {"id": nid(), "leftValue": gauche, "rightValue": droite, "operator": {"type": "string", "operation": op}}
    if op in ("empty", "notEmpty"):
        c["operator"]["singleValue"] = True
        c.pop("rightValue")
    return c

def conditions(liste, comb="and"):
    return {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
            "conditions": liste, "combinator": comb}

# ---------------------------------------------------------------- notes
note("## 👑 Agent Grema — tout sur un seul écran\n"
     "**Entrées** à gauche (WhatsApp, tableau de bord, chat de test, réveil 7 h / 20 h) → "
     "**Agent Patron** au centre qui confie la demande au bon agent → **réponse** à droite, "
     "renvoyée par le même chemin et notée dans le journal du tableau de bord.\n\n"
     "Avant d'activer : remplir **⚙️ Réglages** et créer 3 identifiants (Claude, WhatsApp, clé du tableau de bord). "
     "Voir le guide.\n\n"
     "Règle d'or : les agents **préparent** ; rien n'est publié, payé ou envoyé à un tiers sans le « oui » de GREMA.",
     (-720, -520), 760, 300, 4)
note("### 1. Entrées", (-720, -180), 760, 1060, 7)
note("### 2. Tri et sécurité\nLes clients WhatsApp parlent seulement à l'Agent WhatsApp. "
     "GREMA (son numéro, le tableau de bord, le chat, les réveils) passe par le Patron.", (80, -180), 820, 1060, 6)
note("### 3. Agent Patron et ses 7 agents\nUn seul cerveau Claude et une mémoire partagée par conversation : "
     "les agents forment une famille.", (940, -420), 1200, 1680, 5)
note("### 4. Réponse et journal", (2180, -180), 1000, 1060, 7)

# ---------------------------------------------------------------- 1. entrées
X0 = -660
node("📱 WhatsApp : message reçu", "n8n-nodes-base.whatsAppTrigger", V["watrigger"], (X0, -60),
     {"updates": ["messages"]}, webhookId=nid())
sset("Lire le message WhatsApp", (X0 + 300, -60), [
    ("texte", "={{ $json.messages?.[0]?.text?.body ?? $json.messages?.[0]?.button?.text ?? '' }}", "string"),
    ("canal", "whatsapp", "string"),
    ("expediteur", "={{ $json.messages?.[0]?.from ?? '' }}", "string"),
    ("nom", "={{ $json.contacts?.[0]?.profile?.name ?? '' }}", "string"),
    ("sessionId", "={{ 'wa-' + ($json.messages?.[0]?.from ?? 'inconnu') }}", "string"),
])
lien("📱 WhatsApp : message reçu", "Lire le message WhatsApp")

node("🌐 Tableau de bord : demande", "n8n-nodes-base.webhook", V["webhook"], (X0, 200), {
    "httpMethod": "POST", "path": "agent-grema", "authentication": "headerAuth",
    "responseMode": "responseNode", "options": {"allowedOrigins": "*"}}, webhookId=nid())
node("Journal demandé ?", "n8n-nodes-base.if", V["if"], (X0 + 220, 200), {
    "conditions": conditions([cond_str("={{ $json.body?.action }}", "equals", "journal")]), "options": {}})
lien("🌐 Tableau de bord : demande", "Journal demandé ?")
node("Lire le journal", "n8n-nodes-base.code", V["code"], (X0 + 440, 100), {
    "jsCode": "const memo = $getWorkflowStaticData('global');\nreturn [{ json: { journal: memo.journal || [] } }];"})
lien("Journal demandé ?", "Lire le journal", 0)
node("↩️ Envoyer le journal", "n8n-nodes-base.respondToWebhook", V["respond"], (X0 + 660, 100), {
    "respondWith": "json", "responseBody": "={{ $json }}", "options": {}})
lien("Lire le journal", "↩️ Envoyer le journal")
sset("Lire la demande du tableau", (X0 + 440, 300), [
    ("texte", "={{ ($json.body?.agent ? '[Demande pour l\\'agent ' + $json.body.agent + '] ' : '') + ($json.body?.message ?? '') }}", "string"),
    ("canal", "tableau", "string"),
    ("expediteur", "GREMA", "string"),
    ("nom", "GREMA", "string"),
    ("sessionId", "={{ $json.body?.session || 'tableau-grema' }}", "string"),
])
lien("Journal demandé ?", "Lire la demande du tableau", 1)

node("🖥️ Ouvrir le tableau de bord", "n8n-nodes-base.webhook", V["webhook"], (X0, 480), {
    "path": "grema-tableau", "responseMode": "responseNode", "options": {}}, webhookId=nid())
node("Afficher le tableau de bord", "n8n-nodes-base.respondToWebhook", V["respond"], (X0 + 300, 480), {
    "respondWith": "text", "responseBody": HTML,
    "options": {"responseHeaders": {"entries": [{"name": "Content-Type", "value": "text/html; charset=utf-8"}]}}})
lien("🖥️ Ouvrir le tableau de bord", "Afficher le tableau de bord")

node("💬 Chat de test", "@n8n/n8n-nodes-langchain.chatTrigger", V["chat"], (X0, 660), {"options": {}}, webhookId=nid())
sset("Lire le chat", (X0 + 300, 660), [
    ("texte", "={{ $json.chatInput }}", "string"), ("canal", "chat", "string"),
    ("expediteur", "GREMA", "string"), ("nom", "GREMA", "string"),
    ("sessionId", "={{ $json.sessionId }}", "string"),
])
lien("💬 Chat de test", "Lire le chat")

node("⏰ Réveil 7 h et 20 h", "n8n-nodes-base.scheduleTrigger", V["schedule"], (X0, 820), {
    "rule": {"interval": [{"field": "cronExpression", "expression": "0 7,20 * * *"}]}})
sset("Ma journée / résumé du soir", (X0 + 300, 820), [
    ("texte", "={{ $now.hour < 12 ? '[Demande pour l\\'agent rapports] ☀️ Ma journée : prépare le plan du jour de GREMA en 5 points courts (priorités, une idée réseaux, une action ventes).' : '[Demande pour l\\'agent rapports] 🌙 Fais le résumé du jour pour GREMA en 5 points courts et propose 1 priorité pour demain.' }}", "string"),
    ("canal", "whatsapp", "string"), ("expediteur", "GREMA", "string"),
    ("nom", "GREMA", "string"), ("sessionId", "grema-rapports", "string"),
])
lien("⏰ Réveil 7 h et 20 h", "Ma journée / résumé du soir")

# ---------------------------------------------------------------- 2. tri
REG = "⚙️ Réglages"
sset(REG, (140, 300), [
    ("numeroGrema", "49XXXXXXXXXXX", "string"),
    ("idNumeroWhatsApp", "XXXXXXXXXXXXXXX", "string"),
], inclure=True)
for src in ["Lire le message WhatsApp", "Lire la demande du tableau", "Lire le chat", "Ma journée / résumé du soir"]:
    lien(src, REG)

node("Message vide ?", "n8n-nodes-base.filter", V["filter"], (360, 300), {
    "conditions": conditions([cond_str("={{ $json.texte }}", "notEmpty")]), "options": {}})
lien(REG, "Message vide ?")

node("C'est GREMA ?", "n8n-nodes-base.if", V["if"], (580, 300), {
    "conditions": conditions([
        cond_str("={{ $json.expediteur }}", "equals", "GREMA"),
        cond_str("={{ $json.expediteur }}", "equals", "={{ $json.numeroGrema }}"),
    ], "or"), "options": {}})
lien("Message vide ?", "C'est GREMA ?")

# ---------------------------------------------------------------- 3. agents
BASE = (
    "Tu fais partie de l'équipe d'agents IA de Grema 88 (Grema Agence 88), fondée par GREMA "
    "(Yahaya Nassirou Maman Grema, vit en Allemagne). Grema 88 : applications (RDV Pro en ligne sur rdv-pro.netlify.app, "
    "Nessa Tazo Kussa taxi-moto en prototype), livres, vidéos (dessin animé « Le Conseil de la Savane »), et une boutique "
    "de produits africains « du Sahel pour l'Afrique et le monde » (vendeurs africains, commande par WhatsApp, prix en FCFA, "
    "ex. pagne wax 12 000, miel 1 L 5 000). Paiement : Airtel Money, Moov Money, Orange Money, Wave, espèces à la livraison. "
    "Site : grema88.netlify.app. Réseaux : TikTok et YouTube « grema.11 ».\n\n"
    "Règles :\n"
    "- Réponds dans la langue du message (français par défaut ; GREMA parle aussi haoussa, zarma, allemand, anglais, arabe, "
    "italien). Il écrit souvent en phonétique : comprends-le sans le corriger.\n"
    "- Style WhatsApp : court, chaleureux, clair, quelques emojis, pas de longs pavés. Réponse longue seulement si on demande "
    "« en détail », « complet » ou « sans limite ».\n"
    "- Salue selon l'heure ; si on t'écrit « Salam aleykoum », réponds « Wa aleykoum salam ».\n"
    "- Avance seul avec le choix le plus logique, ne fais jamais répéter. Termine si utile par une question avec 2 ou 3 choix.\n"
    "- Tu PRÉPARES : tu ne prétends jamais avoir publié, payé, envoyé à un tiers ou commandé. Pour toute action réelle, "
    "propose le texte prêt et demande le « oui » de GREMA.\n"
    "- N'invente jamais un prix, un stock, un chiffre ou une date : si tu ne sais pas, dis-le et propose comment le trouver.\n"
    "- Esprit d'équipe : vous êtes une famille qui gagne ensemble ; cite le travail des collègues, jamais de critique.\n"
)
AGENTS = [
    ("whatsapp", "💬 Agent WhatsApp", "Clients et commandes sur WhatsApp",
     "Tu es l'Agent WhatsApp, le vendeur et service client de la boutique Grema 88. Tu réponds aux CLIENTS : produits, "
     "prix connus, commande, livraison, paiement mobile money. Pour une commande, récapitule (produit, quantité, prix si connu, "
     "ville, paiement) et dis qu'un vendeur va confirmer. Ne donne jamais d'information interne sur GREMA, l'agence ou les "
     "autres clients. Si le client est fâché ou si la demande dépasse la boutique, propose qu'un humain le rappelle."),
    ("reseaux", "📣 Agent Réseaux", "Publications TikTok, YouTube, Facebook, Instagram",
     "Tu es l'Agent Réseaux. Tu écris les légendes, hashtags, idées de vidéos, plans de publication et meilleures heures "
     "(Niamey et diaspora). Toujours prêt-à-copier. Pense aux fêtes : Ramadan, Tabaski, 18 décembre, rentrée, fin d'année. "
     "Tu ne publies rien toi-même : tu proposes et GREMA valide."),
    ("ventes", "🛍️ Agent Ventes", "Boutique, caisse, vendeurs, RDV Pro",
     "Tu es l'Agent Ventes. Tu suis la boutique Grema 88, les vendeurs, la caisse (additionne les ventes que GREMA te donne, "
     "en FCFA, avec la calculatrice), les offres (ex. RDV Pro : 1 mois gratuit pour les 10 premiers salons de Niamey) et tu "
     "proposes des idées pour vendre plus. Les calculs détaillés vont à l'Agent Finances."),
    ("recherche", "🔎 Agent Recherche", "Idées, prix, concurrents, nouvelles du Sahel",
     "Tu es l'Agent Recherche. Tu cherches sur Internet (outil Recherche Internet) et sur Wikipédia, compares, analyses un produit (prix, demande, marge, "
     "note sur 10) ou des concurrents, et tu donnes toujours la source (lien)."),
    ("rapports", "📋 Agent Rapports", "Ma journée, résumé du soir, plans",
     "Tu es l'Agent Rapports. Tu écris « ☀️ Ma journée » le matin et le résumé du soir pour GREMA : 5 points maximum, "
     "une priorité claire, un ton encourageant. Appuie-toi sur la mémoire de la conversation."),
    ("creatif", "🎬 Agent Créatif", "Scénarios vidéo, livres, dessins animés, affiches, idées d'applis",
     "Tu es l'Agent Créatif. Tu écris des scénarios de vidéos courtes (20 s, 60 s) avec plans et sous-titres FR/EN, des "
     "histoires et chapitres de livres, des épisodes de dessin animé (comme « Le Conseil de la Savane », roi lion Kadar), des "
     "briefs d'affiches (indigo et or, motifs sahéliens) et des idées d'applications. Toujours concret et prêt à produire."),
    ("finances", "💰 Agent Finances", "Caisse, prix, marges, devis, mobile money, coûts",
     "Tu es l'Agent Finances. Tu calcules (avec la calculatrice) la caisse, les marges, les prix de vente, les devis, les "
     "conversions FCFA / euro (1 € = 655,957 FCFA, taux fixe), les coûts des outils (Claude, n8n, WhatsApp) et tu conseilles "
     "le paiement sécurisé par mobile money (Airtel Money, Moov Money, Orange Money, Wave). Rappelle si besoin que tout revenu "
     "de GREMA doit être déclaré à l'Agentur für Arbeit. Tu ne fais jamais de paiement."),
    ("patron", "👑 Agent Patron", "Discussion, conseils, tout le reste",
     "Tu es l'Agent Patron, chef d'orchestre de l'équipe (WhatsApp, Réseaux, Ventes, Recherche, Rapports, Créatif, Finances). Tu réponds "
     "toi-même aux discussions, aux questions générales sur tous les sujets, aux conseils et aux demandes qui touchent "
     "plusieurs agents (fais alors un plan court : qui fait quoi). Si tu n'es pas sûr d'un fait, cherche sur Internet. Quand GREMA veut juste parler, discute sans ramener le travail."),
]

CLASS = "🧭 Agent Patron : à qui confier ?"
node(CLASS, "@n8n/n8n-nodes-langchain.textClassifier", V["classifier"], (1000, 140), {
    "inputText": "={{ $json.texte }}",
    "categories": {"categories": [
        {"category": a[0], "description": a[2] + (". Si le message commence par « [Demande pour l'agent " + a[0] + "] », c'est cette catégorie." )}
        for a in AGENTS]},
    "options": {"fallback": "other", "systemPromptTemplate":
        "Tu es l'Agent Patron de Grema 88. Classe la demande de GREMA dans la catégorie de l'agent le plus adapté. "
        "Si le message commence par « [Demande pour l'agent X] », choisis X. Une discussion, une salutation ou une question "
        "générale va à « patron »."}})
lien("C'est GREMA ?", CLASS, 0)

MODELE = "🧠 Claude (le cerveau)"
node(MODELE, "@n8n/n8n-nodes-langchain.lmChatAnthropic", V["anthropic"], (1180, 1080), {
    "model": {"__rl": True, "mode": "id", "value": "claude-sonnet-5-5"},
    "options": {"maxTokensToSample": 1500, "temperature": 0.6}})
MEMO = "🗂️ Mémoire des conversations"
node(MEMO, "@n8n/n8n-nodes-langchain.memoryBufferWindow", V["memory"], (1380, 1080), {
    "sessionIdType": "customKey", "sessionKey": "={{ $('⚙️ Réglages').item.json.sessionId }}",
    "contextWindowLength": 20})
CALC = "Calculatrice"
node(CALC, "@n8n/n8n-nodes-langchain.toolCalculator", V["calc"], (1580, 1080), {})
WIKI = "Wikipedia"
node(WIKI, "@n8n/n8n-nodes-langchain.toolWikipedia", V["wiki"], (1760, 1080), {})

WEB = "Recherche Internet (Claude)"
node(WEB, "n8n-nodes-base.httpRequestTool", 4.2, (1940, 1080), {
    "toolDescription": "Cherche une information récente sur Internet (prix, actualité, concurrents, taux, nouvelles du Niger et du Sahel). "
                       "Donne une question précise ; renvoie une réponse courte avec les sources.",
    "method": "POST",
    "url": "https://api.anthropic.com/v1/messages",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "anthropicApi",
    "sendHeaders": True,
    "headerParameters": {"parameters": [{"name": "anthropic-version", "value": "2023-06-01"}]},
    "sendBody": True,
    "specifyBody": "json",
    "jsonBody": "={{ JSON.stringify({ model: 'claude-sonnet-5-5', max_tokens: 1200, "
                "tools: [{ type: 'web_search_20250305', name: 'web_search', max_uses: 3 }], "
                "messages: [{ role: 'user', content: 'Cherche sur Internet puis réponds en français, en 5 lignes maximum, avec les liens des sources : ' + "
                "$fromAI('question', 'La question précise à chercher sur Internet', 'string') }] }) }}",
    "options": {}})
lien(MODELE, CLASS, 0, "ai_languageModel")
ordre_sortie = []
for i, (aid, nom, role, consigne) in enumerate(AGENTS):
    y = -300 + i * 165
    node(nom, "@n8n/n8n-nodes-langchain.agent", V["agent"], (1460, y), {
        "promptType": "define",
        "text": "={{ $('⚙️ Réglages').item.json.texte }}",
        "options": {"systemMessage": "=" + BASE + "\nTon rôle : " + consigne +
                    "\n\nContexte : nous sommes le {{ $now.setLocale('fr').toFormat('cccc d LLLL yyyy, HH:mm') }} (heure d'Allemagne). "
                    "Tu parles à : {{ $('⚙️ Réglages').item.json.expediteur === 'GREMA' || $('⚙️ Réglages').item.json.expediteur === $('⚙️ Réglages').item.json.numeroGrema ? 'GREMA, ton patron' : 'un client (' + ($('⚙️ Réglages').item.json.nom || 'sans nom') + ')' }}.",
                    "maxIterations": 6}})
    lien(MODELE, nom, 0, "ai_languageModel")
    lien(MEMO, nom, 0, "ai_memory")
    if aid in ("ventes", "recherche", "finances", "patron"):
        lien(CALC, nom, 0, "ai_tool")
    if aid in ("recherche", "creatif", "patron"):
        lien(WIKI, nom, 0, "ai_tool")
    if aid in ("recherche", "reseaux", "finances", "patron"):
        lien(WEB, nom, 0, "ai_tool")
    lien(CLASS, nom, i)
# sortie « other » du classeur → Patron
lien(CLASS, "👑 Agent Patron", len(AGENTS))
# clients WhatsApp → Agent WhatsApp directement
lien("C'est GREMA ?", "💬 Agent WhatsApp", 1)

# ---------------------------------------------------------------- 4. réponse
PREP = "📝 Préparer la réponse"
ids = {a[1]: a[0] for a in AGENTS}
sset(PREP, (2240, 300), [
    ("reponse", "={{ $json.output }}", "string"),
    ("agent", "={{ $prevNode.name.replace(/^\\S+\\s/, '') }}", "string"),
    ("agentId", "={{ (" + json.dumps(ids, ensure_ascii=False) + ")[$prevNode.name] || 'patron' }}", "string"),
    ("question", "={{ $('⚙️ Réglages').item.json.texte }}", "string"),
    ("canal", "={{ $('⚙️ Réglages').item.json.canal }}", "string"),
    ("nom", "={{ $('⚙️ Réglages').item.json.nom }}", "string"),
    ("estGrema", "={{ $('⚙️ Réglages').item.json.expediteur === 'GREMA' || $('⚙️ Réglages').item.json.expediteur === $('⚙️ Réglages').item.json.numeroGrema }}", "boolean"),
    ("destinataire", "={{ $('⚙️ Réglages').item.json.expediteur === 'GREMA' ? $('⚙️ Réglages').item.json.numeroGrema : $('⚙️ Réglages').item.json.expediteur }}", "string"),
    ("heure", "={{ $now.toISO() }}", "string"),
])
for a in AGENTS:
    lien(a[1], PREP)

JOUR = "🗒️ Noter dans le journal"
node(JOUR, "n8n-nodes-base.code", V["code"], (2460, 300), {"jsCode": (
    "// Garde les 200 derniers échanges pour le tableau de bord (fonctionne quand le workflow est activé).\n"
    "const memo = $getWorkflowStaticData('global');\n"
    "memo.journal = memo.journal || [];\n"
    "for (const item of $input.all()) {\n"
    "  const j = item.json;\n"
    "  memo.journal.push({ heure: j.heure, agent: j.agent, agentId: j.agentId, canal: j.canal, nom: j.nom,\n"
    "    estGrema: j.estGrema, question: String(j.question || '').slice(0, 300), reponse: String(j.reponse || '').slice(0, 600) });\n"
    "}\n"
    "memo.journal = memo.journal.slice(-200);\n"
    "return $input.all();")})
lien(PREP, JOUR)

SW = "🔀 Par où répondre ?"
def regle(val, cle):
    return {"conditions": conditions([cond_str("={{ $json.canal }}", "equals", val)]), "renameOutput": True, "outputKey": cle}
node(SW, "n8n-nodes-base.switch", V["switch"], (2680, 300), {
    "rules": {"values": [regle("whatsapp", "WhatsApp"), regle("tableau", "Tableau de bord"), regle("chat", "Chat")]},
    "options": {}})
lien(JOUR, SW)

node("📤 Répondre sur WhatsApp", "n8n-nodes-base.whatsApp", V["wa"], (2940, 120), {
    "operation": "send",
    "phoneNumberId": "={{ $('⚙️ Réglages').item.json.idNumeroWhatsApp }}",
    "recipientPhoneNumber": "={{ $json.destinataire }}",
    "textBody": "={{ $json.reponse.slice(0, 4000) }}",
    "additionalFields": {}})
lien(SW, "📤 Répondre sur WhatsApp", 0)
node("↩️ Répondre au tableau de bord", "n8n-nodes-base.respondToWebhook", V["respond"], (2940, 300), {
    "respondWith": "json",
    "responseBody": "={{ { reponse: $json.reponse, agent: $json.agent, agentId: $json.agentId } }}",
    "options": {}})
lien(SW, "↩️ Répondre au tableau de bord", 1)
sset("💬 Réponse du chat", (2940, 480), [("output", "={{ $json.agent + ' : ' + $json.reponse }}", "string")])
lien(SW, "💬 Réponse du chat", 2)

wf = {
    "name": "Agent Grema : Patron + 7 agents (un seul écran)",
    "nodes": nodes,
    "connections": conns,
    "active": False,
    "settings": {"executionOrder": "v1", "timezone": "Europe/Berlin", "saveManualExecutions": True},
    "pinData": {},
    "meta": {"templateCredsSetupCompleted": False},
    "tags": [],
}
SORTIE.write_text(json.dumps(wf, ensure_ascii=False, indent=2), encoding="utf-8")
print("OK", SORTIE, len(nodes), "nœuds")
