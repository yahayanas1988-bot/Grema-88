import threading
import unittest
from types import SimpleNamespace

from agent_expert.config import Settings
from agent_expert.equipe import Equipe, lire_taches

from .fakes import (
    FauxClient,
    FauxClientFonction,
    dernier_texte,
    reponse_repartition,
    reponse_texte,
)

DEUX_TACHES = [
    {"domaine": "droit", "consigne": "Volet juridique"},
    {"domaine": "finance", "consigne": "Volet fiscal"},
]


def _equipe_a_deux(echecs: tuple[str, ...] = ()):
    """Équipe dont le Patron répartit entre droit et finance.

    Les deux spécialistes s'attendent à une barrière : si leur travail n'était
    pas parallèle, la barrière expirerait et les deux échoueraient.
    """
    barriere = threading.Barrier(2, timeout=5)

    def repondre(params):
        if "tool_choice" in params:
            return reponse_repartition(DEUX_TACHES)
        texte = dernier_texte(params)
        if "Rapports de tes spécialistes" in texte:
            return reponse_texte("Synthèse finale.")
        barriere.wait()
        for volet, rapport in (("Volet juridique", "Rapport droit."), ("Volet fiscal", "Rapport finance.")):
            if volet in texte:
                if volet in echecs:
                    raise RuntimeError(f"panne {volet}")
                return reponse_texte(rapport)
        raise AssertionError(f"requête inattendue : {texte[:80]}")

    client = FauxClientFonction(repondre)
    return Equipe(client, Settings()), client


class EquipeTest(unittest.TestCase):
    def test_une_seule_tache_reponse_directe(self):
        client = FauxClient([
            reponse_repartition([{"domaine": "tech", "consigne": "Corriger le bug"}]),
            reponse_texte("Voici la correction."),
        ])
        equipe = Equipe(client, Settings())

        reponse = equipe.ask("Mon code python plante")

        self.assertEqual(reponse.text, "Voici la correction.")
        self.assertEqual(len(client.messages.appels), 2)  # Patron + spécialiste, pas de synthèse
        self.assertIn("Informatique", client.messages.appels[1]["system"][1]["text"])
        self.assertEqual(equipe.agent.messages[0]["content"], "Mon code python plante")

    def test_plusieurs_taches_en_parallele_puis_synthese(self):
        equipe, client = _equipe_a_deux()
        evenements = []

        reponse = equipe.ask(
            "Je veux ouvrir une boutique : contrat et impôts ?",
            on_event=lambda *e: evenements.append(e[0]),
        )

        self.assertEqual(reponse.text, "Synthèse finale.")
        self.assertEqual(len(client.messages.appels), 4)  # Patron, 2 spécialistes, synthèse
        synthese = dernier_texte(client.messages.appels[-1])
        self.assertLess(synthese.index("Rapport droit."), synthese.index("Rapport finance."))
        self.assertEqual(evenements, ["plan", "rapport", "rapport", "synthese"])
        self.assertEqual(equipe.usage.requetes, 4)

    def test_un_specialiste_en_echec_n_arrete_pas_l_equipe(self):
        equipe, client = _equipe_a_deux(echecs=("Volet fiscal",))

        reponse = equipe.ask("contrat et impôts ?")

        self.assertEqual(reponse.text, "Synthèse finale.")
        self.assertIsNone(reponse.rapports[0].erreur)
        self.assertIn("panne", reponse.rapports[1].erreur)
        self.assertIn("rapport indisponible", dernier_texte(client.messages.appels[-1]))

    def test_tous_en_echec_leve_l_erreur(self):
        equipe, _ = _equipe_a_deux(echecs=("Volet juridique", "Volet fiscal"))
        with self.assertRaises(RuntimeError):
            equipe.ask("contrat et impôts ?")
        self.assertEqual(equipe.agent.messages, [])

    def test_repli_sur_les_mots_cles_si_le_patron_echoue(self):
        def repondre(params):
            if "tool_choice" in params:
                raise RuntimeError("Patron injoignable")
            return reponse_texte("Réponse juridique.")

        client = FauxClientFonction(repondre)
        reponse = Equipe(client, Settings()).ask("Mon contrat de bail est résilié")
        self.assertEqual(reponse.taches[0].domaine, "droit")
        self.assertEqual(reponse.text, "Réponse juridique.")

    def test_domaine_impose_sans_patron(self):
        client = FauxClient([reponse_texte("ok")])
        Equipe(client, Settings()).ask("Question", domain="droit")
        self.assertEqual(len(client.messages.appels), 1)
        self.assertNotIn("tool_choice", client.messages.appels[0])

    def test_le_patron_voit_l_echange_precedent(self):
        client = FauxClient([
            reponse_repartition([{"domaine": "droit", "consigne": "c"}]),
            reponse_texte("Premier avis."),
            reponse_repartition([{"domaine": "droit", "consigne": "c"}]),
            reponse_texte("Suite."),
        ])
        equipe = Equipe(client, Settings())
        equipe.ask("Mon bail au Niger ?")
        equipe.ask("Et au Sénégal ?")
        contenu = client.messages.appels[2]["messages"][0]["content"]
        self.assertIn("Échange précédent", contenu)
        self.assertIn("Premier avis.", contenu)


class LireTachesTest(unittest.TestCase):
    @staticmethod
    def _appel(taches):
        return SimpleNamespace(content=[
            SimpleNamespace(type="tool_use", name="repartir", input={"taches": taches})
        ])

    def test_nettoyage(self):
        taches = lire_taches(self._appel([
            {"domaine": "inconnu", "consigne": "a"},
            {"domaine": "droit", "consigne": ""},
            {"domaine": "droit", "consigne": "doublon"},
            "pas un dict",
            {"domaine": "finance", "consigne": "b"},
            {"domaine": "sante", "consigne": "c"},
        ]), "question", maxi=3)

        self.assertEqual([t.domaine for t in taches], ["general", "droit", "finance"])
        self.assertEqual(taches[1].consigne, "question")  # consigne vide : la question

    def test_sans_appel_d_outil(self):
        self.assertEqual(lire_taches(reponse_texte("droit"), "q", maxi=4), [])


if __name__ == "__main__":
    unittest.main()
