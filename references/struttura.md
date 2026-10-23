# Struttura delle sorgenti

Dove vive ogni informazione del progetto, in che forma, come si cita e come si legge. Il principio è uno: ogni informazione sta in un posto solo, in una forma che lo script sa leggere; tutto ciò che si può derivare si genera, e la coerenza la verifica `progetto.py verifica`, non la memoria di chi scrive.

Indice: Mappa · Formati · Id e riferimenti · Incremento di un elemento · Leggere · Scrivere · Deroghe dichiarate.

## Mappa

```
docs/progettazione/
  stato.toml            scheda, punto aperto, registro dei gate, congelamento: si legge a ogni avvio
  gate.toml             chiusure delle voci (le scrive progetto.py chiudi)
  registri.toml         rischi, assunzioni, domande, debito, deperibili, revisioni, modifiche
  prodotto/             visione.md; prodotto.toml: obiettivi, stakeholder, sistemi, non-obiettivi, vincoli,
                        [fattibilita], [stima]
  requisiti/            requisiti.toml: aree, qualità, RNF, requisiti sui dati, percorsi critici, conflitti,
                        [trasversali], metodo_priorita; storie.toml, o storie-<area>.toml
  dominio/              glossario.toml; regole.toml; moduli.toml: sottodomini, moduli, dipendenze;
                        entita.toml: entità con attributi, generalizzazioni, relazioni; stati.toml;
                        processi/<id>.md
  architettura/         architettura.toml: driver, strategie, ambienti, integrazioni; minacce.toml;
                        architettura.md (C4 e deployment); analisi.md; valutazione.md
  dati/                 dati.toml: volumi, accessi, ristrutturazione
  moduli/<modulo>.toml  dettaglio del modulo: facciata, eventi, componenti, pattern, algoritmi,
                        transazioni, porte
  sequenze/<PC-n>.md    sequenza di un percorso critico
  ux/                   ux.toml: personas, sezioni, rotte, schermate; design-system.toml; testi.toml;
                        utenti.md
  piano/                piano.toml: incrementi, archetipi, oracoli, comandi, task; test.toml: livelli
  viste/                generate, mai a mano: indice, checklist, debito di pubblicazione, tracciabilità,
                        E/R concettuale e logico, stati, moduli, contesto, API, SRS
contracts/              openapi.json (o asyncapi.json), schema.toml, autorizzazioni.toml, errori.toml,
                        configurazione.toml
docs/adr/NNNN-<titolo>.md   il perché delle decisioni difficili da invertire
docs/design/mockups/        mockup HTML self-contained
docs/consegna/incremento-<n>/   li scrive parallel-build: esemplari.md (8.12), report.md (fase 12)
```

`assets/esempio/` è un progetto completo congelato all'incremento 1, verde a `progetto.py verifica --congelamento`: è il modello di ogni file, al posto dei template vuoti. I file si creano quando la prima voce che li riguarda si apre, non tutti all'inizio.

## Formati

- **TOML** per i dati: si legge con la libreria standard (`tomllib`, Python 3.11+), ammette commenti, e un diff mostra cosa è cambiato riga per riga.
- **Markdown con frontmatter TOML** tra due righe `+++` per la prosa che porta un id: processi, sequenze. Gli altri Markdown (visione, architettura, analisi, valutazione, utenti) sono documenti con sezioni attese.
- **JSON** per OpenAPI o AsyncAPI, perché la libreria standard lo legge e gli strumenti lo generano. Le estensioni `x-modulo`, `x-storie`, `x-errori`, `x-lista` e `info.x-paginazione` collegano le operazioni al resto.
- **ADR** nel formato di `design-docs`: Status, Context, Decision, Consequences, più *Fonti* quando poggiano su fonti esterne.

Il formato di ogni tipo — sorgente, forma dell'id, campi obbligatori, valori ammessi, riferimenti, un esempio — lo stampa `progetto.py formato <tipo>`, ricavandolo dalle regole dello script e dall'esempio. Non c'è un manuale dei formati da tenere allineato: il manuale è il codice che li controlla.

## Id e riferimenti

