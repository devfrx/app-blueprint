"""Le viste generate: ciò che si può derivare dalle sorgenti non si scrive a mano.

Una vista generata non può contraddire la sorgente, e verifica_freschezza() dice
se il file nel repo è rimasto indietro. Il testo prodotto è deterministico, così
il diff di una rigenerazione mostra solo ciò che è cambiato davvero.
"""
import condizioni
from modello import VISTE, PROGETTAZIONE, Reperto, _valori

INTESTAZIONE = ("<!-- Generato da app-blueprint (progetto.py viste): non modificare a mano. "
                "Le sorgenti sono in docs/progettazione/ e contracts/. -->\n")
# I tipi che l'indice elenca: gli annidati (attributi, colonne…) si leggono dal contenitore.
TIPI_INDICE = (
    "obiettivi", "stakeholder", "sistemi", "non_obiettivi", "vincoli", "aree", "storie", "percorsi",
    "rnf", "requisiti_dati", "conflitti", "glossario", "regole", "sottodomini", "moduli", "dipendenze",
    "entita", "generalizzazioni", "relazioni", "macchine", "processi", "driver", "strategie", "ambienti",
    "integrazioni", "confini", "flussi", "minacce", "volumi", "accessi", "ristrutturazione", "tabelle",
    "api", "facciata", "eventi", "errori", "matrice", "sequenze", "personas", "sezioni", "rotte",
    "schermate", "livelli", "incrementi", "task", "rischi", "assunzioni", "domande", "debito",
    "deperibili", "revisioni", "modifiche", "adr",
)


def _ordina(elementi):
    return sorted(elementi, key=lambda e: _chiave_naturale(e.id))


def _chiave_naturale(testo):
    import re
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", str(testo))]


def _cella(testo):
    return str(testo).replace("|", "\\|").replace("\n", " ")


# --- indice --------------------------------------------------------------------------

def indice(progetto, catalogo):
    righe = [INTESTAZIONE, "# Indice della progettazione", "",
             "Una riga per elemento: id, descrizione, incremento in cui serve, sorgente. "
             "Il dettaglio si legge per id: `progetto.py mostra <id>`.", ""]
    for tipo in TIPI_INDICE:
        elementi = _ordina(progetto.tutti(tipo))
        if not elementi:
            continue
        righe += [f"## {tipo}", "", "| id | descrizione | inc. | sorgente |", "|---|---|---|---|"]
        for e in elementi:
            righe.append(f"| {_cella(e.id)} | {_cella(e.etichetta())} | {progetto.incremento_di(e)} | {e.sorgente} |")
        righe.append("")
    return "\n".join(righe)


# --- checklist ---------------------------------------------------------------------------

