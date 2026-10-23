"""I controlli sull'esempio: verde così com'è, e ogni guasto tipico produce l'errore atteso.

Ogni test copia l'esempio in una cartella temporanea, lo modifica con una
sostituzione testuale e controlla i reperti.
"""
import datetime
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import controlli
import modello
import viste

SKILL = Path(__file__).resolve().parent.parent
ESEMPIO = SKILL / "assets" / "esempio"
CATALOGO = modello.leggi_catalogo(SKILL / "assets" / "checklist.toml")
P = "docs/progettazione"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.radice = self.tmp / "esempio"
        shutil.copytree(ESEMPIO, self.radice)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def sostituisci(self, relativo, vecchio, nuovo, conteggio=1):
        percorso = self.radice / relativo
        testo = percorso.read_text(encoding="utf-8")
        self.assertIn(vecchio, testo, f"testo da sostituire assente in {relativo}")
        percorso.write_text(testo.replace(vecchio, nuovo, conteggio), encoding="utf-8")

    def aggiungi(self, relativo, testo):
        with (self.radice / relativo).open("a", encoding="utf-8") as f:
            f.write(testo)

    def verifica(self, rigenera=True, **kwargs):
        progetto = modello.carica(self.radice, CATALOGO)
        if rigenera:
            viste.scrivi(progetto, CATALOGO)
            progetto = modello.carica(self.radice, CATALOGO)
        congelamento = kwargs.pop("congelamento", None)
        ctx = controlli.Contesto(progetto, CATALOGO, congelamento=congelamento)
        return controlli.verifica(ctx, **kwargs)

    def errori(self, reperti):
        return [r for r in reperti if r.livello == "errore"]

    def assertErrore(self, reperti, *frammenti):
        """Almeno un errore contiene tutti i frammenti."""
        testi = [r.testo() for r in self.errori(reperti)]
        self.assertTrue(any(all(f in t for f in frammenti) for t in testi),
                        f"nessun errore con {frammenti} in:\n" + "\n".join(testi))


class EsempioVerde(Base):
    def test_verde_anche_al_congelamento(self):
        reperti = self.verifica(rigenera=False, al_congelamento=True, congelamento=datetime.date(2026, 10, 22))
        self.assertEqual([r.testo() for r in reperti], [])

    def test_tutte_le_voci_di_progetto_chiuse(self):
        progetto = modello.carica(self.radice, CATALOGO)
        ctx = controlli.Contesto(progetto, CATALOGO)
        aperte = [i for i, st in controlli.stati_voci(ctx).items()
                  if st["fase"] <= 7 and st["skill"] == "app-blueprint"
                  and st["applicabilita"] == "applicabile" and not st["chiusa"]]
        self.assertEqual(aperte, [])

    def test_ogni_controllo_del_catalogo_esiste(self):
        nomi = {n for v in CATALOGO["voci"] for n in v.get("controllo", [])}
        nomi |= {n for v in CATALOGO["trasversali"] for n in v.get("controllo", [])}
        self.assertEqual(sorted(n for n in nomi if controlli.controllo(n) is None), [])

    def test_ogni_dipendenza_e_legge_esistono(self):
        ids = {v["id"] for v in CATALOGO["voci"]}
        # ogni tipo che una voce legge ha le sue regole di struttura in CAMPI
        tipi = set(controlli.CAMPI) | {"scheda", "adr"}
        for v in CATALOGO["voci"]:
            for d in v.get("dipende", []):
                self.assertIn(d, ids, v["id"])
            for t in v.get("legge", []):
                self.assertIn(t, tipi, v["id"])


