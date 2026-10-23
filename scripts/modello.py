"""Il modello del progetto: legge le sorgenti di docs/progettazione/ e contracts/,
le trasforma in elementi con un tipo e un id, e risolve i riferimenti tra loro.

Ogni informazione sta in un posto solo; questo modulo è ciò che permette di
leggerla per id invece che per file, e di calcolare ciò che non si scrive:
l'incremento di ogni elemento, l'indice, i riferimenti in entrata.

Solo libreria standard. Nessuna scrittura: le sorgenti le modifica la sessione.
"""
import json
import re
import subprocess
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

PROGETTAZIONE = "docs/progettazione"
CONTRATTI = "contracts"
ADR = "docs/adr"
MOCKUP = "docs/design/mockups"
VISTE = f"{PROGETTAZIONE}/viste"

# Prefissi degli id: un id prefissato si risolve senza sapere da quale campo arriva.
PREFISSI = {
    "OB": "obiettivi", "NO": "non_obiettivi", "V": "vincoli", "A": "assunzioni",
    "RK": "rischi", "R": "regole", "RNF": "rnf", "RD": "requisiti_dati",
    "PC": "percorsi", "CO": "conflitti", "DR": "driver", "ST": "strategie",
    "MI": "minacce", "FL": "flussi", "AC": "accessi", "DEB": "debito",
    "DEP": "deperibili", "Q": "domande", "REV": "revisioni", "MOD": "modifiche",
    "ADR": "adr",
}
# I riferimenti a elementi con un id libero si scrivono "tipo:id".
TIPIZZATI = {
    "entita": "entita", "attributo": "attributi", "relazione": "relazioni",
    "generalizzazione": "generalizzazioni", "modulo": "moduli", "attore": "stakeholder",
    "stakeholder": "stakeholder", "sistema": "sistemi", "tabella": "tabelle",
    "colonna": "colonne", "indice": "indici", "api": "api", "facciata": "facciata",
    "evento": "eventi", "componente": "componenti", "errore": "errori",
    "schermata": "schermate", "testo": "testi", "rotta": "rotte", "ambiente": "ambienti",
    "processo": "processi", "sequenza": "sequenze", "matrice": "matrice", "voce": "voci",
    "macchina": "macchine", "termine": "glossario", "persona": "personas",
    "sezione": "sezioni", "confine": "confini", "variabile": "variabili",
    "segreto": "segreti", "livello": "livelli", "task": "task",
    "integrazione": "integrazioni", "sottodominio": "sottodomini", "dipendenza": "dipendenze",
    "volume": "volumi", "ristrutturazione": "ristrutturazione", "validazione": "validazioni",
    "algoritmo": "algoritmi", "transazione": "transazioni", "porta": "porte", "pattern": "pattern",
    "dettaglio": "dettaglio", "incremento": "incrementi", "area": "aree", "qualita": "qualita",
}
_TIPO_CITATO = {tipo: nome for nome, tipo in TIPIZZATI.items()}
RE_PREFISSATO = re.compile(r"^([A-Z]+)-([A-Za-z0-9][A-Za-z0-9._-]*)$")
RE_SLUG = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
RE_FRONTMATTER = re.compile(r"\A\+\+\+\n(.*?)\n\+\+\+\n?(.*)\Z", re.S)
RE_ADR_FILE = re.compile(r"^(\d{4})-[a-z0-9-]+\.md$")
RE_STRATEGIA = re.compile(r"\bST-[a-z0-9-]+")


@dataclass
class Reperto:
    """Un esito di un controllo: errore o avviso, con dove guardare."""
    livello: str          # "errore" | "avviso"
    dove: str             # file o id
    messaggio: str
    controllo: str = ""   # nome del controllo che l'ha prodotto

    def testo(self):
        return f"[{self.livello}] {self.dove}: {self.messaggio}"


