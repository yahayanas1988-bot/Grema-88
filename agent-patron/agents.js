/* Données de l'espace Agent Patron.
   Modifiez ce fichier pour mettre à jour la page (agent-patron/index.html).
   Les tâches, le journal et les chiffres sont des exemples.
   L'état des canaux est réel : vérifié le 5 novembre 2026 dans MyChatBot et Metricool. */
window.AGENT_PATRON = {
  majLe: "2026-11-05T15:52:00Z",
  exemple: true,

  // Le premier agent est le Patron : il répartit le travail entre les autres.
  agents: [
    { id: "patron",   nom: "Agent Patron",    role: "Chef d'orchestre : reçoit les demandes et les confie au bon agent", etat: "actif", taches: 12, couleur: "#e3a72f" },
    { id: "whatsapp", nom: "Agent WhatsApp",  role: "Répond aux clients et prend les commandes sur WhatsApp",           etat: "actif", taches: 3,  couleur: "#13785a" },
    { id: "reseaux",  nom: "Agent Réseaux",   role: "Prépare et programme les publications Facebook, TikTok, Instagram", etat: "actif", taches: 4,  couleur: "#b34a2c" },
    { id: "ventes",   nom: "Agent Ventes",    role: "Suit la boutique Grema 88 et les demandes des vendeurs",           etat: "actif", taches: 5,  couleur: "#2c3077" },
    { id: "recherche",nom: "Agent Recherche", role: "Cherche des idées, des prix et des nouvelles du Sahel",            etat: "actif", taches: 4,  couleur: "#7a5bd1" },
    { id: "rapports", nom: "Agent Rapports",  role: "Écrit le résumé du jour pour GREMA",                               etat: "actif", taches: 3,  couleur: "#b8740c" }
  ],

  // Tâches faites par jour (les 7 derniers jours).
  parJour: [
    { jour: "2026-10-25", n: 6 },
    { jour: "2026-10-26", n: 9 },
    { jour: "2026-10-27", n: 7 },
    { jour: "2026-10-28", n: 12 },
    { jour: "2026-10-29", n: 15 },
    { jour: "2026-10-30", n: 18 },
    { jour: "2026-10-31", n: 31 }
  ],

  // Ce que les agents font en ce moment.
  // Une tâche par agent : elle s'affiche aussi sur la fiche de l'agent.
  taches: [
    { agent: "patron",    titre: "Répartir les demandes du jour entre les agents", etat: "en-cours" },
    { agent: "whatsapp",  titre: "Préparer les réponses aux questions fréquentes des clients", etat: "en-cours", note: "WhatsApp relié via MyChatBot (assistant Veronica)" },
    { agent: "reseaux",   titre: "Écrire les textes de la semaine pour la vidéo « Le conseil de la savane »", etat: "en-cours", note: "TikTok relié à Metricool ; publications Facebook et Instagram encore à relier" },
    { agent: "ventes",    titre: "Vérifier les nouveaux produits proposés par les vendeurs", etat: "en-cours" },
    { agent: "recherche", titre: "Relever les prix du marché de Niamey", etat: "en-cours" },
    { agent: "rapports",  titre: "Préparer le résumé de ce soir pour GREMA", etat: "en-attente" }
  ],

  // Journal : le plus récent en premier.
  journal: [
    { heure: "2026-10-31T14:45:00Z", agent: "patron",    texte: "A donné une tâche à chacun des 6 agents." },
    { heure: "2026-10-31T14:30:00Z", agent: "patron",    texte: "A confié 3 tâches à l'Agent Ventes." },
    { heure: "2026-10-31T13:05:00Z", agent: "rapports",  texte: "Résumé du matin envoyé à GREMA." },
    { heure: "2026-10-31T11:20:00Z", agent: "recherche", texte: "5 idées de publications trouvées." },
    { heure: "2026-10-31T09:00:00Z", agent: "patron",    texte: "Démarrage de la journée, 6 agents prêts." }
  ],

  // Canaux : connecte = true seulement quand le compte est vraiment relié.
  canaux: [
    { nom: "Zapier",                      connecte: true,  note: "Connecté" },
    { nom: "WhatsApp",                    connecte: true,  note: "Relié via MyChatBot : l'assistante Veronica répond aux clients" },
    { nom: "Facebook Messenger",          connecte: true,  note: "Relié via MyChatBot : Veronica répond aux messages de la page" },
    { nom: "Publications Facebook / Instagram", connecte: false, note: "À relier dans Metricool (marque grema.11)" },
    { nom: "TikTok",                      connecte: true,  note: "Relié à Metricool (grema.11)" },
    { nom: "YouTube",                     connecte: true,  note: "Relié à Metricool" },
    { nom: "E-mail",                      connecte: true,  note: "Relié via MyChatBot" },
    { nom: "Site Grema 88",               connecte: true,  note: "Boutique, formulaire vendeurs et chat Veronica" }
  ]
};
