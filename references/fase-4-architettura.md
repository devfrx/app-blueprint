# Fase 4 — Progettazione architetturale

Decide la forma del sistema: lo stile, i componenti e le loro dipendenze, le strategie trasversali, il deployment, la sicurezza per costruzione, le tecnologie. Ogni attributo di qualità prioritario esce dalla fase con una decisione che lo indirizza e un modo per verificarlo; ogni rischio tecnico maggiore ridotto o accettato. È la fase con più decisioni difficili da invertire: valgono le regole di `decisioni.md` per ricerca, presentazione e ADR.

L'architettura che rende parallelizzabile il lavoro degli agenti è la stessa che lo rende parallelizzabile per un team: moduli con confini netti, dati con un solo proprietario, contratti espliciti. È la legge di Conway applicata agli agenti, ed è il motivo per cui la progettazione arriva quasi sempre allo stesso stile.

Sorgenti: `architettura/` — `architettura.toml` (driver, strategie, ambienti, integrazioni), `minacce.toml`, `architettura.md`, `analisi.md`, `valutazione.md` — più `dominio/moduli.toml` per archetipi, rischio e comunicazione, e gli ADR.

## 4.01 Driver

`[[driver]]`: le funzionalità chiave, gli attributi di qualità prioritari e i vincoli che decidono l'architettura, ciascuno con i `ref` agli RNF, ai vincoli o ai percorsi da cui nasce e il `motivo`. Sono pochi, di solito da tre a sei: un driver che non orienta alcuna decisione non lo è.

## 4.02 Stile

**Default: monolite modulare.** Un deployabile, moduli con confini interni rigidi verificati da fitness function. Scala organizzativamente come i microservizi, senza rete, deploy multipli e consistenza distribuita da gestire; un modulo ben confinato si estrae più avanti, se un requisito lo chiede. Uno stile diverso — servizi separati, eventi distribuiti, code — si sceglie solo se un RNF misurato lo richiede, e l'ADR dice quale. "Scalabile" senza numero non è un requisito. L'ADR dello stile scrive anche i compromessi accettati.

## 4.03 Componenti, archetipi e rischio

I componenti sono i moduli della fase 3. Qui ognuno riceve:

