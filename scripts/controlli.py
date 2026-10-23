"""I controlli del progetto: struttura delle sorgenti, riferimenti, controlli
nominati del catalogo, chiusure delle voci, gate e congelamento.

Lo script verifica struttura e coerenza, non verità: che una storia sia giusta lo
decide l'utente, che un comando funzioni lo dimostra lo scheletro.

Ogni controllo restituisce una lista di Reperto. Un errore blocca la chiusura
della voce che lo richiede; un avviso va letto ma non blocca.
"""
import datetime
import re
from dataclasses import dataclass, field

import condizioni
from modello import ADR, CONTRATTI, MOCKUP, PREFISSI, PROGETTAZIONE, RE_PREFISSATO, RE_SLUG, Reperto, _valori

CARATTERISTICHE = ("idoneita-funzionale", "efficienza-prestazionale", "compatibilita",
                   "capacita-di-interazione", "affidabilita", "sicurezza", "manutenibilita",
                   "flessibilita", "safety")
STATI_SCHERMATA = ("caricamento", "vuoto", "errore", "parziale", "successo", "permesso_negato")
TRASVERSALI = ("autenticazione", "account-e-profilo", "utenti-e-ruoli", "amministrazione", "audit",
               "notifiche", "ricerca", "import-export", "privacy", "pagine-di-servizio", "onboarding-e-aiuto")
SEZIONI_VISIONE = ("## Problema", "## Contesto", "## Perimetro")
# Le strategie che ogni voce richiede: il tema è l'id senza "ST-".
STRATEGIE_PER_VOCE = {
    "4.04": ("versionamento",),
    "4.05": ("dati",),
    "4.06": ("backup",),
    "4.08": ("autenticazione", "autorizzazione", "errori", "osservabilita", "configurazione",
             "cache", "concorrenza", "segreti", "audit", "i18n", "tempo"),
    "4.09": ("resilienza",),
    "5.06": ("migrazioni",),
    "6.09": ("i18n",),
    "7.07": ("qualita-codice",),
    "7.08": ("ci-cd",),
}
STRATEGIE_PER_INNESCO = {"denaro": "denaro", "multitenant": "multi-tenancy"}

# tipo -> (campi obbligatori, {campo: valori ammessi})
CAMPI = {
    "rischi": (("testo", "tipo", "probabilita", "impatto", "risposta", "stato", "responsabile"),
               {"tipo": {"tecnico", "prodotto", "progetto", "sicurezza", "conformita", "esercizio"},
                "probabilita": {"bassa", "media", "alta"}, "impatto": {"basso", "medio", "alto"},
                "risposta": {"evita", "mitiga", "trasferisci", "accetta"},
                "stato": {"aperto", "accettato", "chiuso"}}),
    "assunzioni": (("testo", "verifica"), {}),
    "domande": (("domanda", "punto"), {}),
    "debito": (("descrizione", "motivo", "segnale", "rientro"), {}),
    "deperibili": (("cosa", "fonte", "verificato_il"), {}),
    "revisioni": (("tipo", "oggetto", "revisore", "data", "incremento", "esito"),
                  {"tipo": {"requisiti", "validazione", "walkthrough", "dominio", "architettura", "dettaglio",
                            "accessibilita", "euristica", "usabilita", "prontezza", "decidibilita", "pre-mortem",
                            "accettazione", "operativa"}}),
    "modifiche": (("descrizione", "motivo", "data", "esito"), {"esito": {"proposta", "approvata", "respinta"}}),
    "obiettivi": (("testo", "metrica", "valore"), {}),
    "stakeholder": (("descrizione", "categorie", "interesse", "influenza", "usa"),
                    {"interesse": {"alto", "medio", "basso"}, "influenza": {"alta", "media", "bassa"}}),
    "sistemi": (("descrizione", "integrazione"), {}),
    "non_obiettivi": (("testo",), {}),
    "vincoli": (("tipo", "testo", "fonte"),
                {"tipo": {"tecnico", "budget", "tempo", "competenze", "organizzativo", "conformita"}}),
    "aree": (("prefisso", "nome"), {}),
    "qualita": (("caratteristica", "rilevanza", "motivo"),
                {"caratteristica": set(CARATTERISTICHE), "rilevanza": {"alta", "media", "bassa", "non-pertinente"}}),
    "rnf": (("caratteristica", "stimolo", "contesto", "risposta", "misura", "prova", "fonte"),
            {"caratteristica": set(CARATTERISTICHE)}),
    "requisiti_dati": (("concetto", "volume", "crescita", "conservazione", "fonte"), {}),
    "percorsi": (("nome", "storie"), {}),
    "conflitti": (("tra", "oggetto", "risoluzione"), {}),
    "storie": (("titolo", "attore", "priorita", "incremento", "fonte"), {}),
    "glossario": (("termine", "definizione"), {}),
    "regole": (("tipo", "testo"), {"tipo": {"regola", "invariante", "eccezione"}}),
    "sottodomini": (("tipo", "descrizione"), {"tipo": {"core", "supporto", "generico"}}),
    "moduli": (("sottodominio", "responsabilita"),
               {"archetipo": {"crud", "workflow", "integrazione", "reportistica", "tempo-reale"},
                "rischio": {"standard", "alto"}}),
    "dipendenze": (("a_valle", "a_monte", "tipo"),
                   {"tipo": {"partnership", "kernel-condiviso", "cliente-fornitore", "conformista",
                             "anticorruzione", "servizio-aperto", "linguaggio-pubblicato"},
                    "comunicazione": {"sincrona", "asincrona"}}),
    "entita": (("termine", "descrizione", "modulo"), {}),
    "attributi": (("nome", "dominio", "descrizione"), {}),
    "generalizzazioni": (("padre", "figli", "copertura", "disgiunzione"),
                         {"copertura": {"totale", "parziale"}, "disgiunzione": {"esclusiva", "sovrapposta"}}),
    "relazioni": (("nome", "partecipanti", "descrizione"), {}),
    "macchine": (("entita", "attributo", "stati", "iniziale", "transizioni"), {}),
    "processi": (("titolo", "tipo"), {"tipo": {"attivita", "caso-d-uso", "event-storming"}}),
    "driver": (("tipo", "ref", "motivo"), {"tipo": {"funzionale", "qualita", "vincolo"}}),
    "strategie": (("tema", "decisione", "motivo"), {}),
    "ambienti": (("scopo", "ospitato", "dati", "accesso"), {"dati": {"sintetici", "anonimizzati", "reali"}}),
    "integrazioni": (("sistema", "modulo", "protocollo", "timeout", "tentativi", "idempotenza", "guasto"), {}),
    "confini": (("descrizione", "da", "a"), {}),
    "flussi": (("descrizione", "confini", "dati"), {}),
    "minacce": (("flusso", "stride", "descrizione", "probabilita", "impatto", "contromisure", "residuo"),
                {"stride": {"S", "T", "R", "I", "D", "E"}, "probabilita": {"bassa", "media", "alta"},
                 "impatto": {"basso", "medio", "alto"}}),
    "volumi": (("concetto", "volume", "crescita"), {}),
    "accessi": (("operazione", "tipo", "frequenza", "per", "cammino", "traccia"),
                {"tipo": {"interattiva", "batch"}, "per": {"ora", "giorno", "settimana", "mese", "anno"}}),
    "ristrutturazione": (("tipo", "oggetto", "decisione", "motivo"),
                         {"tipo": {"ridondanza", "generalizzazione", "partizionamento", "accorpamento", "identificatore"}}),
    "tabelle": (("colonne", "chiave"), {"normalizzazione": {"1NF", "2NF", "3NF", "BCNF"}}),
    "colonne": (("nome", "tipo", "nullo"), {}),
    "indici": (("nome", "colonne"), {}),
    "errori": (("categoria", "http", "recuperabile", "log"),
               {"categoria": {"validazione", "dominio", "autenticazione", "autorizzazione", "non-trovato",
                              "conflitto", "limite", "esterno", "infrastruttura"},
                "log": {"debug", "info", "avviso", "errore"}}),
    "validazioni": (("campo", "regola", "errore"), {}),
    "variabili": (("descrizione", "ambienti"), {}),
    "segreti": (("descrizione", "rotazione"), {}),
    "matrice": (("risorsa", "azione", "consenti"), {}),
    "api": (("x-modulo", "x-storie", "responses"), {}),
    "dettaglio": (("modulo",), {}),
    "facciata": (("operazione", "firma", "semantica", "errori", "traccia"), {}),
    "eventi": (("nome", "dati", "consumatori", "traccia"), {}),
    "componenti": (("nome", "responsabilita", "traccia"), {}),
    "pattern": (("nome", "problema", "dove"), {}),
    "algoritmi": (("nome", "problema", "soluzione", "complessita"), {}),
    "transazioni": (("operazione", "confine", "isolamento", "concorrenza"), {}),
    "porte": (("nome", "verso", "finto"), {}),
    "sequenze": (("percorso",), {}),
    "personas": (("attore", "descrizione", "obiettivi"), {}),
    "sezioni": (("nome", "ruoli"), {}),
    "rotte": (("percorso", "schermata", "ruoli"), {}),
    "schermate": (("scopo", "ruoli", "storie", "stati"), {}),
    "testi": (("chiave", "testo"), {}),
    "task": (("ondata", "agente", "possiede", "criteri"), {}),
    "incrementi": (("numero", "obiettivo", "rilascio"), {"rilascio": {"locale", "staging", "produzione"}}),
    "livelli": (("scopo", "strumento", "ambiente", "dati", "automazione", "ingresso", "uscita"), {}),
}


@dataclass
class Contesto:
    progetto: object
    catalogo: dict
    oggi: datetime.date = field(default_factory=datetime.date.today)
    congelamento: datetime.date | None = None


def _pieno(valore):
    if valore is None:
        return False
    if isinstance(valore, str):
        return bool(valore.strip())
    if isinstance(valore, (list, dict)):
        return bool(valore)
    return True


def _r(livello, dove, messaggio, controllo):
    return Reperto(livello, dove, messaggio, controllo)


# --- struttura e riferimenti ------------------------------------------------------