def checklist(progetto, catalogo):
    import controlli
    ctx = controlli.Contesto(progetto, catalogo)
    stati = controlli.stati_voci(ctx)
    righe = [INTESTAZIONE, "# Checklist dei gate", ""]
    scheda = progetto.scheda
    righe += [f"Esposizione **{scheda.get('esposizione')}**, criticità **{scheda.get('criticita')}**, "
              f"inneschi: {', '.join(scheda.get('inneschi', [])) or 'nessuno'}. "
              f"Incremento corrente: **{progetto.incremento_corrente()}**; ↻ segna le voci che si richiudono "
              "a ogni incremento, e per loro vale la chiusura dell'incremento corrente.", ""]
    for fase in catalogo.get("fasi", []):
        numero = fase["numero"]
        voci = [(i, st) for i, st in stati.items() if st["fase"] == numero]
        if not voci:
            continue
        righe += [f"## {numero}. {fase['nome']}", "", f"**Gate:** {fase['gate']}", "",
                  "| voce | stato | testo | evidenza o motivo |", "|---|---|---|---|"]
        for ident, st in sorted(voci, key=lambda x: condizioni.chiave_id(x[0])):
            if st["applicabilita"] != condizioni.APPLICABILE:
                stato, nota = st["applicabilita"], condizioni.descrivi_motivo(st["voce"], scheda) \
                    if st["applicabilita"] != condizioni.FUORI_CATENA else "fasi 13–15: fuori dalla catena"
            elif st["chiusa"]:
                c = st["chiusura"]
                stato = "fatta" if c.get("esito") == "fatto" else "esclusa"
                nota = ", ".join(_valori(c.get("evidenza"))) or c.get("motivo", "")
            elif st["riaperta_da"]:
                stato, nota = "riaperta", f"da {st['riaperta_da']}"
            else:
                stato, nota = "aperta", ""
            segno = " ↻" if st["per_incremento"] else ""
            righe.append(f"| {ident}{segno} | {stato} | {_cella(st['voce']['testo'])} | {_cella(nota)} |")
        righe.append("")
    noti = set(catalogo.get("inneschi", {}))
    profilo = {"esposizione": scheda.get("esposizione", "personale"), "criticita": scheda.get("criticita", "bassa"),
               "inneschi": scheda.get("inneschi", [])}
    for chiave, titolo, testa in (("trasversali", "Controlli trasversali", "Si rivedono a ogni gate; l'esito va nella nota del registro."),
                                  ("dod", "DoD di incremento", "La applica parallel-build a ogni rientro (task) e alla chiusura dell'incremento.")):
        righe += [f"## {titolo}", "", testa, "", "| voce | stato | testo |", "|---|---|---|"]
        for voce in catalogo.get(chiave, []):
            st = condizioni.stato_voce(voce, profilo, inneschi_noti=noti)
            livello = f" ({voce['livello']})" if voce.get("livello") else ""
            righe.append(f"| {voce['id']}{livello} | {st} | {_cella(voce['testo'])} |")
        righe.append("")
    return "\n".join(righe)


def debito_pubblicazione(progetto, catalogo):
    import controlli
    ctx = controlli.Contesto(progetto, catalogo)
    rinviate = [(i, st) for i, st in controlli.stati_voci(ctx).items() if st["applicabilita"] == condizioni.RINVIATA]
    righe = [INTESTAZIONE, "# Debito di pubblicazione", "",
             "Voci di esercizio che valgono per un'app pubblica e che un progetto pubblicabile rinvia. "
             "Passando l'esposizione a 'pubblico' si riaprono tutte.", ""]
    if not rinviate:
        righe.append("Nessuna voce rinviata.")
    else:
        righe += ["| voce | fase | testo |", "|---|---|---|"]
        for ident, st in sorted(rinviate, key=lambda x: condizioni.chiave_id(x[0])):
            righe.append(f"| {ident} | {st['fase']} | {_cella(st['voce']['testo'])} |")
    return "\n".join(righe) + "\n"


# --- tracciabilità --------------------------------------------------------------------

def tracciabilita(progetto, catalogo):
    entranti = progetto.entranti()
    righe = [INTESTAZIONE, "# Matrice di tracciabilità", "",
             "Dalle storie al progetto e ai test. Gli esiti dei test li aggiunge parallel-build in chiusura.", "",
             "| storia | inc. | priorità | entità | modulo (tocca) | operazioni API | schermate | oracoli | end-to-end |",
             "|---|---|---|---|---|---|---|---|---|"]
    for s in _ordina(progetto.tutti("storie")):
        d = s.dati
        citata = entranti.get(("storie", s.id), [])
        api = sorted({i for t, i, _ in citata if t == "api"})
        schermate = sorted({i for t, i, _ in citata if t == "schermate"})
        task = [progetto.trova("task", i) for t, i, _ in citata if t == "task"]
        oracoli = sorted(t.id for t in task if t and t.dati.get("ondata") == "oracoli" and t.dati.get("modulo"))
        e2e = sorted(t.id for t in task if t and t.dati.get("ondata") == "oracoli" and not t.dati.get("modulo"))
        modulo = d.get("modulo", "")
        if _valori(d.get("tocca")):
            modulo += f" ({', '.join(_valori(d.get('tocca')))})"
        righe.append(f"| {s.id} | {d.get('incremento', '')} | {d.get('priorita', '')} | {', '.join(_valori(d.get('entita')))} | "
                     f"{modulo} | {', '.join(api)} | {', '.join(schermate)} | {', '.join(oracoli)} | {', '.join(e2e)} |")
    righe += ["", "## Requisiti non funzionali", "", "| RNF | caratteristica | indirizzato da | prova |", "|---|---|---|---|"]
    for r in _ordina(progetto.tutti("rnf")):
        righe.append(f"| {r.id} | {r.dati.get('caratteristica', '')} | {', '.join(_valori(r.dati.get('indirizzato_da')))} | "
                     f"{_cella(r.dati.get('prova', ''))} |")
    righe += ["", "## Obiettivi", "", "| obiettivo | storie che lo servono |", "|---|---|"]
    for o in _ordina(progetto.tutti("obiettivi")):
        storie = sorted({i for t, i, _ in entranti.get(("obiettivi", o.id), []) if t == "storie"})
        righe.append(f"| {o.id} | {', '.join(storie)} |")
    return "\n".join(righe) + "\n"


