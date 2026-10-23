"""Il validatore del piano sull'esempio: ogni regola del contratto con parallel-build
produce il suo errore. Si modifica una copia del progetto in memoria."""
import copy
import unittest
from pathlib import Path

import modello
import piano as vp

SKILL = Path(__file__).resolve().parent.parent
CATALOGO = modello.leggi_catalogo(SKILL / "assets" / "checklist.toml")
BASE = modello.carica(SKILL / "assets" / "esempio", CATALOGO)


def progetto():
    return copy.deepcopy(BASE)


def task(p, ident):
    return next(t for t in p.piano["task"] if t["id"] == ident)


def errori(p):
    return [r.messaggio for r in vp.valida(p) if r.livello == "errore"]


def avvisi(p):
    return [r.messaggio for r in vp.valida(p) if r.livello == "avviso"]


class Base(unittest.TestCase):
    def assertErrore(self, p, frammento):
        trovati = errori(p)
        self.assertTrue(any(frammento in e for e in trovati), f"nessun errore con '{frammento}' in {trovati}")


class Esempio(Base):
    def test_valido_e_senza_avvisi(self):
        self.assertEqual(vp.valida(progetto()), [])

    def test_conteggi(self):
        c = vp.conteggi(progetto())
        self.assertEqual(c["task"], {"oracoli": 8, "motore": 1, "esemplari": 2, "costruzione": 5})
        self.assertEqual(c["storie"], 17)


class SintassiDeiPercorsi(Base):
    def test_ammessi(self):
        for p in ("app/Moduli/Clienti/**", "CLAUDE.md", "contracts/openapi.json"):
            self.assertIsNone(vp.errore_percorso(p), p)

    def test_rifiutati(self):
        for p in ("src/*.ts", "/assoluto/**", "../fuori/**", "cartella/", "**", "a/**/b", "a//b", "./a/**", ""):
            self.assertIsNotNone(vp.errore_percorso(p), p)

    def test_sovrapposizioni(self):
        self.assertTrue(vp.si_sovrappongono("app/**", "app/Moduli/**"))
        self.assertFalse(vp.si_sovrappongono("app/Mod/**", "app/Moduli/**"))
        self.assertTrue(vp.dentro("app/Moduli/x.php", "app/**"))
        self.assertFalse(vp.dentro("app/**", "app/Moduli/x.php"))
        self.assertFalse(vp.si_sovrappongono("a.txt", "b.txt"))


class Versione(Base):
    def test_piano_di_un_metodo_precedente(self):
        p = progetto()
        p.piano["progetto"]["versione_metodo"] = "2.1.0"
        trovati = errori(p)
        self.assertEqual(len(trovati), 1)
        self.assertIn("metodo 3", trovati[0])


class Ownership(Base):
    def test_sovrapposizione_nella_stessa_ondata(self):
        p = progetto()
        task(p, "C-fatture-be")["possiede"] = ["app/Moduli/Veicoli/**"]
        self.assertErrore(p, "si sovrappongono")

    def test_sovrapposizione_tra_ondate_diverse_e_ammessa(self):
        p = progetto()
        task(p, "E-clienti")["possiede"].append("app/Moduli/Veicoli/README.md")
        self.assertEqual(errori(p), [])

    def test_costruttore_che_possiede_un_oracolo(self):
        p = progetto()
        task(p, "C-veicoli-be")["possiede"].append("tests/Oracoli/Veicoli/**")
        self.assertErrore(p, "tocca gli oracoli")

    def test_costruttore_che_possiede_test_e2e(self):
        p = progetto()
        task(p, "C-fatture-fe")["possiede"].append("tests/e2e/extra/**")
        self.assertErrore(p, "tocca i test e2e")

    def test_intoccabile(self):
        p = progetto()
        task(p, "C-veicoli-be")["possiede"].append("database/migrations/2026_01_01_veicoli.php")
        self.assertErrore(p, "intoccabile")

    def test_autore_di_test_fuori_dai_suoi_oracoli(self):
        p = progetto()
        task(p, "O-veicoli")["possiede"].append("tests/Oracoli/Fatture/**")
        self.assertErrore(p, "solo i percorsi oracoli del suo modulo")

    def test_e2e_fuori_dai_percorsi_e2e(self):
        p = progetto()
        task(p, "X-intervento-completo")["possiede"] = ["tests/altro/**"]
        self.assertErrore(p, "dentro 'percorsi_e2e'")

    def test_oracoli_di_moduli_diversi_sovrapposti(self):
        p = progetto()
        p.piano["oracoli"]["veicoli"].append("tests/Oracoli/**")
        self.assertErrore(p, "si sovrappongono")

    def test_codice_senza_modulo(self):
        p = progetto()
        del task(p, "C-veicoli-be")["modulo"]
        self.assertErrore(p, "task 'C-veicoli-be': manca 'modulo'")


