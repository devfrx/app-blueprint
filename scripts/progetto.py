#!/usr/bin/env python3
"""Lo strumento della progettazione di app-blueprint: legge le sorgenti per id,
calcola ciò che non si scrive e verifica la coerenza.

Si esegue dalla radice del repo progettato (o con --radice):

  progetto.py stato                       lo stato a colpo d'occhio: scheda, registro, frontiera
  progetto.py checklist [--fase N]        le voci con il loro stato; --dod, --trasversali, --tutte
  progetto.py mostra <id> [<id>…]         un elemento per intero, con chi lo cita
  progetto.py fascio <voce> [--modulo M]  ciò che serve leggere per lavorare una voce
  progetto.py fascio --task <id>          la fetta di progetto di un task di parallel-build
  progetto.py impatto <id>                tutto ciò che dipende da un elemento, anche indirettamente
  progetto.py viste                       rigenera le viste in docs/progettazione/viste/
  progetto.py verifica [--gate N] [--congelamento [AAAA-MM-GG]] [--json]

Esito: 0 nessun errore (gli avvisi non bloccano); 1 errori; 2 errore d'uso.
Le misure di dimensione sono in caratteri: per i token serve il conteggio di
lean-docs (scripts/misura.py --modello), se la policy del progetto lo consente.
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import condizioni  # noqa: E402
import controlli  # noqa: E402
import modello  # noqa: E402
import piano as modulo_piano  # noqa: E402
import viste  # noqa: E402

CATALOGO = Path(__file__).resolve().parent.parent / "assets" / "checklist.toml"
# Budget di dimensione, in caratteri: oltre, una sorgente si spezza (storie per
# area, un file per modulo) e un fascio segnala un modulo troppo grande.
BUDGET_STATO = 6_000
BUDGET_SORGENTE = 40_000
BUDGET_FASCIO = 60_000


class ErroreUso(Exception):
    pass


def _carica(args):
    radice = Path(args.radice)
    if not (radice / modello.PROGETTAZIONE / "stato.toml").exists():
        raise ErroreUso(f"'{radice / modello.PROGETTAZIONE / 'stato.toml'}' non esiste: "
                        "esegui dalla radice del repo progettato, o inizializza lo stato (voce 0.05)")
    catalogo = modello.leggi_catalogo(args.catalogo)
    progetto = modello.carica(radice, catalogo)
    return progetto, catalogo


def _contesto(progetto, catalogo, congelamento=None):
    if congelamento is None:
        c = progetto.stato.get("congelamento")
        if isinstance(c, dict) and isinstance(c.get("data"), datetime.date):
            congelamento = c["data"]
    return controlli.Contesto(progetto, catalogo, congelamento=congelamento)


# --- stato --------------------------------------------------------------------------------

def cmd_stato(args):
    progetto, catalogo = _carica(args)
    ctx = _contesto(progetto, catalogo)
    s = progetto.scheda
    righe = [f"{s.get('progetto', '?')} — esposizione {s.get('esposizione', '?')}, criticità {s.get('criticita', '?')}, "
             f"inneschi: {', '.join(s.get('inneschi', [])) or 'nessuno'}",
             f"Verdetto {s.get('verdetto', '?')}, incremento {s.get('incremento', '?')}, "
             f"costruzione {s.get('costruzione', 'da decidere')}"]
    corrente = progetto.stato.get("corrente", {})
    if corrente.get("punto"):
        voce = progetto.trova("voci", corrente["punto"])
        testo = voce.dati["testo"] if voce else "?"
        righe.append(f"Punto aperto: {corrente['punto']} — {testo} (dal {corrente.get('aperto_il', '?')})")
    else:
        righe.append(f"Fase corrente: {corrente.get('fase', '?')}, nessun punto aperto")
    registro = {r.get("fase"): r for r in progetto.stato.get("registro", [])}
    stati = controlli.stati_voci(ctx)
    righe.append("Registro dei gate:")
    for fase in catalogo.get("fasi", []):
        n = fase["numero"]
        voci = [st for st in stati.values() if st["fase"] == n]
        applicabili = [st for st in voci if st["applicabilita"] == condizioni.APPLICABILE]
        chiuse = sum(1 for st in applicabili if st["chiusa"])
        riga = registro.get(n, {})
        stato = riga.get("stato", "fuori-catena" if fase["skill"] == "fuori-catena" else "da-fare")
        firma = f", approvato da {riga['approvato_da']} il {riga.get('data')}" if riga.get("approvato_da") else ""
        righe.append(f"  {n:>2}. {fase['nome'][:44]:<44} {stato:<12} {chiuse}/{len(applicabili)} voci{firma}")
    pronte = controlli.frontiera(ctx, limite=5)
    if pronte:
        righe.append("Frontiera (voci pronte):")
        for ident in pronte:
            skill = stati[ident]["skill"]
            chi = f" [{skill}]" if skill != "app-blueprint" else ""
            righe.append(f"  {ident}{chi} {stati[ident]['voce']['testo']}")
    domande = progetto.tutti("domande")
    if domande:
        righe.append(f"Domande aperte: {', '.join(d.id for d in domande)}")
    for m in progetto.stato.get("mappe", []):
        righe.append(f"Mappa di decision-map aperta dal punto {m.get('punto')}: {m.get('link')}")
    rinviate = sum(1 for st in stati.values() if st["applicabilita"] == condizioni.RINVIATA)
    if rinviate:
        righe.append(f"Debito di pubblicazione: {rinviate} voci (viste/debito-pubblicazione.md)")
    reperti = controlli.verifica(ctx)
    errori = sum(1 for r in reperti if r.livello == "errore")
    avvisi = len(reperti) - errori
    righe.append(f"Verifica: {errori} errori, {avvisi} avvisi (progetto.py verifica per il dettaglio)")
    peso = len((progetto.radice / modello.PROGETTAZIONE / "stato.toml").read_text(encoding="utf-8"))
    if peso > BUDGET_STATO:
        righe.append(f"Attenzione: stato.toml pesa {peso} caratteri, oltre {BUDGET_STATO}: va letto a ogni avvio")
    print("\n".join(righe))
    return 0


# --- checklist ----------------------------------------------------------------------------

def cmd_checklist(args):
    progetto, catalogo = _carica(args)
    ctx = _contesto(progetto, catalogo)
    scheda = {"esposizione": progetto.scheda.get("esposizione", "personale"),
              "criticita": progetto.scheda.get("criticita", "bassa"),
              "inneschi": progetto.scheda.get("inneschi", [])}
    noti = set(catalogo.get("inneschi", {}))
    if args.dod or args.trasversali:
        chiave = "dod" if args.dod else "trasversali"
        for voce in catalogo.get(chiave, []):
            st = condizioni.stato_voce(voce, scheda, inneschi_noti=noti)
            livello = f" [{voce['livello']}]" if voce.get("livello") else ""
            nota = f" — {voce['nota']}" if voce.get("nota") else ""
            print(f"{voce['id']}{livello} {st:<15} {voce['testo']}{nota}")
        return 0
    stati = controlli.stati_voci(ctx)
    fase = args.fase if args.fase is not None else progetto.stato.get("corrente", {}).get("fase")
    for ident in sorted(stati, key=condizioni.chiave_id):
        st = stati[ident]
        if not args.tutte and st["fase"] != fase:
            continue
        if st["applicabilita"] != condizioni.APPLICABILE:
            stato = st["applicabilita"]
        elif st["chiusa"]:
            stato = "fatta" if st["chiusura"].get("esito") == "fatto" else "esclusa"
        else:
            stato = "aperta"
        print(f"{ident:<7} {stato:<15} {st['voce']['testo']}")
        if args.dettagli and stato == "aperta":
            v = st["voce"]
            print(f"        dove: {v.get('dove', '')}; dipende: {', '.join(v.get('dipende', [])) or '—'}; "
                  f"controllo: {', '.join(v.get('controllo', [])) or '—'}")
    return 0


# --- mostra, fascio, impatto ----------------------------------------------------------------

def _trova(progetto, ident):
    """Trova un elemento per id, con o senza tipo esplicito ("entita:fattura")."""
    risolto = progetto.risolvi(ident)
    if risolto:
        return [progetto.trova(*risolto)]
    return [g[ident] for g in progetto.elementi.values() if ident in g]


def rendi(progetto, el, completo=True):
    righe = [f"### {el.tipo} {el.id}  ({el.sorgente}; incremento {progetto.incremento_di(el)})"]
    for chiave, valore in el.dati.items():
        if chiave.startswith("_") and chiave != "_corpo":
            continue
        if chiave == "_corpo":
            if completo:
                righe.append(valore.strip())
            continue
        if el.tipo == "api" and chiave not in ("x-modulo", "x-storie", "x-errori", "summary"):
            continue
        righe.append(_rendi_campo(chiave, valore))
    if el.tipo == "api" and completo:
        dati = {k: v for k, v in el.dati.items() if not k.startswith("_")}
        righe.append(f"  {el.dati.get('_metodo', '').upper()} {el.dati.get('_percorso', '')}")
        righe.append("```json\n" + json.dumps(dati, ensure_ascii=False, indent=1) + "\n```")
    return "\n".join(righe)


def _rendi_campo(chiave, valore):
    if isinstance(valore, list) and valore and all(isinstance(x, dict) for x in valore):
        sotto = [f"  {chiave}:"]
        for x in valore:
            sotto.append("    - " + "; ".join(f"{k}={_breve(v)}" for k, v in x.items()))
        return "\n".join(sotto)
    if isinstance(valore, dict):
        return f"  {chiave}: " + "; ".join(f"{k}={_breve(v)}" for k, v in valore.items())
    return f"  {chiave}: {_breve(valore)}"


def _breve(valore):
    if isinstance(valore, list):
        return "[" + ", ".join(_breve(v) for v in valore) + "]"
    if isinstance(valore, dict):
        return "{" + ", ".join(f"{k}={_breve(v)}" for k, v in valore.items()) + "}"
    return str(valore)


def cmd_mostra(args):
    progetto, catalogo = _carica(args)
    entranti = progetto.entranti()
    esito = 0
    for ident in args.id:
        trovati = _trova(progetto, ident)
        if not trovati:
            print(f"'{ident}': nessun elemento con questo id")
            esito = 1
            continue
        for el in trovati:
            print(rendi(progetto, el))
            if el.tipo == "voci":
                for c in progetto.chiusure:
                    if c.get("voce") == el.id:
                        print(_rendi_campo("chiusura", c))
            citato = entranti.get((el.tipo, el.id), [])
            if citato:
                print("  citato da: " + ", ".join(f"{t} {i} ({campo})" for t, i, campo in sorted(citato)))
            print()
    return esito


def _legato_al_modulo(progetto, el, modulo):
    d = el.dati
    if el.contenitore == modulo or d.get("modulo") == modulo or d.get("x-modulo") == modulo:
        return True
    if modulo in modello._valori(d.get("tocca")) or modulo in (d.get("a_valle"), d.get("a_monte")):
        return True
    if el.tipo in ("entita",) and d.get("modulo") == modulo:
        return True
    if el.tipo == "matrice":
        entita = progetto.trova("entita", d.get("risorsa"))
        return bool(entita and entita.dati.get("modulo") == modulo)
    if el.tipo == "storie":
        return d.get("modulo") == modulo
    return False


def _misura(testo):
    return f"{len(testo)} caratteri"


def cmd_fascio(args):
    progetto, catalogo = _carica(args)
    if args.task:
        testo = fascio_task(progetto, args.task)
    elif args.voce:
        testo = fascio_voce(progetto, catalogo, args.voce, args.modulo)
    else:
        raise ErroreUso("indica una voce o --task <id>")
    print(testo)
    if len(testo) > BUDGET_FASCIO:
        print(f"\n[avviso] fascio di {_misura(testo)}, oltre {BUDGET_FASCIO}: restringi con --modulo, "
              "o il modulo è troppo grande per un task", file=sys.stderr)
    return 0


def fascio_voce(progetto, catalogo, ident, modulo=None):
    voce = next((v for v in catalogo.get("voci", []) if v["id"] == ident), None)
    if voce is None:
        raise ErroreUso(f"voce '{ident}' sconosciuta")
    righe = [f"## Voce {ident} — {voce['testo']}", f"Dove: {voce.get('dove', '')}"]
    if voce.get("nota"):
        righe.append(f"Nota: {voce['nota']}")
    if voce.get("controllo"):
        righe.append(f"Controlli per chiuderla: {', '.join(voce['controllo'])}")
    for tipo in voce.get("legge", []):
        elementi = progetto.tutti(tipo)
        if tipo == "scheda":
            righe += ["", "## scheda", _rendi_campo("scheda", progetto.scheda)]
            continue
        if modulo:
            elementi = [e for e in elementi if _legato_al_modulo(progetto, e, modulo)]
        righe += ["", f"## {tipo} ({len(elementi)})"]
        for el in sorted(elementi, key=lambda e: viste._chiave_naturale(e.id)):
            righe.append(rendi(progetto, el, completo=False))
    testo = "\n".join(righe)
    return testo + f"\n\n— {_misura(testo)}"


def fascio_task(progetto, ident):
    """Ciò che un task deve leggere, assemblato dalle sorgenti: è la parte specifica del
    brief di parallel-build. Le regole comuni e la procedura sono di parallel-build."""
    t = progetto.trova("task", ident)
    if t is None:
        raise ErroreUso(f"task '{ident}' sconosciuto")
    d = t.dati
    modulo = d.get("modulo")
    corrente = progetto.incremento_corrente()
    righe = [f"# Fascio del task {ident}", "", rendi(progetto, t)]
    storie_ids = set(modello._valori(d.get("storie")))
    if modulo:
        storie_ids |= {s.id for s in progetto.tutti("storie")
                       if s.dati.get("modulo") == modulo and s.dati.get("incremento") == corrente}
        m = progetto.trova("moduli", modulo)
        if m:
            righe += ["", "## Modulo", rendi(progetto, m)]
        det = progetto.trova("dettaglio", modulo)
        if det:
            righe += ["", "## Progetto di dettaglio", rendi(progetto, det)]
    storie = [progetto.trova("storie", s) for s in sorted(storie_ids, key=viste._chiave_naturale)]
    storie = [s for s in storie if s]
    if storie:
        righe += ["", "## Storie"] + [rendi(progetto, s) for s in storie]
    entita_ids = {e.id for e in progetto.tutti("entita") if modulo and e.dati.get("modulo") == modulo}
    entita_ids |= {x for s in storie for x in modello._valori(s.dati.get("entita"))} if not modulo else set()
    if entita_ids:
        righe += ["", "## Entità"] + [rendi(progetto, progetto.trova("entita", e)) for e in sorted(entita_ids)]
        macchine = [m for m in progetto.tutti("macchine") if m.dati.get("entita") in entita_ids]
        if macchine:
            righe += ["", "## Macchine a stati (le transizioni non elencate sono vietate)"]
            righe += [rendi(progetto, m) for m in macchine]
        regole = [r for r in progetto.tutti("regole") if set(modello._valori(r.dati.get("entita"))) & entita_ids]
        if regole:
            righe += ["", "## Regole"] + [rendi(progetto, r) for r in regole]
    futuri = []
    if modulo:
        tabelle = [x for x in progetto.tutti("tabelle") if x.dati.get("modulo") == modulo and progetto.incremento_di(x) <= corrente]
        if tabelle:
            righe += ["", "## Tabelle (contracts/schema.toml), solo ciò che serve a questo incremento"]
            righe += [_rendi_tabella(progetto, x, corrente, futuri) for x in tabelle]
        for e in progetto.tutti("attributi"):
            contenitore = progetto.trova("entita", e.contenitore)
            if contenitore and contenitore.dati.get("modulo") == modulo and progetto.incremento_di(e) > corrente:
                futuri.append(f"attributo {e.id} (incremento {progetto.incremento_di(e)})")
        operazioni = [o for o in progetto.tutti("api") if o.dati.get("x-modulo") == modulo and progetto.incremento_di(o) <= corrente]
        if operazioni:
            righe += ["", "## Operazioni API (contracts/openapi.json)"] + [rendi(progetto, o) for o in operazioni]
        usati = sorted(x.dati.get("a_monte") for x in progetto.tutti("dipendenze") if x.dati.get("a_valle") == modulo)
        facciate = [f for f in progetto.tutti("facciata") if f.contenitore in usati]
        if facciate:
            righe += ["", "## Facciate di altri moduli che puoi usare (negli stub dello scheletro; la semantica è questa)"]
            righe += [rendi(progetto, f) for f in facciate]
        eventi = [e for e in progetto.tutti("eventi") if modulo in modello._valori(e.dati.get("consumatori"))]
        if eventi:
            righe += ["", "## Eventi che consumi"] + [rendi(progetto, e) for e in eventi]
        regole_matrice = [r for r in progetto.tutti("matrice") if _legato_al_modulo(progetto, r, modulo)]
        if regole_matrice:
            righe += ["", "## Matrice delle autorizzazioni (negazione per default)"] + [rendi(progetto, r) for r in regole_matrice]
        codici = {c for o in operazioni for c in modello._valori(o.dati.get("x-errori"))}
        codici |= {c for f in progetto.tutti("facciata") if f.contenitore == modulo for c in modello._valori(f.dati.get("errori"))}
        if codici:
            righe += ["", "## Errori del catalogo"] + [rendi(progetto, progetto.trova("errori", c)) for c in sorted(codici)
                                                      if progetto.trova("errori", c)]
    schermate = [s for s in progetto.tutti("schermate") if set(modello._valori(s.dati.get("storie"))) & storie_ids]
    if schermate and d.get("agente") in ("frontend-builder", "test-author", "sessione"):
        righe += ["", "## Schermate (con i nomi accessibili che gli oracoli cercano)"] + [rendi(progetto, s) for s in schermate]
        chiavi = {k for s in schermate for k in modello._valori(s.dati.get("testi"))}
        testi = [progetto.trova("testi", k) for k in sorted(chiavi)]
        if any(testi):
            righe += ["", "## Testi"] + [rendi(progetto, x) for x in testi if x]
    if not modulo:
        percorsi = [p for p in progetto.tutti("percorsi") if set(modello._valori(p.dati.get("storie"))) <= storie_ids
                    and set(modello._valori(p.dati.get("storie"))) & storie_ids]
        for pc in percorsi:
            righe += ["", "## Percorso critico", rendi(progetto, pc)]
            sequenza = progetto.trova("sequenze", pc.id)
            if sequenza:
                righe += [rendi(progetto, sequenza)]
    if d.get("ondata") == "oracoli":
        livelli = progetto.tutti("livelli")
        if livelli:
            righe += ["", "## Strategia di test"] + [rendi(progetto, x) for x in livelli]
    citate = sorted({v for riga in righe for v in modello.RE_STRATEGIA.findall(riga)})
    strategie = [progetto.trova("strategie", c) for c in citate]
    if any(strategie):
        righe += ["", "## Strategie trasversali citate"] + [rendi(progetto, x) for x in strategie if x]
    if futuri:
        righe += ["", "## Progettato per incrementi futuri: non costruire ora",
                  "Esiste nel progetto perché gli schemi reggano le funzionalità future; "
                  "lo costruirà l'incremento indicato."] + [f"- {f}" for f in sorted(futuri)]
    testo = "\n".join(righe)
    return testo + f"\n\n— {_misura(testo)}"


def _rendi_tabella(progetto, tabella, corrente, futuri):
    """Una tabella con le sole colonne e i soli indici dell'incremento corrente; il
    resto finisce nell'elenco del progettato per gli incrementi futuri."""
    dati = dict(tabella.dati)
    tenute = []
    for c in dati.get("colonne", []):
        col = progetto.trova("colonne", f"{tabella.id}.{c.get('nome')}") if isinstance(c, dict) else None
        if col and progetto.incremento_di(col) > corrente:
            futuri.append(f"colonna {col.id} (incremento {progetto.incremento_di(col)})")
        else:
            tenute.append(c)
    dati["colonne"] = tenute
    indici = []
    for i in dati.get("indici", []) or []:
        ind = progetto.trova("indici", i.get("nome")) if isinstance(i, dict) else None
        if ind and progetto.incremento_di(ind) > corrente:
            futuri.append(f"indice {ind.id} (incremento {progetto.incremento_di(ind)})")
        else:
            indici.append(i)
    if "indici" in dati:
        dati["indici"] = indici
    copia = modello.Elemento(tabella.tipo, tabella.id, dati, tabella.sorgente, tabella.contenitore)
    return rendi(progetto, copia)


