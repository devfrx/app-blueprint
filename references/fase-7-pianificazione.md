# Fase 7 — Pianificazione della realizzazione

Trasforma il progetto in un piano che `parallel-build` esegue senza reinterpretarlo, lo mette alla prova con due verifiche indipendenti, e lo congela. Il parallelismo non lo danno gli agenti, lo dà il piano: venti agenti su un piano vago producono venti stili e un'integrazione che non chiude. Il lavoro parallelo regge solo se esistono decisioni prese, contratti congelati, proprietà dei file disgiunta e criteri eseguibili.

La fase si chiude in due tempi: il congelamento (7.17) chiude la parte di `app-blueprint`; ambienti e walking skeleton (7.09, 7.10) li fa `parallel-build`, e con loro il gate della fase. Quasi tutte le voci si ripetono a ogni incremento.

Sorgenti: `piano/piano.toml`, `piano/test.toml`, le strategie di qualità del codice e di CI/CD in `architettura.toml`, i registri. Formati: `progetto.py formato task`, `livelli`, `incrementi`, e l'esempio.

Indice: Incrementi e modalità · Il piano · Strategia di test e DoD · Qualità del codice e CI/CD · Rischi · Revisione di prontezza · Prova di decidibilità · Deperibili · Pre-mortem · Congelamento.

## Incrementi e modalità

**7.03** `[[incrementi]]` nel piano: numero, obiettivo, `rilascio` (locale, staging o produzione) e quale è l'`mvp`, il primo incremento di valore. Ogni storia ha un incremento dichiarato qui: la roadmap è l'insieme degli incrementi, non un documento a parte.

**7.12** `[scheda].costruzione`: `parallela` con `parallel-build`, o `seriale` quando l'incremento è piccolo o l'ambiente non ha sotto-agenti. La costruzione seriale segue lo stesso piano, le stesse ondate e gli stessi gate in una sessione sola, senza la concorrenza.

## Il piano

**7.01** `piano/piano.toml` per l'incremento corrente, con `[progetto].incremento` uguale a quello della scheda. Storie, moduli, archetipi dei moduli e classi di rischio non si ripetono: lo script li legge dalle loro sorgenti. Il piano aggiunge solo ciò che è suo:

| Sezione | Contenuto |
|---|---|
| `[progetto]` | nome, `versione_metodo`, `incremento`, `branch_integrazione`, `percorsi_e2e`, `intoccabili` |
| `[comandi]` | i comandi del progetto, una sola fonte citata dai criteri: obbligatori `lint`, `fitness`, `suite`, `e2e`, `supply_chain`; per lato `modulo_backend` e `modulo_frontend`, con il segnaposto `{modulo}` |
| `[rischio]` | `criteri_alto_backend`, `criteri_alto_frontend`: i comandi in più per i moduli ad alto rischio, per lato |
| `[oracoli]` | per ogni modulo dell'incremento, dove vivono i suoi test |
| `[[archetipi]]` | per ogni archetipo dei moduli dell'incremento, il modulo `esemplare`; `costruito_in` se l'esemplare è di un incremento precedente |
| `[stima]` | metodo e incertezza (7.02) |
| `[[task]]` | id, `ondata`, `agente`, `modulo`, `storie`, `possiede`, `dipende_da`, `criteri` |

**I moduli dell'incremento** li calcola lo script: quelli che orchestrano o toccano una sua storia, e quelli che possiedono un elemento che nasce nell'incremento — entità, attributo, tabella, colonna, indice, operazione, regola della matrice, schermata, elemento del dettaglio. Un modulo costruito prima e che l'incremento non tocca resta fuori dal piano, con i suoi oracoli verdi nella suite.

**Le ondate** sono fisse, perché sono il metodo:

| Ondata | Agente | Cosa produce |
|---|---|---|
| `oracoli` | `test-author` | per modulo, test d'accettazione, di contratto e di autorizzazione, tutti rossi; la suite di conformità del motore; i test end-to-end dei percorsi critici |
| `motore` | `sessione` | il motore, se c'è, verde contro la sua suite |
| `esemplari` | `sessione` | un modulo completo per archetipo, verde contro i suoi oracoli |
| `costruzione` | `backend-builder`, `frontend-builder` | i moduli restanti, verdi contro oracoli scritti da altri |

**Gli esemplari.** Per ogni archetipo l'esemplare è il modulo più rappresentativo, non il più semplice: lo costruisce la sessione, l'utente lo approva, e gli altri lo replicano. Di solito gli archetipi presenti sono da uno a tre. Dal secondo incremento l'esemplare di un archetipo già costruito esiste: l'archetipo dichiara `costruito_in`, nessuno lo ricostruisce, e se l'incremento cambia quel modulo lo costruiscono i costruttori, come gli altri. Un archetipo nuovo ha il suo esemplare come nel primo incremento.

