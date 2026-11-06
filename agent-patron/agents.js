/* Données de l'espace Agent Patron.
   Modifiez ce fichier pour mettre à jour la page (agent-patron/index.html).
   Données réelles, relevées le 5 novembre 2026 dans MyChatBot et Metricool.
   La mise à jour n'est pas encore automatique : la date en haut de la page
   indique quand ces chiffres ont été relevés.
   Ne mettez ici aucun numéro de téléphone ni nom de client : toute personne
   qui a le lien peut voir cette page. */
window.AGENT_PATRON = {
  majLe: "2026-11-05T15:58:00Z",
  exemple: false,

  // Le premier agent est le Patron : il répartit le travail entre les autres.
  // etat : "actif" quand l'agent travaille vraiment, "a-brancher" sinon.
  // taches : travail réel fait aujourd'hui.
  agents: [
    { id: "patron",   nom: "Agent Patron",    role: "Chef d'orchestre : reçoit les demandes et les confie au bon agent", etat: "a-brancher", taches: 0, couleur: "#e3a72f" },
    { id: "whatsapp", nom: "Agent WhatsApp",  role: "Veronica (MyChatBot) répond aux clients sur WhatsApp, Messenger et le site", etat: "actif", taches: 0, couleur: "#13785a" },
    { id: "reseaux",  nom: "Agent Réseaux",   role: "Prépare et programme les publications Facebook, TikTok, Instagram", etat: "a-brancher", taches: 0, couleur: "#b34a2c" },
    { id: "ventes",   nom: "Agent Ventes",    role: "Suit la boutique Grema 88 et les demandes des vendeurs",           etat: "a-brancher", taches: 0, couleur: "#2c3077" },
    { id: "recherche",nom: "Agent Recherche", role: "Cherche des idées, des prix et des nouvelles du Sahel",            etat: "a-brancher", taches: 0, couleur: "#7a5bd1" },
    { id: "rapports", nom: "Agent Rapports",  role: "Écrit le résumé du jour pour GREMA",                               etat: "a-brancher", taches: 0, couleur: "#b8740c" }
  ],

  // Conversations avec des clients par jour (7 derniers jours), tous canaux.
  // Les e-mails automatiques (PayPal) ne sont pas comptés : ce ne sont pas des clients.
  parJour: [
    { jour: "2026-10-30", n: 0 },
    { jour: "2026-10-31", n: 0 },
    { jour: "2026-11-01", n: 0 },
    { jour: "2026-11-02", n: 0 },
    { jour: "2026-11-03", n: 0 },
    { jour: "2026-11-04", n: 0 },
    { jour: "2026-11-05", n: 0 }
  ],

  // Une tâche par agent : elle s'affiche aussi sur la fiche de l'agent.
  taches: [
    { agent: "patron",    titre: "Mettre en service l'équipe d'agents (code prêt dans agent-expert/)", etat: "en-attente", note: "pas encore en service" },
    { agent: "whatsapp",  titre: "Répondre aux clients sur WhatsApp, Messenger et le site", etat: "en-cours", note: "essai MyChatBot jusqu'au 12 novembre : 22 réponses restantes" },
    { agent: "reseaux",   titre: "Relier Facebook et Instagram à Metricool, puis programmer les publications", etat: "en-attente", note: "TikTok et YouTube reliés ; aucune publication programmée" },
    { agent: "ventes",    titre: "Suivre les commandes de la boutique", etat: "en-attente", note: "aucune commande enregistrée dans MyChatBot" },
    { agent: "recherche", titre: "Relever les prix du marché de Niamey", etat: "en-attente", note: "pas encore branché" },
    { agent: "rapports",  titre: "Écrire le résumé du jour pour GREMA", etat: "en-attente", note: "pas encore branché" }
  ],

  // Journal : événements réels, le plus récent en premier.
  journal: [
    { heure: "2026-11-05T15:58:00Z", agent: "patron",   texte: "Tableau de bord passé aux données réelles." },
    { heure: "2026-11-05T15:56:00Z", agent: "whatsapp", texte: "Canal e-mail retiré de Veronica : il recevait des e-mails personnels." },
    { heure: "2026-11-05T15:50:00Z", agent: "whatsapp", texte: "Veronica testée en français et en allemand : réponses correctes." },
    { heure: "2026-11-04T16:06:11Z", agent: "whatsapp", texte: "Facebook Messenger relié à Veronica." },
    { heure: "2026-11-04T16:02:32Z", agent: "whatsapp", texte: "WhatsApp relié à Veronica." },
    { heure: "2026-11-03T21:07:05Z", agent: "whatsapp", texte: "Chat du site relié à Veronica." },
    { heure: "2026-10-29T12:35:23Z", agent: "reseaux",  texte: "Metricool relié : TikTok et YouTube." }
  ],

  // Canaux : connecte = true seulement quand le compte est vraiment relié.
  canaux: [
    { nom: "Zapier",                      connecte: true,  note: "Connecté" },
    { nom: "WhatsApp",                    connecte: true,  note: "Relié via MyChatBot : l'assistante Veronica répond aux clients" },
    { nom: "Facebook Messenger",          connecte: true,  note: "Relié via MyChatBot : Veronica répond aux messages de la page" },
    { nom: "Publications Facebook / Instagram", connecte: false, note: "À relier dans Metricool (marque grema.11)" },
    { nom: "TikTok",                      connecte: true,  note: "Relié à Metricool (grema.11)" },
    { nom: "YouTube",                     connecte: true,  note: "Relié à Metricool" },
    { nom: "Site Grema 88",               connecte: true,  note: "Boutique, formulaire vendeurs et chat Veronica" }
  ]
};