def struttura(progetto):
    """Campi obbligatori, valori ammessi, forma degli id e riferimenti risolti, per
    ogni elemento letto."""
    reperti = []
    aree = progetto.aree()
    for tipo, gruppo in progetto.elementi.items():
        obbligatori, enumerati = CAMPI.get(tipo, ((), {}))
        for el in gruppo.values():
            dove = f"{el.sorgente} → {el.id}"
            for campo in obbligatori:
                if not _pieno(el.dati.get(campo)):
                    reperti.append(_r("errore", dove, f"manca '{campo}'", "struttura"))
            for campo, ammessi in enumerati.items():
                valore = el.dati.get(campo)
                if valore is not None and valore not in ammessi:
                    reperti.append(_r("errore", dove, f"'{campo}' = '{valore}', ammessi: {sorted(ammessi)}", "struttura"))
            for campo, valore, risolto in progetto.uscenti(el):
                if risolto is None:
                    reperti.append(_r("errore", dove, f"'{campo}': riferimento '{valore}' non risolto", "riferimenti"))
            reperti.extend(_forma_id(el, aree))
    return reperti


def _forma_id(el, aree):
    tipi_prefissati = {v: k for k, v in PREFISSI.items()}
    dove = f"{el.sorgente} → {el.id}"
    if el.tipo in tipi_prefissati and el.tipo not in ("adr",):
        prefisso = tipi_prefissati[el.tipo]
        m = RE_PREFISSATO.match(el.id)
        if not m or m.group(1) != prefisso:
            return [_r("errore", dove, f"l'id di {el.tipo} ha la forma {prefisso}-…", "struttura")]
        if el.tipo == "strategie" and el.id != f"ST-{el.dati.get('tema')}":
            return [_r("errore", dove, f"l'id di una strategia è ST-<tema>, qui ST-{el.dati.get('tema')}", "struttura")]
    if el.tipo == "storie":
        m = RE_PREFISSATO.match(el.id)
        if not m or m.group(1) not in aree:
            return [_r("errore", dove, f"l'id di una storia è <AREA>-n con un'area di [[aree]] ({sorted(aree)})", "struttura")]
    if el.tipo == "aree":
        if not re.fullmatch(r"[A-Z]{2,5}", el.id) or el.id in PREFISSI:
            return [_r("errore", dove, f"prefisso d'area di 2–5 maiuscole, diverso da quelli riservati {sorted(PREFISSI)}", "struttura")]
    if el.tipo in ("stakeholder", "moduli", "entita", "sottodomini", "sistemi", "ambienti", "confini",
                   "schermate", "personas", "sezioni", "relazioni", "generalizzazioni") and not RE_SLUG.match(el.id):
        return [_r("errore", dove, "id in minuscolo, con cifre, '-' o '_'", "struttura")]
    return []


# --- controlli nominati ----------------------------------------------------------------

def c_stato(ctx, voce):
    p, reperti = ctx.progetto, []
    s = p.stato
    dove = f"{PROGETTAZIONE}/stato.toml"
    if not s:
        return [_r("errore", dove, "manca o è vuoto", "stato")]
    scheda = s.get("scheda", {})
    versione = str(s.get("metodo", ""))
    if versione.split(".")[0] != str(ctx.catalogo.get("versione", "")).split(".")[0]:
        reperti.append(_r("errore", dove, f"metodo = '{versione}': il catalogo è della versione "
                          f"{ctx.catalogo.get('versione')}, e un progetto di un'altra versione va migrato", "stato"))
    # La scheda nasce con progetto, responsabile, avvio e incremento (progetto.py inizia);
    # il profilo si compila alla voce 1.13 e il verdetto alla 1.14: prima mancano per forza.
    da_compilare = {"esposizione": "1.13", "criticita": "1.13", "processo": "1.13", "verdetto": "1.14"}
    for campo in ("progetto", "responsabile", "esposizione", "criticita", "processo", "avvio", "verdetto", "incremento"):
        if not _pieno(scheda.get(campo)):
            if campo in da_compilare and voce != da_compilare[campo] and not _chiusa(ctx, da_compilare[campo]):
                reperti.append(_r("avviso", dove, f"[scheda]: '{campo}' si compila alla voce {da_compilare[campo]}", "stato"))
            else:
                reperti.append(_r("errore", dove, f"[scheda]: manca '{campo}'", "stato"))
    ammessi = {
        "esposizione": set(condizioni.ESPOSIZIONI), "criticita": set(condizioni.CRITICITA),
        "processo": {"cascata", "v", "iterativo", "agile", "ibrido"},
        "verdetto": {"nebbia", "fuori-metodo", "incremento-unico", "incrementi"},
        "costruzione": {"parallela", "seriale"},
    }
    for campo, valori in ammessi.items():
        if campo in scheda and scheda[campo] not in valori:
            reperti.append(_r("errore", dove, f"[scheda].{campo} = '{scheda[campo]}', ammessi: {sorted(valori)}", "stato"))
    noti = set(ctx.catalogo.get("inneschi", {}))
    for i in scheda.get("inneschi", []):
        if i not in noti:
            reperti.append(_r("errore", dove, f"innesco '{i}' sconosciuto; noti: {sorted(noti)}", "stato"))
    inc = scheda.get("incremento")
    if not (isinstance(inc, int) and not isinstance(inc, bool) and inc >= 1):
        reperti.append(_r("errore", dove, "[scheda].incremento è un intero da 1", "stato"))
    elif scheda.get("verdetto") == "incremento-unico" and inc != 1:
        reperti.append(_r("errore", dove, "con il verdetto 'incremento-unico', l'incremento è 1", "stato"))
    if voce == "7.12" and scheda.get("costruzione") not in ("parallela", "seriale"):
        reperti.append(_r("errore", dove, "[scheda].costruzione: 'parallela' o 'seriale'", "stato"))
    fasi_note = {f["numero"] for f in ctx.catalogo.get("fasi", [])}
    corrente, viste = p.incremento_corrente(), set()
    for riga in s.get("registro", []):
        fase, inc = riga.get("fase"), riga.get("incremento", 1)
        if fase not in fasi_note:
            reperti.append(_r("errore", dove, f"registro: fase '{fase}' sconosciuta", "stato"))
        if not (isinstance(inc, int) and not isinstance(inc, bool) and 1 <= inc <= corrente):
            reperti.append(_r("errore", dove, f"registro, fase {fase}: incremento '{inc}' fuori da 1–{corrente}", "stato"))
        elif (fase, inc) in viste:
            reperti.append(_r("errore", dove, f"registro, fase {fase}: due righe per l'incremento {inc}", "stato"))
        viste.add((fase, inc))
        if riga.get("stato") not in {"da-fare", "in-corso", "superato", "riaperto", "fuori-catena"}:
            reperti.append(_r("errore", dove, f"registro, fase {fase}: stato '{riga.get('stato')}' non ammesso", "stato"))
        if riga.get("stato") == "superato" and not (_pieno(riga.get("approvato_da")) and _pieno(riga.get("data"))):
            reperti.append(_r("errore", dove, f"registro, fase {fase}: superato senza approvato_da e data", "stato"))
    return reperti


def _chiusa(ctx, ident):
    return bool(stati_voci(ctx).get(ident, {}).get("chiusa"))


def righe_correnti(ctx):
    """fase -> la riga del registro che vale ora. Una fase con voci per incremento
    ha una riga per incremento, e vale quella del corrente (assente: da fare); le
    altre fasi valgono con la riga più recente."""
    p = ctx.progetto
    corrente = p.incremento_corrente()
    ripetute = {st["fase"] for st in stati_voci(ctx).values() if st["per_incremento"]}
    righe = {}
    for riga in p.stato.get("registro", []):
        fase, inc = riga.get("fase"), riga.get("incremento", 1)
        if not isinstance(inc, int) or inc > corrente or (fase in ripetute and inc != corrente):
            continue
        if fase not in righe or inc >= righe[fase].get("incremento", 1):
            righe[fase] = riga
    return righe


def c_visione(ctx, voce):
    relativo = f"{PROGETTAZIONE}/prodotto/visione.md"
    testo = ctx.progetto.testi.get(relativo)
    if testo is None:
        testo = _leggi(ctx, relativo)
    if testo is None:
        return [_r("errore", relativo, "manca", "visione")]
    mancano = [s for s in SEZIONI_VISIONE if s not in testo]
    return [_r("errore", relativo, f"mancano le sezioni {mancano}", "visione")] if mancano else []


def _leggi(ctx, relativo):
    try:
        return (ctx.progetto.radice / relativo).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _presenza(tipo, minimo=1, livello="errore", nome=None):
    def controllo(ctx, voce):
        n = len(ctx.progetto.tutti(tipo))
        if n < minimo:
            return [_r(livello, tipo, f"servono almeno {minimo} elementi, ce ne sono {n}", nome or tipo)]
        return []
    return controllo


def c_stakeholder(ctx, voce):
    p, reperti = ctx.progetto, _presenza("stakeholder")(ctx, voce)
    categorie = {c for e in p.tutti("stakeholder") for c in _valori(e.dati.get("categorie"))}
    for richiesta in ("esercizio", "sicurezza", "legale"):
        if richiesta not in categorie:
            reperti.append(_r("errore", "stakeholder", f"nessuno stakeholder per la categoria '{richiesta}': "
                              "anche se è la stessa persona, va nominato", "stakeholder"))
    if not p.attori():
        reperti.append(_r("errore", "stakeholder", "nessuno stakeholder con usa = true: il prodotto non ha attori", "stakeholder"))
    return reperti


def c_sistemi(ctx, voce):
    p = ctx.progetto
    if "integrazioni" in p.scheda.get("inneschi", []) and not any(e.dati.get("integrazione") for e in p.tutti("sistemi")):
        return [_r("errore", "sistemi", "l'innesco 'integrazioni' richiede almeno un sistema con integrazione = true", "sistemi")]
    return []


def c_fattibilita(ctx, voce):
    f = ctx.progetto.tabelle_libere.get("fattibilita", {})
    mancano = [a for a in ("tecnica", "economica", "operativa", "legale", "temporale") if not _pieno(f.get(a))]
    return [_r("errore", "prodotto.toml [fattibilita]", f"mancano gli assi {mancano}", "fattibilita")] if mancano else []


def c_stima(ctx, voce):
    s = ctx.progetto.tabelle_libere.get("stima", {})
    mancano = [a for a in ("ordine", "incertezza", "base") if not _pieno(s.get(a))]
    return [_r("errore", "prodotto.toml [stima]", f"mancano {mancano}", "stima")] if mancano else []