**Ownership.** Un percorso si scrive come `cartella/**` o come file esatto; niente altri caratteri jolly, percorsi assoluti o `..`. Così la sovrapposizione tra due task è decidibile. Lo script verifica che:

- nella stessa ondata nessun percorso sia di due task (in ondate diverse sì: sono sequenziali);
- nessun task possieda un intoccabile: lockfile, manifest delle dipendenze, migrazioni, contratti, rotte, kernel condiviso, elenco dei test in attesa, CI, `.claude/`, `docs/`, `CLAUDE.md`. Li crea e li congela lo scheletro, o sono la progettazione stessa; toccarli in costruzione è un'escalation;
- gli oracoli vivano fuori dalle cartelle di chi scrive codice: un costruttore che possiede i propri test potrebbe riscriverli per farli passare. Se il framework preferisce i test accanto al codice, qui si rinuncia a quella convenzione, e l'ADR dello stack lo dichiara;
- gli autori di test possiedano solo test: gli oracoli del loro modulo, o percorsi dentro `percorsi_e2e`.

**I task:**

- **un task, un modulo, un lato**: backend e frontend di un modulo sono due task, con due cartelle; è la misura che un agente tiene in contesto senza degradare. Esemplari e motore non hanno task di costruzione;
- **i criteri sono chiavi di `[comandi]`**: ogni task che scrive codice esegue `fitness` e i test del proprio lato del modulo; un modulo ad alto rischio anche i comandi di `[rischio]` del suo lato;
- **`storie` crea la tracciabilità**: ogni storia dell'incremento ha un task di oracoli del modulo che la orchestra; il task di un modulo che la storia tocca può citarla, per ciò che la storia gli chiede; ogni percorso critico ha un task end-to-end, senza `modulo`, che cita tutte le sue storie dell'incremento, accesso compreso;
- **un task dipende solo da task di ondate precedenti**: dentro un'ondata i task partono insieme, ed è ciò che rende il grafo aciclico per costruzione. Se due task di costruzione sembrano dipendere l'uno dall'altro, il piano è sbagliato: un modulo usa l'altro tramite la facciata finta dello scheletro, e un frontend lavora contro il mock generato dalla specifica;
- **la concorrenza**: oltre il limite di sotto-agenti concorrenti (`FONTI.md`) l'ondata procede a lotti, ed è spesso il segnale che serve un incremento in più.

Il brief di ogni task lo costruisce `parallel-build`: la sua procedura più `progetto.py fascio --task <id>`, che assembla dalle sorgenti esattamente ciò che il task deve leggere, ed elenca a parte ciò che è progettato per incrementi futuri e non si costruisce ora. Per questo il piano non ha un campo `legge`.

**7.02** `[stima]`: il `metodo` e l'`incertezza`, sui conteggi che `progetto.py verifica --json` stampa (task per ondata, rientri seriali, moduli, storie). I rientri sono uno alla volta: la parte seriale della costruzione si stima da loro.

**7.04** Nel metodo il team sono gli agenti, e l'ownership dei moduli è quella dei task: la voce si chiude con il piano valido.

## Strategia di test e DoD

**7.05** `piano/test.toml`, un `[[livelli]]` per livello di test, con scopo, strumento, ambiente, dati, automazione, criteri di ingresso e di uscita. Obbligatori `accettazione`, `contratto`, `autorizzazione` ed `e2e`; l'accettazione dichiara le `tecniche` con cui si progettano i casi (classi di equivalenza, valori limite, tabelle di decisione, transizioni di stato). I dati di test sono sintetici. Le prove degli RNF che in locale non si verificano dicono dove si verificano.

**7.06** La DoD di incremento è quella del catalogo, filtrata dal profilo: `progetto.py checklist --dod`. Si adotta così com'è, o con le esclusioni motivate; `parallel-build` la applica a ogni rientro (livello `task`) e alla chiusura dell'incremento (livello `incremento`).

## Qualità del codice e CI/CD