class OndateEDipendenze(Base):
    def test_agente_incompatibile(self):
        p = progetto()
        task(p, "C-veicoli-be")["agente"] = "test-author"
        self.assertErrore(p, "l'agente deve essere")

    def test_dipendenza_dalla_stessa_ondata(self):
        p = progetto()
        task(p, "C-fatture-fe")["dipende_da"].append("C-fatture-be")
        self.assertErrore(p, "non sta in un'ondata precedente")

    def test_dipendenza_inesistente(self):
        p = progetto()
        task(p, "C-fatture-fe")["dipende_da"].append("C-fantasma")
        self.assertErrore(p, "che non esiste")

    def test_ondata_sconosciuta(self):
        p = progetto()
        task(p, "C-fatture-fe")["ondata"] = "e2e"
        self.assertErrore(p, "ondata deve essere")


class MotoreEdEsemplari(Base):
    def test_motore_senza_task_motore(self):
        p = progetto()
        p.piano["task"] = [t for t in p.piano["task"] if t["id"] != "M-prezzi"]
        p.piano["task"] = [dict(t, dipende_da=[d for d in t.get("dipende_da", []) if d != "M-prezzi"])
                           for t in p.piano["task"]]
        self.assertErrore(p, "nessun task lo costruisce nell'ondata 'motore'")

    def test_ondata_motore_per_un_modulo_che_non_lo_e(self):
        p = progetto()
        task(p, "M-prezzi")["modulo"] = "veicoli"
        self.assertErrore(p, "solo moduli con motore = true")

    def test_motore_nell_ondata_di_costruzione(self):
        p = progetto()
        nuovo = copy.deepcopy(task(p, "C-veicoli-be"))
        nuovo.update({"id": "C-prezzi-be", "modulo": "prezzi", "possiede": ["app/Moduli/PrezziExtra/**"]})
        p.piano["task"].append(nuovo)
        self.assertErrore(p, "è un motore e si costruisce nell'ondata 'motore'")

    def test_la_sessione_esegue_i_test_del_modulo(self):
        p = progetto()
        task(p, "M-prezzi")["criteri"].remove("modulo_backend")
        self.assertErrore(p, "la sessione esegue i test del modulo")

    def test_alto_rischio_senza_criterio_aggiuntivo(self):
        p = progetto()
        task(p, "M-prezzi")["criteri"].remove("mutazioni")
        self.assertErrore(p, "il modulo 'prezzi' è ad alto rischio")

    def test_costruzione_di_un_esemplare(self):
        p = progetto()
        nuovo = copy.deepcopy(task(p, "C-veicoli-be"))
        nuovo.update({"id": "C-clienti-be", "modulo": "clienti", "possiede": ["app/Moduli/ClientiExtra/**"]})
        p.piano["task"].append(nuovo)
        self.assertErrore(p, "è un esemplare")

    def test_archetipo_senza_esemplare(self):
        p = progetto()
        p.piano["archetipi"] = [a for a in p.piano["archetipi"] if a["id"] != "crud"]
        self.assertErrore(p, "l'archetipo 'crud' non ha un esemplare")