@dataclass
class Elemento:
    tipo: str
    id: str
    dati: dict
    sorgente: str
    contenitore: str | None = None   # id dell'elemento che lo contiene, per gli annidati

    def etichetta(self):
        """Una descrizione di una riga, per l'indice."""
        d = self.dati
        for campo in ("titolo", "testo", "nome", "operazione", "domanda", "descrizione",
                      "responsabilita", "scopo", "decisione", "definizione", "cosa", "oggetto",
                      "summary", "percorso"):
            valore = d.get(campo)
            if isinstance(valore, str) and valore.strip():
                riga = valore.strip().splitlines()[0]
                return riga if len(riga) <= 100 else riga[:97] + "…"
        return ""


@dataclass
class Documento:
    """Un file Markdown con frontmatter TOML tra righe '+++'."""
    percorso: str
    meta: dict
    corpo: str


@dataclass
class Progetto:
    radice: Path
    stato: dict = field(default_factory=dict)
    chiusure: list = field(default_factory=list)
    elementi: dict = field(default_factory=dict)          # tipo -> id -> Elemento
    testi: dict = field(default_factory=dict)             # percorso -> testo letto
    reperti: list = field(default_factory=list)           # problemi di lettura
    tabelle_libere: dict = field(default_factory=dict)    # sezioni non a elenco: fattibilita, stima, trasversali…
    openapi: dict | None = None
    matrice: dict | None = None
    piano: dict | None = None

    # --- accesso ---------------------------------------------------------------

    def tutti(self, tipo):
        return list(self.elementi.get(tipo, {}).values())

    def trova(self, tipo, ident):
        return self.elementi.get(tipo, {}).get(ident)

    def aggiungi(self, elemento):
        gruppo = self.elementi.setdefault(elemento.tipo, {})
        if elemento.id in gruppo:
            self.reperti.append(Reperto("errore", elemento.sorgente,
                                        f"{elemento.tipo} '{elemento.id}': id duplicato (anche in {gruppo[elemento.id].sorgente})",
                                        "struttura"))
            return
        gruppo[elemento.id] = elemento

    @property
    def scheda(self):
        return self.stato.get("scheda", {}) if isinstance(self.stato, dict) else {}

    def incremento_corrente(self):
        valore = self.scheda.get("incremento", 1)
        return valore if isinstance(valore, int) and not isinstance(valore, bool) else 1

    def attori(self):
        """Gli stakeholder che usano il prodotto: sono i ruoli della matrice."""
        return {e.id for e in self.tutti("stakeholder") if e.dati.get("usa") is True}

    def aree(self):
        return {e.dati.get("prefisso") for e in self.tutti("aree")}

    # --- riferimenti -------------------------------------------------------------

    def risolvi(self, valore, atteso=None):
        """Restituisce (tipo, id) del riferimento, o None se non si risolve.

        atteso: il tipo che il campo si aspetta, per i valori senza prefisso.
        """
        if not isinstance(valore, str) or not valore:
            return None
        if ":" in valore:
            tipo_rif, _, ident = valore.partition(":")
            tipo = TIPIZZATI.get(tipo_rif)
            if tipo and ident in self.elementi.get(tipo, {}):
                return (tipo, ident)
            return None
        m = RE_PREFISSATO.match(valore)
        if m:
            tipo = PREFISSI.get(m.group(1))
            if tipo is None and m.group(1) in self.aree():
                tipo = "storie"
            if tipo and valore in self.elementi.get(tipo, {}):
                return (tipo, valore)
            if atteso is None:
                return None
        if atteso:
            for t in (atteso if isinstance(atteso, tuple) else (atteso,)):
                if valore in self.elementi.get(t, {}):
                    return (t, valore)
        return None

    def uscenti(self, elemento):
        """Tutti i riferimenti che partono da un elemento: [(campo, valore, risolto)]."""
        risultato = []
        for campo, atteso in RIFERIMENTI.get(elemento.tipo, {}).items():
            for valore in _valori(elemento.dati.get(campo)):
                risultato.append((campo, valore, self.risolvi(valore, atteso)))
        return risultato

    def entranti(self):
        """Indice inverso dei riferimenti: (tipo, id) -> [(tipo, id, campo)] di chi lo cita."""
        indice = {}
        for gruppo in self.elementi.values():
            for el in gruppo.values():
                for campo, _, risolto in self.uscenti(el):
                    if risolto:
                        indice.setdefault(risolto, []).append((el.tipo, el.id, campo))
        return indice

    # --- incrementi ---------------------------------------------------------------

    def incremento_di(self, elemento, _visitati=None):
        """L'incremento in cui un elemento serve: il minimo tra quelli delle storie che
        lo giustificano. Le storie lo dichiarano; tutto il resto lo eredita dalla
        traccia. Senza storie nella traccia vale 1: è trasversale."""
        if elemento.tipo == "storie":
            valore = elemento.dati.get("incremento")
            return valore if isinstance(valore, int) and not isinstance(valore, bool) else 1
        cache = self.__dict__.setdefault("_incrementi", {})
        chiave = (elemento.tipo, elemento.id)
        if chiave in cache:
            return cache[chiave]
        visitati = _visitati or set()
        if chiave in visitati:
            return None
        visitati = visitati | {chiave}
        candidati = []
        for campo, _, risolto in self.uscenti(elemento):
            if campo in CAMPI_DI_TRACCIA and risolto and risolto[0] in TIPI_CHE_PORTANO_INCREMENTO:
                inc = self.incremento_di(self.trova(*risolto), visitati)
                if inc is not None:
                    candidati.append(inc)
        if not candidati and elemento.tipo == "entita":
            # un'entità serve dall'incremento della prima storia che la usa
            for s in self.tutti("storie"):
                if elemento.id in _valori(s.dati.get("entita")):
                    candidati.append(self.incremento_di(s))
        if not candidati and elemento.tipo == "relazioni":
            # senza traccia, una relazione non esiste prima delle sue entità
            incrementi = [self.incremento_di(e, visitati) for e in
                          (self.trova("entita", x) for x in _valori(elemento.dati.get("entita"))) if e]
            incrementi = [i for i in incrementi if i is not None]
            if incrementi:
                candidati.append(max(incrementi))
        if not candidati and elemento.contenitore:
            tipo_contenitore = CONTENITORE.get(elemento.tipo)
            contenitore = self.trova(tipo_contenitore, elemento.contenitore) if tipo_contenitore else None
            if contenitore:
                inc = self.incremento_di(contenitore, visitati)
                if inc is not None:
                    candidati.append(inc)
        risultato = min(candidati) if candidati else 1
        cache[chiave] = risultato
        return risultato

    def tag_git(self):
        """I tag del repo, se la radice è un repo git; altrimenti None, e chi li usa
        non li può verificare. Si leggono una volta."""
        if "_tag_git" not in self.__dict__:
            tag = None
            if (self.radice / ".git").exists():
                try:
                    uscita = subprocess.run(["git", "-C", str(self.radice), "tag", "--list"],
                                            capture_output=True, text=True, timeout=30, check=True)
                    tag = set(uscita.stdout.split())
                except (OSError, subprocess.SubprocessError):
                    tag = None
            self.__dict__["_tag_git"] = tag
        return self.__dict__["_tag_git"]

    def modulo_di(self, elemento):
        """Il modulo che possiede un elemento, o None. Una storia è del modulo che la
        orchestra; gli annidati sono del modulo del loro contenitore; una regola della
        matrice è del modulo dell'entità che protegge."""
        d = elemento.dati
        if elemento.tipo == "api":
            return d.get("x-modulo")
        if elemento.tipo == "dettaglio":
            return elemento.id
        if elemento.tipo == "matrice":
            entita = self.trova("entita", d.get("risorsa"))
            return self.modulo_di(entita) if entita else None
        tipo_contenitore = CONTENITORE.get(elemento.tipo)
        if tipo_contenitore == "dettaglio":
            return elemento.contenitore
        if tipo_contenitore:
            contenitore = self.trova(tipo_contenitore, elemento.contenitore)
            return self.modulo_di(contenitore) if contenitore else None
        return d.get("modulo") if isinstance(d.get("modulo"), str) else None