# --- diagrammi ------------------------------------------------------------------------

SINISTRA = {(0, 1): "|o", (1, 1): "||", (0, "N"): "}o", (1, "N"): "}|"}
DESTRA = {(0, 1): "o|", (1, 1): "||", (0, "N"): "o{", (1, "N"): "|{"}


def _nome_mermaid(ident):
    return ident.upper().replace("-", "_")


def _tipo_mermaid(tipo):
    return str(tipo).replace(" ", "_").replace(",", "_") or "valore"


def _etichetta(testo):
    return '"' + str(testo).replace('"', "'").replace(":", " –") + '"'


def er_concettuale(progetto, catalogo):
    righe = [INTESTAZIONE, "# Schema E/R concettuale", "",
             "Generato da dominio/entita.toml. Notazione a zampa di gallina: il simbolo accanto a un'entità dice "
             "quante sue istanze partecipano per ogni istanza dell'altra. Gli identificatori principali sono marcati PK, "
             "gli altri UK.", "", "```mermaid", "erDiagram"]
    for e in _ordina(progetto.tutti("entita")):
        righe.append(f"  {_nome_mermaid(e.id)} {{")
        identificatori = e.dati.get("identificatori") or []
        principale = set(identificatori[0]) if identificatori else set()
        altri = {a for ident in identificatori[1:] for a in ident}
        for a in e.dati.get("attributi", []):
            if not isinstance(a, dict):
                continue
            chiave = " PK" if a.get("nome") in principale else (" UK" if a.get("nome") in altri else "")
            nota = []
            if a.get("obbligatorio") is False:
                nota.append("facoltativo")
            if a.get("multiplo"):
                nota.append("multiplo")
            if a.get("derivato"):
                nota.append("derivato")
            commento = f" {_etichetta(', '.join(nota))}" if nota else ""
            righe.append(f"    {_tipo_mermaid(a.get('dominio'))} {a.get('nome')}{chiave}{commento}")
        righe.append("  }")
    for r in _ordina(progetto.tutti("relazioni")):
        parti = [x for x in r.dati.get("partecipanti", []) if isinstance(x, dict)]
        if len(parti) == 2:
            a, b = parti
            sinistra = SINISTRA.get((b.get("min"), b.get("max")), "||")
            destra = DESTRA.get((a.get("min"), a.get("max")), "||")
            righe.append(f"  {_nome_mermaid(a.get('entita', ''))} {sinistra}--{destra} "
                         f"{_nome_mermaid(b.get('entita', ''))} : {_etichetta(r.dati.get('nome', r.id))}")
        else:
            nodo = _nome_mermaid(r.id)
            for x in parti:
                destra = DESTRA.get((x.get("min"), x.get("max")), "||")
                righe.append(f"  {_nome_mermaid(x.get('entita', ''))} ||--{destra} {nodo} : {_etichetta('partecipa')}")
    for g in _ordina(progetto.tutti("generalizzazioni")):
        for figlio in _valori(g.dati.get("figli")):
            righe.append(f"  {_nome_mermaid(g.dati.get('padre', ''))} ||--o| {_nome_mermaid(figlio)} : "
                         f"{_etichetta('è un (' + str(g.dati.get('copertura')) + ', ' + str(g.dati.get('disgiunzione')) + ')')}")
    righe += ["```", ""]
    righe += ["## Proprietari", "", "| entità | modulo | descrizione |", "|---|---|---|"]
    for e in _ordina(progetto.tutti("entita")):
        righe.append(f"| {e.id} | {e.dati.get('modulo', '')} | {_cella(e.dati.get('descrizione', ''))} |")
    return "\n".join(righe) + "\n"


