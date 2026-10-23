---
name: app-blueprint
description: Progettazione ingegneristica completa di una nuova app, per fasi e gate, finché parallel-build può costruirla in parallelo senza decidere nulla — avvio e fattibilità, requisiti di tutte le funzionalità, modello di dominio e schema E/R, architettura con ADR e threat model, progettazione logica dei dati, contratti, UX, piano con ownership disgiunta, congelamento verificato da uno script. Usa questa skill OGNI VOLTA che l'utente vuole progettare o pianificare un'app nuova da zero — "voglio costruire un'app, un SaaS, un gestionale", "progettiamo l'architettura", "scegliamo lo stack", "facciamo lo schema del database", "preparami il piano per costruirla in parallelo" — anche se non nomina il metodo, e quando riprende una progettazione, apre l'incremento successivo o deve cambiare un progetto già congelato. Decide e specifica; la costruzione è di parallel-build. NON usarla per un'idea ancora nebulosa, la cui destinazione non sta in una frase verificabile (prima decision-map), né per modifiche a un'app non progettata così o per un'app che sta in una sessione (dev-discipline), e in quei casi dillo e indirizza.
---

# App Blueprint

Questa skill porta una nuova app dall'idea a un progetto congelato che `parallel-build` costruisce con più sotto-agenti in parallelo. Segue la progettazione ingegneristica convenzionale — fattibilità, ingegneria dei requisiti, modellazione del dominio, architettura, progettazione di dettaglio e dei dati, UX, pianificazione — come una checklist di fasi con un gate ciascuna, e ogni voce si chiude con un'evidenza che uno script verifica. Decide e specifica; non scrive codice applicativo.

Il problema che risolve è doppio. Il parallelismo non lo danno gli agenti, lo dà il progetto: venti agenti su un progetto vago producono venti interpretazioni. E un progetto completo, scritto come documenti, costa centinaia di migliaia di token a ogni ripresa e prima o poi si contraddice. Qui il progetto vive in sorgenti strutturate, una informazione in un posto, lette per id; ciò che si deriva si genera; la coerenza la controlla `progetto.py`.

**Catena.** `app-blueprint` esegue le fasi 0–7 fino al congelamento; `parallel-build` esegue ambienti e scheletro (7.09, 7.10) e le fasi 8–12, sullo stesso registro e con gli stessi comandi; le fasi 13–15 sono fuori catena. `decision-map` entra per la nebbia vera, in qualunque punto.

**Prerequisiti.** Python 3.11 o successivo (solo libreria standard). Skill su cui il metodo si appoggia, senza ripeterle: `decision-principles` (come si decide e si delega), `lean-code`, `lean-docs`, `frontend-craft` (tutto ciò che è interfaccia), `design-docs` (formato degli ADR e dei mockup), `dev-communication`, `compliance-docs` (con dati personali o mercato UE), `session-resume` e `session-handoff`, `decision-map`, `parallel-build`. Leggile se non sono già in contesto.

## Le regole che governano tutto

In caso di tensione tra qualsiasi indicazione di questa skill, vincono queste, in quest'ordine:

1. **Nessuna decisione strutturale arriva aperta alla costruzione.** I costruttori non possono prendere decisioni strutturali (`decision-principles`), e i sotto-agenti non possono nemmeno fare domande all'utente (`FONTI.md`). Ogni decisione aperta diventa, nel caso migliore, un'escalation che ferma il lavoro parallelo; nel peggiore, venti interpretazioni silenziose. Ciò che non si sa decidere si decide con l'utente o si dichiara fuori scope.
2. **Ciò che non si esegue non è un criterio.** Ogni storia ha criteri che diventano test scritti prima del codice da chi non costruisce, ogni task termina con comandi, ogni voce si chiude con un'evidenza che lo script controlla. "Funziona" non è un esito.
3. **Ogni informazione sta in un posto solo, e si legge per id.** Le sorgenti si citano, non si copiano; le viste si generano; nessuna sessione legge la progettazione per file. È ciò che tiene il contesto leggero e il progetto coerente (`references/struttura.md`).
4. **Il progetto si fa con tutte le funzionalità davanti.** Inventario dei requisiti, modello di dominio, dati e architettura coprono tutti gli incrementi; solo il dettaglio dell'incremento corrente si completa e si congela. Gli schemi si progettano una volta, bene, e crescono con modifiche tracciate.
5. **Il rigore si dosa sul profilo, mai sul tempo.** La scheda del progetto dice quali voci valgono; una voce che vale si chiude o si esclude con un motivo. Il metodo non ha durate: una scadenza riduce lo scope, non il rigore. E sa quando non usarsi: un'idea nebulosa va prima diradata, un'app piccola si fa in una sessione.

