import datetime
import tomllib
import unittest

import scrittura

GATE = """# Chiusure delle voci.

[[chiusure]]
voce = "1.01"
esito = "fatto"
evidenza = ["prodotto/visione.md"]
data = 2026-10-07

[[chiusure]]
voce = "2.02"
incremento = 1
esito = "fatto"
evidenza = ["requisiti/storie.toml"]
data = 2026-10-10
"""

STATO = """metodo = "3.0.0"

[scheda]
progetto = "Prova"

[corrente]
# il punto aperto
fase = 2
punto = "2.02"

[[registro]]
fase = 1
stato = "superato"

[congelamento]
data = 2026-10-22
"""


class Valori(unittest.TestCase):
    def test_letterali(self):
        campi = {"s": 'virgolette " e \\ e à', "n": 3, "b": True, "d": datetime.date(2026, 1, 2),
                 "l": ["a", "b"], "vuota": []}
        testo = scrittura.blocco("[x]", campi)
        self.assertEqual(tomllib.loads(testo)["x"], campi)

    def test_none_si_omette(self):
        self.assertNotIn("motivo", scrittura.blocco("[x]", {"a": 1, "motivo": None}))

    def test_tipo_non_scrivibile(self):
        with self.assertRaises(TypeError):
            scrittura.valore({"a": 1})


class Sezioni(unittest.TestCase):
    def test_sostituisce_la_sezione_giusta_e_conserva_il_resto(self):
        nuovo, esito = scrittura.aggiorna_sezione(
            GATE, "[[chiusure]]", lambda d: d["voce"] == "2.02" and d.get("incremento") == 1,
            {"voce": "2.02", "incremento": 1, "esito": "fatto", "evidenza": ["altro.toml"], "data": datetime.date(2026, 11, 1)})
        self.assertEqual(esito, "sostituita")
        self.assertTrue(nuovo.startswith("# Chiusure delle voci."))
        chiusure = tomllib.loads(nuovo)["chiusure"]
        self.assertEqual([c["voce"] for c in chiusure], ["1.01", "2.02"])
        self.assertEqual(chiusure[1]["evidenza"], ["altro.toml"])

    def test_aggiunge_in_fondo_se_non_trova(self):
        nuovo, esito = scrittura.aggiorna_sezione(
            GATE, "[[chiusure]]", lambda d: False, {"voce": "2.03", "esito": "fatto", "evidenza": ["x"], "data": datetime.date(2026, 11, 1)})
        self.assertEqual(esito, "aggiunta")
        self.assertEqual([c["voce"] for c in tomllib.loads(nuovo)["chiusure"]], ["1.01", "2.02", "2.03"])

    def test_aggiunge_dopo_l_ultima_dello_stesso_tipo(self):
        nuovo, _ = scrittura.aggiorna_sezione(
            STATO, "[[registro]]", lambda d: d["fase"] == 2, {"fase": 2, "incremento": 1, "stato": "in-corso"})
        dati = tomllib.loads(nuovo)
        self.assertEqual([r["fase"] for r in dati["registro"]], [1, 2])
        self.assertLess(nuovo.index("fase = 2\nincremento"), nuovo.index("[congelamento]"))
        self.assertEqual(dati["congelamento"]["data"], datetime.date(2026, 10, 22))

    def test_tabella_sostituita_senza_toccare_le_altre(self):
        nuovo, esito = scrittura.aggiorna_sezione(STATO, "[corrente]", lambda d: True, {"fase": 3, "punto": ""})
        self.assertEqual(esito, "sostituita")
        dati = tomllib.loads(nuovo)
        self.assertEqual(dati["corrente"], {"fase": 3, "punto": ""})
        self.assertEqual(dati["scheda"]["progetto"], "Prova")
        self.assertEqual(len(dati["registro"]), 1)

    def test_tabella_assente_si_aggiunge(self):
        nuovo, esito = scrittura.aggiorna_sezione('metodo = "3.0.0"\n', "[corrente]", lambda d: True, {"fase": 0})
        self.assertEqual(esito, "aggiunta")
        self.assertEqual(tomllib.loads(nuovo)["corrente"], {"fase": 0})

    def test_file_vuoto(self):
        nuovo, _ = scrittura.aggiorna_sezione("", "[[chiusure]]", lambda d: False, {"voce": "0.01"})
        self.assertEqual(tomllib.loads(nuovo), {"chiusure": [{"voce": "0.01"}]})


if __name__ == "__main__":
    unittest.main()