def citabile(elemento):
    """L'id con cui un elemento si cita in un campo di riferimenti: prefissato, o
    "tipo:id"."""
    if elemento.tipo == "storie" or elemento.tipo in PREFISSI.values():
        return elemento.id
    tipo = _TIPO_CITATO.get(elemento.tipo)
    return f"{tipo}:{elemento.id}" if tipo else elemento.id


def _valori(valore):
    """Normalizza un campo di riferimenti in una lista di stringhe."""
    if valore is None:
        return []
    if isinstance(valore, str):
        return [valore]
    if isinstance(valore, list):
        return [v for v in valore if isinstance(v, str)]
    return []


# Per ogni tipo, i campi che contengono riferimenti e il tipo atteso dei valori senza
# prefisso. None: il valore deve avere un prefisso o essere tipizzato ("tipo:id").
RIFERIMENTI = {
    "rischi": {"traccia": None},
    "domande": {"punto": "voci", "bloccata_da": "domande"},
    "revisioni": {"traccia": None},
    "modifiche": {"impatto": None, "riapre": "voci"},
    "rnf": {"fonte": "stakeholder", "assunzione": None, "indirizzato_da": None},
    "requisiti_dati": {"concetto": "glossario", "fonte": "stakeholder"},
    "percorsi": {"storie": "storie"},
    "conflitti": {"tra": "stakeholder"},
    "storie": {"attore": "stakeholder", "fonte": "stakeholder", "entita": "entita",
               "modulo": "moduli", "tocca": "moduli", "traccia": None},
    "regole": {"entita": "entita", "traccia": None},
    "moduli": {"sottodominio": "sottodomini"},
    "dipendenze": {"a_valle": "moduli", "a_monte": "moduli"},
    "entita": {"termine": "glossario", "modulo": "moduli", "traccia": None},
    "attributi": {"traccia": None},
    "generalizzazioni": {"padre": "entita", "figli": "entita", "traccia": None},
    "relazioni": {"entita": "entita", "traccia": None},
    "macchine": {"entita": "entita"},
    "processi": {"storie": "storie", "entita": "entita"},
    "driver": {"ref": None},
    "strategie": {"adr": "adr", "traccia": None},
    "integrazioni": {"sistema": "sistemi", "modulo": "moduli"},
    "flussi": {"confini": "confini", "percorsi": "percorsi"},
    "minacce": {"flusso": "flussi", "contromisure": None},
    "volumi": {"concetto": None, "fonte": None},
    "accessi": {"traccia": None, "concetti": None, "filtri": "colonne"},
    "ristrutturazione": {"oggetto": None, "accessi": "accessi"},
    "tabelle": {"modulo": "moduli", "da": None, "strategia": None},
    "colonne": {"da": "attributi", "traccia": None},
    "indici": {"accessi": "accessi", "traccia": None},
    "errori": {"utente": "testi", "traccia": None},
    "validazioni": {"campo": "attributi", "errore": "errori"},
    "variabili": {"ambienti": "ambienti"},
    "matrice": {"consenti": "stakeholder", "traccia": None},
    "api": {"x-modulo": "moduli", "x-storie": "storie", "x-errori": "errori"},
    "facciata": {"errori": "errori", "traccia": None},
    "eventi": {"consumatori": "moduli", "traccia": None},
    "componenti": {"traccia": None},
    "algoritmi": {"volumi": None, "traccia": None},
    "transazioni": {"operazione": None},
    "porte": {"verso": None},
    "sequenze": {"percorso": "percorsi", "operazioni": "api", "facciate": "facciata"},
    "personas": {"attore": "stakeholder"},
    "sezioni": {"ruoli": "stakeholder"},
    "rotte": {"schermata": "schermate", "ruoli": "stakeholder"},
    "schermate": {"ruoli": "stakeholder", "storie": "storie", "dati": "api", "testi": "testi"},
    "task": {"modulo": "moduli", "storie": "storie", "dipende_da": "task"},
    "livelli": {},
}
# I tipi la cui presenza in una traccia porta un incremento.
TIPI_CHE_PORTANO_INCREMENTO = {"storie", "entita", "relazioni", "attributi", "tabelle",
                               "accessi", "api", "facciata", "schermate", "percorsi"}