def c_rischi(ctx, voce):
    reperti = _presenza("rischi")(ctx, voce)
    for e in ctx.progetto.tutti("rischi"):
        if e.dati.get("stato") == "accettato" and not _pieno(e.dati.get("segnale")):
            reperti.append(_r("errore", e.id, "un rischio accettato ha il segnale che lo farà emergere", "rischi"))
        if voce == "4.19" and e.dati.get("tipo") == "tecnico" and e.dati.get("stato") == "aperto":
            reperti.append(_r("errore", e.id, "rischio tecnico ancora aperto: va ridotto, chiuso o accettato", "rischi"))
    return reperti


def c_fonti(ctx, voce):
    p, reperti = ctx.progetto, []
    fonti = {f for tipo in ("storie", "rnf", "requisiti_dati") for e in p.tutti(tipo) for f in _valori(e.dati.get("fonte"))}
    for s in p.tutti("stakeholder"):
        if s.dati.get("interesse") == "alto" and s.id not in fonti:
            reperti.append(_r("avviso", s.id, "stakeholder d'interesse alto che non è fonte di alcun requisito", "fonti"))
    return reperti


def _valori_priorita(p):
    metodo = p.tabelle_libere.get("metodo_priorita")
    if isinstance(metodo, dict) and isinstance(metodo.get("valori"), list):
        return metodo.get("nome", ""), set(metodo["valori"])
    return None, set()


def c_storie(ctx, voce):
    """L'inventario: priorità dal metodo dichiarato, attori, incremento di ogni storia."""
    p, reperti = ctx.progetto, _presenza("storie")(ctx, voce)
    nome, valori = _valori_priorita(p)
    if not valori:
        reperti.append(_r("errore", "requisiti.toml", "metodo_priorita = { nome, valori } mancante", "storie"))
    attori = p.attori()
    for s in p.tutti("storie"):
        d, dove = s.dati, f"{s.sorgente} → {s.id}"
        if valori and d.get("priorita") not in valori:
            reperti.append(_r("errore", dove, f"priorità '{d.get('priorita')}' fuori dal metodo {nome} {sorted(valori)}", "storie"))
        if d.get("attore") and d.get("attore") not in attori:
            reperti.append(_r("errore", dove, f"l'attore '{d.get('attore')}' non è uno stakeholder con usa = true", "storie"))
        inc = d.get("incremento")
        if not (isinstance(inc, int) and not isinstance(inc, bool) and inc >= 1):
            reperti.append(_r("errore", dove, "incremento è un intero da 1", "storie"))
    return reperti


def c_criteri(ctx, voce):
    """Le storie dell'incremento corrente hanno i criteri, e ogni criterio scritto è completo."""
    p, reperti = ctx.progetto, []
    corrente = p.incremento_corrente()
    for s in p.tutti("storie"):
        d, dove = s.dati, f"{s.sorgente} → {s.id}"
        criteri = d.get("criteri") or []
        if d.get("incremento") == corrente:
            if not criteri:
                reperti.append(_r("errore", dove, "storia dell'incremento corrente senza criteri dato/quando/allora", "criteri"))
            elif len(criteri) < 2:
                reperti.append(_r("avviso", dove, "un solo criterio: manca la variante o il caso d'errore?", "criteri"))
        for n, c in enumerate(criteri, 1):
            mancano = [k for k in ("dato", "quando", "allora") if not (isinstance(c, dict) and _pieno(c.get(k)))]
            if mancano:
                reperti.append(_r("errore", dove, f"criterio {n}: manca {', '.join(mancano)}", "criteri"))
    return reperti


def c_trasversali(ctx, voce):
    p = ctx.progetto
    t = p.tabelle_libere.get("trasversali")
    if not isinstance(t, dict):
        return [_r("errore", "requisiti.toml", "manca la tabella [trasversali]", "trasversali")]
    reperti = []
    for chiave in TRASVERSALI:
        valori = _valori(t.get(chiave))
        if not valori:
            reperti.append(_r("errore", "[trasversali]", f"'{chiave}': elenca le storie o i non-obiettivi che la coprono", "trasversali"))
        for v in valori:
            risolto = p.risolvi(v)
            if not risolto or risolto[0] not in ("storie", "non_obiettivi"):
                reperti.append(_r("errore", "[trasversali]", f"'{chiave}': '{v}' non è una storia né un non-obiettivo", "trasversali"))
    for chiave in t:
        if chiave not in TRASVERSALI:
            reperti.append(_r("avviso", "[trasversali]", f"chiave '{chiave}' non prevista: {list(TRASVERSALI)}", "trasversali"))
    return reperti


def c_qualita(ctx, voce):
    presenti = {e.id for e in ctx.progetto.tutti("qualita")}
    mancano = [c for c in CARATTERISTICHE if c not in presenti]
    return [_r("errore", "[[qualita]]", f"caratteristiche non passate in rassegna: {mancano}", "qualita")] if mancano else []


def c_rnf(ctx, voce):
    p, reperti = ctx.progetto, _presenza("rnf")(ctx, voce)
    con_rnf = {e.dati.get("caratteristica") for e in p.tutti("rnf")}
    for q in p.tutti("qualita"):
        if q.dati.get("rilevanza") == "alta" and q.id not in con_rnf:
            reperti.append(_r("errore", q.id, "caratteristica di rilevanza alta senza un RNF misurabile", "rnf"))
        elif q.dati.get("rilevanza") == "media" and q.id not in con_rnf:
            reperti.append(_r("avviso", q.id, "caratteristica di rilevanza media senza RNF", "rnf"))
    return reperti


def c_conformita(ctx, voce):
    p = ctx.progetto
    vincoli = [e for e in p.tutti("vincoli") if e.dati.get("tipo") == "conformita"]
    if not vincoli:
        return [_r("errore", "[[vincoli]]", "nessun vincolo di conformità: se non ce ne sono, scrivilo come vincolo", "conformita")]
    testo = " ".join(e.dati.get("testo", "") + " " + e.dati.get("norma", "") for e in vincoli).lower()
    reperti = []
    for innesco, parola in (("dati-personali", "gdpr"), ("mercato-ue", "cyber resilience"), ("ia", "ai act")):
        if innesco in p.scheda.get("inneschi", []) and parola not in testo:
            reperti.append(_r("avviso", "[[vincoli]]", f"innesco '{innesco}' senza un vincolo che nomini {parola.upper()}", "conformita"))
    return reperti


def c_revisione(tipo):
    """Una revisione del tipo esiste; per una voce che si ripete, nell'incremento corrente."""
    def controllo(ctx, voce):
        revisioni = [e for e in ctx.progetto.tutti("revisioni") if e.dati.get("tipo") == tipo]
        if voce is not None and per_incremento(ctx, voce):
            corrente = ctx.progetto.incremento_corrente()
            revisioni = [e for e in revisioni if e.dati.get("incremento") == corrente]
            if not revisioni:
                return [_r("errore", "[[revisioni]]", f"nessuna revisione di tipo '{tipo}' nell'incremento {corrente}",
                           f"revisione:{tipo}")]
        if not revisioni:
            return [_r("errore", "[[revisioni]]", f"nessuna revisione di tipo '{tipo}'", f"revisione:{tipo}")]
        ultima = max(revisioni, key=lambda e: str(e.dati.get("data")))
        reperti = []
        if tipo == "prontezza":
            for campo in ("p0", "p1"):
                if ultima.dati.get(campo) != 0:
                    reperti.append(_r("errore", ultima.id, f"la revisione di prontezza deve chiudere con {campo} = 0", "revisione:prontezza"))
        if tipo == "decidibilita" and ultima.dati.get("domande") != 0:
            reperti.append(_r("errore", ultima.id, "la prova di decidibilità deve chiudere con domande = 0", "revisione:decidibilita"))
        return reperti
    return controllo


def c_glossario(ctx, voce):
    p, reperti = ctx.progetto, _presenza("glossario")(ctx, voce)
    vietati = {v.lower(): t.id for t in p.tutti("glossario") for v in _valori(t.dati.get("evitare"))}
    for s in p.tutti("storie"):
        titolo = s.dati.get("titolo", "").lower()
        for parola, termine in vietati.items():
            if re.search(rf"\b{re.escape(parola)}\b", titolo):
                reperti.append(_r("avviso", s.id, f"usa '{parola}': il glossario dice '{termine}'", "glossario"))
    if voce == "3.02":
        termini = {t.id for t in p.tutti("glossario")}
        for e in p.tutti("entita"):
            if e.dati.get("termine") not in termini:
                reperti.append(_r("errore", e.id, "il termine dell'entità non è nel glossario", "glossario"))
    return reperti


def c_percorsi(ctx, voce):
    reperti = _presenza("percorsi")(ctx, voce)
    for pc in ctx.progetto.tutti("percorsi"):
        if len(_valori(pc.dati.get("storie"))) < 2:
            reperti.append(_r("avviso", pc.id, "un percorso critico attraversa di solito più storie, accesso compreso", "percorsi"))
    return reperti


def _dag(nodi, archi):
    """Restituisce un ciclo come lista di nodi, o None se il grafo è aciclico."""
    figli = {n: [] for n in nodi}
    for a, b in archi:
        figli.setdefault(a, []).append(b)
    stato, pila = {}, []

    def visita(n):
        stato[n] = 1
        pila.append(n)
        for f in figli.get(n, []):
            if stato.get(f) == 1:
                return pila[pila.index(f):] + [f]
            if f not in stato:
                ciclo = visita(f)
                if ciclo:
                    return ciclo
        pila.pop()
        stato[n] = 2
        return None

    for n in list(figli):
        if n not in stato:
            ciclo = visita(n)
            if ciclo:
                return ciclo
    return None


def c_moduli(ctx, voce):
    p, reperti = ctx.progetto, _presenza("moduli")(ctx, voce)
    archi = [(d.dati.get("a_valle"), d.dati.get("a_monte")) for d in p.tutti("dipendenze")]
    ciclo = _dag({m.id for m in p.tutti("moduli")}, archi)
    if ciclo:
        reperti.append(_r("errore", "[[dipendenze]]", f"dipendenze circolari tra moduli: {' → '.join(ciclo)}", "moduli"))
    for a, b in archi:
        if a == b:
            reperti.append(_r("errore", "[[dipendenze]]", f"il modulo '{a}' dipende da sé stesso", "moduli"))
    if voce in ("4.03", "4.04"):
        for m in p.tutti("moduli"):
            if m.dati.get("motore") is not True and not m.dati.get("archetipo"):
                reperti.append(_r("errore", m.id, "manca l'archetipo (o motore = true)", "moduli"))
            if m.dati.get("motore") is True and m.dati.get("archetipo"):
                reperti.append(_r("errore", m.id, "un motore non ha archetipo", "moduli"))
            if not m.dati.get("rischio"):
                reperti.append(_r("errore", m.id, "manca la classe di rischio", "moduli"))
    if voce == "4.04":
        for d in p.tutti("dipendenze"):
            if not d.dati.get("comunicazione"):
                reperti.append(_r("errore", d.id, "manca 'comunicazione': sincrona o asincrona", "moduli"))
    return reperti


