"""La riga di comando su una copia dell'esempio: lettura, protocollo dei punti e
delle fasi (apri, chiudi, approva), modifiche e congelamento."""
import contextlib
import io
import json
import re
import shutil
import tempfile
import tomllib
import unittest
from pathlib import Path

import progetto as cli

ESEMPIO = Path(__file__).resolve().parent.parent / "assets" / "esempio"
P = "docs/progettazione"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.radice = self.tmp / "esempio"
        shutil.copytree(ESEMPIO, self.radice)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def esegui(self, *argomenti):
        uscita, errori = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(uscita), contextlib.redirect_stderr(errori):
            esito = cli.principale(["--radice", str(self.radice), *argomenti])
        return esito, uscita.getvalue() + errori.getvalue()

    def leggi(self, relativo):
        return tomllib.loads((self.radice / relativo).read_text(encoding="utf-8"))

    def sostituisci(self, relativo, vecchio, nuovo):
        percorso = self.radice / relativo
        testo = percorso.read_text(encoding="utf-8")
        self.assertIn(vecchio, testo)
        percorso.write_text(testo.replace(vecchio, nuovo, 1), encoding="utf-8")

    def togli_chiusura(self, voce):
        percorso = self.radice / P / "gate.toml"
        testo = percorso.read_text(encoding="utf-8")
        nuovo = re.sub(rf'\[\[chiusure\]\]\nvoce = "{re.escape(voce)}"\n[^\[]*', "", testo)
        self.assertNotEqual(nuovo, testo)
        percorso.write_text(nuovo, encoding="utf-8")

    def apri_incremento_2(self):
        self.sostituisci(f"{P}/stato.toml", "incremento = 1\ncostruzione", "incremento = 2\ncostruzione")
        self.esegui("viste")


class Lettura(Base):
    def test_stato(self):
        esito, testo = self.esegui("stato")
        self.assertEqual(esito, 0)
        self.assertIn("Registro dei gate (incremento 1", testo)
        self.assertIn("7.09 [parallel-build]", testo)
        self.assertIn("Verifica: 0 errori", testo)

    def test_checklist_di_una_fase(self):
        esito, testo = self.esegui("checklist", "--fase", "6")
        self.assertEqual(esito, 0)
        self.assertRegex(testo, r"6\.08\s+↻ rinviata")
        self.assertRegex(testo, r"6\.05\s+↻ fatta")

    def test_mostra_e_impatto(self):
        esito, testo = self.esegui("mostra", "entita:fattura", "RNF-7")
        self.assertEqual(esito, 0)
        self.assertIn("### entita fattura", testo)
        self.assertIn("citato da:", testo)
        esito, testo = self.esegui("impatto", "entita:fattura")
        self.assertEqual(esito, 0)
        self.assertIn("tabelle fatture", testo)

    def test_fascio_di_un_task(self):
        esito, testo = self.esegui("fascio", "--task", "C-veicoli-be")
        self.assertEqual(esito, 0)
        self.assertIn("# Fascio del task C-veicoli-be", testo)
        self.assertIn("non costruire ora", testo)
        prima, dopo = testo.split("non costruire ora", 1)
        self.assertIn("scadenza_revisione", dopo)
        self.assertIn("componente veicoli.PromemoriaRevisione (incremento 2)", dopo)
        self.assertNotIn("PromemoriaRevisione", prima)
        self.assertLess(len(testo), cli.BUDGET_FASCIO)

    def test_verifica_json(self):
        esito, testo = self.esegui("verifica", "--json")
        self.assertEqual(esito, 0)
        dati = json.loads(testo)
        self.assertEqual(dati["errori"], [])
        self.assertEqual(dati["conteggi"]["storie"], 17)

    def test_formato(self):
        esito, testo = self.esegui("formato")
        self.assertEqual(esito, 0)
        self.assertIn("storie", testo)
        esito, testo = self.esegui("formato", "storie")
        self.assertIn("obbligatori: titolo, attore, priorita, incremento, fonte", testo)
        self.assertIn("### storie ACC-1", testo)
        self.assertEqual(self.esegui("formato", "ignoto")[0], 2)

    def test_schema_dell_incremento(self):
        esito, testo = self.esegui("schema")
        self.assertEqual(esito, 0)
        self.assertIn("### tabelle veicoli", testo)
        futuri = testo.split("Progettato per incrementi futuri", 1)[1]
        self.assertIn("colonna veicoli.scadenza_revisione (incremento 2)", futuri)
        self.assertNotIn("scadenza_revisione", testo.split("Progettato per incrementi futuri", 1)[0])
        self.apri_incremento_2()
        _, testo = self.esegui("schema", "--nuovi")
        self.assertIn("nome=scadenza_revisione", testo)
        self.assertNotIn("### tabelle fatture", testo)

    def test_voce_sconosciuta_e_errore_d_uso(self):
        self.assertEqual(self.esegui("fascio", "9.99")[0], 2)
        self.assertEqual(self.esegui("apri", "9.99")[0], 2)

    def test_radice_senza_stato(self):
        self.radice = self.tmp
        esito, testo = self.esegui("stato")
        self.assertEqual(esito, 2)
        self.assertIn("voce 0.05", testo)


