"""Validazione del piano di costruzione (docs/progettazione/piano/piano.toml).

Il piano è il contratto tra la progettazione e parallel-build: chi fa cosa, dove
può scrivere, da cosa dipende e come si dimostra che ha finito. Le storie, i
moduli, gli archetipi dei moduli e le classi di rischio non si ripetono qui: si
leggono dalle loro sorgenti. Il piano aggiunge solo ciò che è suo: comandi,
percorsi degli oracoli, archetipi con il loro esemplare, incrementi, stima, task.

Controlli:
  1. versione: un piano di un metodo precedente si rifiuta
  2. struttura: sezioni e campi obbligatori, valori ammessi, id univoci
  3. riferimenti: moduli, storie, task e comandi citati esistono
  4. ondate: ogni task sta in un'ondata con l'agente giusto e dipende solo da task
     di ondate precedenti, quindi il grafo è aciclico per costruzione
  5. ownership: percorsi nella sintassi ammessa; nessuna sovrapposizione tra task
     della stessa ondata; nessun task possiede intoccabili; chi scrive codice non
     possiede oracoli né test end-to-end; gli autori di test possiedono solo test
  6. copertura: ogni modulo dell'incremento ha oracoli e chi lo costruisce, e chi
     ne costruisce il frontend se possiede schermate dell'incremento; ogni
     storia dell'incremento ha un task di oracoli del modulo che la orchestra; ogni
     percorso critico ha un task end-to-end che cita tutte le sue storie
     dell'incremento. Un archetipo il cui esemplare è stato costruito in un
     incremento precedente (costruito_in) non ha un'ondata di esemplari
  7. criteri: chi scrive codice esegue fitness e i test del proprio lato del
     modulo, e per un modulo ad alto rischio anche i criteri aggiuntivi del lato

L'ownership si esprime solo per cartella ('dir/**') o per file esatto: con questi
due modi la sovrapposizione tra due task è decidibile senza ambiguità.
"""
import re

from modello import Reperto, _valori

VERSIONE = 3
ONDATE = ("oracoli", "motore", "esemplari", "costruzione")
AGENTI_PER_ONDATA = {
    "oracoli": {"test-author"},
    "motore": {"sessione"},
    "esemplari": {"sessione"},
    "costruzione": {"backend-builder", "frontend-builder"},
}
SCRIVONO_CODICE = ("motore", "esemplari", "costruzione")
COMANDI_OBBLIGATORI = ("lint", "fitness", "suite", "e2e", "supply_chain")
COMANDO_PER_LATO = {"backend": "modulo_backend", "frontend": "modulo_frontend"}
LATO_DEL_COSTRUTTORE = {"backend-builder": "backend", "frontend-builder": "frontend"}
SEGNAPOSTO_MODULO = "{modulo}"
# Limite predefinito di sotto-agenti concorrenti in Claude Code (verificato sulla
# documentazione il 2026-10-20): oltre, l'ondata procede a lotti.
LIMITE_CONCORRENZA = 20
CARATTERI_JOLLY = set("*?[]")
DOVE = "docs/progettazione/piano/piano.toml"
# Gli elementi che appartengono a un modulo: uno nuovo nell'incremento porta il suo
# modulo nello scope, anche senza storie che il modulo orchestra.
TIPI_DEL_MODULO = ("entita", "attributi", "tabelle", "colonne", "indici", "api", "matrice", "schermate",
                   "facciata", "eventi", "componenti", "pattern", "algoritmi", "transazioni", "porte")