def c_proprietari(ctx, voce):
    p, reperti = ctx.progetto, []
    proprietario = {e.id: e.dati.get("modulo") for e in p.tutti("entita")}
    for t in p.tutti("tabelle"):
        if t.dati.get("piattaforma"):
            continue
        for concetto in _valori(t.dati.get("da")):
            r = p.risolvi(concetto)
            if r and r[0] == "entita" and proprietario.get(r[1]) != t.dati.get("modulo"):
                reperti.append(_r("errore", t.id, f"traduce '{r[1]}', di proprietà di '{proprietario.get(r[1])}', "
                                  f"ma appartiene a '{t.dati.get('modulo')}'", "proprietari"))
    return reperti


def c_processi(ctx, voce):
    reperti = _presenza("processi")(ctx, voce)
    for e in ctx.progetto.tutti("processi"):
        if "```mermaid" not in e.dati.get("_corpo", ""):
            reperti.append(_r("errore", e.sorgente, "un processo ha il suo diagramma Mermaid", "processi"))
    return reperti


def c_macchine(ctx, voce):
    p, reperti = ctx.progetto, []
    attori = p.attori()
    con_macchina = {m.dati.get("entita") for m in p.tutti("macchine")}
    for e in p.tutti("entita"):
        nomi = {a.get("nome") for a in e.dati.get("attributi", []) if isinstance(a, dict)}
        if "stato" in nomi and e.id not in con_macchina:
            reperti.append(_r("errore", e.id, "ha un attributo 'stato' ma nessuna macchina a stati", "macchine"))
    for m in p.tutti("macchine"):
        d, dove = m.dati, m.id
        entita = p.trova("entita", d.get("entita"))
        if entita and d.get("attributo") not in {a.get("nome") for a in entita.dati.get("attributi", []) if isinstance(a, dict)}:
            reperti.append(_r("errore", dove, f"l'attributo '{d.get('attributo')}' non è dell'entità", "macchine"))
        stati = set(_valori(d.get("stati")))
        if d.get("iniziale") not in stati:
            reperti.append(_r("errore", dove, "lo stato iniziale non è tra gli stati", "macchine"))
        for f in _valori(d.get("finali")):
            if f not in stati:
                reperti.append(_r("errore", dove, f"stato finale '{f}' sconosciuto", "macchine"))
        uscite, raggiunti = {}, {d.get("iniziale")}
        for n, t in enumerate(d.get("transizioni", []), 1):
            if not isinstance(t, dict):
                continue
            if t.get("da") not in stati or t.get("a") not in stati:
                reperti.append(_r("errore", dove, f"transizione {n}: stati sconosciuti {t.get('da')} → {t.get('a')}", "macchine"))
            if not _pieno(t.get("evento")):
                reperti.append(_r("errore", dove, f"transizione {n}: manca l'evento", "macchine"))
            for ruolo in _valori(t.get("ruoli")):
                if ruolo not in attori:
                    reperti.append(_r("errore", dove, f"transizione {n}: ruolo '{ruolo}' non è un attore", "macchine"))
            uscite.setdefault(t.get("da"), []).append(t.get("a"))
        coda = [d.get("iniziale")]
        while coda:
            s = coda.pop()
            for a in uscite.get(s, []):
                if a not in raggiunti:
                    raggiunti.add(a)
                    coda.append(a)
        for s in sorted(stati - raggiunti):
            reperti.append(_r("errore", dove, f"stato '{s}' irraggiungibile dall'iniziale", "macchine"))
        finali = set(_valori(d.get("finali")))
        for s in sorted(stati - finali):
            if not uscite.get(s):
                reperti.append(_r("avviso", dove, f"stato '{s}' senza uscite e non dichiarato finale", "macchine"))
    return reperti


def c_entita(ctx, voce):
    p, reperti = ctx.progetto, _presenza("entita")(ctx, voce)
    figli = {f for g in p.tutti("generalizzazioni") for f in _valori(g.dati.get("figli"))}
    for e in p.tutti("entita"):
        d, dove = e.dati, e.id
        nomi = {a.get("nome") for a in d.get("attributi", []) if isinstance(a, dict)}
        if not nomi and e.id not in figli:
            reperti.append(_r("errore", dove, "entità senza attributi", "entita"))
        identificatori = d.get("identificatori")
        if not isinstance(identificatori, list) or not identificatori:
            if e.id not in figli:
                reperti.append(_r("errore", dove, "entità senza identificatore: una lista di liste di attributi", "entita"))
            continue
        for ident in identificatori:
            if not isinstance(ident, list) or not ident:
                reperti.append(_r("errore", dove, "ogni identificatore è una lista non vuota", "entita"))
                continue
            for parte in ident:
                if isinstance(parte, str) and parte.startswith("relazione:"):
                    if not p.risolvi(parte):
                        reperti.append(_r("errore", dove, f"identificazione esterna '{parte}' non risolta", "entita"))
                elif parte not in nomi:
                    reperti.append(_r("errore", dove, f"l'identificatore usa '{parte}', che non è un attributo", "entita"))
    usate = {x for s in p.tutti("storie") for x in _valori(s.dati.get("entita"))}
    for e in p.tutti("entita"):
        if e.id not in usate:
            reperti.append(_r("avviso", e.id, "nessuna storia la usa: a cosa serve?", "entita"))
    return reperti


def c_relazioni(ctx, voce):
    p, reperti = ctx.progetto, []
    for r in p.tutti("relazioni"):
        parti = r.dati.get("partecipanti") or []
        if len(parti) < 2:
            reperti.append(_r("errore", r.id, "una relazione ha almeno due partecipanti", "relazioni"))
        for n, x in enumerate(parti, 1):
            if not isinstance(x, dict):
                continue
            minimo, massimo = x.get("min"), x.get("max")
            if minimo not in (0, 1):
                reperti.append(_r("errore", r.id, f"partecipante {n}: min è 0 o 1", "relazioni"))
            if massimo not in (1, "N"):
                reperti.append(_r("errore", r.id, f"partecipante {n}: max è 1 o \"N\"", "relazioni"))
    for g in p.tutti("generalizzazioni"):
        if len(_valori(g.dati.get("figli"))) < 1:
            reperti.append(_r("errore", g.id, "una generalizzazione ha almeno un figlio", "relazioni"))
    return reperti


def c_regole(ctx, voce):
    reperti = _presenza("regole")(ctx, voce)
    if voce == "3.08" and not any(e.dati.get("tipo") == "eccezione" for e in ctx.progetto.tutti("regole")):
        reperti.append(_r("avviso", "[[regole]]", "nessuna regola di tipo eccezione: i casi limite stanno tutti nei criteri?", "regole"))
    return reperti


def c_storie_entita(ctx, voce):
    reperti = []
    for s in ctx.progetto.tutti("storie"):
        if not _valori(s.dati.get("entita")):
            reperti.append(_r("errore", s.id, "storia senza entità: il modello non è stato provato su di lei", "storie-entita"))
    return reperti


def c_storie_moduli(ctx, voce):
    reperti = []
    for s in ctx.progetto.tutti("storie"):
        if not s.dati.get("modulo"):
            reperti.append(_r("errore", s.id, "storia senza il modulo che la orchestra", "storie-moduli"))
        if s.dati.get("modulo") in _valori(s.dati.get("tocca")):
            reperti.append(_r("errore", s.id, "'tocca' elenca gli altri moduli, non quello che la orchestra", "storie-moduli"))
    return reperti


def c_strategie(ctx, voce):
    p = ctx.progetto
    presenti = {e.dati.get("tema") for e in p.tutti("strategie")}
    richieste = list(STRATEGIE_PER_VOCE.get(voce, ()))
    if voce == "4.08":
        for innesco, tema in STRATEGIE_PER_INNESCO.items():
            if innesco in p.scheda.get("inneschi", []):
                richieste.append(tema)
    if voce is None:
        richieste = sorted({t for temi in STRATEGIE_PER_VOCE.values() for t in temi})
    mancano = [t for t in richieste if t not in presenti]
    return [_r("errore", "[[strategie]]", f"mancano le strategie {['ST-' + t for t in mancano]}", "strategie")] if mancano else []


def c_integrazioni(ctx, voce):
    p, reperti = ctx.progetto, []
    con_integrazione = {e.id for e in p.tutti("integrazioni")}
    for s in p.tutti("sistemi"):
        if s.dati.get("integrazione") and s.id not in con_integrazione:
            reperti.append(_r("errore", s.id, "sistema da integrare senza [[integrazioni]] (timeout, tentativi, guasto)", "integrazioni"))
    return reperti


def c_minacce(ctx, voce):
    p = ctx.progetto
    reperti = _presenza("confini")(ctx, voce) + _presenza("flussi")(ctx, voce) + _presenza("minacce")(ctx, voce)
    con_minacce = {m.dati.get("flusso") for m in p.tutti("minacce")}
    for f in p.tutti("flussi"):
        if f.id not in con_minacce:
            reperti.append(_r("avviso", f.id, "flusso senza minacce analizzate", "minacce"))
    return reperti


def c_documento(relativo, mermaid=False, nome=""):
    def controllo(ctx, voce):
        testo = ctx.progetto.testi.get(relativo) or _leggi(ctx, relativo)
        if testo is None or not testo.strip():
            return [_r("errore", relativo, "manca o è vuoto", nome)]
        if mermaid and "```mermaid" not in testo:
            return [_r("errore", relativo, "manca il diagramma Mermaid", nome)]
        return []
    return controllo


