import unittest
from unittest import mock

from agent_expert.agent import ExpertAgent, bloc_vers_param, system_blocks
from agent_expert.config import Settings
from agent_expert.domains import DOMAINS_BY_ID

from .fakes import FauxClient, reponse_outil, reponse_texte


def _sans_routage(**kw) -> Settings:
    return Settings(**kw)


class AgentTest(unittest.TestCase):
    def test_routage_puis_reponse(self):
        client = FauxClient([reponse_texte("tech"), reponse_texte("Réponse.")])
        agent = ExpertAgent(client, Settings())

        reponse = agent.ask("Mon code python plante")

        self.assertEqual(reponse.text, "Réponse.")
        self.assertEqual(reponse.domain, "tech")
        appel_routage, appel_expert = client.messages.appels
        self.assertEqual(appel_routage["model"], Settings().router_model)
        self.assertEqual(appel_expert["model"], Settings().model)
        self.assertIn(DOMAINS_BY_ID["tech"].nom, appel_expert["system"][1]["text"])
        self.assertEqual(len(agent.messages), 2)

    def test_domaine_impose_pas_d_appel_de_routage(self):
        client = FauxClient([reponse_texte("ok")])
        agent = ExpertAgent(client, Settings())
        agent.ask("Question", domain="droit")
        self.assertEqual(len(client.messages.appels), 1)

    def test_prompt_mis_en_cache(self):
        client = FauxClient([reponse_texte("ok")])
        ExpertAgent(client, Settings()).ask("Question", domain="droit")
        systeme = client.messages.appels[0]["system"]
        self.assertTrue(all(b.get("cache_control") == {"type": "ephemeral"} for b in systeme))

    def test_outil_calcul_puis_reponse(self):
        client = FauxClient([
            reponse_outil("calculer", {"expression": "6*7"}),
            reponse_texte("Le résultat est 42."),
        ])
        agent = ExpertAgent(client, Settings())

        reponse = agent.ask("Combien font 6 fois 7 ?", domain="sciences")

        self.assertEqual(reponse.text, "Le résultat est 42.")
        resultat = client.messages.appels[1]["messages"][-1]["content"][0]
        self.assertEqual(resultat["type"], "tool_result")
        self.assertEqual(resultat["content"], "42")
        self.assertFalse(resultat["is_error"])

    def test_derniere_etape_sans_outils(self):
        client = FauxClient([
            reponse_outil("calculer", {"expression": "1+1"}),
            reponse_texte("Terminé."),
        ])
        agent = ExpertAgent(client, _sans_routage(max_tool_steps=1))
        agent.ask("Question", domain="sciences")
        self.assertNotIn("tools", client.messages.appels[1])

    def test_streaming_envoie_les_morceaux(self):
        client = FauxClient([reponse_texte("Bonjour le monde")])
        morceaux: list[str] = []
        reponse = ExpertAgent(client, Settings()).ask(
            "Question", domain="general", on_text=morceaux.append
        )
        self.assertEqual("".join(morceaux), "Bonjour le monde")
        self.assertEqual(reponse.text, "Bonjour le monde")

    def test_erreur_ne_laisse_pas_de_question_orpheline(self):
        client = FauxClient([])  # plus de réponse : l'appel échoue
        agent = ExpertAgent(client, Settings())
        with self.assertRaises(IndexError):
            agent.ask("Question", domain="general")
        self.assertEqual(agent.messages, [])

    def test_historique_borne_et_repris_sur_une_question(self):
        client = FauxClient([reponse_texte("ok")] * 4)
        agent = ExpertAgent(client, _sans_routage(max_history_messages=4))
        for i in range(4):
            agent.ask(f"question {i}", domain="general")

        self.assertLessEqual(len(agent.messages), 4)
        self.assertEqual(agent.messages[0]["role"], "user")
        self.assertIsInstance(agent.messages[0]["content"], str)

    def test_dernier_message_porte_le_cache(self):
        client = FauxClient([reponse_texte("a"), reponse_texte("b")])
        agent = ExpertAgent(client, Settings())
        agent.ask("premier", domain="general")
        agent.ask("second", domain="general")
        dernier = client.messages.appels[1]["messages"][-1]
        self.assertEqual(dernier["content"][-1]["cache_control"], {"type": "ephemeral"})

    def test_reset(self):
        client = FauxClient([reponse_texte("ok")])
        agent = ExpertAgent(client, Settings())
        agent.ask("Question", domain="general")
        agent.reset()
        self.assertEqual(agent.messages, [])

    def test_compteur_de_tokens(self):
        client = FauxClient([reponse_texte("ok")])
        agent = ExpertAgent(client, Settings())
        agent.ask("Question", domain="general")
        self.assertEqual(agent.usage.requetes, 1)
        self.assertEqual(agent.usage.tokens_entree, 10)
        self.assertEqual(agent.usage.tokens_sortie, 5)


class OutilsDeConversionTest(unittest.TestCase):
    def test_bloc_vers_param_objet_et_dict(self):
        from types import SimpleNamespace

        self.assertEqual(
            bloc_vers_param(SimpleNamespace(type="text", text="a", citations=None)),
            {"type": "text", "text": "a"},
        )
        self.assertEqual(bloc_vers_param({"type": "text", "text": "b", "x": None}),
                         {"type": "text", "text": "b"})

    def test_system_blocks_contient_base_et_domaine(self):
        blocs = system_blocks(DOMAINS_BY_ID["droit"])
        self.assertEqual(len(blocs), 2)
        self.assertIn("Droit", blocs[1]["text"])


class SettingsTest(unittest.TestCase):
    def test_lecture_de_l_environnement(self):
        env = {"AGENT_MODEL": "mon-modele", "AGENT_DOMAINE": "droit", "AGENT_MAX_TOKENS": "900"}
        with mock.patch.dict("os.environ", env, clear=False):
            reglages = Settings.from_env()
        self.assertEqual(reglages.model, "mon-modele")
        self.assertEqual(reglages.forced_domain, "droit")
        self.assertEqual(reglages.max_tokens, 900)


if __name__ == "__main__":
    unittest.main()
