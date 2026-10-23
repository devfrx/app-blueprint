"""Applicabilità delle voci del catalogo: la condizione `quando` valutata sulla
scheda del progetto.

Sintassi di `quando`, parole separate da spazi:
  espressione  := congiunzione ("o" congiunzione)*
  congiunzione := atomo ("e" atomo)*
  atomo        := ["non"] ( "sempre"
                          | "esposizione" OP livello
                          | "criticita" OP livello
                          | "innesco" nome )
  OP           := ">=" | "<=" | "==" | ">" | "<"
"e" lega più di "o"; non ci sono parentesi.

Una voce è, per un progetto:
  - applicabile: si lavora e si chiude;
  - rinviata: con esposizione "pubblicabile", una voce di esercizio che varrebbe
    per un'app pubblica: finisce nel debito di pubblicazione;
  - non-applicabile: la condizione è falsa;
  - fuori-catena: appartiene alle fasi 13–15, che nessuna skill esegue.
Con esposizione "pubblicabile" una voce di progetto si valuta come per un'app
pubblica: passare al pubblico non deve costare una riprogettazione.
"""

ESPOSIZIONI = ("personale", "pubblicabile", "pubblico")
CRITICITA = ("bassa", "media", "alta", "regolamentata")
NATURE = ("progetto", "esercizio")
OPERATORI = {
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
}
SCALE = {"esposizione": ESPOSIZIONI, "criticita": CRITICITA}

APPLICABILE = "applicabile"
RINVIATA = "rinviata"
NON_APPLICABILE = "non-applicabile"
FUORI_CATENA = "fuori-catena"


class CondizioneNonValida(ValueError):
    pass


def analizza(testo, inneschi_noti=None):
    """Trasforma `quando` in una lista di alternative, ciascuna una lista di atomi
    (negato, tipo, operatore, valore). Solleva CondizioneNonValida."""
    if not isinstance(testo, str) or not testo.strip():
        raise CondizioneNonValida("condizione vuota")
    alternative = []
    for pezzo in _dividi(testo.split(), "o"):
        congiunzione = []
        for atomo in _dividi(pezzo, "e"):
            congiunzione.append(_atomo(atomo, testo, inneschi_noti))
        alternative.append(congiunzione)
    return alternative


def _dividi(parole, separatore):
    gruppi, corrente = [], []
    for p in parole:
        if p == separatore:
            gruppi.append(corrente)
            corrente = []
        else:
            corrente.append(p)
    gruppi.append(corrente)
    if any(not g for g in gruppi):
        raise CondizioneNonValida(f"'{separatore}' senza un termine da entrambi i lati")
    return gruppi


def _atomo(parole, testo, inneschi_noti):
    negato = False
    if parole[0] == "non":
        negato, parole = True, parole[1:]
    if parole == ["sempre"]:
        return (negato, "sempre", None, None)
    if len(parole) == 2 and parole[0] == "innesco":
        if inneschi_noti is not None and parole[1] not in inneschi_noti:
            raise CondizioneNonValida(f"innesco '{parole[1]}' sconosciuto in '{testo}'")
        return (negato, "innesco", None, parole[1])
    if len(parole) == 3 and parole[0] in SCALE:
        scala = SCALE[parole[0]]
        if parole[1] not in OPERATORI:
            raise CondizioneNonValida(f"operatore '{parole[1]}' non valido in '{testo}'")
        if parole[2] not in scala:
            raise CondizioneNonValida(f"livello '{parole[2]}' non valido per {parole[0]} in '{testo}'")
        return (negato, parole[0], parole[1], parole[2])
    raise CondizioneNonValida(f"termine non riconosciuto: '{' '.join(parole)}' in '{testo}'")


def vale(alternative, esposizione, criticita, inneschi):
    """True se la condizione analizzata vale per questi valori della scheda."""
    for congiunzione in alternative:
        if all(_vale_atomo(a, esposizione, criticita, inneschi) for a in congiunzione):
            return True
    return False


def _vale_atomo(atomo, esposizione, criticita, inneschi):
    negato, tipo, op, valore = atomo
    if tipo == "sempre":
        esito = True
    elif tipo == "innesco":
        esito = valore in inneschi
    else:
        scala = SCALE[tipo]
        attuale = esposizione if tipo == "esposizione" else criticita
        esito = OPERATORI[op](scala.index(attuale), scala.index(valore))
    return not esito if negato else esito


def stato_voce(voce, scheda, fasi_fuori_catena=frozenset({13, 14, 15}), inneschi_noti=None):
    """Lo stato d'applicabilità di una voce per la scheda data.

    voce: dict con 'quando', 'natura' e 'fase' (le trasversali e la DoD non hanno
    fase né natura: valgono come voci di progetto).
    scheda: dict con 'esposizione', 'criticita', 'inneschi'.
    """
    alternative = analizza(voce["quando"], inneschi_noti)
    esposizione = scheda["esposizione"]
    criticita = scheda["criticita"]
    inneschi = set(scheda.get("inneschi", []))
    natura = voce.get("natura", "progetto")

    if esposizione == "pubblicabile":
        if natura == "progetto":
            applicabile = vale(alternative, "pubblico", criticita, inneschi)
            stato = APPLICABILE if applicabile else NON_APPLICABILE
        elif vale(alternative, "pubblicabile", criticita, inneschi):
            stato = APPLICABILE
        elif vale(alternative, "pubblico", criticita, inneschi):
            stato = RINVIATA
        else:
            stato = NON_APPLICABILE
    else:
        stato = APPLICABILE if vale(alternative, esposizione, criticita, inneschi) else NON_APPLICABILE

    if voce.get("fase") in fasi_fuori_catena and stato != NON_APPLICABILE:
        return FUORI_CATENA
    return stato


def profilo(scheda):
    """Il profilo della scheda con i default: finché la voce 1.13 non lo compila, un
    progetto vale come personale, a criticità bassa, senza inneschi."""
    scheda = scheda if isinstance(scheda, dict) else {}
    esposizione = scheda.get("esposizione")
    criticita = scheda.get("criticita")
    inneschi = scheda.get("inneschi")
    return {"esposizione": esposizione if esposizione in ESPOSIZIONI else "personale",
            "criticita": criticita if criticita in CRITICITA else "bassa",
            "inneschi": [i for i in inneschi if isinstance(i, str)] if isinstance(inneschi, list) else []}


def descrivi_motivo(voce, scheda):
    """Una riga che spiega perché una voce non si applica o è rinviata."""
    if profilo(scheda)["esposizione"] == "pubblicabile" and voce.get("natura") == "esercizio":
        return f"voce di esercizio rinviata al passaggio al pubblico (quando: {voce['quando']})"
    return f"condizione falsa per la scheda (quando: {voce['quando']})"


def chiave_id(ident):
    """Chiave d'ordinamento degli id delle voci: '5.05.1' dopo '5.05' e prima di '5.06';
    T.* e D.* dopo le fasi."""
    testa, _, resto = ident.partition(".")
    if testa.isdigit():
        return (0, int(testa)) + tuple(int(p) if p.isdigit() else 0 for p in resto.split("."))
    return (1, testa) + tuple(int(p) if p.isdigit() else 0 for p in resto.split("."))