def errore_percorso(p):
    """Un messaggio se il percorso non rispetta la sintassi ammessa, altrimenti None."""
    if not isinstance(p, str) or not p.strip():
        return "percorso vuoto o non testuale"
    if p.startswith("/") or "\\" in p:
        return f"'{p}': usa percorsi relativi alla radice del repo, con /"
    segmenti = p.split("/")
    if any(s in ("..", ".", "") for s in segmenti[:-1]) or segmenti[-1] in ("..", "."):
        return f"'{p}': niente segmenti vuoti, '.' o '..'"
    if p.endswith("/**"):
        base = p[:-3]
        if not base or CARATTERI_JOLLY & set(base):
            return f"'{p}': ammesso solo 'cartella/**' con una cartella esplicita"
        return None
    if p.endswith("/"):
        return f"'{p}': per una cartella scrivi '{p}**'"
    if CARATTERI_JOLLY & set(p):
        return f"'{p}': ammessi solo 'cartella/**' o un file esatto"
    return None


def _cartella(p):
    return p[:-3] if p.endswith("/**") else None


def dentro(a, b):
    """True se tutto ciò che a descrive è descritto anche da b."""
    ca, cb = _cartella(a), _cartella(b)
    if cb is None:
        return ca is None and a == b
    radice = ca if ca is not None else a
    return radice == cb or radice.startswith(cb + "/")


def si_sovrappongono(a, b):
    """True se esiste almeno un percorso descritto sia da a sia da b."""
    return dentro(a, b) or dentro(b, a)


def versione(piano):
    progetto = piano.get("progetto")
    v = progetto.get("versione_metodo") if isinstance(progetto, dict) else None
    if isinstance(v, str) and re.fullmatch(r"\d+\.\d+\.\d+", v):
        return int(v.split(".")[0])
    return None


def moduli_in_scope(progetto):
    """I moduli che l'incremento corrente costruisce o cambia: quelli che orchestrano o
    toccano una sua storia, e quelli che possiedono un elemento che nasce in questo
    incremento. Un modulo costruito prima e che l'incremento non tocca resta fuori."""
    corrente = progetto.incremento_corrente()
    in_scope = set()
    for s in progetto.tutti("storie"):
        if s.dati.get("incremento") == corrente:
            if s.dati.get("modulo"):
                in_scope.add(s.dati["modulo"])
            in_scope.update(_valori(s.dati.get("tocca")))
    in_scope.update(schermate_dell_incremento(progetto))
    for tipo in TIPI_DEL_MODULO:
        for el in progetto.tutti(tipo):
            modulo = progetto.modulo_di(el)
            if modulo and progetto.incremento_di(el) == corrente:
                in_scope.add(modulo)
    return in_scope


def schermate_dell_incremento(progetto):
    """modulo -> le sue schermate toccate da una storia dell'incremento corrente: le
    costruisce, o le cambia, il frontend del modulo che le possiede."""
    correnti = set(storie_in_scope(progetto))
    risultato = {}
    for s in progetto.tutti("schermate"):
        if s.dati.get("modulo") and set(_valori(s.dati.get("storie"))) & correnti:
            risultato.setdefault(s.dati["modulo"], []).append(s.id)
    return risultato


def storie_in_scope(progetto):
    corrente = progetto.incremento_corrente()
    return {s.id: s.dati for s in progetto.tutti("storie") if s.dati.get("incremento") == corrente}


def _lati(task, ondata):
    if ondata == "costruzione":
        lato = LATO_DEL_COSTRUTTORE.get(task.get("agente"))
        return [lato] if lato else []
    criteri = _valori(task.get("criteri"))
    return [lato for lato, comando in COMANDO_PER_LATO.items() if comando in criteri]