| Forma | Tipi | Si cita |
|---|---|---|
| `PREFISSO-n` | obiettivi `OB`, non-obiettivi `NO`, vincoli `V`, assunzioni `A`, rischi `RK`, regole `R`, RNF `RNF`, requisiti sui dati `RD`, percorsi `PC`, conflitti `CO`, driver `DR`, strategie `ST-<tema>`, minacce `MI`, flussi `FL`, accessi `AC`, debito `DEB`, deperibili `DEP`, domande `Q`, revisioni `REV`, modifiche `MOD`, decisioni `ADR-NNNN` | così com'è, da qualunque campo |
| `<AREA>-n` | storie, con il prefisso di un'area di `[[aree]]` | così com'è |
| slug minuscolo | stakeholder, sistemi, entità, relazioni, generalizzazioni, moduli, sottodomini, ambienti, schermate, personas, sezioni, confini, tabelle, errori, task… | `tipo:id`, per esempio `entita:fattura`; senza prefisso solo nei campi che si aspettano quel tipo |
| `<contenitore>.<nome>` | attributi, colonne, indici, elementi del dettaglio di un modulo | `attributo:fattura.numero` |
| numero di voce | voci del catalogo | `3.07`, nei campi che si aspettano voci |

Il campo `traccia` dice da cosa nasce un elemento: storie, regole, RNF, strategie. È ciò che fa funzionare tracciabilità, impatto e incremento calcolato. Un riferimento che non si risolve è un errore di `verifica`, e rinominare un id spezza chi lo cita: gli id, una volta usati, non si rinominano.

## Incremento di un elemento

Si progetta con tutte le funzionalità davanti: l'inventario delle storie copre tutti gli incrementi, e il modello di dominio, i dati e l'architettura le spiegano tutte. Solo le storie dichiarano il loro `incremento`; per ogni altro elemento lo calcola lo script, come il minimo tra quelli di ciò che lo giustifica: la sua `traccia`, e i campi che dicono perché esiste (le `storie` di una schermata o di un'operazione, il `da` di una tabella o di una colonna, gli `accessi` di un indice). Ciò che un elemento usa non conta: un algoritmo per una storia futura non si costruisce prima perché legge un'entità che esiste già. Senza giustificazione l'elemento eredita l'incremento dal contenitore, e altrimenti vale 1: è trasversale.

Così una colonna che serve solo a una storia del secondo incremento esiste già nello schema, marcata dall'incremento 2: il fascio di un task dell'incremento 1 la elenca tra ciò che non si costruisce ora, e l'incremento successivo la trova progettata invece di doverla inventare.

## Leggere

Nessuna sessione legge la progettazione per file. Quattro livelli, dal più leggero:

1. **Stato**, a ogni avvio: `progetto.py stato`. Scheda, punto aperto, registro, frontiera, domande, verifica.
2. **Indice**: `viste/indice.md`, una riga per elemento, per trovare un id.
3. **Dettaglio per id**: `progetto.py mostra <id>` stampa l'elemento e chi lo cita; `progetto.py fascio <voce>` ciò che serve per lavorare una voce; `progetto.py fascio --task <id>` la fetta di progetto di un task di costruzione; `progetto.py impatto <id>` ciò che dipende da un elemento.
4. **Perché**: un ADR si legge quando si rimette in discussione la decisione che registra, non per sapere cosa si costruisce.

Le misure sono in caratteri. Una sorgente oltre il budget di `progetto.py` si spezza (storie per area, un file per modulo); un fascio oltre il budget dice che il modulo è troppo grande per un task.

## Scrivere

- Le sorgenti le scrive la sessione, partendo da `progetto.py formato <tipo>` e dall'esempio. Un'informazione nuova va nella sorgente del suo tipo, e gli altri la citano per id: mai copiata.
- Le viste non si toccano: `progetto.py viste` le rigenera, `verifica` segnala quelle rimaste indietro, e `chiudi` le rigenera da sé.
- Chiusure, punto aperto, registro, congelamento, incremento corrente e approvazione delle modifiche li scrivono i comandi `apri`, `chiudi`, `approva`, `modifica`, `congela` e `incrementa` (`gate.md`): leggono e scrivono al posto della sessione, che così non apre mai `gate.toml`.
- Ogni chiusura si chiude con un commit; in un ambiente effimero anche con un push, se l'utente l'ha permesso.

## Deroghe dichiarate

- **A `design-docs`.** Il progetto pianificato non vive negli ADR ma qui, in sorgenti strutturate da cui si generano i diagrammi: un ADR registra il perché di una decisione, e le sue conseguenze stanno nelle sorgenti che cita. I mockup restano in `docs/design/mockups/` come vuole `design-docs`. A costruzione avvenuta le viste descrivono il sistema corrente e si tengono allineate al codice (DoD D.11, voce 14.08): sostituiscono i diagrammi strutturali di `docs/design/`, che quindi non si scrivono una seconda volta.
- **Percorsi fissi.** Lo script legge questi percorsi. In un repo nuovo sono la convenzione; se il repo ne usa già altri per ADR o contratti, la voce 0.04 lo fa emergere e si decide con l'utente se migrare al layout del metodo, perché due layout non si verificano insieme.
