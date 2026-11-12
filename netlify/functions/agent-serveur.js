// Agent Serveur : reçoit un message et le fait traiter par Claude.
//
// Variables à définir dans Netlify (Site settings > Environment variables).
// Elles ne doivent jamais être écrites dans ce fichier :
//   ANTHROPIC_API_KEY  clé API Anthropic (facturée sur votre compte)
//   CLAUDE_MODEL       nom du modèle Claude à utiliser
//   AGENT_TOKEN        mot de passe partagé ; l'appelant l'envoie dans l'en-tête x-agent-token
//
// Appel : POST /.netlify/functions/agent-serveur  avec {"message": "..."}

const API_URL = "https://api.anthropic.com/v1/messages";
const API_VERSION = "2023-06-01";
const MAX_MESSAGE_CHARS = 4000;
const MAX_TOKENS = 1024;

const CONSIGNE =
  "Tu es l'Agent Serveur de Grema 88, relié à l'Agent Patron. " +
  "Réponds en français, de façon courte et claire.";

function reponse(statusCode, corps) {
  return {
    statusCode,
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify(corps),
  };
}

exports.handler = async function (event) {
  if (event.httpMethod !== "POST") {
    return reponse(405, { erreur: "Méthode non autorisée. Utilisez POST." });
  }

  const env = process.env;
  if (!env.ANTHROPIC_API_KEY || !env.CLAUDE_MODEL || !env.AGENT_TOKEN) {
    return reponse(500, {
      erreur:
        "Serveur mal configuré : ANTHROPIC_API_KEY, CLAUDE_MODEL et AGENT_TOKEN doivent être définis dans Netlify.",
    });
  }

  const headers = event.headers || {};
  const jeton = headers["x-agent-token"] || headers["X-Agent-Token"] || "";
  if (jeton !== env.AGENT_TOKEN) {
    return reponse(401, { erreur: "Jeton invalide." });
  }

  let demande;
  try {
    demande = JSON.parse(event.body || "{}");
  } catch (e) {
    return reponse(400, { erreur: "Corps JSON invalide." });
  }

  const message = typeof demande.message === "string" ? demande.message.trim() : "";
  if (!message) {
    return reponse(400, { erreur: "Champ « message » manquant." });
  }
  if (message.length > MAX_MESSAGE_CHARS) {
    return reponse(400, {
      erreur: `Message trop long (${MAX_MESSAGE_CHARS} caractères maximum).`,
    });
  }

  let res;
  try {
    res = await fetch(API_URL, {
      method: "POST",
      headers: {
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": API_VERSION,
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: env.CLAUDE_MODEL,
        max_tokens: MAX_TOKENS,
        system: CONSIGNE,
        messages: [{ role: "user", content: message }],
      }),
    });
  } catch (e) {
    return reponse(502, { erreur: "Claude est injoignable pour le moment." });
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    // On ne renvoie pas le détail de l'erreur Anthropic au navigateur.
    return reponse(502, { erreur: "Claude n'a pas pu traiter la demande.", statut: res.status });
  }

  const texte = (data.content || [])
    .filter((bloc) => bloc.type === "text")
    .map((bloc) => bloc.text)
    .join("\n");

  return reponse(200, { reponse: texte });
};