class Inizio(Base):
    def test_inizia_un_progetto_nuovo(self):
        self.radice = self.tmp / "nuovo"
        self.radice.mkdir()
        esito, testo = self.esegui("inizia", "--progetto", "Prova", "--responsabile", "utente", "--data", "2026-10-23")
        self.assertEqual(esito, 0, testo)
        stato = self.leggi(f"{P}/stato.toml")
        self.assertEqual(stato["scheda"], {"progetto": "Prova", "responsabile": "utente",
                                           "avvio": __import__("datetime").date(2026, 10, 23), "incremento": 1})
        esito, testo = self.esegui("verifica")
        self.assertEqual(esito, 0, testo)
        self.assertIn("si compila alla voce 1.13", testo)
        _, testo = self.esegui("stato")
        self.assertIn("0.01 Repo git", testo)
        self.assertEqual(self.esegui("inizia", "--progetto", "Prova", "--responsabile", "utente")[0], 2)

    def test_la_scheda_si_compila_alla_1_13(self):
        self.radice = self.tmp / "nuovo"
        self.radice.mkdir()
        self.esegui("inizia", "--progetto", "Prova", "--responsabile", "utente")
        esito, testo = self.esegui("chiudi", "1.13", "--evidenza", "stato.toml")
        self.assertEqual(esito, 1)
        self.assertIn("manca 'esposizione'", testo)