**7.07** `ST-qualita-codice`: repository, strategia di branching (di solito un branch d'integrazione e un branch per task), linter, formatter, analisi statica, fitness function dei confini tra moduli. Se il repo ha già convenzioni di codice, vincono quelle.

**7.08** `ST-ci-cd`: la pipeline — lint, typecheck, test, fitness, supply chain (audit delle vulnerabilità bloccante per severità alta, licenze, segreti, SBOM se il profilo la chiede), build, rilascio — progettata ora e costruita dallo scheletro. Ogni dipendenza nuova dopo il congelamento è una decisione strutturale: una modifica, non un dettaglio.

## 7.11 Rischi

Il registro aggiornato per l'incremento: i rischi della costruzione (moduli ad alto rischio, integrazioni senza ambiente di prova, esemplari difficili), ciascuno con risposta, responsabile e, se accettato, il segnale.

## 7.13 Revisione di prontezza

Un `reviewer`, con le voci delle fasi 1–7 come checklist e una domanda per ciascuna: ciò che è scritto basta a costruire senza decidere? Per ogni modulo ad alto rischio, un `reviewer` dedicato in più. Il brief gli dà la scala:

| Livello | Significato |
|---|---|
| **P0** | Rende la costruzione impossibile o sbagliata: una decisione strutturale aperta, contratti che si contraddicono, un buco nella matrice |
| **P1** | Una lacuna che un costruttore colmerebbe indovinando: un criterio senza il caso d'errore, uno stato d'interfaccia mancante, un errore fuori catalogo |
| **P2** | Un'incoerenza che non cambia ciò che si costruisce: un termine fuori glossario, un riferimento impreciso |
| **P3** | Rifinitura |

I findings si correggono dove stanno, tornando alla voce che li riguarda se serve. La revisione si registra con `p0` e `p1`, entrambi a zero per chiudere la voce.

## 7.14 Prova di decidibilità

Un `reviewer` per archetipo, più uno per il motore se c'è, senza rete e con i soli file del repo, prepara la costruzione dell'esemplare come se dovesse costruirlo, partendo da `progetto.py fascio --task <id>` dei suoi task: esattamente ciò che riceverà il costruttore. Descrive file, operazioni, dati, errori, stati dell'interfaccia e test, senza scrivere codice. Ogni domanda che dovrebbe fare a qualcuno è una lacuna, e si tratta come un P1; la revisione si registra con `domande`, a zero per chiudere. Si chiama così per non confonderla con la prova a secco di `parallel-build`, che verifica esemplari e generatori a costruzione iniziata.

Revisione e prova partono dopo un commit: i `reviewer` lavorano in un worktree e vedono solo ciò che è committato.

## 7.15 Deperibili

Un `researcher` riapre le fonti di tutti i `[[deperibili]]` alla data del congelamento e aggiorna `verificato_il`. Se qualcosa è cambiato — una versione fuori supporto, un advisory, uno standard sostituito — si torna alla decisione che ne dipende prima di congelare.

## 7.16 Pre-mortem

Con l'utente: "Immagina che la costruzione sia fallita. Cosa è andato storto?". Si raccolgono le risposte senza discuterle, si aggiungono le cause che vede la sessione, e per ciascuna si decide insieme: plausibile e correggibile ora, si corregge; plausibile e non correggibile ora, rischio accettato con il segnale che lo farà emergere; non plausibile, scartata. La revisione registra l'esito.

## 7.17 Congelamento

1. **Debito**: ogni `[[debito]]` ha `accettato_il`, cioè l'utente l'ha visto e accettato.
2. **Brief del gate**, in una pagina, in conversazione o in `.build/congelamento.md` se è lungo. Il rischio di un congelamento è l'approvazione senza lettura: il brief rende la lettura breve e mirata.
   - In testa le decisioni difficili da invertire: scelta, alternativa scartata, ADR.
   - Gli scostamenti dallo stato dell'arte, da accettare.
   - Assunzioni, debito, debito di pubblicazione, e ciò che in locale non si verifica.
   - Gli esiti di prontezza e decidibilità, e i rischi del pre-mortem.
   - Cosa guardare per primo: dove un errore costerebbe di più, la matrice dei moduli ad alto rischio, i mockup dei percorsi critici.
   - Il piano in numeri: moduli, archetipi, task per ondata, incremento.
3. **Approvazione** esplicita dell'utente, poi:

   ```bash
   progetto.py congela --da <chi approva>
   ```

   Controlla la Definition of Ready alla data del giorno — ogni voce applicabile di `app-blueprint` delle fasi 0–7 chiusa, nessuna domanda aperta, deperibili verificati da quella data, debito accettato, prontezza e decidibilità superate nell'incremento, viste aggiornate — e solo se è verde scrive `[congelamento]` in `stato.toml` e chiude la 7.17.
4. **Commit, tag** con il nome che `congela` stampa, **push** se permesso. L'handoff di progettazione, se c'era, si toglie.

Da qui i contratti sono congelati: ogni cambio è una modifica (`gate.md`), e una modifica approvata dopo il congelamento lo annulla. La frontiera passa a `parallel-build`, che parte dagli ambienti e dallo scheletro.