class Copertura(Base):
    def test_modulo_senza_costruzione(self):
        p = progetto()
        p.piano["task"] = [t for t in p.piano["task"] if t["id"] != "C-veicoli-be"]
        self.assertErrore(p, "'veicoli': nessun task di costruzione")

    def test_storia_di_un_altro_modulo_nel_task_di_oracoli(self):
        p = progetto()
        task(p, "O-veicoli")["storie"].append("FAT-1")
        self.assertErrore(p, "orchestrata dal modulo 'fatture'")

    def test_storia_senza_oracoli(self):
        p = progetto()
        task(p, "O-veicoli")["storie"] = []
        self.assertErrore(p, "storia 'VEI-1': nessun task di oracoli")

    def test_storia_futura(self):
        p = progetto()
        task(p, "O-clienti")["storie"].append("CLI-2")
        self.assertErrore(p, "la storia 'CLI-2' non è dell'incremento corrente")

    def test_schermate_senza_chi_ne_costruisce_il_frontend(self):
        p = progetto()
        p.piano["task"] = [t for t in p.piano["task"] if t["id"] != "C-fatture-fe"]
        self.assertErrore(p, "modulo 'fatture': ha schermate dell'incremento (fattura) e nessun task ne costruisce il frontend")

    def test_frontend_senza_schermate(self):
        p = progetto()
        nuovo = copy.deepcopy(task(p, "C-fatture-fe"))
        nuovo.update({"id": "C-veicoli-fe", "modulo": "veicoli", "possiede": ["resources/js/moduli/veicoli/**"]})
        p.piano["task"].append(nuovo)
        self.assertEqual(errori(p), [])
        self.assertTrue(any("'veicoli': un task ne costruisce il frontend" in a for a in avvisi(p)))

    def test_e2e_senza_storie(self):
        p = progetto()
        task(p, "X-intervento-completo")["storie"] = []
        self.assertErrore(p, "cita le storie che copre")

    def test_modulo_senza_oracoli_nella_tabella(self):
        p = progetto()
        del p.piano["oracoli"]["veicoli"]
        self.assertErrore(p, "[oracoli]: manca 'veicoli'")


def incremento_2():
    """L'esempio all'incremento 2, con il suo piano: cambiano clienti, veicoli, fatture
    e il motore dei prezzi, che acquista una schermata; accessi e interventi, costruiti
    nell'incremento 1, restano fuori. Gli esemplari esistono già."""
    p = progetto()
    p.stato["scheda"]["incremento"] = 2
    pi = p.piano
    pi["progetto"]["incremento"] = 2
    pi["oracoli"] = {m: pi["oracoli"][m] for m in ("clienti", "veicoli", "fatture")}
    pi["oracoli"]["prezzi"] = ["tests/Oracoli/Prezzi/**", "tests/frontend/prezzi/**"]
    for a in pi["archetipi"]:
        a["costruito_in"] = 1

    def oracoli(modulo, storie):
        return {"id": f"O-{modulo}", "ondata": "oracoli", "agente": "test-author", "modulo": modulo,
                "storie": storie, "possiede": pi["oracoli"][modulo], "criteri": ["lint"]}

    def costruzione(modulo, lato, *altri):
        cartella = (f"app/Moduli/{modulo.capitalize()}/**" if lato == "be"
                    else f"resources/js/moduli/{modulo}/**")
        criteri = (["modulo_backend", "fitness", "lint"] if lato == "be"
                   else ["modulo_frontend", "fitness", "lint", "typecheck"])
        return {"id": f"C-{modulo}-{lato}", "ondata": "costruzione",
                "agente": "backend-builder" if lato == "be" else "frontend-builder", "modulo": modulo,
                "possiede": [cartella], "dipende_da": [f"O-{modulo}"], "criteri": criteri + list(altri)}

    pi["task"] = [
        oracoli("clienti", ["CLI-2"]), oracoli("veicoli", ["VEI-2"]), oracoli("fatture", ["FAT-2"]),
        oracoli("prezzi", ["PRZ-1"]),
        {"id": "M-prezzi", "ondata": "motore", "agente": "sessione", "modulo": "prezzi",
         "possiede": ["app/Moduli/Prezzi/**", "resources/js/moduli/prezzi/**"], "dipende_da": ["O-prezzi"],
         "criteri": ["modulo_backend", "modulo_frontend", "fitness", "lint", "typecheck", "mutazioni"]},
        costruzione("clienti", "be"), costruzione("clienti", "fe"), costruzione("veicoli", "be"),
        costruzione("fatture", "be", "mutazioni"), costruzione("fatture", "fe"),
    ]
    return p