- **l'archetipo**, perché moduli con forme diverse hanno pattern diversi, e replicare il pattern sbagliato produce codice coerente e sbagliato: `crud` (risorsa con elenco paginato, dettaglio, creazione, modifica, cancellazione), `workflow` (entità con macchina a stati e transizioni autorizzate), `integrazione` (dialogo con un servizio esterno: idempotenza, tentativi, riconciliazione), `reportistica` (aggregazioni in sola lettura, filtri, esportazioni), `tempo-reale` (aggiornamenti spinti al client);
- oppure **`motore = true`**, per la logica condivisa da più moduli che nessun archetipo descrive (un calcolo di prezzi, un motore di regole, un pianificatore), se la scelta build-buy-riuso dice di costruirla. Un motore ha un'API versionata, invarianti e una suite di conformità, e lo costruisce la sessione prima di chi lo usa;
- **la classe di rischio**, `standard` o `alto`. È `alto` se tocca anche solo una di queste cose: autenticazione o sessioni; autorizzazioni non banali, come condizioni di proprietà o deleghe; denaro; cancellazione o esportazione di dati personali; integrazioni che muovono denaro o dati personali; calcoli con conseguenze legali o contrattuali. Un modulo ad alto rischio riceve gate più severi nel piano (mutation testing, test basati su proprietà, revisione di sicurezza approfondita, diff guardato dall'utente).

Le regole di confine: ogni entità ha un solo modulo proprietario, e gli altri non ne toccano le tabelle; i moduli comunicano solo tramite facciate o eventi dichiarati; le dipendenze vanno in una direzione. Lo script verifica proprietari e cicli.

## 4.04 Interfacce tra componenti

Per ogni dipendenza della context map, la `comunicazione`: sincrona tramite facciata (il default dentro un monolite) o asincrona tramite eventi (quando chi pubblica non deve aspettare, o deve ignorare chi consuma). La strategia `ST-versionamento` dice come evolvono API pubbliche, facciate ed eventi senza rompere chi li usa. Le firme si scrivono nella fase 5.

## 4.05 e 4.06 Dati, RPO e RTO

`ST-dati`: quale storage per ogni bisogno (relazionale per default; altro solo con un requisito), il modello di consistenza, partizionamento e replica se i volumi li chiedono, la conservazione. Gli obiettivi di RPO e RTO sono un RNF di affidabilità; `ST-backup` dice come il backup li rispetta e come si prova il ripristino. Un backup mai ripristinato non è una strategia.

## 4.07 e 4.09 Integrazioni e resilienza

Ogni sistema con `integrazione = true` ha la sua voce in `[[integrazioni]]`: modulo che la possiede, protocollo, `timeout`, `tentativi`, `idempotenza`, cosa succede quando il sistema non risponde (`guasto`) e dove si prova (`ambiente_prova`). `ST-resilienza` dice le regole comuni: timeout su ogni chiamata esterna, retry con backoff e jitter solo per le operazioni idempotenti, circuit breaker dove un guasto si propagherebbe, degrado controllato.

## 4.08 Strategie trasversali

Una strategia per ogni preoccupazione che attraversa i moduli, in `[[strategie]]` con id `ST-<tema>`, la `decisione`, il `motivo` e l'`adr` se viene da una decisione difficile da invertire: autenticazione, autorizzazione, errori, osservabilità, configurazione, cache, concorrenza, segreti, audit, i18n, tempo e fusi; denaro con l'innesco `denaro`, multi-tenancy con `multitenant`. Lo script le pretende tutte: una preoccupazione senza strategia la decide ogni costruttore a modo suo. "Nessuna cache" è una strategia legittima, se scritta con il motivo.

## 4.10 Deployment

`[[ambienti]]` con scopo, dove è ospitato, che dati contiene (sintetici, anonimizzati, reali) e chi vi accede; in `architettura.md` la vista di deployment in Mermaid, con rete, scalabilità e infrastruttura come codice. Gli ambienti che servono dipendono dal profilo: in un progetto personale locale e produzione possono bastare, e la 7.09 li rende disponibili.

## 4.11 Threat model

Proporzionato al rischio: leggero per un gestionale interno, approfondito dove ci sono denaro, dati personali o azioni irreversibili. Si fa sui percorsi critici, con i diagrammi davanti, in `minacce.toml`:

1. **Asset**: i dati e le funzioni che vale la pena proteggere.
2. **Attori**: gli stakeholder che usano il prodotto, più l'anonimo e un utente legittimo che prova a uscire dal suo perimetro.
3. **`[[confini]]` di fiducia**: dove i dati passano da un contesto meno fidato a uno più fidato (browser → API, API → database, API ↔ servizi esterni, webhook in ingresso).
4. **`[[flussi]]`** che li attraversano, con i dati che portano e i percorsi critici di cui fanno parte.
5. **`[[minacce]]`** per flusso, con le sei domande STRIDE: qualcuno può fingersi un altro (S)? alterare un dato (T)? negare di aver agito (R)? leggere ciò che non deve (I)? rendere il servizio inutilizzabile (D)? ottenere più permessi di quanti ne ha (E)? Ognuna con probabilità, impatto, `contromisure` e rischio `residuo`.

Ogni contromisura è un requisito testabile, citato per id: una regola della matrice, un errore del catalogo, una strategia, una regola di business, un RNF. Da lì finisce negli oracoli. I livelli di verifica di OWASP ASVS si applicano nella fase 5 (5.12).

## 4.12 Analisi quantitative

Con esposizione da pubblicabile in su o criticità alta, in `analisi.md`, con i numeri dei requisiti sui dati e degli RNF: capacità (righe e spazio nell'orizzonte di crescita), prestazioni (le operazioni più frequenti contro i budget degli RNF), costi d'infrastruttura (contro il vincolo di budget), affidabilità (disponibilità del deployment scelto, RPO e RTO realistici). Le stime si dichiarano come assunzioni. Un'analisi che dimostra che il caso semplice regge è un risultato: evita la complessità che nessun numero chiede.

## 4.13 Tecnologie

Si scelgono su criteri espliciti — maturità, supporto e licenza, competenze di chi manterrà l'app, lock-in, costo totale — con un `researcher` per scelta e la verifica delle fonti (`decisioni.md`). Insieme allo stack si scelgono gli strumenti che lo rendono adatto al metodo: generazione di codice e mock dal contratto, test per modulo eseguibili in isolamento, fitness function sui confini tra moduli. Versioni e finestre di supporto sono deperibili. Una decisione presa per vincolo non si ricerca: l'ADR cita il vincolo.

## 4.14 Spike

Le incognite che solo il codice risolve si riducono qui, prima di specificare: `decisioni.md`, *Spike*. La voce si chiude quando non restano domande con un criterio aperte, e gli esiti stanno negli ADR o nei rischi che ne dipendevano.

## 4.15 Valutazione dell'architettura

Con esposizione da pubblicabile in su o criticità da media in su, una revisione in stile ATAM, proporzionata, in `valutazione.md`, fatta da un `reviewer` che non ha scritto l'architettura:

1. si parte dagli scenari di qualità di rilevanza alta, cioè gli RNF, ordinati per importanza e difficoltà;
2. per ogni scenario, le decisioni che lo indirizzano;
3. per ciascuna, i punti sensibili (dove un piccolo cambio sposta molto la qualità), i compromessi (dove migliorare una qualità ne peggiora un'altra), i rischi e i non-rischi;
4. un esito: rischi accettati, da mitigare o da riportare alle decisioni.

## 4.16 Ogni qualità ha la sua decisione

Ogni RNF ha in `indirizzato_da` le decisioni che lo soddisfano: ADR, strategie, accessi, regole. Lo script lo pretende per le caratteristiche di rilevanza alta. La prova di ogni RNF, scritta in fase 2, è il modo di verificarlo: se la decisione la rende impossibile, si cambia una delle due.

## 4.17 e 4.18 ADR e diagrammi

Un ADR per decisione difficile da invertire (`decisioni.md`); lo script controlla sezioni, stato e citazioni. In `architettura.md` i diagrammi C4 di container e la vista di deployment, in Mermaid; contesto e moduli sono generati. Il diagramma dice cosa c'è, l'ADR perché.

## 4.19 Rischi residui

Nessun rischio tecnico resta `aperto` alla fine della fase: ridotto (con uno spike, una decisione), chiuso, o accettato dall'utente con un responsabile e il segnale che lo farà emergere.

## Gate

Il brief: stile e moduli con archetipi e rischio, le decisioni difficili da invertire in testa con le alternative scartate, le strategie trasversali in una riga ciascuna, le minacce principali e le loro contromisure, gli esiti di analisi e valutazione, i rischi accettati. Da qui stack, stile e confini sono la base di tutto il dettaglio.