class Struttura(Base):
    def test_campo_obbligatorio_mancante(self):
        self.sostituisci(f"{P}/requisiti/requisiti.toml", 'misura = "300 ms al 95° percentile"\n', "")
        self.assertErrore(self.verifica(), "RNF-1: manca 'misura'")

    def test_riferimento_non_risolto(self):
        self.sostituisci(f"{P}/requisiti/storie.toml", 'entita = ["account"]', 'entita = ["utente"]')
        self.assertErrore(self.verifica(), "riferimento 'utente' non risolto")

    def test_valore_non_ammesso(self):
        self.sostituisci(f"{P}/dominio/moduli.toml", 'rischio = "standard"', 'rischio = "medio"')
        self.assertErrore(self.verifica(), "'rischio' = 'medio'")

    def test_id_duplicato(self):
        self.sostituisci(f"{P}/requisiti/storie.toml", 'id = "ACC-2"', 'id = "ACC-1"')
        self.assertErrore(self.verifica(), "id duplicato")

    def test_area_della_storia(self):
        self.sostituisci(f"{P}/requisiti/storie.toml", 'id = "PRZ-1"', 'id = "XYZ-1"')
        self.assertErrore(self.verifica(), "l'id di una storia è <AREA>-n")


class ControlliDelleVoci(Base):
    def test_dipendenze_circolari(self):
        self.aggiungi(f"{P}/dominio/moduli.toml", '\n[[dipendenze]]\na_valle = "accessi"\na_monte = "fatture"\n'
                      'tipo = "cliente-fornitore"\ncomunicazione = "sincrona"\n')
        self.assertErrore(self.verifica(), "dipendenze circolari")

    def test_indice_senza_accessi(self):
        self.sostituisci("contracts/schema.toml", 'colonne = ["cliente_id"], accessi = ["AC-9"]', 'colonne = ["cliente_id"]')
        self.assertErrore(self.verifica(), "indice senza gli accessi")

    def test_filtro_senza_indice(self):
        self.sostituisci("contracts/schema.toml", '  { nome = "ix_interventi_stato_aperto", colonne = ["stato", "aperto_il"], accessi = ["AC-1"] },\n', "")
        self.assertErrore(self.verifica(), "filtra su 'interventi.stato' senza un indice")

    def test_entita_non_tradotta(self):
        self.sostituisci("contracts/schema.toml", 'da = ["entita:veicolo"]', 'da = ["entita:cliente"]')
        self.assertErrore(self.verifica(), "veicolo:", "entità non tradotta")

    def test_proprietario_della_tabella(self):
        self.sostituisci("contracts/schema.toml", 'modulo = "veicoli"\nda = ["entita:veicolo"]', 'modulo = "clienti"\nda = ["entita:veicolo"]')
        self.assertErrore(self.verifica(), "di proprietà di 'veicoli'")

    def test_schermata_senza_uno_stato(self):
        self.sostituisci(f"{P}/ux/ux.toml", 'vuoto = "Nessun cliente: il comando Nuovo cliente in evidenza.", ', "")
        self.assertErrore(self.verifica(), "stati non progettati: ['vuoto']")

    def test_ruoli_della_matrice(self):
        self.sostituisci("contracts/autorizzazioni.toml", 'ruoli = ["operatore", "responsabile", "cliente"]', 'ruoli = ["operatore", "responsabile"]')
        self.assertErrore(self.verifica(), "devono essere gli attori")

    def test_condizione_non_definita(self):
        self.sostituisci("contracts/autorizzazioni.toml", 'condizioni = { cliente = "proprietario" }', 'condizioni = { cliente = "titolare" }')
        self.assertErrore(self.verifica(), "condizione 'titolare' non definita")

    def test_stato_irraggiungibile(self):
        self.sostituisci(f"{P}/dominio/stati.toml", 'stati = ["accettazione", "lavorazione", "chiuso"]',
                         'stati = ["accettazione", "lavorazione", "chiuso", "sospeso"]')
        self.assertErrore(self.verifica(), "stato 'sospeso' irraggiungibile")

    def test_generalizzazione_senza_ristrutturazione(self):
        self.sostituisci(f"{P}/dati/dati.toml", 'oggetto = "generalizzazione:voce-listino-tipo"', 'oggetto = "entita:voce_listino"')
        self.assertErrore(self.verifica(), "generalizzazione senza decisione di ristrutturazione")

    def test_storia_corrente_senza_criteri(self):
        self.sostituisci(f"{P}/requisiti/storie.toml", 'priorita = "should"\nincremento = 2\nfonte = ["operatore"]\nentita = ["cliente"]',
                         'priorita = "should"\nincremento = 1\nfonte = ["operatore"]\nentita = ["cliente"]')
        self.assertErrore(self.verifica(), "CLI-2:", "storia dell'incremento corrente senza criteri")

    def test_trasversale_scoperta(self):
        self.sostituisci(f"{P}/requisiti/requisiti.toml", 'ricerca = ["CLI-2"]\n', "")
        self.assertErrore(self.verifica(), "'ricerca': elenca le storie")

    def test_rnf_alta_senza_decisione(self):
        self.sostituisci(f"{P}/requisiti/requisiti.toml", 'indirizzato_da = ["ADR-0004", "ST-denaro"]', "indirizzato_da = []")
        self.assertErrore(self.verifica(), "RNF-7:", "nessuna decisione lo indirizza")

    def test_strategia_mancante(self):
        testo = (self.radice / f"{P}/architettura/architettura.toml").read_text(encoding="utf-8")
        testo = re.sub(r'\[\[strategie\]\]\nid = "ST-cache".*?(?=\n\[\[)', "", testo, flags=re.S)
        (self.radice / f"{P}/architettura/architettura.toml").write_text(testo, encoding="utf-8")
        self.assertErrore(self.verifica(), "ST-cache")

    def test_api_senza_esempio(self):
        self.sostituisci("contracts/openapi.json", '"example": "(PDF della fattura 42/2026)"', '"description": "pdf"')
        self.assertErrore(self.verifica(), "pdfFattura:", "risposta 200 senza esempio")


