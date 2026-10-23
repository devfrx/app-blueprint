#!/usr/bin/env python3
"""Lo strumento della progettazione di app-blueprint: legge le sorgenti per id,
calcola ciò che non si scrive e verifica la coerenza.

Si esegue dalla radice del repo progettato (o con --radice):

  progetto.py inizia --progetto N --responsabile R   crea stato, chiusure e registri (voce 0.05)
  progetto.py stato                       lo stato a colpo d'occhio: scheda, registro, frontiera
  progetto.py apri <voce>                 inizio di un punto: lo registra e stampa il suo fascio
  progetto.py chiudi <voce> --evidenza E… fine di un punto: controlla e registra la chiusura
                [--non-applicabile --motivo M [--approvato A]] [--nota "…"] [--data AAAA-MM-GG]
  progetto.py approva <fase> --da NOME    fine di una fase: gate verde, approvazione nel registro
  progetto.py modifica <MOD-n>            applica una modifica approvata: riapre le fasi delle sue voci
  progetto.py congela --da NOME           Definition of Ready verde: congela l'incremento e chiude la 7.17
  progetto.py checklist [--fase N]        le voci con il loro stato; --dod, --trasversali, --tutte
  progetto.py mostra <id> [<id>…]         un elemento per intero, con chi lo cita
  progetto.py fascio <voce> [--modulo M]  ciò che serve leggere per lavorare una voce
  progetto.py fascio --task <id>          la fetta di progetto di un task di parallel-build
  progetto.py impatto <id>                tutto ciò che dipende da un elemento, anche indirettamente
  progetto.py formato [<tipo>]            il formato di un tipo di sorgente, con un esempio
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
import scrittura  # noqa: E402
import viste  # noqa: E402

CATALOGO = Path(__file__).resolve().parent.parent / "assets" / "checklist.toml"
ESEMPIO = Path(__file__).resolve().parent.parent / "assets" / "esempio"
# Dove vivono i tipi che l'esempio, congelato, non contiene.
SORGENTI_SENZA_ESEMPIO = {"domande": f"{modello.PROGETTAZIONE}/registri.toml",
                          "eventi": f"{modello.PROGETTAZIONE}/moduli/<modulo>.toml"}
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
    registro = controlli.righe_correnti(ctx)
    stati = controlli.stati_voci(ctx)
    righe.append(f"Registro dei gate (incremento {progetto.incremento_corrente()}; ↻ = fase che si ripete a ogni incremento):")
    for fase in catalogo.get("fasi", []):
        n = fase["numero"]
        voci = [st for st in stati.values() if st["fase"] == n]
        applicabili = [st for st in voci if st["applicabilita"] == condizioni.APPLICABILE]
        chiuse = sum(1 for st in applicabili if st["chiusa"])
        riga = registro.get(n, {})
        stato = riga.get("stato", "fuori-catena" if fase["skill"] == "fuori-catena" else "da-fare")
        ripete = "↻" if any(st["per_incremento"] for st in voci) else " "
        firma = f", approvato da {riga['approvato_da']} il {riga.get('data')}" if riga.get("approvato_da") else ""
        righe.append(f"  {n:>2}.{ripete}{fase['nome'][:44]:<44} {stato:<12} {chiuse}/{len(applicabili)} voci{firma}")
    riaperte = sorted((i for i, st in stati.items() if st["riaperta_da"]), key=condizioni.chiave_id)
    if riaperte:
        righe.append("Voci riaperte da modifiche: " + ", ".join(f"{i} ({stati[i]['riaperta_da']})" for i in riaperte))
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


# --- inizio ---------------------------------------------------------------------------------

INTESTAZIONI = {
    "stato.toml": "# Stato della progettazione: si legge a ogni avvio, quindi resta breve.\n"
                  "# Lo stato a colpo d'occhio lo stampa `progetto.py stato`.\n",
    "gate.toml": "# Chiusure delle voci dei gate: le scrive `progetto.py chiudi`. Le voci che il\n"
                 "# profilo esclude o rinvia le calcola lo script.\n",
    "registri.toml": "# Registri trasversali: rischi, assunzioni, domande, debito, deperibili,\n"
                     "# revisioni, modifiche. Formati: `progetto.py formato <tipo>`.\n",
}


def cmd_inizia(args):
    cartella = Path(args.radice) / modello.PROGETTAZIONE
    if (cartella / "stato.toml").exists():
        raise ErroreUso(f"'{cartella / 'stato.toml'}' esiste già: la progettazione è iniziata (progetto.py stato)")
    catalogo = modello.leggi_catalogo(args.catalogo)
    cartella.mkdir(parents=True, exist_ok=True)
    stato = INTESTAZIONI["stato.toml"] + f"\nmetodo = {scrittura.valore(catalogo.get('versione', ''))}\n\n"
    stato += scrittura.blocco("[scheda]", {"progetto": args.progetto, "responsabile": args.responsabile,
                                            "avvio": _oggi(args), "incremento": 1})
    stato += "\n" + scrittura.blocco("[corrente]", {"fase": 0, "punto": ""})
    (cartella / "stato.toml").write_text(stato, encoding="utf-8")
    for nome in ("gate.toml", "registri.toml"):
        if not (cartella / nome).exists():
            (cartella / nome).write_text(INTESTAZIONI[nome], encoding="utf-8")
    viste.scrivi(modello.carica(Path(args.radice), catalogo), catalogo)
    print(f"Progettazione di {args.progetto} iniziata in {modello.PROGETTAZIONE}/. Prossimo passo: progetto.py stato")
    return 0


# --- punti e fasi: apri, chiudi, approva --------------------------------------------------

def _percorso_stato(progetto):
    return progetto.radice / modello.PROGETTAZIONE / "stato.toml"


def _scrivi(percorso, intestazione, trova, campi):
    testo = percorso.read_text(encoding="utf-8") if percorso.exists() else ""
    nuovo, esito = scrittura.aggiorna_sezione(testo, intestazione, trova, campi)
    percorso.write_text(nuovo, encoding="utf-8")
    return esito


def _riga_registro(ctx, fase):
    """La riga del registro che vale ora per la fase, e come ritrovarla: una fase che si
    ripete ha una riga per incremento, le altre una sola."""
    corrente = ctx.progetto.incremento_corrente()
    ripete = any(st["per_incremento"] for st in controlli.stati_voci(ctx).values() if st["fase"] == fase)
    riga = controlli.righe_correnti(ctx).get(fase)
    if ripete:
        return riga, (lambda d: d.get("fase") == fase and d.get("incremento", 1) == corrente), {"incremento": corrente}
    return riga, (lambda d: d.get("fase") == fase), ({"incremento": riga["incremento"]} if riga and "incremento" in riga else {})


def _aggiorna_registro(ctx, fase, **campi):
    riga, trova, chiave = _riga_registro(ctx, fase)
    dati = {"fase": fase, **chiave}
    for nome in ("stato", "approvato_da", "data", "tag", "note"):
        valore = campi[nome] if nome in campi else (riga or {}).get(nome)
        if valore not in (None, ""):
            dati[nome] = valore
    return _scrivi(_percorso_stato(ctx.progetto), "[[registro]]", trova, dati)


def _oggi(args):
    if getattr(args, "data", None):
        try:
            return datetime.date.fromisoformat(args.data)
        except ValueError as e:
            raise ErroreUso(f"data non valida '{args.data}': AAAA-MM-GG") from e
    return datetime.date.today()


def cmd_apri(args):
    progetto, catalogo = _carica(args)
    ctx = _contesto(progetto, catalogo)
    ident = args.voce
    st = controlli.stati_voci(ctx).get(ident)
    if st is None:
        raise ErroreUso(f"voce '{ident}' sconosciuta")
    if st["applicabilita"] != condizioni.APPLICABILE:
        raise ErroreUso(f"voce {ident}: {st['applicabilita']} per la scheda, non si lavora")
    if st["chiusa"]:
        raise ErroreUso(f"voce {ident} chiusa il {st['chiusura'].get('data')}: riaprirla è una modifica, "
                        f"da registrare come MOD-n con riapre = [\"{ident}\"] (references/gate.md)")
    aperto = progetto.stato.get("corrente", {}).get("punto")
    if aperto and aperto != ident and not any(d.dati.get("punto") == aperto for d in progetto.tutti("domande")):
        raise ErroreUso(f"il punto {aperto} è aperto: chiudilo, o registra la domanda che lo blocca "
                        f"(Q-n con punto = \"{aperto}\")")
    stati = controlli.stati_voci(ctx)
    attese = [d for d in st["voce"].get("dipende", [])
              if not stati.get(d, {}).get("chiusa") and stati.get(d, {}).get("applicabilita") == condizioni.APPLICABILE]
    oggi = _oggi(args)
    _scrivi(_percorso_stato(progetto), "[corrente]", lambda d: True,
            {"fase": st["fase"], "punto": ident, "aperto_il": oggi})
    riga, _, _ = _riga_registro(ctx, st["fase"])
    stato_fase = (riga or {}).get("stato", "da-fare")
    if stato_fase in ("da-fare", "superato"):
        nota = f"riaperta: {st['riaperta_da'] or 'punto ' + ident}" if stato_fase == "superato" else None
        _aggiorna_registro(ctx, st["fase"], stato="in-corso" if stato_fase == "da-fare" else "riaperto",
                           approvato_da=None, data=None, tag=None, **({"note": nota} if nota else {}))
    print(f"Inizio punto {ident} — {st['voce']['testo']}")
    if attese:
        print(f"[avviso] dipende da voci ancora aperte: {', '.join(attese)}")
    print()
    print(fascio_voce(progetto, catalogo, ident))
    return 0


def cmd_chiudi(args):
    progetto, catalogo = _carica(args)
    viste.scrivi(progetto, catalogo)
    progetto = modello.carica(progetto.radice, catalogo)
    ctx = _contesto(progetto, catalogo)
    ident = args.voce
    st = controlli.stati_voci(ctx).get(ident)
    if st is None:
        raise ErroreUso(f"voce '{ident}' sconosciuta")
    chiusura = {"voce": ident}
    if st["per_incremento"]:
        chiusura["incremento"] = progetto.incremento_corrente()
    if args.non_applicabile:
        if not args.motivo:
            raise ErroreUso("un'esclusione ha il motivo: --motivo \"…\"")
        if args.evidenza:
            raise ErroreUso("un'esclusione non ha evidenze: o --evidenza, o --non-applicabile")
        chiusura.update(esito="non-applicabile", motivo=args.motivo, approvato=args.approvato)
    else:
        if not args.evidenza:
            raise ErroreUso("una voce fatta ha l'evidenza: --evidenza <percorso | id | tag:…>")
        chiusura.update(esito="fatto", evidenza=args.evidenza)
    chiusura["data"] = _oggi(args)
    chiusura["nota"] = args.nota
    chiusura = {k: v for k, v in chiusura.items() if v is not None}
    errori = [r for r in controlli.valida_chiusura(ctx, chiusura, scritta=False) if r.livello == "errore"]
    if errori:
        for r in errori:
            print(r.testo())
        print(f"\nLa voce {ident} non si chiude: {len(errori)} errori.")
        return 1
    ripete = st["per_incremento"]
    _scrivi(progetto.radice / modello.PROGETTAZIONE / "gate.toml", "[[chiusure]]",
            lambda d: d.get("voce") == ident and (not ripete or d.get("incremento") == chiusura.get("incremento")),
            chiusura)
    corrente = progetto.stato.get("corrente", {})
    if corrente.get("punto") == ident:
        _scrivi(_percorso_stato(progetto), "[corrente]", lambda d: True, {"fase": st["fase"], "punto": ""})
    progetto = modello.carica(progetto.radice, catalogo)
    viste.scrivi(progetto, catalogo)
    ctx = _contesto(progetto, catalogo)
    stati = controlli.stati_voci(ctx)
    prove = ", ".join(args.evidenza) if args.evidenza else f"non applicabile — {args.motivo}"
    print(f"Fine punto {ident} — {prove}")
    aperte = [i for i, s in stati.items() if s["fase"] == st["fase"]
              and s["applicabilita"] == condizioni.APPLICABILE and not s["chiusa"]]
    if not aperte:
        print(f"Fase {st['fase']}: voci tutte chiuse. Il gate si chiude con l'approvazione dell'utente: "
              f"progetto.py approva {st['fase']} --da <chi approva>")
    pronte = controlli.frontiera(ctx, limite=3)
    if pronte:
        print("Frontiera: " + "; ".join(f"{i} {stati[i]['voce']['testo'][:60]}" for i in pronte))
    return 0


def cmd_approva(args):
    progetto, catalogo = _carica(args)
    viste.scrivi(progetto, catalogo)
    progetto = modello.carica(progetto.radice, catalogo)
    ctx = _contesto(progetto, catalogo)
    fase = args.fase
    if fase not in {f["numero"] for f in catalogo.get("fasi", [])}:
        raise ErroreUso(f"fase '{fase}' sconosciuta")
    errori = [r for r in controlli.verifica(ctx, fase_gate=fase) if r.livello == "errore"]
    if errori:
        for r in errori:
            print(r.testo())
        print(f"\nIl gate {fase} non si approva: {len(errori)} errori.")
        return 1
    data = _oggi(args)
    tag = f"progettazione/gate-{fase}-{data.isoformat()}"
    campi = {"stato": "superato", "approvato_da": args.da, "data": data, "tag": tag}
    if args.note:
        campi["note"] = args.note
    _aggiorna_registro(ctx, fase, **campi)
    progetto = modello.carica(progetto.radice, catalogo)
    ctx = _contesto(progetto, catalogo)
    pronte = controlli.frontiera(ctx, limite=1)
    prossima = controlli.stati_voci(ctx)[pronte[0]]["fase"] if pronte else fase
    _scrivi(_percorso_stato(progetto), "[corrente]", lambda d: True, {"fase": prossima, "punto": ""})
    viste.scrivi(modello.carica(progetto.radice, catalogo), catalogo)
    print(f"Fine fase {fase} — approvata da {args.da} il {data}.")
    print(f"Dopo il commit: git tag -a {tag} -m \"Gate {fase} superato\"")
    return 0


def cmd_modifica(args):
    progetto, catalogo = _carica(args)
    ctx = _contesto(progetto, catalogo)
    m = progetto.trova("modifiche", args.id)
    if m is None:
        raise ErroreUso(f"modifica '{args.id}' sconosciuta: si registra prima in registri.toml")
    errori = [r for r in controlli.c_modifiche(ctx, None) if r.dove == m.id]
    if m.dati.get("esito") != "approvata":
        errori.append(modello.Reperto("errore", m.id, "si applica solo una modifica approvata", "modifiche"))
    stati = controlli.stati_voci(ctx)
    ignote = [v for v in modello._valori(m.dati.get("riapre")) if v not in stati]
    if ignote:
        errori.append(modello.Reperto("errore", m.id, f"voci sconosciute in riapre: {ignote}", "modifiche"))
    if errori:
        for r in errori:
            print(r.testo())
        return 1
    voci = modello._valori(m.dati.get("riapre"))
    riaperte = []
    fasi = {stati[v]["fase"] for v in voci} | {st["fase"] for st in stati.values() if st["riaperta_da"] == m.id}
    for fase in sorted(fasi):
        riga, _, _ = _riga_registro(ctx, fase)
        if riga and riga.get("stato") == "superato":
            nota = f"riaperta da {m.id} (superata il {riga.get('data')}, approvata da {riga.get('approvato_da')})"
            _aggiorna_registro(ctx, fase, stato="riaperto", approvato_da=None, data=None, tag=None, note=nota)
            riaperte.append(fase)
    progetto = modello.carica(progetto.radice, catalogo)
    viste.scrivi(progetto, catalogo)
    print(f"Modifica {m.id} applicata: voci riaperte {', '.join(voci)}; "
          f"fasi riaperte: {', '.join(map(str, riaperte)) or 'nessuna'}.")
    return 0


def cmd_congela(args):
    progetto, catalogo = _carica(args)
    viste.scrivi(progetto, catalogo)
    progetto = modello.carica(progetto.radice, catalogo)
    data = _oggi(args)
    ctx = _contesto(progetto, catalogo, congelamento=data)
    voce = next(v["id"] for v in catalogo.get("voci", []) if "congelamento" in v.get("controllo", []))
    errori = [r for r in controlli.verifica(ctx, al_congelamento=True) if r.livello == "errore" and r.dove != voce]
    if errori:
        for r in errori:
            print(r.testo())
        print(f"\nL'incremento non si congela: {len(errori)} errori alla Definition of Ready del {data}.")
        return 1
    corrente = progetto.incremento_corrente()

    def ultima(tipo):
        revisioni = [r for r in progetto.tutti("revisioni")
                     if r.dati.get("tipo") == tipo and r.dati.get("incremento") == corrente]
        return max(revisioni, key=lambda r: str(r.dati.get("data"))).id

    tag = controlli.tag_congelamento(corrente, data)
    _scrivi(_percorso_stato(progetto), "[congelamento]", lambda d: True,
            {"incremento": corrente, "data": data, "approvato_da": args.da, "tag": tag,
             "revisione": ultima("prontezza"), "prova": ultima("decidibilita")})
    progetto = modello.carica(progetto.radice, catalogo)
    ctx = _contesto(progetto, catalogo, congelamento=data)
    chiusura = {"voce": voce, "incremento": corrente, "esito": "fatto",
                "evidenza": ["stato.toml#congelamento"], "data": data}
    errori = [r for r in controlli.valida_chiusura(ctx, chiusura, scritta=False) if r.livello == "errore"]
    if errori:
        for r in errori:
            print(r.testo())
        return 1
    _scrivi(progetto.radice / modello.PROGETTAZIONE / "gate.toml", "[[chiusure]]",
            lambda d: d.get("voce") == voce and d.get("incremento") == corrente, chiusura)
    if progetto.stato.get("corrente", {}).get("punto") == voce:
        _scrivi(_percorso_stato(progetto), "[corrente]", lambda d: True, {"fase": 7, "punto": ""})
    progetto = modello.carica(progetto.radice, catalogo)
    viste.scrivi(progetto, catalogo)
    print(f"Incremento {corrente} congelato il {data}, approvato da {args.da}.")
    print(f"Dopo il commit: git tag -a {tag} -m \"Progetto dell'incremento {corrente} congelato\"")
    pronte = controlli.frontiera(_contesto(progetto, catalogo), limite=3)
    stati = controlli.stati_voci(_contesto(progetto, catalogo))
    if pronte:
        print("Frontiera: " + "; ".join(f"{i} [{stati[i]['skill']}]" for i in pronte))
    return 0


# --- checklist ----------------------------------------------------------------------------

def cmd_checklist(args):
    progetto, catalogo = _carica(args)
    ctx = _contesto(progetto, catalogo)
    scheda = condizioni.profilo(progetto.scheda)
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
    info = next((f for f in catalogo.get("fasi", []) if f["numero"] == fase), None)
    if info and not args.tutte:
        print(f"Fase {fase} — {info['nome']} ({info['skill']})\nGate: {info['gate']}\n")
    for ident in sorted(stati, key=condizioni.chiave_id):
        st = stati[ident]
        if not args.tutte and st["fase"] != fase:
            continue
        if st["applicabilita"] != condizioni.APPLICABILE:
            stato = st["applicabilita"]
        elif st["chiusa"]:
            stato = "fatta" if st["chiusura"].get("esito") == "fatto" else "esclusa"
        elif st["riaperta_da"]:
            stato = f"riaperta {st['riaperta_da']}"
        else:
            stato = "aperta"
        ripete = "↻" if st["per_incremento"] else " "
        print(f"{ident:<7}{ripete} {stato:<15} {st['voce']['testo']}")
        if args.dettagli and not st["chiusa"] and st["applicabilita"] == condizioni.APPLICABILE:
            v = st["voce"]
            print(f"         dove: {v.get('dove', '')}; dipende: {', '.join(v.get('dipende', [])) or '—'}; "
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


def cmd_formato(args):
    """Il formato di ogni tipo, ricavato dalle regole dello script e dall'esempio: la
    documentazione dei formati è il codice che li controlla, non un testo a parte."""
    catalogo = modello.leggi_catalogo(args.catalogo)
    esempio = modello.carica(ESEMPIO, catalogo)
    tipi = sorted(set(controlli.CAMPI) | {"adr"})
    if not args.tipo:
        print("Tipi di sorgente (progetto.py formato <tipo> per il dettaglio):")
        for tipo in tipi:
            elementi = esempio.tutti(tipo)
            sorgente = elementi[0].sorgente if elementi else SORGENTI_SENZA_ESEMPIO.get(tipo, "?")
            print(f"  {tipo:<18} {sorgente}")
        return 0
    tipo = args.tipo
    if tipo not in tipi:
        raise ErroreUso(f"tipo '{tipo}' sconosciuto: progetto.py formato elenca i tipi")
    elementi = sorted(esempio.tutti(tipo), key=lambda e: viste._chiave_naturale(e.id))
    sorgente = elementi[0].sorgente if elementi else SORGENTI_SENZA_ESEMPIO.get(tipo, "?")
    prefisso = next((k for k, v in modello.PREFISSI.items() if v == tipo), None)
    tipizzato = next((k for k, v in modello.TIPIZZATI.items() if v == tipo), None)
    if prefisso:
        forma = f"{prefisso}-n, citato così da ogni campo"
    elif tipo == "storie":
        forma = "<AREA>-n, con il prefisso di un'area di [[aree]]"
    elif tipo in modello.CONTENITORE:
        forma = f"<{modello.CONTENITORE[tipo]}>.<nome>, citato come \"{tipizzato or tipo}:<id>\""
    else:
        forma = f"slug in minuscolo, citato come \"{tipizzato}:<id>\"" if tipizzato else "slug in minuscolo"
    obbligatori, ammessi = controlli.CAMPI.get(tipo, ((), {}))
    righe = [f"## {tipo} — {sorgente}", f"id: {forma}",
             f"obbligatori: {', '.join(obbligatori) or '—'}"]
    for campo, valori in ammessi.items():
        righe.append(f"valori di {campo}: {', '.join(sorted(valori))}")
    riferimenti = modello.RIFERIMENTI.get(tipo, {})
    if riferimenti:
        righe.append("riferimenti: " + "; ".join(f"{c} → {a or 'id prefissati o tipo:id'}" for c, a in riferimenti.items()))
    righe += ["", "Esempio da assets/esempio:" if elementi else "Nessun esempio: l'esempio è congelato senza."]
    if elementi:
        righe.append(rendi(esempio, elementi[0]))
    print("\n".join(righe))
    return 0


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
    ini = sotto.add_parser("inizia")
    ini.add_argument("--progetto", required=True)
    ini.add_argument("--responsabile", required=True)
    ini.add_argument("--data", help=argparse.SUPPRESS)
    ini.set_defaults(funzione=cmd_inizia)
    sotto.add_parser("stato").set_defaults(funzione=cmd_stato)
    a = sotto.add_parser("apri")
    a.add_argument("voce")
    a.add_argument("--data", help=argparse.SUPPRESS)
    a.set_defaults(funzione=cmd_apri)
    ch = sotto.add_parser("chiudi")
    ch.add_argument("voce")
    ch.add_argument("--evidenza", nargs="+")
    ch.add_argument("--non-applicabile", action="store_true")
    ch.add_argument("--motivo")
    ch.add_argument("--approvato")
    ch.add_argument("--nota", help="una riga che spiega l'evidenza")
    ch.add_argument("--data")
    ch.set_defaults(funzione=cmd_chiudi)
    ap = sotto.add_parser("approva")
    ap.add_argument("fase", type=int)
    ap.add_argument("--da", required=True)
    ap.add_argument("--note")
    ap.add_argument("--data", help=argparse.SUPPRESS)
    ap.set_defaults(funzione=cmd_approva)
    mo = sotto.add_parser("modifica")
    mo.add_argument("id")
    mo.set_defaults(funzione=cmd_modifica)
    co = sotto.add_parser("congela")
    co.add_argument("--da", required=True)
    co.add_argument("--data", help=argparse.SUPPRESS)
    co.set_defaults(funzione=cmd_congela)
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
    fo = sotto.add_parser("formato")
    fo.add_argument("tipo", nargs="?")
    fo.set_defaults(funzione=cmd_formato)
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