# I campi che dicono perché un elemento esiste: solo loro gli trasmettono un
# incremento. Gli altri riferimenti dicono cosa l'elemento usa (i dati di una
# schermata, i volumi di un algoritmo, i concetti di un accesso), e un elemento
# non si costruisce prima perché usa qualcosa che esiste già.
CAMPI_DI_TRACCIA = {"traccia", "storie", "x-storie", "da", "accessi", "operazione", "percorso"}
CONTENITORE = {"attributi": "entita", "colonne": "tabelle", "indici": "tabelle",
               "facciata": "dettaglio", "eventi": "dettaglio", "componenti": "dettaglio",
               "algoritmi": "dettaglio", "transazioni": "dettaglio", "porte": "dettaglio",
               "pattern": "dettaglio"}


# --- lettura --------------------------------------------------------------------

def _leggi_testo(progetto, relativo):
    percorso = progetto.radice / relativo
    try:
        testo = percorso.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as e:
        progetto.reperti.append(Reperto("errore", relativo, f"non leggibile: {e}", "lettura"))
        return None
    progetto.testi[relativo] = testo
    return testo


def _leggi_toml(progetto, relativo):
    testo = _leggi_testo(progetto, relativo)
    if testo is None:
        return None
    try:
        return tomllib.loads(testo)
    except tomllib.TOMLDecodeError as e:
        progetto.reperti.append(Reperto("errore", relativo, f"TOML non valido: {e}", "lettura"))
        return None