class Chiusure(Base):
    def test_evidenza_inesistente(self):
        self.sostituisci(f"{P}/gate.toml", 'evidenza = ["REV-6"]', 'evidenza = ["REV-99"]')
        self.assertErrore(self.verifica(), "evidenza 'REV-99' non trovata")

    def test_esclusione_senza_motivo(self):
        self.sostituisci(f"{P}/gate.toml", 'voce = "4.12"\nesito = "fatto"\nevidenza = ["architettura/analisi.md"]',
                         'voce = "4.12"\nesito = "non-applicabile"')
        self.assertErrore(self.verifica(), "un'esclusione ha il motivo")

    def test_esclusione_da_approvare_con_criticita_alta(self):
        self.sostituisci(f"{P}/stato.toml", 'criticita = "media"', 'criticita = "alta"')
        self.sostituisci(f"{P}/gate.toml", 'voce = "4.12"\nesito = "fatto"\nevidenza = ["architettura/analisi.md"]',
                         'voce = "4.12"\nesito = "non-applicabile"\nmotivo = "prova"')
        self.assertErrore(self.verifica(), "un'esclusione è approvata")

    def test_voce_chiusa_con_controllo_rosso(self):
        self.sostituisci(f"{P}/registri.toml", "p0 = 0", "p0 = 1")
        self.assertErrore(self.verifica(), "[voce 7.13 chiusa] la revisione di prontezza deve chiudere con p0 = 0")

    def test_vista_non_aggiornata(self):
        self.sostituisci(f"{P}/requisiti/storie.toml", 'titolo = "L\'operatore accede ed esce"', 'titolo = "L\'operatore entra ed esce"')
        self.assertErrore(self.verifica(rigenera=False), "vista non aggiornata")

    def test_gate_con_voci_aperte(self):
        self.sostituisci(f"{P}/gate.toml", 'voce = "3.06"', 'voce = "3.06-tolta"')
        reperti = self.verifica()
        self.assertErrore(reperti, "voce '3.06-tolta' sconosciuta")
        self.assertErrore(reperti, "superato con voci aperte: ['3.06']")


class Congelamento(Base):
    def test_domanda_aperta(self):
        self.aggiungi(f"{P}/registri.toml", '\n[[domande]]\nid = "Q-1"\ndomanda = "Il VPS regge?"\npunto = "4.12"\n')
        self.assertErrore(self.verifica(al_congelamento=True, congelamento=datetime.date(2026, 10, 22)), "domande aperte")

    def test_deperibile_scaduto(self):
        self.sostituisci(f"{P}/registri.toml", "verificato_il = 2026-10-22", "verificato_il = 2026-10-01")
        self.assertErrore(self.verifica(al_congelamento=True, congelamento=datetime.date(2026, 10, 22)),
                          "prima del congelamento")