## Lo strumento

`scripts/progetto.py`, eseguito dalla radice del repo progettato:

| Comando | Serve a |
|---|---|
| `inizia --progetto N --responsabile R` | creare lo stato della progettazione (voce 0.05) |
| `stato` | lo stato a colpo d'occhio: scheda, punto aperto, registro, frontiera, verifica. Si esegue a ogni avvio |
| `apri <voce>` / `chiudi <voce> --evidenza …` | l'inizio e la fine di un punto; `chiudi` controlla prima di scrivere |
| `approva <fase> --da <chi>` | la fine di una fase, dopo l'approvazione dell'utente |
| `modifica <MOD-n>` / `congela --da <chi>` | applicare una modifica approvata; congelare l'incremento |
| `checklist [--fase N] [--dod] [--trasversali]` | le voci con il loro stato e il gate della fase |
| `mostra <id>`, `fascio <voce>`, `fascio --task <id>`, `impatto <id>` | leggere per id: un elemento e chi lo cita, ciò che serve per una voce o per un task, ciò che dipende da un elemento |
| `formato [<tipo>]` | il formato di un tipo di sorgente, con un esempio |
| `schema [--nuovi]` | le tabelle dell'incremento corrente, o solo ciò che aggiunge: la base delle migrazioni |
| `viste`, `verifica [--gate N] [--congelamento [data]] [--json]` | rigenerare le viste; controllare la coerenza |

Esito: 0 senza errori, 1 con errori, 2 errore d'uso. `assets/esempio/` è un progetto completo, congelato all'incremento 1 e verde: è il modello di ogni file. `assets/checklist.toml` è il catalogo delle voci, con le condizioni d'applicabilità e i controlli.

## Il protocollo

Dettagli in `references/gate.md`.

- **Avvio di sessione**: `session-resume` se c'è un handoff, poi `progetto.py stato`. Nient'altro si legge all'avvio.
- **Un punto** è il lavoro su una voce, con inizio e fine espliciti: `apri <voce>` → si segue la reference della fase → `chiudi <voce> --evidenza …` → commit. Un punto alla volta; si lascia aperto solo se lo blocca una domanda registrata.
- **Una fase** finisce così: voci chiuse, `verifica --gate N` verde, controlli trasversali in rassegna, brief del gate all'utente, approvazione esplicita, `approva N`, commit e tag.
- **Fine di sessione**: `session-handoff` alla fine di una fase o prima che il contesto si saturi.

## Le fasi

| Fase | Reference | Cosa produce |
|---|---|---|
| 0 Precondizioni | `fase-0-precondizioni.md` | repo, worktree, agenti installati e provati, stato inizializzato |
| 1 Avvio, problema, fattibilità | `fase-1-avvio.md` | problema, obiettivi misurabili, stakeholder, perimetro, vincoli, fattibilità, make/buy, rischi, scheda, verdetto, go |
| 2 Requisiti | `fase-2-requisiti.md` | inventario delle storie di tutti gli incrementi, criteri di quello corrente, trasversali, qualità ISO/IEC 25010, RNF misurabili, conformità, percorsi critici |
| 3 Dominio | `fase-3-dominio.md` | schema E/R concettuale, regole, macchine a stati, processi, sottodomini e moduli, context map |
| 4 Architettura | `fase-4-architettura.md` | stile, archetipi e rischio dei moduli, strategie trasversali, deployment, threat model, analisi, tecnologie, ADR |
| 5 Dettaglio | `fase-5-dettaglio.md` | interno dei moduli, tavole dei volumi e degli accessi, ristrutturazione, schema logico e fisico, API, errori, matrice, configurazione, ASVS |
| 6 UX/UI, con l'innesco `ui`, intrecciata alle fasi 2–5 | `fase-6-ux.md` | personas, architettura dell'informazione, design system, schermate in tutti gli stati, mockup, testi, accessibilità |
| 7 Pianificazione | `fase-7-pianificazione.md` | piano con ondate e ownership, strategia di test, DoD, revisione di prontezza, prova di decidibilità, pre-mortem, congelamento |