def er_logico(progetto, catalogo):
    righe = [INTESTAZIONE, "# Schema logico", "",
             "Generato da contracts/schema.toml: tabelle, chiavi e chiavi esterne.", "", "```mermaid", "erDiagram"]
    tabelle = _ordina(progetto.tutti("tabelle"))
    for t in tabelle:
        d = t.dati
        chiave = set(_valori(d.get("chiave")))
        esterne = {c for fk in d.get("esterne") or [] if isinstance(fk, dict) for c in _valori(fk.get("colonne"))}
        uniche = {c for u in d.get("uniche") or [] for c in _valori(u)}
        righe.append(f"  {_nome_mermaid(t.id)} {{")
        for c in d.get("colonne", []):
            if not isinstance(c, dict):
                continue
            segni = [s for s, dentro in (("PK", c.get("nome") in chiave), ("FK", c.get("nome") in esterne),
                                         ("UK", c.get("nome") in uniche)) if dentro]
            nullo = ' "null"' if c.get("nullo") else ""
            righe.append(f"    {_tipo_mermaid(c.get('tipo'))} {c.get('nome')}{(' ' + ','.join(segni)) if segni else ''}{nullo}")
        righe.append("  }")
    for t in tabelle:
        colonne = {c.get("nome"): c for c in t.dati.get("colonne", []) if isinstance(c, dict)}
        uniche = [set(_valori(u)) for u in t.dati.get("uniche") or []] + [set(_valori(t.dati.get("chiave")))]
        for fk in t.dati.get("esterne") or []:
            if not isinstance(fk, dict):
                continue
            cols = set(_valori(fk.get("colonne")))
            unica = any(u and u <= cols for u in uniche)
            nullo = any(colonne.get(c, {}).get("nullo") for c in cols)
            sinistra = "|o" if unica else "}o"
            destra = "o|" if nullo else "||"
            righe.append(f"  {_nome_mermaid(t.id)} {sinistra}--{destra} {_nome_mermaid(fk.get('riferisce', ''))} : "
                         f"{_etichetta(', '.join(sorted(cols)))}")
    righe += ["```", "", "| tabella | modulo | forma normale | traduce |", "|---|---|---|---|"]
    for t in tabelle:
        righe.append(f"| {t.id} | {t.dati.get('modulo', '')} | {t.dati.get('normalizzazione', '')} | {', '.join(_valori(t.dati.get('da')))} |")
    return "\n".join(righe) + "\n"


def stati(progetto, catalogo):
    righe = [INTESTAZIONE, "# Macchine a stati", "",
             "Generate da dominio/stati.toml. Le transizioni non elencate sono vietate: gli oracoli lo provano."]
    for m in _ordina(progetto.tutti("macchine")):
        d = m.dati
        righe += ["", f"## {d.get('entita')} ({d.get('attributo')})", "", "```mermaid", "stateDiagram-v2",
                  f"  [*] --> {d.get('iniziale')}"]
        ammesse = set()
        for t in d.get("transizioni", []):
            if isinstance(t, dict):
                ruoli = f" [{', '.join(_valori(t.get('ruoli')))}]" if _valori(t.get("ruoli")) else ""
                evento = str(t.get("evento", "")).replace(":", " –")
                righe.append(f"  {t.get('da')} --> {t.get('a')} : {evento}{ruoli}")
                ammesse.add((t.get("da"), t.get("a")))
        for f in _valori(d.get("finali")):
            righe.append(f"  {f} --> [*]")
        righe.append("```")
        stati_m = _valori(d.get("stati"))
        vietate = [(a, b) for a in stati_m for b in stati_m if a != b and (a, b) not in ammesse]
        if vietate:
            righe += ["", "Transizioni vietate: " + "; ".join(f"{a} → {b}" for a, b in vietate) + "."]
    return "\n".join(righe) + "\n"