def cmd_impatto(args):
    progetto, catalogo = _carica(args)
    entranti = progetto.entranti()
    trovati = _trova(progetto, args.id)
    if not trovati:
        print(f"'{args.id}': nessun elemento con questo id")
        return 1
    radice = trovati[0]
    visti, coda, livelli = {(radice.tipo, radice.id)}, [((radice.tipo, radice.id), 0)], []
    while coda:
        nodo, profondita = coda.pop(0)
        if profondita >= args.profondita:
            continue
        for tipo, ident, campo in sorted(entranti.get(nodo, [])):
            if (tipo, ident) not in visti:
                visti.add((tipo, ident))
                livelli.append((profondita + 1, tipo, ident, campo, nodo))
                coda.append(((tipo, ident), profondita + 1))
    if not livelli:
        print(f"Nessun elemento dipende da {radice.tipo} {radice.id}.")
        return 0
    print(f"Dipendono da {radice.tipo} {radice.id}:")
    for profondita, tipo, ident, campo, da in livelli:
        print(f"{'  ' * profondita}{tipo} {ident} (campo {campo} → {da[1]})")
    return 0


# --- viste e verifica ---------------------------------------------------------------------

def cmd_viste(args):
    progetto, catalogo = _carica(args)
    scritte = viste.scrivi(progetto, catalogo)
    print("\n".join(f"aggiornata: {s}" for s in scritte) or "viste già aggiornate")
    return 0


