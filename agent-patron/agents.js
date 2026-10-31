/* Données de l'espace Agent Patron.
   Modifiez ce fichier pour mettre à jour la page (agent-patron/index.html).
   Ce sont des données d'exemple tant que les agents ne sont pas branchés. */
window.AGENT_PATRON = {
  majLe: "2026-10-31T14:40:00Z",
  exemple: true,

  // Le premier agent est le Patron : il répartit le travail entre les autres.
  agents: [
    { id: "patron",   nom: "Agent Patron",    role: "Chef d'orchestre : reçoit les demandes et les confie au bon agent", etat: "actif",    taches: 12, couleur: "#e3a72f" },
    { id: "whatsapp", nom: "Agent WhatsApp",  role: "Répond aux clients et prend les commandes sur WhatsApp",           etat: "a-brancher", taches: 0,  couleur: "#13785a" },
    { id: "reseaux",  nom: "Agent Réseaux",   role: "Prépare et programme les publications Facebook, TikTok, Instagram", etat: "a-brancher", taches: 0,  couleur: "#b34a2c" },
    { id: "ventes",   nom: "Agent Ventes",    role: "Suit la boutique Grema 88 et les demandes des vendeurs",           etat: "actif",    taches: 5,  couleur: "#2c3077" },
    { id: "recherche",nom: "Agent Recherche", role: "Cherche des idées, des prix et des nouvelles du Sahel",            etat: "actif",    taches: 4,  couleur: "#7a5bd1" },
    { id: "rapports", nom: "Agent Rapports",  role: "Écrit le résumé du jour pour GREMA",                               etat: "actif",    taches: 3,  couleur: "#b8740c" }
  ],

  // Tâches faites par jour (les 7 derniers jours).
  parJour: [
    { jour: "2026-10-25", n: 6 },
    { jour: "2026-10-26", n: 9 },
    { jour: "2026-10-27", n: 7 },
    { jour: "2026-10-28", n: 12 },
    { jour: "2026-10-29", n: 15 },
    { jour: "2026-10-30", n: 18 },
    { jour: "2026-10-31", n: 24 }
  ],

  // Ce que les agents font en ce moment.
  taches: [
    { agent: "patron",    titre: "Répartir les demandes du jour",                 etat: "en-cours" },
    { agent: "ventes",    titre: "Vérifier les nouveaux produits proposés",       etat: "en-cours" },
    { agent: "recherche", titre: "Relever les prix du marché de Niamey",          etat: "en-attente" },
    { agent: "rapports",  titre: "Préparer le résumé de ce soir",                 etat: "en-attente" },
    { agent: "reseaux",   titre: "Programmer la vidéo « Le conseil de la savane »", etat: "bloque", note: "réseaux sociaux pas encore connectés" }
  ],

  // Journal : le plus récent en premier.
  journal: [
    { heure: "2026-10-31T14:30:00Z", agent: "patron",    texte: "A confié 3 tâches à l'Agent Ventes." },
    { heure: "2026-10-31T13:05:00Z", agent: "rapports",  texte: "Résumé du matin envoyé à GREMA." },
    { heure: "2026-10-31T11:20:00Z", agent: "recherche", texte: "5 idées de publications trouvées." },
    { heure: "2026-10-31T09:00:00Z", agent: "patron",    texte: "Démarrage de la journée, 6 agents prêts." }
  ],

  // Canaux : connecte = true quand le compte est vraiment relié.
  canaux: [
    { nom: "Zapier",            connecte: true,  note: "Connecté" },
    { nom: "WhatsApp",          connecte: false, note: "À connecter (MyChatBot ou Sent)" },
    { nom: "Facebook / Instagram", connecte: false, note: "À connecter (Metricool)" },
    { nom: "TikTok",            connecte: false, note: "À connecter (Metricool)" },
    { nom: "Site Grema 88",     connecte: true,  note: "Boutique et formulaire vendeurs" }
  ]
};
