import unittest
from pathlib import Path

import modello
import viste

SKILL = Path(__file__).resolve().parent.parent
CATALOGO = modello.leggi_catalogo(SKILL / "assets" / "checklist.toml")
ESEMPIO = SKILL / "assets" / "esempio"


class Viste(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = modello.carica(ESEMPIO, CATALOGO)
        cls.v = viste.genera(cls.p, CATALOGO)

    def test_l_esempio_ha_le_viste_aggiornate(self):
        self.assertEqual(viste.verifica_freschezza(self.p, CATALOGO), [])

    def test_deterministiche(self):
        self.assertEqual(viste.genera(self.p, CATALOGO), self.v)

    def test_ogni_vista_dichiara_di_essere_generata(self):
        for relativo, testo in self.v.items():
            self.assertTrue(testo.startswith(viste.INTESTAZIONE), relativo)

    def test_er_concettuale_in_zampa_di_gallina(self):
        er = self.v[f"{modello.VISTE}/er-concettuale.md"]
        self.assertIn("erDiagram", er)
        # un cliente ha zero o più veicoli, un veicolo uno e un solo cliente
        self.assertRegex(er, r"(CLIENTE \|\|--o\{ VEICOLO|VEICOLO \}o--\|\| CLIENTE)")
        self.assertIn("VOCE_LISTINO ||--o| MANODOPERA", er)

    def test_checklist_e_debito(self):
        checklist = self.v[f"{modello.VISTE}/checklist.md"]
        self.assertIn("| 6.08 ↻ | rinviata |", checklist)
        self.assertIn("## Controlli trasversali", checklist)
        debito = self.v[f"{modello.VISTE}/debito-pubblicazione.md"]
        self.assertEqual(debito.count("\n| "), 14 + 1)

    def test_tracciabilita_dalle_storie_ai_test(self):
        t = self.v[f"{modello.VISTE}/tracciabilita.md"]
        riga = next(r for r in t.splitlines() if r.startswith("| FAT-1 |"))
        self.assertIn("O-fatture", riga)
        self.assertIn("X-intervento-completo", riga)


if __name__ == "__main__":
    unittest.main()
