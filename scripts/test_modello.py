import shutil
import tempfile
import unittest
from pathlib import Path

import modello

SKILL = Path(__file__).resolve().parent.parent
CATALOGO = modello.leggi_catalogo(SKILL / "assets" / "checklist.toml")
ESEMPIO = SKILL / "assets" / "esempio"
P = modello.PROGETTAZIONE


class Lettura(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = modello.carica(ESEMPIO, CATALOGO)

    def test_nessun_problema_di_lettura(self):
        self.assertEqual(self.p.reperti, [])

    def test_ogni_sorgente_diventa_elementi(self):
        conteggi = {tipo: len(g) for tipo, g in self.p.elementi.items()}
        self.assertEqual(conteggi["storie"], 22)
        self.assertEqual(conteggi["moduli"], 6)
        self.assertEqual(conteggi["api"], 27)
        self.assertEqual(conteggi["voci"], len(CATALOGO["voci"]))
        self.assertGreater(conteggi["attributi"], conteggi["entita"])

    def test_annidati_con_id_composto(self):
        colonna = self.p.trova("colonne", "veicoli.targa")
        self.assertEqual((colonna.contenitore, colonna.sorgente), ("veicoli", "contracts/schema.toml"))
        self.assertIsNotNone(self.p.trova("attributi", "fattura.numero"))

    def test_documenti_con_frontmatter(self):
        processo = self.p.trova("processi", "ciclo-intervento")
        self.assertIn("_corpo", processo.dati)
        self.assertEqual(self.p.trova("sequenze", "PC-1").dati["percorso"], "PC-1")

    def test_openapi_e_adr(self):
        op = self.p.trova("api", "pdfFattura")
        self.assertEqual(op.dati["_metodo"], "get")
        self.assertTrue(op.dati["_percorso"].startswith("/"))
        self.assertEqual(self.p.trova("adr", "ADR-0004").dati["status"], "Accepted")


class Riferimenti(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = modello.carica(ESEMPIO, CATALOGO)

    def test_prefissato_tipizzato_e_atteso(self):
        self.assertEqual(self.p.risolvi("RNF-7"), ("rnf", "RNF-7"))
        self.assertEqual(self.p.risolvi("CLI-1"), ("storie", "CLI-1"))
        self.assertEqual(self.p.risolvi("entita:fattura"), ("entita", "fattura"))
        self.assertEqual(self.p.risolvi("fattura", "entita"), ("entita", "fattura"))
        self.assertEqual(self.p.risolvi("3.07", "voci"), ("voci", "3.07"))

    def test_non_risolti(self):
        for valore, atteso in (("RNF-99", None), ("entita:inesistente", None), ("fattura", None),
                               ("tipo-ignoto:x", None), ("", None)):
            self.assertIsNone(self.p.risolvi(valore, atteso), valore)

    def test_entranti(self):
        citano = {(t, i) for t, i, _ in self.p.entranti()[("entita", "fattura")]}
        self.assertIn(("tabelle", "fatture"), citano)


class Duplicati(unittest.TestCase):
    def test_id_duplicato_tra_file(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(ESEMPIO, tmp / "e")
            sorgente = tmp / "e" / P / "requisiti" / "storie.toml"
            testo = sorgente.read_text(encoding="utf-8")
            inizio = testo.index('[[storie]]\nid = "CLI-1"')
            fine = testo.index("[[storie]]", inizio + 1)
            (tmp / "e" / P / "requisiti" / "storie-copia.toml").write_text(testo[inizio:fine], encoding="utf-8")
            p = modello.carica(tmp / "e", CATALOGO)
            self.assertTrue(any("id duplicato" in r.messaggio for r in p.reperti))
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