def leggi_documento(progetto, relativo):
    """Un Markdown con frontmatter TOML facoltativo."""
    testo = _leggi_testo(progetto, relativo)
    if testo is None:
        return None
    m = RE_FRONTMATTER.match(testo)
    if not m:
        return Documento(relativo, {}, testo)
    try:
        meta = tomllib.loads(m.group(1))
    except tomllib.TOMLDecodeError as e:
        progetto.reperti.append(Reperto("errore", relativo, f"frontmatter TOML non valido: {e}", "lettura"))
        meta = {}
    return Documento(relativo, meta, m.group(2))


def _elenco(progetto, dati, chiave, tipo, sorgente, campo_id="id", contenitore=None, id_di=None):
    """Aggiunge gli elementi di una lista [[chiave]]. Restituisce gli elementi aggiunti."""
    voci = dati.get(chiave) if isinstance(dati, dict) else None
    if voci is None:
        return []
    if not isinstance(voci, list):
        progetto.reperti.append(Reperto("errore", sorgente, f"'{chiave}' deve essere un elenco [[{chiave}]]", "struttura"))
        return []
    aggiunti = []
    for n, voce in enumerate(voci, 1):
        if not isinstance(voce, dict):
            progetto.reperti.append(Reperto("errore", sorgente, f"'{chiave}' n. {n} non è una tabella", "struttura"))
            continue
        ident = id_di(voce) if id_di else voce.get(campo_id)
        if not isinstance(ident, str) or not ident.strip():
            progetto.reperti.append(Reperto("errore", sorgente, f"'{chiave}' n. {n}: manca '{campo_id}'", "struttura"))
            continue
        el = Elemento(tipo, ident, voce, sorgente, contenitore)
        progetto.aggiungi(el)
        aggiunti.append(el)
    return aggiunti