def c_rnf_indirizzati(ctx, voce):
    p, reperti = ctx.progetto, []
    rilevanza = {q.id: q.dati.get("rilevanza") for q in p.tutti("qualita")}
    for r in p.tutti("rnf"):
        if not _valori(r.dati.get("indirizzato_da")):
            livello = "errore" if rilevanza.get(r.dati.get("caratteristica")) == "alta" else "avviso"
            reperti.append(_r(livello, r.id, "nessuna decisione lo indirizza (indirizzato_da)", "rnf-indirizzati"))
    return reperti


def c_adr(ctx, voce):
    p, reperti = ctx.progetto, _presenza("adr")(ctx, voce)
    for a in p.tutti("adr"):
        testo = a.dati.get("_testo", "")
        for sezione in ("## Context", "## Decision", "## Consequences"):
            if sezione not in testo:
                reperti.append(_r("errore", a.sorgente, f"manca la sezione '{sezione}'", "adr"))
        if not a.dati.get("status"):
            reperti.append(_r("errore", a.sorgente, "manca '- **Status:** …'", "adr"))
        for citato in sorted(set(re.findall(r"\b(ADR-\d{4}|DEP-\w+)\b", testo))):
            if citato != a.id and not p.risolvi(citato):
                reperti.append(_r("errore", a.sorgente, f"cita '{citato}', che non esiste", "adr"))
    return reperti


def c_domande(ctx, voce):
    domande = ctx.progetto.tutti("domande")
    if voce == "4.14":
        domande = [d for d in domande if _pieno(d.dati.get("criterio"))]
        cosa = "spike ancora aperti"
    else:
        cosa = "domande aperte"
    return [_r("errore", d.id, cosa, "domande") for d in domande]


def c_deperibili(ctx, voce):
    p, reperti = ctx.progetto, _presenza("deperibili")(ctx, voce)
    soglia = ctx.congelamento if voce in ("7.15", None) else None
    for d in p.tutti("deperibili"):
        data = d.dati.get("verificato_il")
        if not isinstance(data, datetime.date) or isinstance(data, datetime.datetime):
            reperti.append(_r("errore", d.id, "verificato_il è una data (AAAA-MM-GG)", "deperibili"))
        elif soglia and data < soglia:
            reperti.append(_r("errore", d.id, f"verificato il {data}, prima del congelamento {soglia}", "deperibili"))
    return reperti


def c_dettaglio(ctx, voce):
    p, reperti = ctx.progetto, []
    corrente = p.incremento_corrente()
    con_dettaglio = {e.id for e in p.tutti("dettaglio")}
    for m in p.tutti("moduli"):
        if _incremento_modulo(p, m.id) <= corrente and m.id not in con_dettaglio:
            reperti.append(_r("errore", m.id, f"manca {PROGETTAZIONE}/moduli/{m.id}.toml", "dettaglio"))
    for d in p.tutti("dipendenze"):
        if d.dati.get("comunicazione") == "sincrona":
            a_monte = d.dati.get("a_monte")
            if not any(f.contenitore == a_monte for f in p.tutti("facciata")):
                reperti.append(_r("errore", d.id, f"dipendenza sincrona, ma '{a_monte}' non espone una facciata", "dettaglio"))
        if d.dati.get("comunicazione") == "asincrona":
            if not any(ev.contenitore == d.dati.get("a_monte") and d.dati.get("a_valle") in _valori(ev.dati.get("consumatori"))
                       for ev in p.tutti("eventi")):
                reperti.append(_r("errore", d.id, "dipendenza asincrona senza un evento consumato da chi sta a valle", "dettaglio"))
    if voce == "5.12":
        for m in p.tutti("moduli"):
            det = p.trova("dettaglio", m.id)
            sic = det.dati.get("sicurezza") if det else None
            if det and not (isinstance(sic, dict) and isinstance(sic.get("asvs"), int)):
                reperti.append(_r("errore", det.sorgente, "[sicurezza]: manca il livello ASVS", "dettaglio"))
    return reperti


def _incremento_modulo(p, modulo):
    valori = [p.incremento_di(s) for s in p.tutti("storie") if s.dati.get("modulo") == modulo or modulo in _valori(s.dati.get("tocca"))]
    valori += [p.incremento_di(e) for e in p.tutti("entita") if e.dati.get("modulo") == modulo]
    return min(valori) if valori else 1


def c_volumi(ctx, voce):
    p, reperti = ctx.progetto, _presenza("volumi")(ctx, voce)
    con_volume = {e.id for e in p.tutti("volumi")}
    for e in p.tutti("entita"):
        if f"entita:{e.id}" not in con_volume:
            reperti.append(_r("errore", e.id, "entità senza volume nella tavola dei volumi", "volumi"))
    for r in p.tutti("relazioni"):
        if f"relazione:{r.id}" not in con_volume:
            reperti.append(_r("avviso", r.id, "relazione senza volume", "volumi"))
    for v in p.tutti("volumi"):
        if not isinstance(v.dati.get("volume"), int):
            reperti.append(_r("errore", v.id, "volume è un numero intero di istanze", "volumi"))
        if not (_valori(v.dati.get("fonte")) or _pieno(v.dati.get("calcolo"))):
            reperti.append(_r("errore", v.id, "un volume cita la fonte (RD-…) o il calcolo", "volumi"))
    return reperti


def c_accessi(ctx, voce):
    p, reperti = ctx.progetto, _presenza("accessi")(ctx, voce)
    for a in p.tutti("accessi"):
        if not isinstance(a.dati.get("frequenza"), int):
            reperti.append(_r("errore", a.id, "frequenza è un numero intero", "accessi"))
        for n, passo in enumerate(a.dati.get("cammino") or [], 1):
            if not isinstance(passo, dict):
                continue
            if not p.risolvi(passo.get("concetto")):
                reperti.append(_r("errore", a.id, f"cammino {n}: concetto '{passo.get('concetto')}' non risolto", "accessi"))
            if passo.get("tipo") not in ("L", "S") or not isinstance(passo.get("accessi"), int):
                reperti.append(_r("errore", a.id, f"cammino {n}: tipo L o S e accessi interi", "accessi"))
    return reperti


def c_ristrutturazione(ctx, voce):
    p, reperti = ctx.progetto, []
    oggetti = {e.dati.get("oggetto") for e in p.tutti("ristrutturazione")}
    for g in p.tutti("generalizzazioni"):
        if f"generalizzazione:{g.id}" not in oggetti:
            reperti.append(_r("errore", g.id, "generalizzazione senza decisione di ristrutturazione", "ristrutturazione"))
    for a in p.tutti("attributi"):
        if _pieno(a.dati.get("derivato")) and f"attributo:{a.id}" not in oggetti:
            reperti.append(_r("errore", a.id, "attributo derivato (ridondanza) senza decisione: tenerlo o no, con i numeri", "ristrutturazione"))
    for e in p.tutti("entita"):
        if len(e.dati.get("identificatori") or []) > 1 and f"entita:{e.id}" not in oggetti:
            reperti.append(_r("errore", e.id, "più identificatori senza la scelta di quello principale", "ristrutturazione"))
    return reperti


def c_schema(ctx, voce):
    p, reperti = ctx.progetto, _presenza("tabelle")(ctx, voce)
    tradotti = set()
    for t in p.tutti("tabelle"):
        if t.dati.get("piattaforma"):
            if not t.dati.get("strategia"):
                reperti.append(_r("errore", t.id, "una tabella di piattaforma cita la strategia che la richiede", "schema"))
            continue
        for campo in ("modulo", "da"):
            if not _pieno(t.dati.get(campo)):
                reperti.append(_r("errore", t.id, f"manca '{campo}': il modulo proprietario e i concetti tradotti", "schema"))
        tradotti.update(_valori(t.dati.get("da")))
        for fk in t.dati.get("esterne") or []:
            if isinstance(fk, dict) and fk.get("relazione"):
                tradotti.add(fk["relazione"])
    # una relazione assorbita da una decisione di ristrutturazione è tradotta da quella decisione
    tradotti.update(r.dati.get("oggetto") for r in p.tutti("ristrutturazione") if r.dati.get("tipo") == "accorpamento")
    for e in p.tutti("entita"):
        if f"entita:{e.id}" not in tradotti:
            reperti.append(_r("errore", e.id, "entità non tradotta in nessuna tabella (campo da)", "schema"))
    for r in p.tutti("relazioni"):
        if f"relazione:{r.id}" not in tradotti:
            reperti.append(_r("errore", r.id, "relazione non tradotta: né tabella né chiave esterna con relazione", "schema"))
    for t in p.tutti("tabelle"):
        d, dove = t.dati, t.id
        colonne = {c.get("nome") for c in d.get("colonne", []) if isinstance(c, dict)}
        for c in _valori(d.get("chiave")):
            if c not in colonne:
                reperti.append(_r("errore", dove, f"chiave su colonna inesistente '{c}'", "schema"))
        for u in d.get("uniche") or []:
            for c in _valori(u):
                if c not in colonne:
                    reperti.append(_r("errore", dove, f"vincolo d'unicità su colonna inesistente '{c}'", "schema"))
        for fk in d.get("esterne") or []:
            if not isinstance(fk, dict):
                continue
            for c in _valori(fk.get("colonne")):
                if c not in colonne:
                    reperti.append(_r("errore", dove, f"chiave esterna su colonna inesistente '{c}'", "schema"))
            destinazione = p.trova("tabelle", fk.get("riferisce"))
            if not destinazione:
                reperti.append(_r("errore", dove, f"chiave esterna verso tabella inesistente '{fk.get('riferisce')}'", "schema"))
            else:
                cols = {c.get("nome") for c in destinazione.dati.get("colonne", []) if isinstance(c, dict)}
                for c in _valori(fk.get("colonne_rif")):
                    if c not in cols:
                        reperti.append(_r("errore", dove, f"chiave esterna verso colonna inesistente '{destinazione.id}.{c}'", "schema"))
                if not d.get("piattaforma") and destinazione.dati.get("modulo") != d.get("modulo") and not _pieno(fk.get("motivo")):
                    reperti.append(_r("errore", dove, f"chiave esterna verso '{destinazione.id}' di un altro modulo senza motivo", "schema"))
            for azione in ("cancellazione", "aggiornamento"):
                if fk.get(azione) not in ("restrict", "cascade", "set-null", "no-action"):
                    reperti.append(_r("errore", dove, f"chiave esterna: '{azione}' tra restrict, cascade, set-null, no-action", "schema"))
        forma = d.get("normalizzazione")
        if forma not in ("3NF", "BCNF") and not _pieno(d.get("motivo")):
            reperti.append(_r("errore", dove, "forma normale sotto la 3NF, o non dichiarata, senza motivo", "schema"))
        for c in d.get("colonne", []):
            if isinstance(c, dict) and not (c.get("da") or _valori(c.get("traccia"))) and c.get("nome") not in _valori(d.get("chiave")):
                reperti.append(_r("avviso", f"{dove}.{c.get('nome')}", "colonna senza 'da' né traccia", "schema"))
    reperti += c_proprietari(ctx, voce)
    return reperti