class Piano(Base):
    def test_sovrapposizione_nella_stessa_ondata(self):
        self.sostituisci(f"{P}/piano/piano.toml", 'possiede = ["app/Moduli/Veicoli/**"]', 'possiede = ["app/Moduli/Accessi/**"]')
        self.assertErrore(self.verifica(), "si sovrappongono su 'app/Moduli/Accessi/**'")

    def test_percorso_critico_senza_e2e(self):
        self.sostituisci(f"{P}/piano/piano.toml", 'storie = ["CLI-1", "VEI-1", "ACC-5", "INT-3"]', 'storie = ["CLI-1", "VEI-1"]')
        self.assertErrore(self.verifica(), "percorso 'PC-2': nessun task end-to-end")

    def test_storia_futura_nel_piano(self):
        self.sostituisci(f"{P}/piano/piano.toml", 'storie = ["CLI-1"]', 'storie = ["CLI-1", "CLI-2"]')
        self.assertErrore(self.verifica(), "la storia 'CLI-2' non è dell'incremento corrente")


class Profilo(Base):
    def test_passaggio_al_pubblico_riapre_le_voci_rinviate(self):
        progetto = modello.carica(self.radice, CATALOGO)
        ctx = controlli.Contesto(progetto, CATALOGO)
        rinviate = {i for i, st in controlli.stati_voci(ctx).items() if st["applicabilita"] == "rinviata"}
        self.assertIn("6.08", rinviate)
        self.sostituisci(f"{P}/stato.toml", 'esposizione = "pubblicabile"', 'esposizione = "pubblico"')
        progetto = modello.carica(self.radice, CATALOGO)
        ctx = controlli.Contesto(progetto, CATALOGO)
        stati = controlli.stati_voci(ctx)
        self.assertTrue(all(stati[i]["applicabilita"] == "applicabile" for i in rinviate))
        self.assertErrore(controlli.verifica(ctx, fase_gate=6), "6.08: aperta")


class Incrementi(Base):
    def apri_incremento_2(self):
        self.sostituisci(f"{P}/stato.toml", "incremento = 1\ncostruzione", "incremento = 2\ncostruzione")

    def contesto(self):
        progetto = modello.carica(self.radice, CATALOGO)
        viste.scrivi(progetto, CATALOGO)
        return controlli.Contesto(modello.carica(self.radice, CATALOGO), CATALOGO)

    def test_il_nuovo_incremento_riapre_solo_le_voci_che_si_ripetono(self):
        self.apri_incremento_2()
        ctx = self.contesto()
        stati = controlli.stati_voci(ctx)
        self.assertFalse(stati["2.02"]["chiusa"])
        self.assertTrue(stati["3.07"]["chiusa"])
        self.assertFalse(stati["8.01"]["chiusa"])
        self.assertEqual(controlli.frontiera(ctx)[0], "2.02")
        self.assertEqual(controlli.verifica(ctx), [])

    def test_chiusura_per_incremento_senza_incremento(self):
        self.sostituisci(f"{P}/gate.toml", 'voce = "7.11"\nincremento = 1\n', 'voce = "7.11"\n')
        self.assertErrore(self.verifica(), "voce 7.11: si richiude a ogni incremento")

    def test_due_chiusure_nello_stesso_incremento(self):
        self.aggiungi(f"{P}/gate.toml", '\n[[chiusure]]\nvoce = "7.11"\nincremento = 1\nesito = "fatto"\n'
                      'evidenza = ["RK-1"]\ndata = 2026-10-23\n')
        self.assertErrore(self.verifica(), "voce 7.11 chiusa due volte nell'incremento 1")

    def test_fase_superata_nell_incremento_con_voci_aperte(self):
        self.apri_incremento_2()
        self.aggiungi(f"{P}/stato.toml", '\n[[registro]]\nfase = 2\nincremento = 2\nstato = "superato"\n'
                      'approvato_da = "responsabile"\ndata = 2026-11-02\n')
        self.assertErrore(self.verifica(), "registro, fase 2: superato con voci aperte: ['2.02', '2.07', '2.10']")

    def test_la_revisione_e_dell_incremento(self):
        self.apri_incremento_2()
        self.aggiungi(f"{P}/gate.toml", '\n[[chiusure]]\nvoce = "7.13"\nincremento = 2\nesito = "fatto"\n'
                      'evidenza = ["REV-9"]\ndata = 2026-11-10\n')
        self.assertErrore(self.verifica(), "nessuna revisione di tipo 'prontezza' nell'incremento 2")

    def test_il_piano_di_un_incremento_passato_non_chiude_la_7_01(self):
        self.apri_incremento_2()
        self.aggiungi(f"{P}/gate.toml", '\n[[chiusure]]\nvoce = "7.01"\nincremento = 2\nesito = "fatto"\n'
                      'evidenza = ["piano/piano.toml"]\ndata = 2026-11-10\n')
        self.assertErrore(self.verifica(), "[progetto].incremento = 1")

    def test_incremento_calcolato_dalla_traccia(self):
        progetto = modello.carica(self.radice, CATALOGO)
        self.assertEqual(progetto.incremento_di(progetto.trova("colonne", "veicoli.scadenza_revisione")), 2)
        self.assertEqual(progetto.incremento_di(progetto.trova("indici", "ix_clienti_cognome")), 2)
        self.assertEqual(progetto.incremento_di(progetto.trova("tabelle", "veicoli")), 1)
        self.assertEqual(progetto.incremento_di(progetto.trova("api", "cercaClienti")), 2)