def carica(radice, catalogo=None):
    """Legge tutte le sorgenti sotto la radice del repo progettato."""
    progetto = Progetto(radice=Path(radice))
    p = PROGETTAZIONE

    progetto.stato = _leggi_toml(progetto, f"{p}/stato.toml") or {}
    gate = _leggi_toml(progetto, f"{p}/gate.toml") or {}
    progetto.chiusure = [c for c in gate.get("chiusure", []) if isinstance(c, dict)]

    registri = _leggi_toml(progetto, f"{p}/registri.toml") or {}
    for chiave in ("rischi", "assunzioni", "domande", "debito", "deperibili", "revisioni", "modifiche"):
        _elenco(progetto, registri, chiave, chiave, f"{p}/registri.toml")

    prodotto = _leggi_toml(progetto, f"{p}/prodotto/prodotto.toml") or {}
    for chiave in ("obiettivi", "stakeholder", "sistemi", "non_obiettivi", "vincoli"):
        _elenco(progetto, prodotto, chiave, chiave, f"{p}/prodotto/prodotto.toml")
    for tabella in ("fattibilita", "stima"):
        if isinstance(prodotto.get(tabella), dict):
            progetto.tabelle_libere[tabella] = prodotto[tabella]

    requisiti = _leggi_toml(progetto, f"{p}/requisiti/requisiti.toml") or {}
    sorgente = f"{p}/requisiti/requisiti.toml"
    _elenco(progetto, requisiti, "aree", "aree", sorgente, campo_id="prefisso")
    _elenco(progetto, requisiti, "qualita", "qualita", sorgente, campo_id="caratteristica")
    for chiave in ("rnf", "requisiti_dati", "percorsi", "conflitti"):
        _elenco(progetto, requisiti, chiave, chiave, sorgente)
    for tabella in ("trasversali", "metodo_priorita"):
        if tabella in requisiti:
            progetto.tabelle_libere[tabella] = requisiti[tabella]
    for file_storie in sorted((progetto.radice / p / "requisiti").glob("storie*.toml")):
        relativo = file_storie.relative_to(progetto.radice).as_posix()
        _elenco(progetto, _leggi_toml(progetto, relativo) or {}, "storie", "storie", relativo)

    dominio = f"{p}/dominio"
    _elenco(progetto, _leggi_toml(progetto, f"{dominio}/glossario.toml") or {}, "termini", "glossario",
            f"{dominio}/glossario.toml", campo_id="termine")
    _elenco(progetto, _leggi_toml(progetto, f"{dominio}/regole.toml") or {}, "regole", "regole", f"{dominio}/regole.toml")
    moduli = _leggi_toml(progetto, f"{dominio}/moduli.toml") or {}
    _elenco(progetto, moduli, "sottodomini", "sottodomini", f"{dominio}/moduli.toml")
    _elenco(progetto, moduli, "moduli", "moduli", f"{dominio}/moduli.toml")
    _elenco(progetto, moduli, "dipendenze", "dipendenze", f"{dominio}/moduli.toml",
            campo_id="a_valle e a_monte",
            id_di=lambda d: f"{d.get('a_valle')}>{d.get('a_monte')}" if d.get("a_valle") and d.get("a_monte") else None)
    entita = _leggi_toml(progetto, f"{dominio}/entita.toml") or {}
    for el in _elenco(progetto, entita, "entita", "entita", f"{dominio}/entita.toml"):
        _elenco(progetto, el.dati, "attributi", "attributi", el.sorgente, campo_id="nome", contenitore=el.id,
                id_di=lambda a, e=el.id: f"{e}.{a.get('nome')}" if a.get("nome") else None)
    _elenco(progetto, entita, "generalizzazioni", "generalizzazioni", f"{dominio}/entita.toml")
    for el in _elenco(progetto, entita, "relazioni", "relazioni", f"{dominio}/entita.toml"):
        # i partecipanti si citano come entità: li espongo come campo di riferimenti
        el.dati = dict(el.dati, entita=[x.get("entita") for x in el.dati.get("partecipanti", []) if isinstance(x, dict)])
    _elenco(progetto, _leggi_toml(progetto, f"{dominio}/stati.toml") or {}, "macchine", "macchine",
            f"{dominio}/stati.toml", campo_id="entita")
    for doc in _documenti(progetto, f"{dominio}/processi"):
        if doc.meta.get("id"):
            progetto.aggiungi(Elemento("processi", doc.meta["id"], dict(doc.meta, _corpo=doc.corpo), doc.percorso))
        else:
            progetto.reperti.append(Reperto("errore", doc.percorso, "manca 'id' nel frontmatter", "struttura"))

    architettura = _leggi_toml(progetto, f"{p}/architettura/architettura.toml") or {}
    sorgente = f"{p}/architettura/architettura.toml"
    for chiave in ("driver", "strategie", "ambienti"):
        _elenco(progetto, architettura, chiave, chiave, sorgente)
    _elenco(progetto, architettura, "integrazioni", "integrazioni", sorgente, campo_id="sistema")
    minacce = _leggi_toml(progetto, f"{p}/architettura/minacce.toml") or {}
    for chiave in ("confini", "flussi", "minacce"):
        _elenco(progetto, minacce, chiave, chiave, f"{p}/architettura/minacce.toml")

    dati = _leggi_toml(progetto, f"{p}/dati/dati.toml") or {}
    _elenco(progetto, dati, "volumi", "volumi", f"{p}/dati/dati.toml", campo_id="concetto")
    _elenco(progetto, dati, "accessi", "accessi", f"{p}/dati/dati.toml")
    _elenco(progetto, dati, "ristrutturazione", "ristrutturazione", f"{p}/dati/dati.toml")

    for file_modulo in sorted((progetto.radice / p / "moduli").glob("*.toml")):
        relativo = file_modulo.relative_to(progetto.radice).as_posix()
        d = _leggi_toml(progetto, relativo) or {}
        modulo = d.get("modulo")
        if not isinstance(modulo, str) or not modulo:
            progetto.reperti.append(Reperto("errore", relativo, "manca 'modulo'", "struttura"))
            continue
        progetto.aggiungi(Elemento("dettaglio", modulo, d, relativo))
        for chiave, campo in (("facciata", "operazione"), ("eventi", "nome"), ("componenti", "nome"),
                              ("pattern", "nome"), ("algoritmi", "nome"), ("transazioni", "operazione"),
                              ("porte", "nome")):
            _elenco(progetto, d, chiave, chiave, relativo, campo_id=campo, contenitore=modulo,
                    id_di=lambda v, m=modulo, c=campo: f"{m}.{v.get(c)}" if v.get(c) else None)

    for doc in _documenti(progetto, f"{p}/sequenze"):
        ident = doc.meta.get("percorso") or Path(doc.percorso).stem
        progetto.aggiungi(Elemento("sequenze", ident, dict(doc.meta, _corpo=doc.corpo), doc.percorso))

    ux = _leggi_toml(progetto, f"{p}/ux/ux.toml") or {}
    for chiave in ("personas", "sezioni", "schermate"):
        _elenco(progetto, ux, chiave, chiave, f"{p}/ux/ux.toml")
    _elenco(progetto, ux, "rotte", "rotte", f"{p}/ux/ux.toml", campo_id="percorso")
    design_system = _leggi_toml(progetto, f"{p}/ux/design-system.toml")
    if design_system is not None:
        progetto.tabelle_libere["design_system"] = design_system
    _elenco(progetto, _leggi_toml(progetto, f"{p}/ux/testi.toml") or {}, "testi", "testi",
            f"{p}/ux/testi.toml", campo_id="chiave")

    progetto.piano = _leggi_toml(progetto, f"{p}/piano/piano.toml")
    if progetto.piano:
        _elenco(progetto, progetto.piano, "task", "task", f"{p}/piano/piano.toml")
        _elenco(progetto, progetto.piano, "incrementi", "incrementi", f"{p}/piano/piano.toml",
                campo_id="numero", id_di=lambda d: str(d.get("numero")) if d.get("numero") is not None else None)
    _elenco(progetto, _leggi_toml(progetto, f"{p}/piano/test.toml") or {}, "livelli", "livelli", f"{p}/piano/test.toml")

    c = CONTRATTI
    schema = _leggi_toml(progetto, f"{c}/schema.toml") or {}
    for t in _elenco(progetto, schema, "tabelle", "tabelle", f"{c}/schema.toml", campo_id="nome"):
        _elenco(progetto, t.dati, "colonne", "colonne", t.sorgente, campo_id="nome", contenitore=t.id,
                id_di=lambda col, n=t.id: f"{n}.{col.get('nome')}" if col.get("nome") else None)
        _elenco(progetto, t.dati, "indici", "indici", t.sorgente, campo_id="nome", contenitore=t.id)
    progetto.matrice = _leggi_toml(progetto, f"{c}/autorizzazioni.toml")
    if progetto.matrice:
        _elenco(progetto, progetto.matrice, "regole", "matrice", f"{c}/autorizzazioni.toml",
                campo_id="risorsa e azione", id_di=lambda r: f"{r.get('risorsa')}.{r.get('azione')}" if r.get("risorsa") and r.get("azione") else None)
    errori = _leggi_toml(progetto, f"{c}/errori.toml") or {}
    _elenco(progetto, errori, "errori", "errori", f"{c}/errori.toml", campo_id="codice")
    _elenco(progetto, errori, "validazioni", "validazioni", f"{c}/errori.toml", campo_id="campo")
    configurazione = _leggi_toml(progetto, f"{c}/configurazione.toml") or {}
    _elenco(progetto, configurazione, "variabili", "variabili", f"{c}/configurazione.toml", campo_id="nome")
    _elenco(progetto, configurazione, "segreti", "segreti", f"{c}/configurazione.toml", campo_id="nome")
    _carica_openapi(progetto, f"{c}/openapi.json")

    _carica_adr(progetto)
    if catalogo:
        for voce in catalogo.get("voci", []):
            progetto.aggiungi(Elemento("voci", voce["id"], voce, "catalogo"))
    return progetto