def c_indici(ctx, voce):
    p, reperti = ctx.progetto, []
    coperte = set()
    for t in p.tutti("tabelle"):
        for i in t.dati.get("indici") or []:
            if isinstance(i, dict) and _valori(i.get("colonne")):
                coperte.add(f"{t.id}.{_valori(i.get('colonne'))[0]}")
                if not _valori(i.get("accessi")) and not i.get("unico"):
                    reperti.append(_r("errore", i.get("nome"), "indice senza gli accessi che lo giustificano", "indici"))
        for gruppo in [t.dati.get("chiave") or []] + list(t.dati.get("uniche") or []):
            if _valori(gruppo):
                coperte.add(f"{t.id}.{_valori(gruppo)[0]}")
    for a in p.tutti("accessi"):
        for filtro in _valori(a.dati.get("filtri")):
            if filtro not in coperte:
                reperti.append(_r("errore", a.id, f"filtra su '{filtro}' senza un indice che la abbia come prima colonna", "indici"))
    return reperti


def c_api(ctx, voce):
    p, reperti = ctx.progetto, []
    spec = p.openapi
    dove = f"{CONTRATTI}/openapi.json"
    if not spec:
        return [_r("errore", dove, "manca il contratto OpenAPI", "api")]
    if not str(spec.get("openapi", "")).startswith("3."):
        reperti.append(_r("errore", dove, "il campo 'openapi' dichiara una versione 3.x", "api"))
    paginazione = _valori((spec.get("info") or {}).get("x-paginazione"))
    for op in p.tutti("api"):
        d = op.dati
        risposte = d.get("responses") or {}
        if not any(str(c).startswith("4") for c in risposte):
            reperti.append(_r("errore", op.id, "nessuna risposta d'errore 4xx", "api"))
        if not _valori(d.get("x-errori")):
            reperti.append(_r("errore", op.id, "x-errori: i codici del catalogo che può restituire", "api"))
        for codice, r in risposte.items():
            for tipo_media in ((r or {}).get("content") or {}).values():
                if not (tipo_media.get("example") is not None or tipo_media.get("examples")):
                    reperti.append(_r("errore", op.id, f"risposta {codice} senza esempio: i mock nascono dagli esempi", "api"))
        if d.get("x-lista"):
            nomi = {par.get("name") for par in d.get("parameters", []) if isinstance(par, dict)}
            if not paginazione:
                reperti.append(_r("errore", dove, "info.x-paginazione: i nomi dei parametri di paginazione", "api"))
            elif not set(paginazione) <= nomi:
                reperti.append(_r("errore", op.id, f"lista senza i parametri di paginazione {paginazione}", "api"))
    coperte = {s for op in p.tutti("api") for s in _valori(op.dati.get("x-storie"))}
    corrente = p.incremento_corrente()
    for s in p.tutti("storie"):
        if s.dati.get("incremento") == corrente and s.id not in coperte:
            reperti.append(_r("avviso", s.id, "storia dell'incremento corrente senza operazioni API", "api"))
    return reperti


def c_sequenze(ctx, voce):
    p, reperti = ctx.progetto, []
    con_sequenza = {e.dati.get("percorso") for e in p.tutti("sequenze")}
    for pc in p.tutti("percorsi"):
        if pc.id not in con_sequenza:
            reperti.append(_r("errore", pc.id, f"manca {PROGETTAZIONE}/sequenze/{pc.id}.md", "sequenze"))
    for s in p.tutti("sequenze"):
        if "sequenceDiagram" not in s.dati.get("_corpo", ""):
            reperti.append(_r("errore", s.sorgente, "manca il sequenceDiagram", "sequenze"))
    return reperti


def c_errori(ctx, voce):
    p, reperti = ctx.progetto, _presenza("errori")(ctx, voce)
    ui = "ui" in p.scheda.get("inneschi", [])
    for e in p.tutti("errori"):
        http = e.dati.get("http")
        if not (isinstance(http, int) and 400 <= http <= 599):
            reperti.append(_r("errore", e.id, "http è un codice 4xx o 5xx", "errori"))
        if ui and not e.dati.get("utente"):
            reperti.append(_r("errore", e.id, "manca 'utente': la chiave del testo che l'utente vede", "errori"))
    return reperti


def c_matrice(ctx, voce):
    p = ctx.progetto
    dove = f"{CONTRATTI}/autorizzazioni.toml"
    m = p.matrice
    if not m:
        return [_r("errore", dove, "manca la matrice delle autorizzazioni", "matrice")]
    reperti = []
    if m.get("predefinito") != "nega":
        reperti.append(_r("errore", dove, "predefinito = \"nega\": ciò che la matrice non consente è vietato", "matrice"))
    ruoli, attori = set(_valori(m.get("ruoli"))), p.attori()
    if ruoli != attori:
        reperti.append(_r("errore", dove, f"i ruoli {sorted(ruoli)} devono essere gli attori {sorted(attori)}", "matrice"))
    risorse = {e.id for e in p.tutti("entita")} | set(_valori(m.get("risorse")))
    definite = m.get("condizioni") if isinstance(m.get("condizioni"), dict) else {}
    for r in p.tutti("matrice"):
        if r.dati.get("risorsa") not in risorse:
            reperti.append(_r("errore", r.id, "risorsa sconosciuta: un'entità o una voce di 'risorse'", "matrice"))
        condizioni_regola = r.dati.get("condizioni") or {}
        if not isinstance(condizioni_regola, dict):
            reperti.append(_r("errore", r.id, "condizioni = { ruolo = \"condizione\" }", "matrice"))
            continue
        for ruolo, condizione in condizioni_regola.items():
            if ruolo not in _valori(r.dati.get("consenti")):
                reperti.append(_r("errore", r.id, f"condizione per '{ruolo}', che la regola non consente", "matrice"))
            if condizione not in definite:
                reperti.append(_r("errore", r.id, f"condizione '{condizione}' non definita in [condizioni]", "matrice"))
        if not _valori(r.dati.get("traccia")):
            reperti.append(_r("avviso", r.id, "regola senza traccia: quale storia o minaccia la chiede?", "matrice"))
    return reperti


def c_configurazione(ctx, voce):
    return _presenza("variabili")(ctx, voce)


def c_contratti(ctx, voce):
    reperti = []
    for nome in ("schema", "indici", "api", "errori", "matrice", "configurazione", "dettaglio"):
        reperti += [r for r in CONTROLLI[nome](ctx, voce) if r.livello == "errore"]
    return reperti


def c_personas(ctx, voce):
    p = ctx.progetto
    reperti = _presenza("personas")(ctx, voce) + c_documento(f"{PROGETTAZIONE}/ux/utenti.md", nome="personas")(ctx, voce)
    con_persona = {e.dati.get("attore") for e in p.tutti("personas")}
    for a in sorted(p.attori() - con_persona):
        reperti.append(_r("avviso", a, "attore senza persona", "personas"))
    return reperti


def c_navigazione(ctx, voce):
    p = ctx.progetto
    reperti = _presenza("sezioni")(ctx, voce) + _presenza("rotte")(ctx, voce)
    con_rotta = {e.dati.get("schermata") for e in p.tutti("rotte")}
    for s in p.tutti("schermate"):
        if s.id not in con_rotta:
            reperti.append(_r("errore", s.id, "schermata senza rotta", "navigazione"))
    return reperti


def c_mockup(ctx, voce):
    p, reperti = ctx.progetto, []
    for s in p.tutti("schermate"):
        m = s.dati.get("mockup")
        if m and not (p.radice / m).is_file():
            reperti.append(_r("errore", s.id, f"mockup '{m}' inesistente", "mockup"))
    for pc in p.tutti("percorsi"):
        storie = set(_valori(pc.dati.get("storie")))
        if not any(s.dati.get("mockup") and storie & set(_valori(s.dati.get("storie"))) for s in p.tutti("schermate")):
            reperti.append(_r("errore", pc.id, "nessuna schermata del percorso critico ha un mockup", "mockup"))
    if not (p.radice / MOCKUP).is_dir():
        reperti.append(_r("errore", MOCKUP, "manca la cartella dei mockup", "mockup"))
    return reperti


def c_design_system(ctx, voce):
    p = ctx.progetto
    ds = p.tabelle_libere.get("design_system")
    if not ds:
        return [_r("errore", f"{PROGETTAZIONE}/ux/design-system.toml", "manca", "design-system")]
    if ds.get("adozione"):
        return [] if p.risolvi(ds["adozione"]) else [_r("errore", "design-system.toml", "adozione: l'ADR non esiste", "design-system")]
    mancano = [k for k in ("token", "componenti") if not ds.get(k)]
    return [_r("errore", "design-system.toml", f"mancano {mancano}, o 'adozione' con l'ADR", "design-system")] if mancano else []


def c_schermate(ctx, voce):
    p, reperti = ctx.progetto, _presenza("schermate")(ctx, voce)
    for s in p.tutti("schermate"):
        stati = s.dati.get("stati") or {}
        mancano = [k for k in STATI_SCHERMATA if not _pieno(stati.get(k))]
        if mancano:
            reperti.append(_r("errore", s.id, f"stati non progettati: {mancano} (o 'non-applicabile: motivo')", "schermate"))
        for n, a in enumerate(s.dati.get("azioni") or [], 1):
            if not isinstance(a, dict):
                continue
            for campo in ("nome", "ruoli", "nome_accessibile"):
                if not _pieno(a.get(campo)):
                    reperti.append(_r("errore", s.id, f"azione {n}: manca '{campo}'", "schermate"))
            if a.get("operazione") and not p.risolvi(a["operazione"], "api"):
                reperti.append(_r("errore", s.id, f"azione {n}: operazione '{a['operazione']}' inesistente", "schermate"))
    coperte = {x for s in p.tutti("schermate") for x in _valori(s.dati.get("storie"))}
    for st in p.tutti("storie"):
        if st.dati.get("incremento") == p.incremento_corrente() and st.id not in coperte:
            reperti.append(_r("avviso", st.id, "storia dell'incremento corrente senza schermata", "schermate"))
    return reperti