def moduli(progetto, catalogo):
    righe = [INTESTAZIONE, "# Moduli e context map", "",
             "Generata da dominio/moduli.toml. Una freccia va dal modulo a valle a quello da cui dipende.", "",
             "```mermaid", "flowchart LR"]
    for sd in _ordina(progetto.tutti("sottodomini")):
        righe.append(f"  subgraph {sd.id} [{sd.id} — {sd.dati.get('tipo')}]")
        for m in _ordina(progetto.tutti("moduli")):
            if m.dati.get("sottodominio") == sd.id:
                tipo = "motore" if m.dati.get("motore") else m.dati.get("archetipo", "?")
                righe.append(f"    {m.id}[\"{m.id}<br/>{tipo}, rischio {m.dati.get('rischio', '?')}\"]")
        righe.append("  end")
    for d in _ordina(progetto.tutti("dipendenze")):
        etichetta = d.dati.get("tipo", "")
        if d.dati.get("comunicazione"):
            etichetta += f", {d.dati['comunicazione']}"
        righe.append(f"  {d.dati.get('a_valle')} -->|{etichetta}| {d.dati.get('a_monte')}")
    righe += ["```", "", "| modulo | responsabilità | entità possedute |", "|---|---|---|"]
    for m in _ordina(progetto.tutti("moduli")):
        possedute = sorted(e.id for e in progetto.tutti("entita") if e.dati.get("modulo") == m.id)
        righe.append(f"| {m.id} | {_cella(m.dati.get('responsabilita', ''))} | {', '.join(possedute)} |")
    return "\n".join(righe) + "\n"


def contesto(progetto, catalogo):
    nome = progetto.scheda.get("progetto", "sistema")
    righe = [INTESTAZIONE, "# Diagramma di contesto", "",
             "Generato da prodotto/prodotto.toml: chi usa il sistema e con quali sistemi esterni dialoga.", "",
             "```mermaid", "flowchart LR", f"  sistema[\"{nome}\"]"]
    for s in _ordina(progetto.tutti("stakeholder")):
        if s.dati.get("usa"):
            righe.append(f"  {s.id}([\"{s.id}\"]) --> sistema")
    for s in _ordina(progetto.tutti("sistemi")):
        freccia = "-->" if s.dati.get("integrazione") else "-.->"
        righe.append(f"  sistema {freccia} {s.id}[(\"{s.id}\")]")
    righe += ["```", ""]
    return "\n".join(righe)


def api(progetto, catalogo):
    righe = [INTESTAZIONE, "# Operazioni API", "", "Generato da contracts/openapi.json.", ""]
    per_modulo = {}
    for op in progetto.tutti("api"):
        per_modulo.setdefault(op.dati.get("x-modulo", "?"), []).append(op)
    for modulo in sorted(per_modulo):
        righe += [f"## {modulo}", "", "| operazione | metodo e percorso | storie | errori |", "|---|---|---|---|"]
        for op in sorted(per_modulo[modulo], key=lambda o: o.id):
            d = op.dati
            righe.append(f"| {op.id} | {d.get('_metodo', '').upper()} {d.get('_percorso', '')} | "
                         f"{', '.join(_valori(d.get('x-storie')))} | {', '.join(_valori(d.get('x-errori')))} |")
        righe.append("")
    return "\n".join(righe)


