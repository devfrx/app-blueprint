"""La riga di comando su una copia dell'esempio: lettura, protocollo dei punti e
delle fasi (apri, chiudi, approva), modifiche e congelamento."""
import contextlib
import io
import json
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

import controlli
import modello
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

    def chiudi_incremento_1(self):
        """La costruzione dell'incremento 1 chiusa: qui non si costruisce, quindi le voci
        aperte delle fasi 7–12 si escludono, e le fasi risultano approvate."""
        catalogo = modello.leggi_catalogo(cli.CATALOGO)
        progetto = modello.carica(self.radice, catalogo)
        stati = controlli.stati_voci(controlli.Contesto(progetto, catalogo))
        chiusure = ""
        for ident, st in stati.items():
            if 7 <= st["fase"] <= 12 and st["applicabilita"] == "applicabile" and not st["chiusa"]:
                chiusure += (f'\n[[chiusure]]\nvoce = "{ident}"\n' + ("incremento = 1\n" if st["per_incremento"] else "")
                             + 'esito = "non-applicabile"\nmotivo = "Costruzione simulata nel test."\ndata = 2026-10-22\n')
        with (self.radice / P / "gate.toml").open("a", encoding="utf-8") as f:
            f.write(chiusure)
        self.sostituisci(f"{P}/stato.toml", 'fase = 7\nincremento = 1\nstato = "in-corso"',
                         'fase = 7\nincremento = 1\nstato = "superato"\napprovato_da = "responsabile"\ndata = 2026-10-22')
        with (self.radice / P / "stato.toml").open("a", encoding="utf-8") as f:
            for fase in range(8, 13):
                f.write(f'\n[[registro]]\nfase = {fase}\nincremento = 1\nstato = "superato"\n'
                        'approvato_da = "responsabile"\ndata = 2026-10-22\n')
        self.esegui("viste")

    def apri_incremento_2(self):
        self.chiudi_incremento_1()
        esito, testo = self.esegui("incrementa")
        self.assertEqual(esito, 0, testo)

    def aggiungi_modifica(self, **campi):
        dati = {"id": "MOD-2", "descrizione": "Il veicolo registra il telaio.", "motivo": "Richiami.",
                "data": "2026-10-22", "impatto": ["entita:veicolo"], "riapre": ["3.07", "5.05.4"], "esito": "proposta"}
        dati.update(campi)
        righe = "".join(f"{k} = {json.dumps(v) if not k == 'data' else v}\n" for k, v in dati.items() if v is not None)
        with (self.radice / P / "registri.toml").open("a", encoding="utf-8") as f:
            f.write("\n[[modifiche]]\n" + righe)
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
        self.assertIn("tabella:fatture (campo da)", testo)
        _, testo = self.esegui("impatto", "colonna:veicoli.targa")
        self.assertIn('impatto = ["colonna:veicoli.targa"]', testo)
        self.assertIn('riapre = ["5.05", "5.05.4", "5.14"]', testo)

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
        self.assertNotIn("Cambiati da modifiche", testo)
        self.aggiungi_modifica(impatto=["colonna:veicoli.targa"], riapre=["5.05"])
        self.assertEqual(self.esegui("modifica", "MOD-2", "--da", "responsabile")[0], 0)
        _, testo = self.esegui("schema", "--nuovi")
        self.assertIn("- MOD-2: Il veicolo registra il telaio. — impatto colonna:veicoli.targa", testo)

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
        self.assertIn("Frontiera (voci pronte):\n  0.05 Stato della progettazione", testo)
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

    def test_richiudere_in_una_fase_superata_e_una_modifica(self):
        esito, testo = self.esegui("chiudi", "3.07", "--evidenza", "dominio/entita.toml")
        self.assertEqual(esito, 2)
        self.assertIn("è una modifica", testo)

    def test_data_futura_rifiutata(self):
        self.togli_chiusura("4.12")
        self.sostituisci(f"{P}/stato.toml", 'fase = 4\nstato = "superato"', 'fase = 4\nstato = "in-corso"')
        domani = (__import__("datetime").date.today() + __import__("datetime").timedelta(days=1)).isoformat()
        esito, testo = self.esegui("chiudi", "4.12", "--evidenza", "architettura/analisi.md", "--data", domani)
        self.assertEqual(esito, 2)
        self.assertIn("nel futuro", testo)

    def test_chiudi_non_scrive_nulla_se_fallisce(self):
        self.togli_chiusura("4.12")
        self.sostituisci(f"{P}/stato.toml", 'fase = 4\nstato = "superato"', 'fase = 4\nstato = "in-corso"')
        self.sostituisci(f"{P}/requisiti/storie.toml", 'titolo = "L\'operatore accede ed esce"',
                         'titolo = "L\'operatore entra ed esce"')
        prima = {f: f.read_text(encoding="utf-8") for f in (self.radice / P).rglob("*") if f.is_file()}
        esito, _ = self.esegui("chiudi", "4.12", "--evidenza", "inesistente.md")
        self.assertEqual(esito, 1)
        dopo = {f: f.read_text(encoding="utf-8") for f in (self.radice / P).rglob("*") if f.is_file()}
        self.assertEqual(prima, dopo)

    def test_esclusione(self):
        self.togli_chiusura("4.12")
        self.sostituisci(f"{P}/stato.toml", 'fase = 4\nstato = "superato"', 'fase = 4\nstato = "in-corso"')
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

    def test_i_gate_si_approvano_in_ordine(self):
        self.togli_chiusura("4.12")
        self.sostituisci(f"{P}/stato.toml", 'fase = 4\nstato = "superato"', 'fase = 4\nstato = "in-corso"')
        self.sostituisci(f"{P}/stato.toml", 'fase = 5\nincremento = 1\nstato = "superato"',
                         'fase = 5\nincremento = 1\nstato = "in-corso"')
        esito, testo = self.esegui("approva", "5", "--da", "responsabile")
        self.assertEqual(esito, 1)
        self.assertIn("fase 4: in-corso; i gate si approvano in ordine", testo)

    def test_lo_stesso_tag_nello_stesso_giorno_prende_un_suffisso(self):
        self.togli_chiusura("4.12")
        self.sostituisci(f"{P}/stato.toml", 'fase = 4\nstato = "superato"', 'fase = 4\nstato = "in-corso"')
        self.assertEqual(self.esegui("chiudi", "4.12", "--evidenza", "architettura/analisi.md")[0], 0)
        subprocess.run(["git", "-C", str(self.radice), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(self.radice), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                        "--allow-empty", "-m", "x"], check=True)
        subprocess.run(["git", "-C", str(self.radice), "tag", "progettazione/gate-4-2026-10-16"], check=True)
        esito, testo = self.esegui("approva", "4", "--da", "responsabile", "--data", "2026-10-16")
        self.assertEqual(esito, 0, testo)
        self.assertIn("git tag -a progettazione/gate-4-2026-10-16-2", testo)

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
    def test_modifica_approva_e_applica(self):
        self.aggiungi_modifica()
        self.assertEqual(self.esegui("verifica")[0], 0)
        esito, testo = self.esegui("modifica", "MOD-2", "--da", "responsabile", "--data", "2026-10-23")
        self.assertEqual(esito, 0, testo)
        self.assertIn("Chiusure annullate: 3.07, 5.05.4, 7.13, 7.14, 7.17; fasi riaperte: 3, 5.", testo)
        mod = next(m for m in self.leggi(f"{P}/registri.toml")["modifiche"] if m["id"] == "MOD-2")
        self.assertEqual((mod["esito"], mod["approvato_da"], mod["approvata_il"].isoformat(), mod["incremento"]),
                         ("approvata", "responsabile", "2026-10-23", 1))
        annullate = {c["voce"] for c in self.leggi(f"{P}/gate.toml")["chiusure"] if c.get("annullata_da") == "MOD-2"}
        self.assertEqual(annullate, {"3.07", "5.05.4", "7.13", "7.14", "7.17"})
        righe = {r["fase"]: r for r in self.leggi(f"{P}/stato.toml")["registro"]}
        self.assertEqual((righe[3]["stato"], righe[5]["stato"]), ("riaperto", "riaperto"))
        self.assertIn("progettazione/gate-3-2026-10-13", righe[3]["note"])
        self.assertEqual(self.esegui("verifica")[0], 0)
        _, testo = self.esegui("checklist", "--fase", "7")
        self.assertRegex(testo, r"7\.17\s+↻ riaperta MOD-2")
        # la voce riaperta si lavora come un punto, e la chiusura annullata resta storia
        self.assertEqual(self.esegui("apri", "3.07")[0], 0)
        esito, testo = self.esegui("chiudi", "3.07", "--evidenza", "dominio/entita.toml")
        self.assertEqual(esito, 0, testo)
        chiusure = [c for c in self.leggi(f"{P}/gate.toml")["chiusure"] if c["voce"] == "3.07"]
        self.assertEqual([c.get("annullata_da") for c in chiusure], ["MOD-2", None])
        self.assertEqual(self.esegui("modifica", "MOD-2", "--da", "responsabile")[0], 2)

    def test_cambio_di_profilo(self):
        self.sostituisci(f"{P}/stato.toml", 'esposizione = "pubblicabile"', 'esposizione = "pubblico"')
        esito, testo = self.esegui("verifica")
        self.assertIn("registro, fase 6: superato con voci aperte: ['6.08']", testo)
        self.aggiungi_modifica(descrizione="L'app diventa pubblica.", impatto=["voce:6.08"], riapre=["6.08"])
        self.assertEqual(self.esegui("modifica", "MOD-2", "--da", "responsabile")[0], 0)
        righe = {r["fase"]: r for r in self.leggi(f"{P}/stato.toml")["registro"]}
        self.assertEqual(righe[6]["stato"], "riaperto")
        esito, testo = self.esegui("verifica")
        self.assertNotIn("superato con voci aperte", testo)

    def test_modifica_rifiutata(self):
        self.assertEqual(self.esegui("modifica", "MOD-9", "--da", "responsabile")[0], 2)
        self.assertEqual(self.esegui("modifica", "MOD-1", "--da", "responsabile")[0], 2)
        self.aggiungi_modifica(riapre=None, impatto=["registraCliente"])
        prima = (self.radice / P / "registri.toml").read_text(encoding="utf-8")
        esito, testo = self.esegui("modifica", "MOD-2", "--da", "responsabile")
        self.assertEqual(esito, 1)
        self.assertIn("manca 'riapre'", testo)
        self.assertIn("'registraCliente' non è un id citabile", testo)
        self.assertEqual((self.radice / P / "registri.toml").read_text(encoding="utf-8"), prima)