def c_testi(ctx, voce):
    return _presenza("testi")(ctx, voce)


def c_incrementi(ctx, voce):
    p = ctx.progetto
    reperti = _presenza("incrementi")(ctx, voce)
    dichiarati = {e.dati.get("numero") for e in p.tutti("incrementi")}
    for s in p.tutti("storie"):
        if s.dati.get("incremento") not in dichiarati:
            reperti.append(_r("errore", s.id, f"incremento {s.dati.get('incremento')} non dichiarato in [[incrementi]]", "incrementi"))
    if not any(e.dati.get("mvp") for e in p.tutti("incrementi")):
        reperti.append(_r("errore", "[[incrementi]]", "nessun incremento con mvp = true", "incrementi"))
    return reperti


def c_strategia_test(ctx, voce):
    p, reperti = ctx.progetto, []
    presenti = {e.id for e in p.tutti("livelli")}
    for richiesto in ("accettazione", "contratto", "autorizzazione", "e2e"):
        if richiesto not in presenti:
            reperti.append(_r("errore", "piano/test.toml", f"manca il livello '{richiesto}'", "strategia-test"))
    acc = p.trova("livelli", "accettazione")
    if acc and not _valori(acc.dati.get("tecniche")):
        reperti.append(_r("errore", "accettazione", "tecniche di progettazione dei casi non dichiarate", "strategia-test"))
    return reperti


def c_debito(ctx, voce):
    reperti = []
    for d in ctx.progetto.tutti("debito"):
        if not isinstance(d.dati.get("accettato_il"), datetime.date):
            livello = "errore" if ctx.congelamento else "avviso"
            reperti.append(_r(livello, d.id, "debito non ancora accettato dall'utente (accettato_il)", "debito"))
    return reperti


def c_piano(ctx, voce):
    """Il piano dell'incremento corrente. Uno di un incremento passato è storia: non
    si valida finché la voce 7.01 non lo riscrive, e non può chiuderla."""
    import piano
    p = ctx.progetto
    inc = (p.piano.get("progetto") or {}).get("incremento") if isinstance(p.piano, dict) else None
    if inc != p.incremento_corrente():
        if voce is None:
            return []
        return [_r("errore", piano.DOVE, f"[progetto].incremento = {inc!r}: il piano si scrive per l'incremento "
                   f"corrente ({p.incremento_corrente()})", "piano")]
    return piano.valida(p)


def c_viste(ctx, voce):
    import viste
    return viste.verifica_freschezza(ctx.progetto, ctx.catalogo)


def c_gate(ctx, voce):
    """Il registro dice il vero: una fase superata, nella riga che vale ora, non ha
    voci applicabili aperte. Una modifica approvata o un nuovo incremento che
    riaprono voci di una fase superata chiedono di riaprirla."""
    reperti, stati = [], stati_voci(ctx)
    for fase, riga in sorted(righe_correnti(ctx).items(), key=lambda x: str(x[0])):
        if riga.get("stato") != "superato":
            continue
        aperte = sorted((i for i, st in stati.items() if st["fase"] == fase
                         and st["applicabilita"] == condizioni.APPLICABILE and not st["chiusa"]), key=condizioni.chiave_id)
        if aperte:
            reperti.append(_r("errore", f"{PROGETTAZIONE}/stato.toml", f"registro, fase {fase}: superato con voci "
                              f"aperte: {aperte}; una modifica le riapre (MOD-n, poi progetto.py modifica MOD-n)",
                              "gate"))
    return reperti


def tag_congelamento(incremento, data):
    return f"progettazione/incremento-{incremento}-{data.isoformat()}"


def c_congelamento(ctx, voce):
    """[congelamento] certifica l'incremento corrente: data, approvazione, tag che
    li nomina, revisione di prontezza e prova di decidibilità dell'incremento."""
    p, reperti = ctx.progetto, []
    c = p.stato.get("congelamento")
    dove = f"{PROGETTAZIONE}/stato.toml [congelamento]"
    if not isinstance(c, dict):
        return [_r("errore", dove, "manca", "congelamento")]
    for campo in ("incremento", "data", "approvato_da", "tag", "revisione", "prova"):
        if not _pieno(c.get(campo)):
            reperti.append(_r("errore", dove, f"manca '{campo}'", "congelamento"))
    corrente = p.incremento_corrente()
    if c.get("incremento") != corrente:
        reperti.append(_r("errore", dove, f"incremento {c.get('incremento')!r}: il corrente è {corrente}", "congelamento"))
    if isinstance(c.get("data"), datetime.date) and c.get("tag") != tag_congelamento(corrente, c["data"]):
        reperti.append(_r("errore", dove, f"tag '{c.get('tag')}': per questo congelamento è "
                          f"'{tag_congelamento(corrente, c['data'])}'", "congelamento"))
    for campo, tipo in (("revisione", "prontezza"), ("prova", "decidibilita")):
        r = p.trova("revisioni", c.get(campo)) if isinstance(c.get(campo), str) else None
        if r is None or r.dati.get("tipo") != tipo or r.dati.get("incremento") != corrente:
            reperti.append(_r("errore", dove, f"'{campo}' è l'id della revisione di tipo '{tipo}' dell'incremento "
                              f"{corrente}", "congelamento"))
    return reperti


def c_modifiche(ctx, voce):
    """Una modifica approvata dice chi l'ha approvata e quali voci riapre: è la
    gestione delle modifiche (2.11, T.04) resa verificabile."""
    reperti = []
    for m in ctx.progetto.tutti("modifiche"):
        if m.dati.get("esito") != "approvata":
            continue
        for campo in ("approvato_da", "impatto", "riapre"):
            if not _pieno(m.dati.get(campo)):
                reperti.append(_r("errore", m.id, f"modifica approvata senza '{campo}'", "modifiche"))
    return reperti


CONTROLLI = {
    "stato": c_stato,
    "visione": c_visione,
    "obiettivi": _presenza("obiettivi"),
    "stakeholder": c_stakeholder,
    "sistemi": c_sistemi,
    "fattibilita": c_fattibilita,
    "non-obiettivi": _presenza("non_obiettivi", livello="avviso", nome="non-obiettivi"),
    "vincoli": _presenza("vincoli"),
    "rischi": c_rischi,
    "stima": c_stima,
    "fonti": c_fonti,
    "storie": c_storie,
    "criteri": c_criteri,
    "trasversali": c_trasversali,
    "qualita": c_qualita,
    "rnf": c_rnf,
    "requisiti-dati": _presenza("requisiti_dati", nome="requisiti-dati"),
    "conformita": c_conformita,
    "glossario": c_glossario,
    "percorsi": c_percorsi,
    "regole": c_regole,
    "moduli": c_moduli,
    "proprietari": c_proprietari,
    "processi": c_processi,
    "macchine": c_macchine,
    "entita": c_entita,
    "relazioni": c_relazioni,
    "storie-entita": c_storie_entita,
    "driver": _presenza("driver"),
    "adr": c_adr,
    "strategie": c_strategie,
    "integrazioni": c_integrazioni,
    "ambienti": _presenza("ambienti"),
    "minacce": c_minacce,
    "analisi": c_documento(f"{PROGETTAZIONE}/architettura/analisi.md", nome="analisi"),
    "valutazione": c_documento(f"{PROGETTAZIONE}/architettura/valutazione.md", nome="valutazione"),
    "architettura-md": c_documento(f"{PROGETTAZIONE}/architettura/architettura.md", mermaid=True, nome="architettura-md"),
    "rnf-indirizzati": c_rnf_indirizzati,
    "domande": c_domande,
    "deperibili": c_deperibili,
    "storie-moduli": c_storie_moduli,
    "dettaglio": c_dettaglio,
    "volumi": c_volumi,
    "accessi": c_accessi,
    "ristrutturazione": c_ristrutturazione,
    "schema": c_schema,
    "indici": c_indici,
    "api": c_api,
    "sequenze": c_sequenze,
    "errori": c_errori,
    "matrice": c_matrice,
    "configurazione": c_configurazione,
    "contratti": c_contratti,
    "personas": c_personas,
    "navigazione": c_navigazione,
    "mockup": c_mockup,
    "design-system": c_design_system,
    "schermate": c_schermate,
    "testi": c_testi,
    "incrementi": c_incrementi,
    "strategia-test": c_strategia_test,
    "debito": c_debito,
    "piano": c_piano,
    "viste": c_viste,
    "gate": c_gate,
    "modifiche": c_modifiche,
    "congelamento": c_congelamento,
}


def controllo(nome):
    if nome.startswith("revisione:"):
        return c_revisione(nome.split(":", 1)[1])
    return CONTROLLI.get(nome)


# --- voci, chiusure, gate -------------------------------------------------------------

def per_incremento(ctx, ident):
    voce = next((v for v in ctx.catalogo.get("voci", []) if v["id"] == ident), None)
    return bool(voce and voce.get("per_incremento"))


def stati_voci(ctx):
    """id -> {fase, applicabilita, chiusa, chiusura, riaperta_da, per_incremento, skill, voce}
    per tutte le voci del catalogo.

    La chiusura che vale è, per una voce che si ripete, quella dell'incremento
    corrente; per le altre, l'unica. Una modifica approvata che elenca la voce in
    'riapre' annulla una chiusura con data anteriore alla sua; il congelamento lo
    annulla qualunque modifica approvata dopo, perché certifica il progetto di quel
    giorno. Una modifica dello stesso giorno di una chiusura si intende recepita."""
    cache = ctx.__dict__.setdefault("_stati_voci", None)
    if cache is not None:
        return cache
    p = ctx.progetto
    scheda = condizioni.profilo(p.scheda)
    fasi_skill = {f["numero"]: f["skill"] for f in ctx.catalogo.get("fasi", [])}
    corrente = p.incremento_corrente()
    per_voce = {}
    for c in p.chiusure:
        per_voce.setdefault(c.get("voce"), []).append(c)
    modifiche = [m for m in p.tutti("modifiche")
                 if m.dati.get("esito") == "approvata" and isinstance(m.dati.get("data"), datetime.date)]
    risultato = {}
    noti = set(ctx.catalogo.get("inneschi", {}))
    for voce in ctx.catalogo.get("voci", []):
        ripete = bool(voce.get("per_incremento"))
        candidate = per_voce.get(voce["id"], [])
        if ripete:
            candidate = [c for c in candidate if c.get("incremento") == corrente]
        chiusura = candidate[-1] if candidate else None
        riaperta_da = None
        if chiusura is not None and isinstance(chiusura.get("data"), datetime.date):
            congela = "congelamento" in voce.get("controllo", [])
            riaperta_da = next((m.id for m in modifiche if chiusura["data"] < m.dati["data"]
                                and (congela or voce["id"] in _valori(m.dati.get("riapre")))), None)
        risultato[voce["id"]] = {
            "fase": voce["fase"], "applicabilita": condizioni.stato_voce(voce, scheda, inneschi_noti=noti),
            "chiusura": chiusura, "riaperta_da": riaperta_da, "per_incremento": ripete,
            "chiusa": chiusura is not None and chiusura.get("esito") in ("fatto", "non-applicabile") and riaperta_da is None,
            "skill": voce.get("skill", fasi_skill.get(voce["fase"])), "voce": voce,
        }
    ctx.__dict__["_stati_voci"] = risultato
    return risultato


