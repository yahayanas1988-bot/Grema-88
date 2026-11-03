import unittest

from agent_expert.tools import CALCULATRICE, ToolBox, default_toolbox, evaluer


class CalculatriceTest(unittest.TestCase):
    def test_calculs(self):
        self.assertEqual(evaluer("2+3*4"), 14)
        self.assertEqual(evaluer("(12.5*4)+sqrt(9)"), 53.0)
        self.assertEqual(evaluer("-3**2"), -9)
        self.assertEqual(evaluer("10 // 3"), 3)
        self.assertEqual(evaluer("7 % 4"), 3)
        self.assertEqual(evaluer("max(2, 9, 4)"), 9)

    def test_refuse_ce_qui_nest_pas_arithmetique(self):
        for expression in ["__import__('os')", "open('x')", "'abc'", "True", "[1, 2]",
                           "x + 1", "(1, 2)", "min(a=1)"]:
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    evaluer(expression)

    def test_refuse_exposant_enorme_et_expression_longue(self):
        with self.assertRaises(ValueError):
            evaluer("10**100000")
        with self.assertRaises(ValueError):
            evaluer("1+" * 150 + "1")

    def test_format_du_resultat(self):
        box = default_toolbox()
        self.assertEqual(box.run("calculer", {"expression": "10/4"}), ("2.5", False))
        self.assertEqual(box.run("calculer", {"expression": "8/2"}), ("4", False))


class ToolBoxTest(unittest.TestCase):
    def test_outil_inconnu(self):
        texte, erreur = default_toolbox().run("supprimer_tout", {})
        self.assertTrue(erreur)
        self.assertIn("inconnu", texte)

    def test_argument_manquant_devient_erreur(self):
        texte, erreur = default_toolbox().run("calculer", {})
        self.assertTrue(erreur)
        self.assertTrue(texte.startswith("Erreur"))

    def test_schemas_au_format_api(self):
        schemas = ToolBox([CALCULATRICE]).schemas()
        self.assertEqual(schemas[0]["name"], "calculer")
        self.assertIn("input_schema", schemas[0])


if __name__ == "__main__":
    unittest.main()