def cmd_verifica(args):
    progetto, catalogo = _carica(args)
    congelamento = None
    if args.congelamento is not None:
        if args.congelamento == "stato":
            c = progetto.stato.get("congelamento")
            congelamento = c.get("data") if isinstance(c, dict) else None
            if not isinstance(congelamento, datetime.date):
                raise ErroreUso("[congelamento].data assente in stato.toml: passa la data, --congelamento AAAA-MM-GG")
        else:
            try:
                congelamento = datetime.date.fromisoformat(args.congelamento)
            except ValueError as e:
                raise ErroreUso(f"data non valida '{args.congelamento}': AAAA-MM-GG") from e
    ctx = _contesto(progetto, catalogo, congelamento)
    reperti = controlli.verifica(ctx, fase_gate=args.gate, al_congelamento=args.congelamento is not None)
    for relativo, testo in progetto.testi.items():
        if relativo.startswith(modello.PROGETTAZIONE) and "/viste/" not in relativo and len(testo) > BUDGET_SORGENTE:
            reperti.append(modello.Reperto("avviso", relativo, f"{len(testo)} caratteri, oltre {BUDGET_SORGENTE}: "
                                           "spezzalo (storie per area, un file per modulo)", "budget"))
    errori = [r for r in reperti if r.livello == "errore"]
    avvisi = [r for r in reperti if r.livello == "avviso"]
    if args.json:
        print(json.dumps({"errori": [r.__dict__ for r in errori], "avvisi": [r.__dict__ for r in avvisi],
                          "conteggi": modulo_piano.conteggi(progetto) if progetto.piano else {}},
                         ensure_ascii=False, indent=1, default=str))
    else:
        for r in errori + avvisi:
            print(r.testo())
        bersaglio = f" per il gate {args.gate}" if args.gate is not None else ""
        bersaglio += f" al congelamento del {congelamento}" if congelamento else ""
        print(f"\n{len(errori)} errori, {len(avvisi)} avvisi{bersaglio}.")
    return 1 if errori else 0