class Congelamento(Base):
    def setUp(self):
        super().setUp()
        self.togli_chiusura("7.17")
        percorso = self.radice / P / "stato.toml"
        testo = re.sub(r"\[congelamento\]\n[^\[]*", "", percorso.read_text(encoding="utf-8"))
        percorso.write_text(testo.rstrip() + "\n", encoding="utf-8")

    def test_definition_of_ready_rossa(self):
        self.sostituisci(f"{P}/registri.toml", "verificato_il = 2026-10-22", "verificato_il = 2026-10-10")
        esito, testo = self.esegui("congela", "--da", "responsabile", "--data", "2026-10-22")
        self.assertEqual(esito, 1)
        self.assertIn("prima del congelamento del 2026-10-22", testo)
        self.assertNotIn("congelamento", self.leggi(f"{P}/stato.toml"))

    def test_congela(self):
        esito, testo = self.esegui("congela", "--da", "responsabile", "--data", "2026-10-22")
        self.assertEqual(esito, 0, testo)
        c = self.leggi(f"{P}/stato.toml")["congelamento"]
        self.assertEqual((c["tag"], c["revisione"], c["prova"]), ("progettazione/incremento-1-2026-10-22", "REV-9", "REV-10"))
        self.assertTrue(any(x["voce"] == "7.17" for x in self.leggi(f"{P}/gate.toml")["chiusure"]))
        self.assertIn("7.09 [parallel-build]", testo)
        self.assertEqual(self.esegui("verifica", "--congelamento")[0], 0)

    def test_dopo_una_modifica_si_ricongela_con_fasi_e_revisioni_nuove(self):
        self.assertEqual(self.esegui("congela", "--da", "responsabile", "--data", "2026-10-22")[0], 0)
        self.aggiungi_modifica(riapre=["3.07"])
        self.assertEqual(self.esegui("modifica", "MOD-2", "--da", "responsabile", "--data", "2026-10-23")[0], 0)
        esito, testo = self.esegui("congela", "--da", "responsabile", "--data", "2026-10-23")
        self.assertEqual(esito, 1)
        for atteso in ("3.07: aperta", "fase 3: gate non approvato (riaperto)", "7.13: aperta", "7.14: aperta",
                       "REV-9: è la revisione di prima di MOD-2"):
            self.assertIn(atteso, testo)