def _documenti(progetto, cartella):
    base = progetto.radice / cartella
    if not base.is_dir():
        return []
    risultato = []
    for f in sorted(base.glob("*.md")):
        doc = leggi_documento(progetto, f.relative_to(progetto.radice).as_posix())
        if doc:
            risultato.append(doc)
    return risultato


METODI_HTTP = ("get", "put", "post", "delete", "patch", "head", "options", "trace")


def _carica_openapi(progetto, relativo):
    testo = _leggi_testo(progetto, relativo)
    if testo is None:
        return
    try:
        spec = json.loads(testo)
    except json.JSONDecodeError as e:
        progetto.reperti.append(Reperto("errore", relativo, f"JSON non valido: {e}", "lettura"))
        return
    progetto.openapi = spec
    for percorso, voci in (spec.get("paths") or {}).items():
        if not isinstance(voci, dict):
            continue
        for metodo, op in voci.items():
            if metodo not in METODI_HTTP or not isinstance(op, dict):
                continue
            ident = op.get("operationId")
            if not ident:
                progetto.reperti.append(Reperto("errore", relativo, f"{metodo.upper()} {percorso}: manca operationId", "api"))
                continue
            progetto.aggiungi(Elemento("api", ident, dict(op, _metodo=metodo, _percorso=percorso), relativo))


def _carica_adr(progetto):
    base = progetto.radice / ADR
    if not base.is_dir():
        return
    for f in sorted(base.glob("*.md")):
        relativo = f.relative_to(progetto.radice).as_posix()
        m = RE_ADR_FILE.match(f.name)
        if not m:
            progetto.reperti.append(Reperto("avviso", relativo, "nome non nella forma NNNN-titolo.md", "adr"))
            continue
        testo = _leggi_testo(progetto, relativo) or ""
        titolo = next((r[2:].strip() for r in testo.splitlines() if r.startswith("# ")), "")
        stato = re.search(r"\*\*Status:\*\*\s*([^\n]+)", testo)
        progetto.aggiungi(Elemento("adr", f"ADR-{m.group(1)}", {
            "titolo": titolo, "status": stato.group(1).strip() if stato else "", "_testo": testo,
        }, relativo))


def leggi_catalogo(percorso):
    with open(percorso, "rb") as f:
        return tomllib.load(f)