class Punti(Base):
    def test_apri_una_voce_chiusa_chiede_una_modifica(self):
        esito, testo = self.esegui("apri", "3.07")
        self.assertEqual(esito, 2)
        self.assertIn("MOD-n", testo)

    def test_apri_e_chiudi(self):
        self.togli_chiusura("4.12")
        self.sostituisci(f"{P}/stato.toml", 'fase = 4\nstato = "superato"', 'fase = 4\nstato = "in-corso"')
        esito, testo = self.esegui("apri", "4.12")
        self.assertEqual(esito, 0, testo)
        self.assertIn("Inizio punto 4.12", testo)
        self.assertEqual(self.leggi(f"{P}/stato.toml")["corrente"]["punto"], "4.12")
        esito, testo = self.esegui("chiudi", "4.12", "--evidenza", "architettura/analisi.md", "--data", "2026-10-15")
        self.assertEqual(esito, 0, testo)
        self.assertIn("Fine punto 4.12", testo)
        self.assertIn("approva 4", testo)
        self.assertEqual(self.leggi(f"{P}/stato.toml")["corrente"]["punto"], "")
        chiusure = [c for c in self.leggi(f"{P}/gate.toml")["chiusure"] if c["voce"] == "4.12"]
        self.assertEqual(len(chiusure), 1)
        self.assertNotIn("incremento", chiusure[0])
        self.assertEqual(self.esegui("verifica")[0], 0)

    def test_un_punto_alla_volta(self):
        self.togli_chiusura("4.12")
        self.togli_chiusura("4.19")
        self.sostituisci(f"{P}/stato.toml", 'fase = 4\nstato = "superato"', 'fase = 4\nstato = "in-corso"')
        self.assertEqual(self.esegui("apri", "4.12")[0], 0)
        esito, testo = self.esegui("apri", "4.19")
        self.assertEqual(esito, 2)
        self.assertIn("il punto 4.12 è aperto", testo)
        with (self.radice / P / "registri.toml").open("a", encoding="utf-8") as f:
            f.write('\n[[domande]]\nid = "Q-1"\ndomanda = "Quale carico regge il VPS?"\npunto = "4.12"\n')
        self.assertEqual(self.esegui("apri", "4.19")[0], 0)

    def test_chiudi_rifiuta_una_voce_che_non_passa(self):
        self.apri_incremento_2()
        prima = (self.radice / P / "gate.toml").read_text(encoding="utf-8")
        esito, testo = self.esegui("chiudi", "2.02", "--evidenza", "requisiti/storie.toml")
        self.assertEqual(esito, 1)
        self.assertIn("CLI-2", testo)
        self.assertIn("[voce 2.02]", testo)
        self.assertEqual((self.radice / P / "gate.toml").read_text(encoding="utf-8"), prima)

    def test_chiusura_per_incremento_e_richiusura(self):
        esito, testo = self.esegui("chiudi", "7.11", "--evidenza", "RK-1", "--data", "2026-10-23")
        self.assertEqual(esito, 0, testo)
        chiusure = [c for c in self.leggi(f"{P}/gate.toml")["chiusure"] if c["voce"] == "7.11"]
        self.assertEqual(len(chiusure), 1)
        self.assertEqual((chiusure[0]["incremento"], chiusure[0]["data"].isoformat()), (1, "2026-10-23"))

    def test_esclusione(self):
        self.assertEqual(self.esegui("chiudi", "4.12", "--non-applicabile")[0], 2)
        self.assertEqual(self.esegui("chiudi", "4.12", "--non-applicabile", "--motivo", "m", "--evidenza", "x")[0], 2)
        esito, _ = self.esegui("chiudi", "4.12", "--non-applicabile", "--motivo", "VPS unico, carico trascurabile")
        self.assertEqual(esito, 0)
        c = next(c for c in self.leggi(f"{P}/gate.toml")["chiusure"] if c["voce"] == "4.12")
        self.assertEqual((c["esito"], "evidenza" in c), ("non-applicabile", False))


class Fasi(Base):
    def test_approva_rifiuta_un_gate_con_voci_aperte(self):
        self.apri_incremento_2()
        esito, testo = self.esegui("approva", "2", "--da", "responsabile")
        self.assertEqual(esito, 1)
        self.assertIn("2.02: aperta", testo)

    def test_nuovo_incremento_dalla_prima_voce_all_approvazione(self):
        self.apri_incremento_2()
        esito, testo = self.esegui("stato")
        self.assertIn("2.↻Ingegneria dei requisiti                     da-fare", testo)
        self.assertEqual(self.esegui("apri", "2.02")[0], 0)
        riga = [r for r in self.leggi(f"{P}/stato.toml")["registro"] if r["fase"] == 2]
        self.assertEqual([(r.get("incremento"), r["stato"]) for r in riga], [(1, "superato"), (2, "in-corso")])

    def test_approva(self):
        self.togli_chiusura("4.12")
        self.sostituisci(f"{P}/stato.toml", 'fase = 4\nstato = "superato"', 'fase = 4\nstato = "in-corso"')
        self.assertEqual(self.esegui("chiudi", "4.12", "--evidenza", "architettura/analisi.md")[0], 0)
        esito, testo = self.esegui("approva", "4", "--da", "responsabile", "--data", "2026-10-16")
        self.assertEqual(esito, 0, testo)
        self.assertIn("git tag -a progettazione/gate-4-2026-10-16", testo)
        riga = next(r for r in self.leggi(f"{P}/stato.toml")["registro"] if r["fase"] == 4)
        self.assertEqual((riga["stato"], riga["approvato_da"], riga["tag"]),
                         ("superato", "responsabile", "progettazione/gate-4-2026-10-16"))
        self.assertIn("note", riga)
        self.assertEqual(self.esegui("verifica")[0], 0)