def valida(progetto):
    """Restituisce i reperti della validazione del piano letto nel progetto."""
    errori, avvisi = [], []
    piano = progetto.piano or {}
    v = versione(piano)
    if v is None or v != VERSIONE:
        return [Reperto("errore", DOVE, f'[progetto]: versione_metodo deve essere "{VERSIONE}.x.y"; '
                        "un piano di un metodo precedente va riscritto sulle sorgenti del metodo 3", "piano")]

    prog = piano["progetto"]
    for campo in ("nome", "branch_integrazione"):
        if not (isinstance(prog.get(campo), str) and prog[campo].strip()):
            errori.append(f"[progetto]: manca '{campo}'")
    percorsi_e2e = _valori(prog.get("percorsi_e2e"))
    if not percorsi_e2e:
        errori.append("[progetto]: 'percorsi_e2e' deve elencare almeno una cartella")
    intoccabili = _valori(prog.get("intoccabili"))
    if not intoccabili:
        avvisi.append("[progetto]: nessun percorso intoccabile: lockfile, manifest e migrazioni restano senza protezione")
    for p in percorsi_e2e + intoccabili:
        msg = errore_percorso(p)
        if msg:
            errori.append(f"[progetto]: {msg}")

    comandi = piano.get("comandi") if isinstance(piano.get("comandi"), dict) else {}
    if not comandi:
        errori.append("manca la sezione [comandi]")
    for chiave in COMANDI_OBBLIGATORI:
        if not (isinstance(comandi.get(chiave), str) and comandi[chiave].strip()):
            errori.append(f"[comandi]: manca '{chiave}'")
    for chiave in COMANDO_PER_LATO.values():
        if isinstance(comandi.get(chiave), str) and SEGNAPOSTO_MODULO not in comandi[chiave]:
            errori.append(f"[comandi]: '{chiave}' deve contenere {SEGNAPOSTO_MODULO}, per i gate incrementali")

    rischio = piano.get("rischio") if isinstance(piano.get("rischio"), dict) else {}
    criteri_alto = {}
    for lato in COMANDO_PER_LATO:
        chiave = f"criteri_alto_{lato}"
        criteri_alto[lato] = _valori(rischio.get(chiave))
        for c in criteri_alto[lato]:
            if c not in comandi:
                errori.append(f"[rischio]: criterio aggiuntivo '{c}' di '{chiave}' non definito in [comandi]")

    stima = piano.get("stima") if isinstance(piano.get("stima"), dict) else {}
    for campo in ("metodo", "incertezza"):
        if not (isinstance(stima.get(campo), str) and stima[campo].strip()):
            errori.append(f"[stima]: manca '{campo}'")

    # moduli dell'incremento, con i dati delle loro sorgenti
    in_scope = moduli_in_scope(progetto)
    moduli = {}
    for m in progetto.tutti("moduli"):
        if m.id in in_scope:
            moduli[m.id] = m.dati
    oracoli_tab = piano.get("oracoli") if isinstance(piano.get("oracoli"), dict) else {}
    motori, oracoli_di = set(), {}
    for ident, m in moduli.items():
        if m.get("motore") is True:
            motori.add(ident)
        oracoli = _valori(oracoli_tab.get(ident))
        if not oracoli:
            errori.append(f"[oracoli]: manca '{ident}', con i percorsi dove vivono i test del modulo")
        oracoli_di[ident] = oracoli
        for p in oracoli:
            msg = errore_percorso(p)
            if msg:
                errori.append(f"[oracoli] '{ident}': {msg}")
            for e in percorsi_e2e:
                if si_sovrappongono(p, e):
                    errori.append(f"[oracoli] '{ident}': '{p}' si sovrappone ai test e2e '{e}'")
    for ident in oracoli_tab:
        if ident not in moduli:
            avvisi.append(f"[oracoli]: '{ident}' non è un modulo dell'incremento corrente")
    nomi = sorted(moduli)
    for i, a in enumerate(nomi):
        for b in nomi[i + 1:]:
            for pa in oracoli_di[a]:
                for pb in oracoli_di[b]:
                    if si_sovrappongono(pa, pb):
                        errori.append(f"oracoli dei moduli '{a}' e '{b}' si sovrappongono: '{pa}' / '{pb}'")

    archetipi = {}
    for a in piano.get("archetipi", []) or []:
        if isinstance(a, dict) and a.get("id"):
            if a["id"] in archetipi:
                errori.append(f"archetipo '{a['id']}': id duplicato")
            archetipi[a["id"]] = a
    esemplari = set()
    corrente = progetto.incremento_corrente()
    for ident, a in archetipi.items():
        es = a.get("esemplare")
        costruito = a.get("costruito_in")
        if costruito is not None:
            # l'esemplare esiste già: i costruttori lo seguono, nessuno lo ricostruisce
            if not (isinstance(costruito, int) and not isinstance(costruito, bool) and 1 <= costruito < corrente):
                errori.append(f"archetipo '{ident}': costruito_in è un incremento precedente al corrente ({corrente})")
            modulo_es = progetto.trova("moduli", es)
            if modulo_es is None:
                errori.append(f"archetipo '{ident}': esemplare '{es}' non è un modulo")
            elif modulo_es.dati.get("archetipo") != ident:
                errori.append(f"archetipo '{ident}': l'esemplare '{es}' appartiene a un altro archetipo")
            continue
        if es not in moduli:
            errori.append(f"archetipo '{ident}': esemplare '{es}' non è un modulo dell'incremento "
                          "(se è stato costruito in un incremento precedente, dichiara costruito_in)")
        elif moduli[es].get("archetipo") != ident:
            errori.append(f"archetipo '{ident}': l'esemplare '{es}' appartiene a un altro archetipo")
        else:
            esemplari.add(es)
    for ident, m in moduli.items():
        if m.get("motore") is not True and m.get("archetipo") not in archetipi:
            errori.append(f"modulo '{ident}': l'archetipo '{m.get('archetipo')}' non ha un esemplare in [[archetipi]]")

    storie = storie_in_scope(progetto)
    task = {}
    for t in piano.get("task", []) or []:
        if isinstance(t, dict) and t.get("id"):
            task[t["id"]] = t
    if not task:
        errori.append("il piano non dichiara task")

    agenti_usati = {t.get("agente") for t in task.values()}
    for agente, lato in LATO_DEL_COSTRUTTORE.items():
        chiave = COMANDO_PER_LATO[lato]
        if agente in agenti_usati and not (isinstance(comandi.get(chiave), str) and comandi[chiave].strip()):
            errori.append(f"[comandi]: manca '{chiave}', richiesto dai task di '{agente}'")

    tutti_oracoli = [(m_id, p) for m_id, ps in oracoli_di.items() for p in ps]
    indice_ondata = {o: i for i, o in enumerate(ONDATE)}
    per_ondata = {o: [] for o in ONDATE}
    storie_con_oracoli, storie_e2e = set(), {}
    con_oracoli, costruiti, esemplari_con_task, motori_con_task = set(), set(), set(), set()
    lati_costruiti = {}

    for ident, t in task.items():
        ondata = t.get("ondata")
        if ondata not in indice_ondata:
            errori.append(f"task '{ident}': ondata deve essere una tra {list(ONDATE)}")
            continue
        per_ondata[ondata].append(ident)
        agente = t.get("agente")
        if agente not in AGENTI_PER_ONDATA[ondata]:
            errori.append(f"task '{ident}': nell'ondata '{ondata}' l'agente deve essere uno tra {sorted(AGENTI_PER_ONDATA[ondata])}")
        e2e = ondata == "oracoli" and "modulo" not in t
        modulo = t.get("modulo")
        if modulo is None and not e2e:
            errori.append(f"task '{ident}': manca 'modulo'")
        elif modulo is not None and modulo not in moduli:
            errori.append(f"task '{ident}': modulo '{modulo}' non è dell'incremento corrente")
            modulo = None
        if modulo and ondata == "motore" and modulo not in motori:
            errori.append(f"task '{ident}': nell'ondata 'motore' si costruiscono solo moduli con motore = true")
        if modulo and ondata == "esemplari" and modulo not in esemplari:
            errori.append(f"task '{ident}': nell'ondata 'esemplari' si costruiscono solo moduli esemplari")
        if modulo and ondata == "costruzione" and modulo in esemplari:
            errori.append(f"task '{ident}': '{modulo}' è un esemplare e si completa nell'ondata 'esemplari'")
        if modulo and ondata == "costruzione" and modulo in motori:
            errori.append(f"task '{ident}': '{modulo}' è un motore e si costruisce nell'ondata 'motore'")

        possiede = _valori(t.get("possiede"))
        if not possiede:
            errori.append(f"task '{ident}': 'possiede' deve elencare almeno un percorso")
        for p in possiede:
            msg = errore_percorso(p)
            if msg:
                errori.append(f"task '{ident}': {msg}")
                continue
            for x in intoccabili:
                if si_sovrappongono(p, x):
                    errori.append(f"task '{ident}': possiede '{p}', che tocca l'intoccabile '{x}'")
            if e2e:
                if not any(dentro(p, e) for e in percorsi_e2e):
                    errori.append(f"task '{ident}': un task end-to-end possiede solo percorsi dentro 'percorsi_e2e', non '{p}'")
            elif ondata == "oracoli":
                if modulo and not any(dentro(p, o) for o in oracoli_di.get(modulo, [])):
                    errori.append(f"task '{ident}': un autore di test possiede solo i percorsi oracoli del suo modulo, non '{p}'")
            else:
                for m_id, o in tutti_oracoli:
                    if si_sovrappongono(p, o):
                        errori.append(f"task '{ident}': possiede '{p}', che tocca gli oracoli del modulo '{m_id}'")
                for e in percorsi_e2e:
                    if si_sovrappongono(p, e):
                        errori.append(f"task '{ident}': possiede '{p}', che tocca i test e2e")

        for dip in _valori(t.get("dipende_da")):
            if dip not in task:
                errori.append(f"task '{ident}': dipende da '{dip}', che non esiste")
            elif task[dip].get("ondata") in indice_ondata and indice_ondata[task[dip]["ondata"]] >= indice_ondata[ondata]:
                errori.append(f"task '{ident}': dipende da '{dip}', che non sta in un'ondata precedente")

        criteri = _valori(t.get("criteri"))
        if not criteri:
            errori.append(f"task '{ident}': 'criteri' deve elencare almeno un comando")
        for c in criteri:
            if c not in comandi:
                errori.append(f"task '{ident}': criterio '{c}' non definito in [comandi]")
        if ondata in SCRIVONO_CODICE:
            if "fitness" not in criteri:
                errori.append(f"task '{ident}': un task che scrive codice esegue sempre 'fitness'")
            if agente in LATO_DEL_COSTRUTTORE and ondata == "costruzione":
                richiesto = COMANDO_PER_LATO[LATO_DEL_COSTRUTTORE[agente]]
                if richiesto not in criteri:
                    errori.append(f"task '{ident}': un task di '{agente}' esegue sempre '{richiesto}'")
            elif ondata != "costruzione" and not _lati(t, ondata):
                errori.append(f"task '{ident}': la sessione esegue i test del modulo che costruisce, "
                              f"'{COMANDO_PER_LATO['backend']}' e/o '{COMANDO_PER_LATO['frontend']}'")
            if modulo and moduli[modulo].get("rischio") == "alto":
                for lato in _lati(t, ondata):
                    for c in criteri_alto[lato]:
                        if c not in criteri:
                            errori.append(f"task '{ident}': il modulo '{modulo}' è ad alto rischio e il task deve eseguire '{c}'")

        storie_task = _valori(t.get("storie"))
        if ondata == "oracoli" and not storie_task and (e2e or modulo not in motori):
            errori.append(f"task '{ident}': un task di test cita le storie che copre, per la tracciabilità")
        for s in storie_task:
            if s not in storie:
                errori.append(f"task '{ident}': la storia '{s}' non è dell'incremento corrente")
            elif ondata == "oracoli" and not e2e and modulo and storie[s].get("modulo") != modulo \
                    and modulo not in _valori(storie[s].get("tocca")):
                errori.append(f"task '{ident}': la storia '{s}' è orchestrata dal modulo '{storie[s].get('modulo')}' "
                              f"e '{modulo}' non è tra quelli che tocca")
            elif ondata == "oracoli" and not e2e and storie[s].get("modulo") == modulo:
                storie_con_oracoli.add(s)
        if e2e:
            storie_e2e[ident] = set(storie_task)

        if modulo and ondata in SCRIVONO_CODICE:
            lati_costruiti.setdefault(modulo, set()).update(_lati(t, ondata))
        if modulo and ondata == "oracoli":
            con_oracoli.add(modulo)
        elif modulo and ondata == "motore":
            motori_con_task.add(modulo)
        elif modulo and ondata == "esemplari":
            esemplari_con_task.add(modulo)
        elif modulo:
            costruiti.add(modulo)

    for o in ONDATE:
        ids = per_ondata[o]
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                for pa in _valori(task[a].get("possiede")):
                    for pb in _valori(task[b].get("possiede")):
                        if errore_percorso(pa) is None and errore_percorso(pb) is None and si_sovrappongono(pa, pb):
                            errori.append(f"ondata '{o}': i task '{a}' e '{b}' si sovrappongono su '{pa}' / '{pb}'")

    for m_id in moduli:
        if m_id not in con_oracoli:
            errori.append(f"modulo '{m_id}': nessun task di oracoli")
        if m_id in motori and m_id not in motori_con_task:
            errori.append(f"modulo '{m_id}': è un motore e nessun task lo costruisce nell'ondata 'motore'")
        elif m_id not in motori and m_id not in esemplari and m_id not in costruiti:
            errori.append(f"modulo '{m_id}': nessun task di costruzione")
    con_schermate = schermate_dell_incremento(progetto)
    for m_id in sorted(set(con_schermate) & set(moduli)):
        if "frontend" not in lati_costruiti.get(m_id, set()):
            errori.append(f"modulo '{m_id}': ha schermate dell'incremento ({', '.join(con_schermate[m_id])}) e nessun "
                          "task ne costruisce il frontend")
    for m_id in sorted(lati_costruiti):
        if "frontend" in lati_costruiti[m_id] and m_id not in con_schermate:
            avvisi.append(f"modulo '{m_id}': un task ne costruisce il frontend, ma il modulo non possiede schermate "
                          "dell'incremento")
    for es in esemplari:
        if es not in esemplari_con_task:
            errori.append(f"esemplare '{es}': nessun task nell'ondata 'esemplari'")
    for s_id in storie:
        if s_id not in storie_con_oracoli:
            errori.append(f"storia '{s_id}': nessun task di oracoli del modulo che la orchestra la copre")
    for pc in progetto.tutti("percorsi"):
        richieste = set(_valori(pc.dati.get("storie")))
        if not richieste & set(storie):
            continue
        if not any(richieste & set(storie) <= coperte for coperte in storie_e2e.values()):
            errori.append(f"percorso '{pc.id}': nessun task end-to-end cita tutte le sue storie dell'incremento")

    if len(per_ondata["costruzione"]) > LIMITE_CONCORRENZA:
        avvisi.append(f"ondata 'costruzione': {len(per_ondata['costruzione'])} task, oltre il limite predefinito di "
                      f"{LIMITE_CONCORRENZA} sotto-agenti concorrenti: procederà a lotti. Valuta il verdetto 'incrementi'")

    return ([Reperto("errore", DOVE, e, "piano") for e in errori]
            + [Reperto("avviso", DOVE, a, "piano") for a in avvisi])


def conteggi(progetto):
    """Task per ondata e rientri seriali: la base della stima (voce 7.02)."""
    per_ondata = {o: 0 for o in ONDATE}
    for t in (progetto.piano or {}).get("task", []) or []:
        if isinstance(t, dict) and t.get("ondata") in per_ondata:
            per_ondata[t["ondata"]] += 1
    return {"task": per_ondata, "rientri_seriali": sum(per_ondata.values()),
            "moduli": len(moduli_in_scope(progetto)), "storie": len(storie_in_scope(progetto))}