def chiusure(ctx):
    """Valida le chiusure di gate.toml. Di tutte si controlla la forma; di quelle che
    valgono ora anche la sostanza. Le chiusure di incrementi passati, o annullate da
    una modifica, sono storia."""
    p, reperti, stati, viste = ctx.progetto, [], stati_voci(ctx), set()
    for c in p.chiusure:
        st = stati.get(c.get("voce"))
        if st is not None and isinstance(c.get("incremento", 0), int):
            chiave = (c.get("voce"), c.get("incremento") if st["per_incremento"] else None)
            if chiave in viste:
                reperti.append(_r("errore", f"{PROGETTAZIONE}/gate.toml", f"voce {chiave[0]} chiusa due volte" +
                                  (f" nell'incremento {chiave[1]}" if chiave[1] else ""), "chiusure"))
            viste.add(chiave)
        reperti += valida_chiusura(ctx, c, completa=st is not None and st["chiusura"] is c and st["chiusa"])
    return reperti


def valida_chiusura(ctx, c, completa=True, scritta=True):
    """I reperti di una chiusura: voce esistente, esito, data, incremento per le voci
    che si ripetono; con completa, anche evidenze che esistono, motivo ed eventuale
    approvazione di un'esclusione, e i controlli della voce, i cui errori diventano
    errori della chiusura. scritta=False: la chiusura si sta ancora scrivendo."""
    p, reperti = ctx.progetto, []
    dove = f"{PROGETTAZIONE}/gate.toml"
    ident = c.get("voce")
    st = stati_voci(ctx).get(ident)
    if st is None:
        return [_r("errore", dove, f"voce '{ident}' sconosciuta", "chiusure")]
    corrente = p.incremento_corrente()
    inc = c.get("incremento")
    if st["per_incremento"]:
        if not (isinstance(inc, int) and not isinstance(inc, bool) and 1 <= inc <= corrente):
            return [_r("errore", dove, f"voce {ident}: si richiude a ogni incremento, e la chiusura porta "
                       f"'incremento' (da 1 a {corrente})", "chiusure")]
    elif inc is not None:
        reperti.append(_r("avviso", dove, f"voce {ident}: non si ripete per incremento, 'incremento' è superfluo", "chiusure"))
    esito = c.get("esito")
    if esito not in ("fatto", "non-applicabile"):
        return reperti + [_r("errore", dove, f"voce {ident}: esito 'fatto' o 'non-applicabile'", "chiusure")]
    if not isinstance(c.get("data"), datetime.date):
        reperti.append(_r("errore", dove, f"voce {ident}: manca la data", "chiusure"))
    if not completa:
        return reperti
    if st["applicabilita"] != condizioni.APPLICABILE:
        reperti.append(_r("avviso", dove, f"voce {ident} chiusa ma {st['applicabilita']} per la scheda", "chiusure"))
    if esito == "non-applicabile":
        criticita = p.scheda.get("criticita")
        alta = criticita in condizioni.CRITICITA and \
            condizioni.CRITICITA.index(criticita) >= condizioni.CRITICITA.index("alta")
        if not _pieno(c.get("motivo")):
            reperti.append(_r("errore", dove, f"voce {ident}: un'esclusione ha il motivo", "chiusure"))
        if alta and not _pieno(c.get("approvato")):
            reperti.append(_r("errore", dove, f"voce {ident}: da criticità alta un'esclusione è approvata (approvato)", "chiusure"))
        return reperti
    evidenze = _valori(c.get("evidenza"))
    if not evidenze:
        reperti.append(_r("errore", dove, f"voce {ident}: 'fatto' senza evidenza", "chiusure"))
    for ev in evidenze:
        if not _evidenza_esiste(p, ev):
            reperti.append(_r("errore", dove, f"voce {ident}: evidenza '{ev}' non trovata", "chiusure"))
    for nome in st["voce"].get("controllo", []):
        funzione = controllo(nome)
        if funzione is None:
            reperti.append(_r("errore", "catalogo", f"voce {ident}: controllo '{nome}' sconosciuto", "chiusure"))
            continue
        for r in funzione(ctx, ident):
            if r.livello == "errore":
                reperti.append(_r("errore", r.dove, f"[voce {ident}{' chiusa' if scritta else ''}] {r.messaggio}",
                                  r.controllo))
    return reperti


def _evidenza_esiste(p, ev):
    """Un tag o un URL si accettano; altrimenti l'evidenza è un percorso che esiste,
    dalla radice o da docs/progettazione/, con un'eventuale ancora, o un id che si risolve."""
    if ev.startswith("tag:") or ev.startswith("http"):
        return True
    percorso = ev.split("#", 1)[0]
    if percorso and ((p.radice / percorso).exists() or (p.radice / PROGETTAZIONE / percorso).exists()):
        return True
    return p.risolvi(ev) is not None


def gate(ctx, fase):
    """Le voci applicabili di una fase ancora aperte, e gli errori dei loro controlli."""
    reperti = []
    for ident, st in stati_voci(ctx).items():
        if st["fase"] != fase or st["applicabilita"] != condizioni.APPLICABILE:
            continue
        if not st["chiusa"]:
            reperti.append(_r("errore", ident, f"aperta: {st['voce']['testo']}", "gate"))
    return reperti


def congelamento(ctx):
    """La Definition of Ready: ogni voce applicabile di app-blueprint delle fasi 0–7
    chiusa, nessuna domanda aperta, deperibili riverificati, debito accettato,
    revisione di prontezza e prova di decidibilità superate, viste aggiornate."""
    reperti = []
    for ident, st in stati_voci(ctx).items():
        if st["fase"] <= 7 and st["skill"] == "app-blueprint" and st["applicabilita"] == condizioni.APPLICABILE and not st["chiusa"]:
            reperti.append(_r("errore", ident, f"aperta: {st['voce']['testo']}", "congelamento"))
    reperti += c_domande(ctx, None)
    reperti += c_deperibili(ctx, None)
    reperti += c_debito(ctx, None)
    reperti += c_revisione("prontezza")(ctx, "7.13")
    reperti += c_revisione("decidibilita")(ctx, "7.14")
    reperti += c_viste(ctx, None)
    return reperti


def frontiera(ctx, limite=5):
    """Le voci applicabili aperte, della fase più bassa che ne ha ancora, le cui
    dipendenze sono chiuse o non si applicano: il bordo del lavoro, da cui si sceglie
    il prossimo punto. La fase 6 corre intrecciata alle fasi 2–5: le sue voci entrano
    nella frontiera dalla fase 2 in poi."""
    stati = stati_voci(ctx)
    aperte = {i: st for i, st in stati.items() if st["applicabilita"] == condizioni.APPLICABILE and not st["chiusa"]}
    fasi_aperte = sorted({st["fase"] for st in aperte.values() if st["fase"] != 6})
    if not fasi_aperte and not any(st["fase"] == 6 for st in aperte.values()):
        return []
    fase = fasi_aperte[0] if fasi_aperte else 6
    ammesse = {fase} | ({6} if 2 <= fase <= 7 or not fasi_aperte else set())
    pronte = []
    for ident, st in aperte.items():
        if st["fase"] not in ammesse:
            continue
        dipendenze = st["voce"].get("dipende", [])
        if all(stati.get(d, {}).get("chiusa") or stati.get(d, {}).get("applicabilita") != condizioni.APPLICABILE
               for d in dipendenze):
            pronte.append(ident)
    pronte.sort(key=lambda i: (stati[i]["fase"] if stati[i]["fase"] != 6 else 5.5, condizioni.chiave_id(i)))
    return pronte[:limite] if limite else pronte


def verifica(ctx, fase_gate=None, al_congelamento=False):
    """Tutti i controlli che valgono sempre, più quelli del gate o del congelamento richiesti."""
    p = ctx.progetto
    reperti = list(p.reperti) + struttura(p) + c_stato(ctx, None) + c_gate(ctx, None) + c_modifiche(ctx, None)
    reperti += chiusure(ctx)
    if p.piano:
        reperti += c_piano(ctx, None)
    reperti += c_viste(ctx, None)
    if fase_gate is not None:
        reperti += gate(ctx, fase_gate)
    if al_congelamento:
        reperti += congelamento(ctx)
    return _accorpa(reperti)


RE_PREFISSO_VOCE = re.compile(r"^\[voce (\S+) chiusa\] ")


def _accorpa(reperti):
    """Un reperto per difetto: lo stesso messaggio arrivato da più voci chiuse, o anche
    da un controllo diretto, diventa uno solo che nomina le voci."""
    gruppi = {}
    for r in reperti:
        m = RE_PREFISSO_VOCE.match(r.messaggio)
        chiave = (r.livello, r.dove, RE_PREFISSO_VOCE.sub("", r.messaggio))
        voci, primo = gruppi.setdefault(chiave, ([], r))
        if m and m.group(1) not in voci:
            voci.append(m.group(1))
    unici = []
    for (livello, dove, messaggio), (voci, primo) in gruppi.items():
        if voci:
            etichetta = f"[voce {voci[0]} chiusa]" if len(voci) == 1 else f"[voci {', '.join(voci)} chiuse]"
            messaggio = f"{etichetta} {messaggio}"
        unici.append(Reperto(livello, dove, messaggio, primo.controllo))
    return unici