class Modifiche(Base):
    MOD = ('\n[[modifiche]]\nid = "MOD-2"\ndescrizione = "Il veicolo registra il telaio."\nmotivo = "Richiami."\n'
           'data = 2026-11-03\nimpatto = ["entita:veicolo"]\nriapre = ["3.07", "5.05.4"]\nesito = "approvata"\n'
           'approvato_da = "responsabile"\n')

    def test_modifica_riapre_fasi_e_congelamento(self):
        with (self.radice / P / "registri.toml").open("a", encoding="utf-8") as f:
            f.write(self.MOD)
        esito, testo = self.esegui("verifica")
        self.assertEqual(esito, 1)
        self.assertIn("progetto.py modifica", testo)
        esito, testo = self.esegui("modifica", "MOD-2")
        self.assertEqual(esito, 0, testo)
        self.assertIn("fasi riaperte: 3, 5", testo)
        righe = {r["fase"]: r for r in self.leggi(f"{P}/stato.toml")["registro"]}
        self.assertEqual((righe[3]["stato"], righe[5]["stato"]), ("riaperto", "riaperto"))
        self.assertIn("MOD-2", righe[3]["note"])
        self.assertEqual(self.esegui("verifica")[0], 0)
        _, testo = self.esegui("checklist", "--fase", "7")
        self.assertRegex(testo, r"7\.17\s+↻ riaperta MOD-2")

    def test_modifica_sconosciuta_o_incompleta(self):
        self.assertEqual(self.esegui("modifica", "MOD-9")[0], 2)
        with (self.radice / P / "registri.toml").open("a", encoding="utf-8") as f:
            f.write(self.MOD.replace('riapre = ["3.07", "5.05.4"]\n', ""))
        esito, testo = self.esegui("modifica", "MOD-2")
        self.assertEqual(esito, 1)
        self.assertIn("senza 'riapre'", testo)


class Congelamento(Base):
    def setUp(self):
        super().setUp()
        self.togli_chiusura("7.17")
        percorso = self.radice / P / "stato.toml"
        testo = re.sub(r"\[congelamento\]\n[^\[]*", "", percorso.read_text(encoding="utf-8"))
        percorso.write_text(testo.rstrip() + "\n", encoding="utf-8")

    def test_definition_of_ready_rossa(self):
        esito, testo = self.esegui("congela", "--da", "responsabile", "--data", "2026-10-25")
        self.assertEqual(esito, 1)
        self.assertIn("prima del congelamento 2026-10-25", testo)
        self.assertNotIn("congelamento", self.leggi(f"{P}/stato.toml"))

    def test_congela(self):
        esito, testo = self.esegui("congela", "--da", "responsabile", "--data", "2026-10-22")
        self.assertEqual(esito, 0, testo)
        c = self.leggi(f"{P}/stato.toml")["congelamento"]
        self.assertEqual((c["tag"], c["revisione"], c["prova"]), ("progettazione/incremento-1-2026-10-22", "REV-9", "REV-10"))
        self.assertTrue(any(x["voce"] == "7.17" for x in self.leggi(f"{P}/gate.toml")["chiusure"]))
        self.assertIn("7.09 [parallel-build]", testo)
        self.assertEqual(self.esegui("verifica", "--congelamento")[0], 0)


if __name__ == "__main__":
    unittest.main()