def srs(progetto, catalogo):
    """Una specifica dei requisiti leggibile da una persona, nell'ordine di una SRS."""
    p = progetto
    righe = [INTESTAZIONE, f"# Specifica dei requisiti — {p.scheda.get('progetto', '')}", "",
             "Vista generata dalle sorgenti dei requisiti: per leggerla, non per modificarla.", "", "## Obiettivi", ""]
    for o in _ordina(p.tutti("obiettivi")):
        righe.append(f"- **{o.id}** {o.dati.get('testo', '')} — metrica: {o.dati.get('metrica', '')}; valore atteso: {o.dati.get('valore', '')}.")
    righe += ["", "## Stakeholder e attori", ""]
    for s in _ordina(p.tutti("stakeholder")):
        ruolo = "attore" if s.dati.get("usa") else "non usa il prodotto"
        righe.append(f"- **{s.id}** ({ruolo}; {', '.join(_valori(s.dati.get('categorie')))}): {s.dati.get('descrizione', '')}")
    righe += ["", "## Perimetro", "", "Non-obiettivi:", ""]
    for n in _ordina(p.tutti("non_obiettivi")):
        righe.append(f"- **{n.id}** {n.dati.get('testo', '')}")
    righe += ["", "## Vincoli", ""]
    for v in _ordina(p.tutti("vincoli")):
        righe.append(f"- **{v.id}** ({v.dati.get('tipo', '')}) {v.dati.get('testo', '')}")
    righe += ["", "## Requisiti funzionali", ""]
    for area in _ordina(p.tutti("aree")):
        righe += [f"### {area.dati.get('nome', area.id)}", ""]
        for s in _ordina([x for x in p.tutti("storie") if x.id.startswith(area.id + "-")]):
            d = s.dati
            righe.append(f"- **{s.id}** {d.get('titolo', '')} — attore {d.get('attore', '')}, priorità {d.get('priorita', '')}, "
                         f"incremento {d.get('incremento', '')}.")
            for c in d.get("criteri") or []:
                if isinstance(c, dict):
                    righe.append(f"  - *Dato* {c.get('dato', '')}, *quando* {c.get('quando', '')}, *allora* {c.get('allora', '')}.")
        righe.append("")
    righe += ["## Requisiti di qualità", ""]
    for q in _ordina(p.tutti("qualita")):
        righe.append(f"- **{q.id}** — rilevanza {q.dati.get('rilevanza', '')}: {q.dati.get('motivo', '')}")
    righe.append("")
    for r in _ordina(p.tutti("rnf")):
        d = r.dati
        righe.append(f"- **{r.id}** ({d.get('caratteristica', '')}) Quando {d.get('stimolo', '')}, in {d.get('contesto', '')}, "
                     f"il sistema {d.get('risposta', '')} entro {d.get('misura', '')}. Prova: {d.get('prova', '')}")
    righe += ["", "## Requisiti sui dati", ""]
    for r in _ordina(p.tutti("requisiti_dati")):
        d = r.dati
        righe.append(f"- **{r.id}** {d.get('concetto', '')}: volume {d.get('volume', '')}, crescita {d.get('crescita', '')}, "
                     f"conservazione {d.get('conservazione', '')}.")
    righe += ["", "## Glossario", ""]
    for t in sorted(p.tutti("glossario"), key=lambda e: e.id):
        righe.append(f"- **{t.id}**: {t.dati.get('definizione', '')}")
    return "\n".join(righe) + "\n"


VISTE_GENERATE = {
    "indice.md": indice,
    "checklist.md": checklist,
    "debito-pubblicazione.md": debito_pubblicazione,
    "tracciabilita.md": tracciabilita,
    "er-concettuale.md": er_concettuale,
    "er-logico.md": er_logico,
    "stati.md": stati,
    "moduli.md": moduli,
    "contesto.md": contesto,
    "api.md": api,
    "srs.md": srs,
}


def genera(progetto, catalogo):
    """{percorso relativo: testo} di tutte le viste."""
    return {f"{VISTE}/{nome}": funzione(progetto, catalogo) for nome, funzione in VISTE_GENERATE.items()}


def scrivi(progetto, catalogo):
    cartella = progetto.radice / VISTE
    cartella.mkdir(parents=True, exist_ok=True)
    scritte = []
    for relativo, testo in genera(progetto, catalogo).items():
        percorso = progetto.radice / relativo
        precedente = percorso.read_text(encoding="utf-8") if percorso.exists() else None
        if precedente != testo:
            percorso.write_text(testo, encoding="utf-8")
            scritte.append(relativo)
    return scritte


def verifica_freschezza(progetto, catalogo):
    """Un errore per ogni vista mancante o rimasta indietro rispetto alle sorgenti."""
    reperti = []
    for relativo, testo in genera(progetto, catalogo).items():
        percorso = progetto.radice / relativo
        if not percorso.exists():
            reperti.append(Reperto("errore", relativo, "vista mancante: esegui progetto.py viste", "viste"))
        elif percorso.read_text(encoding="utf-8") != testo:
            reperti.append(Reperto("errore", relativo, "vista non aggiornata: esegui progetto.py viste", "viste"))
    return reperti
