import unittest

from agent_expert.router import Router, keyword_domain, parse_domain_id
from agent_expert.usage import Usage

from .fakes import FauxClient, reponse_texte


class ParseDomainIdTest(unittest.TestCase):
    def test_identifiant_seul(self):
        self.assertEqual(parse_domain_id("droit"), "droit")

    def test_ponctuation_et_espaces(self):
        self.assertEqual(parse_domain_id("  Tech.\n"), "tech")

    def test_identifiant_dans_une_phrase(self):
        self.assertEqual(parse_domain_id("Je pense que finance"), "finance")

    def test_inconnu(self):
        self.assertIsNone(parse_domain_id("inconnu"))
        self.assertIsNone(parse_domain_id(""))


class KeywordDomainTest(unittest.TestCase):
    def test_droit(self):
        self.assertEqual(keyword_domain("Mon contrat de travail et mon licenciement"), "droit")

    def test_tech(self):
        self.assertEqual(keyword_domain("Bug dans mon code python"), "tech")

    def test_repli_general(self):
        self.assertEqual(keyword_domain("Bonjour, ça va ?"), "general")

    def test_mot_entier_seulement(self):
        # "eau" ne doit pas déclencher "bureau" ni "bateau" ailleurs
        self.assertNotEqual(keyword_domain("Je range mon bureau"), "agriculture")


class RouterTest(unittest.TestCase):
    def test_reponse_du_modele(self):
        client = FauxClient([reponse_texte("sante")])
        self.assertEqual(Router(client, "m", 16).choose("J'ai mal à la tête"), "sante")

    def test_reponse_inexploitable_repli_mots_cles(self):
        client = FauxClient([reponse_texte("je ne sais pas trop")])
        self.assertEqual(Router(client, "m", 16).choose("mon code python plante"), "tech")

    def test_exception_repli_mots_cles(self):
        class Casse:
            class messages:  # noqa: N801
                @staticmethod
                def create(**_):
                    raise RuntimeError("réseau coupé")

        self.assertEqual(Router(Casse(), "m", 16).choose("contrat de bail"), "droit")

    def test_usage_compte_le_routage(self):
        usage = Usage()
        client = FauxClient([reponse_texte("tech")])
        Router(client, "m", 16, usage).choose("code")
        self.assertEqual(usage.requetes, 1)


if __name__ == "__main__":
    unittest.main()