class Incrementa(Base):
    def test_un_incremento_non_chiuso_non_si_lascia(self):
        esito, testo = self.esegui("incrementa")
        self.assertEqual(esito, 1)
        self.assertIn("l'incremento 1 non è chiuso: la fase 12 non è superata", testo)
        self.assertEqual(self.leggi(f"{P}/stato.toml")["scheda"]["incremento"], 1)

    def test_incrementa(self):
        self.aggiungi_modifica()
        self.chiudi_incremento_1()
        esito, testo = self.esegui("incrementa")
        self.assertEqual(esito, 0, testo)
        self.assertIn("Incremento 2 aperto", testo)
        self.assertIn("Modifiche proposte da decidere per prime: MOD-2", testo)
        stato = self.leggi(f"{P}/stato.toml")
        self.assertEqual((stato["scheda"]["incremento"], stato["corrente"]["fase"]), (2, 2))
        self.assertIn("# Stato della progettazione", (self.radice / P / "stato.toml").read_text(encoding="utf-8"))
        esito, testo = self.esegui("verifica")
        self.assertEqual(esito, 0, testo)
        _, testo = self.esegui("stato")
        self.assertIn("Frontiera (voci pronte):\n  2.02", testo)

    def test_oltre_la_roadmap(self):
        self.chiudi_incremento_1()
        self.sostituisci(f"{P}/piano/piano.toml", "[[incrementi]]\nnumero = 2", "[[incrementi]]\nnumero = 3")
        esito, testo = self.esegui("incrementa")
        self.assertEqual(esito, 1)
        self.assertIn("nessun incremento 2 in [[incrementi]]", testo)


if __name__ == "__main__":
    unittest.main()