class IncrementoSuccessivo(Base):
    def test_piano_dell_incremento_2_valido(self):
        self.assertEqual(vp.valida(incremento_2()), [])

    def test_scope_dell_incremento_2(self):
        self.assertEqual(vp.moduli_in_scope(incremento_2()), {"clienti", "veicoli", "fatture", "prezzi"})

    def test_modulo_costruito_prima_e_non_toccato_resta_fuori(self):
        p = incremento_2()
        p.piano["task"].append({"id": "C-accessi-be", "ondata": "costruzione", "agente": "backend-builder",
                                "modulo": "accessi", "possiede": ["app/Moduli/Accessi/**"],
                                "criteri": ["modulo_backend", "fitness", "lint", "mutazioni"]})
        self.assertErrore(p, "modulo 'accessi' non è dell'incremento corrente")

    def test_elemento_nuovo_porta_il_suo_modulo_nello_scope(self):
        p = incremento_2()
        p.trova("storie", "VEI-2").dati["incremento"] = 3
        # senza VEI-2 restano gli elementi nuovi di veicoli tracciati altrove: nessuno
        self.assertNotIn("veicoli", vp.moduli_in_scope(p))
        p.trova("indici", "ix_veicoli_scadenza_revisione").dati["traccia"] = ["CLI-2"]
        p.__dict__.pop("_incrementi", None)
        self.assertIn("veicoli", vp.moduli_in_scope(p))

    def test_esemplare_costruito_prima_e_un_modulo_normale(self):
        p = incremento_2()
        p.piano["task"].append({"id": "E-clienti", "ondata": "esemplari", "agente": "sessione",
                                "modulo": "clienti", "possiede": ["app/Moduli/ClientiEsemplare/**"],
                                "criteri": ["modulo_backend", "fitness", "lint"]})
        self.assertErrore(p, "nell'ondata 'esemplari' si costruiscono solo moduli esemplari")

    def test_esemplare_costruito_prima_senza_costruito_in(self):
        p = incremento_2()
        del next(a for a in p.piano["archetipi"] if a["id"] == "workflow")["costruito_in"]
        self.assertErrore(p, "dichiara costruito_in")

    def test_costruito_in_non_precedente(self):
        p = incremento_2()
        p.piano["archetipi"][0]["costruito_in"] = 2
        self.assertErrore(p, "costruito_in è un incremento precedente al corrente (2)")

    def test_oracoli_di_una_storia_che_il_modulo_tocca(self):
        p = incremento_2()
        task(p, "O-clienti")["storie"].append("VEI-2")
        self.assertEqual(errori(p), [])

    def test_la_copertura_resta_del_modulo_che_orchestra(self):
        p = incremento_2()
        task(p, "O-clienti")["storie"].append("VEI-2")
        task(p, "O-veicoli")["storie"] = ["CLI-2"]
        self.assertErrore(p, "la storia 'CLI-2' è orchestrata dal modulo 'clienti' e 'veicoli' non è tra quelli che tocca")
        self.assertErrore(p, "storia 'VEI-2': nessun task di oracoli del modulo che la orchestra")


class CriteriEComandi(Base):
    def test_costruzione_senza_fitness(self):
        p = progetto()
        task(p, "C-veicoli-be")["criteri"].remove("fitness")
        self.assertErrore(p, "esegue sempre 'fitness'")

    def test_criterio_non_definito(self):
        p = progetto()
        task(p, "C-veicoli-be")["criteri"].append("benchmark")
        self.assertErrore(p, "'benchmark' non definito")

    def test_comando_di_lato_senza_segnaposto(self):
        p = progetto()
        p.piano["comandi"]["modulo_backend"] = "composer test"
        self.assertErrore(p, "{modulo}")

    def test_comando_di_lato_mancante(self):
        p = progetto()
        del p.piano["comandi"]["modulo_frontend"]
        self.assertErrore(p, "manca 'modulo_frontend', richiesto dai task di 'frontend-builder'")

    def test_criteri_alto_rischio_per_lato(self):
        p = progetto()
        p.piano["rischio"]["criteri_alto_frontend"] = ["typecheck"]
        task(p, "C-fatture-fe")["criteri"].remove("typecheck")
        self.assertErrore(p, "ad alto rischio e il task deve eseguire 'typecheck'")

    def test_stima_senza_incertezza(self):
        p = progetto()
        del p.piano["stima"]["incertezza"]
        self.assertErrore(p, "[stima]: manca 'incertezza'")

    def test_troppi_task_di_costruzione_e_un_avviso(self):
        p = progetto()
        base = task(p, "C-veicoli-be")
        for i in range(vp.LIMITE_CONCORRENZA):
            t = copy.deepcopy(base)
            t.update({"id": f"C-extra-{i}", "possiede": [f"app/Extra{i}/**"]})
            p.piano["task"].append(t)
        self.assertEqual(errori(p), [])
        self.assertTrue(any("procederà a lotti" in a for a in avvisi(p)))


if __name__ == "__main__":
    unittest.main()
