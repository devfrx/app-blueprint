"""Le sole scritture dello strumento sulle sorgenti: le chiusure in gate.toml, il
punto aperto e le righe del registro in stato.toml. Tutto il resto lo scrive la
sessione.

Si modifica il testo per sezioni ([tabella] o [[voce di un array]]) senza
riserializzare il file, così commenti e ordine restano. Ogni scrittura si rilegge
con tomllib prima di salvare: un file che non si rilegge non si salva.
"""
import datetime
import json
import re
import tomllib

RE_INTESTAZIONE = re.compile(r"^\[\[?[A-Za-z0-9_.-]+\]\]?[ \t]*$", re.M)


def valore(v):
    """Un valore Python come letterale TOML (stringhe, interi, booleani, date, liste)."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, datetime.date):
        return v.isoformat()
    if isinstance(v, str):
        # una stringa JSON è anche una stringa base TOML valida
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ", ".join(valore(x) for x in v) + "]"
    raise TypeError(f"valore non scrivibile in TOML: {v!r}")


def blocco(intestazione, campi):
    return intestazione + "\n" + "".join(f"{k} = {valore(v)}\n" for k, v in campi.items() if v is not None)


def _sezioni(testo):
    """[(intestazione o None per il preambolo, testo della sezione)]"""
    inizi = [m.start() for m in RE_INTESTAZIONE.finditer(testo)]
    if not inizi:
        return [(None, testo)]
    sezioni = [(None, testo[:inizi[0]])] if inizi[0] > 0 else []
    for i, inizio in enumerate(inizi):
        fine = inizi[i + 1] if i + 1 < len(inizi) else len(testo)
        parte = testo[inizio:fine]
        sezioni.append((parte.split("\n", 1)[0].strip(), parte))
    return sezioni


def _dati(intestazione, parte):
    nome = intestazione.strip("[]")
    letti = tomllib.loads(parte)
    return letti[nome][0] if intestazione.startswith("[[") else letti[nome]


def aggiorna_sezione(testo, intestazione, trova, campi):
    """Sostituisce la prima sezione con questa intestazione per cui trova(dati) è vero,
    oppure aggiunge la sezione dopo l'ultima con la stessa intestazione (o in fondo).
    Restituisce (nuovo testo, "sostituita" | "aggiunta")."""
    nuovo = blocco(intestazione, campi)
    sezioni = _sezioni(testo)
    ultima = None
    for i, (testa, parte) in enumerate(sezioni):
        if testa != intestazione:
            continue
        ultima = i
        if trova(_dati(testa, parte)):
            coda = parte[len(parte.rstrip("\n")):]
            sezioni[i] = (testa, nuovo.rstrip("\n") + (coda if len(coda) >= 2 else "\n\n"))
            esito = "sostituita"
            break
    else:
        esito = "aggiunta"
        if ultima is None:
            corpo = "".join(p for _, p in sezioni).rstrip("\n")
            risultato = (corpo + "\n\n" if corpo else "") + nuovo
            tomllib.loads(risultato)
            return risultato, esito
        testa, parte = sezioni[ultima]
        sezioni[ultima] = (testa, parte.rstrip("\n") + "\n\n")
        sezioni.insert(ultima + 1, (intestazione, nuovo + "\n"))
    risultato = "".join(p for _, p in sezioni).rstrip("\n") + "\n"
    tomllib.loads(risultato)
    return risultato, esito