def principale(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--radice", default=".", help="radice del repo progettato")
    parser.add_argument("--catalogo", default=str(CATALOGO), help=argparse.SUPPRESS)
    sotto = parser.add_subparsers(dest="comando", required=True)
    sotto.add_parser("stato").set_defaults(funzione=cmd_stato)
    c = sotto.add_parser("checklist")
    c.add_argument("--fase", type=int)
    c.add_argument("--tutte", action="store_true")
    c.add_argument("--dod", action="store_true")
    c.add_argument("--trasversali", action="store_true")
    c.add_argument("--dettagli", action="store_true")
    c.set_defaults(funzione=cmd_checklist)
    m = sotto.add_parser("mostra")
    m.add_argument("id", nargs="+")
    m.set_defaults(funzione=cmd_mostra)
    f = sotto.add_parser("fascio")
    f.add_argument("voce", nargs="?")
    f.add_argument("--modulo")
    f.add_argument("--task")
    f.set_defaults(funzione=cmd_fascio)
    i = sotto.add_parser("impatto")
    i.add_argument("id")
    i.add_argument("--profondita", type=int, default=2, help="livelli di dipendenza indiretta (default 2)")
    i.set_defaults(funzione=cmd_impatto)
    sotto.add_parser("viste").set_defaults(funzione=cmd_viste)
    v = sotto.add_parser("verifica")
    v.add_argument("--gate", type=int)
    v.add_argument("--congelamento", nargs="?", const="stato")
    v.add_argument("--json", action="store_true")
    v.set_defaults(funzione=cmd_verifica)
    args = parser.parse_args(argv)
    try:
        return args.funzione(args)
    except (ErroreUso, condizioni.CondizioneNonValida, FileNotFoundError) as e:
        print(f"errore d'uso: {e}", file=sys.stderr)
        return 2
    except BrokenPipeError:
        # l'output è finito in un comando come head: non è un errore
        sys.stderr.close()
        return 0


if __name__ == "__main__":
    sys.exit(principale())