class Modifiche(Base):
    MOD = ('\n[[modifiche]]\nid = "MOD-1"\ndescrizione = "Il veicolo registra il telaio."\nmotivo = "Richiami."\n'
           'data = 2026-11-03\nimpatto = ["entita:veicolo"]\nriapre = ["3.07"]\nesito = "approvata"\n'
           'approvato_da = "responsabile"\n')

    def stati(self):
        return controlli.stati_voci(controlli.Contesto(modello.carica(self.radice, CATALOGO), CATALOGO))

    def test_riapre_le_voci_chiuse_prima(self):
        self.aggiungi(f"{P}/registri.toml", self.MOD)
        stati = self.stati()
        self.assertEqual(stati["3.07"]["riaperta_da"], "MOD-1")
        self.assertFalse(stati["3.07"]["chiusa"])
        self.assertTrue(stati["3.06"]["chiusa"])

    def test_annulla_il_congelamento_anche_senza_nominarlo(self):
        self.aggiungi(f"{P}/registri.toml", self.MOD)
        self.assertEqual(self.stati()["7.17"]["riaperta_da"], "MOD-1")

    def test_una_chiusura_successiva_vale(self):
        self.aggiungi(f"{P}/registri.toml", self.MOD.replace("2026-11-03", "2026-10-01"))
        self.assertTrue(self.stati()["3.07"]["chiusa"])

    def test_proposta_o_respinta_non_riapre(self):
        for esito in ("proposta", "respinta"):
            with self.subTest(esito):
                self.setUp()
                self.aggiungi(f"{P}/registri.toml", self.MOD.replace('"approvata"', f'"{esito}"'))
                self.assertTrue(self.stati()["3.07"]["chiusa"])

    def test_approvata_senza_chi_la_approva(self):
        self.aggiungi(f"{P}/registri.toml", self.MOD.replace('approvato_da = "responsabile"\n', ""))
        self.assertErrore(self.verifica(), "modifica approvata senza 'approvato_da'")


class RecordDelCongelamento(Base):
    def test_tag_che_non_nomina_incremento_e_data(self):
        self.sostituisci(f"{P}/stato.toml", 'tag = "progettazione/incremento-1-2026-10-22"', 'tag = "progettazione/incremento-1"')
        self.assertErrore(self.verifica(), "per questo congelamento è 'progettazione/incremento-1-2026-10-22'")

    def test_revisione_di_un_altro_tipo(self):
        self.sostituisci(f"{P}/stato.toml", 'revisione = "REV-9"', 'revisione = "REV-6"')
        self.assertErrore(self.verifica(), "'revisione' è l'id della revisione di tipo 'prontezza'")


if __name__ == "__main__":
    unittest.main()