Si legge la reference della fase quando si apre il suo primo punto, non prima. `references/decisioni.md` vale in ogni fase in cui si decide; `references/profili.md` alle voci 1.13 e 1.14 e quando la scheda cambia; `references/struttura.md` quando si crea o si legge una sorgente nuova.

## Profilo, incrementi, modifiche

- **Profilo**: esposizione (`personale`, `pubblicabile`, `pubblico`), criticità, inneschi. Con `pubblicabile` le voci di progetto valgono come per un'app pubblica e quelle di esercizio vanno nel debito di pubblicazione, che si paga passando al pubblico. `references/profili.md`.
- **Incrementi**: le voci che dipendono dall'incremento si richiudono a ogni incremento; aprire il successivo è aumentare `[scheda].incremento`, a costruzione chiusa. `references/gate.md`.
- **Modifiche**: ciò che cambia una voce chiusa passa da una modifica registrata (`MOD-n`) con l'analisi d'impatto e l'approvazione dell'utente; una modifica dopo il congelamento lo annulla. `references/gate.md`.

## Deroghe dichiarate

- **A `dev-communication`**, nel prodotto, nei requisiti e nelle decisioni: si incalza con domande concrete, perché le domande sono la produzione (`references/decisioni.md`).
- **A `design-docs`**: il progetto pianificato vive in `docs/progettazione/`, in sorgenti da cui si generano i diagrammi; gli ADR registrano solo il perché delle decisioni difficili da invertire (`references/struttura.md`).

## Casi limite

- **L'utente vuole saltare oracoli, threat model, revisioni o la prova di decidibilità per fare prima.** Dillo prima di eseguire: senza oracoli il lavoro parallelo non si verifica, senza matrice il rischio più frequente delle applicazioni web resta scoperto, senza revisioni le lacune emergono come escalation in piena costruzione. Proponi l'alternativa onesta: ridurre lo scope, o costruire in una sessione. Un'esclusione si può fare, con il motivo scritto; un metodo degradato in silenzio no.
- **Il repo contiene già un'app non progettata con il metodo.** È fuori dal metodo: dillo e indirizza a `dev-discipline` o `code-walkthrough`. Un'app nata dal metodo cresce per incrementi e modifiche.
- **La progettazione rivela che la destinazione è sbagliata.** Fermati ed esponi: o si corregge con una modifica dichiarando cosa resta valido, o si torna a `decision-map`.
- **Un controllo dello script sembra sbagliato per il progetto.** Non aggirarlo con un'evidenza di comodo: esponi il caso all'utente; se il controllo è davvero sbagliato, è un difetto della skill da correggere, e la voce si chiude come non applicabile con quel motivo.

## Cosa NON fare

- Non scrivere codice applicativo: costruire è di `parallel-build`, e il codice degli spike è usa e getta.
- Non lasciare una decisione strutturale "da vedere durante la costruzione".
- Non scrivere la stessa informazione in due posti, né modificare a mano una vista generata, `gate.toml` o il registro: per quelli ci sono i comandi.
- Non chiudere una voce senza evidenza, né approvare un gate senza il sì esplicito dell'utente.
- Non scrivere RNF senza numero, né numeri senza dichiarare se sono assunzioni.
- Non citare versioni o fatti che scadono senza fonte e data: vanno nei deperibili.
- Non far decidere ai sotto-agenti, e non presentare una decisione su un dossier di cui non hai verificato le fonti.
- Non proporre microservizi, code o cache senza il requisito misurato che li giustifica.
- Non lasciare il lavoro solo su disco in un ambiente effimero, né pushare senza il permesso dell'utente.
- Non procedere con il metodo quando il verdetto d'ingresso dice di non usarlo.
