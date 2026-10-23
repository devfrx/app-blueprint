# Fase 5 — Progettazione di dettaglio

Porta l'architettura al livello a cui si costruisce senza decidere: ogni requisito assegnato a un modulo, l'interno di ogni modulo progettato, lo schema dei dati ricavato con il metodo classico, i contratti — API, errori, autorizzazioni, configurazione — abbastanza stabili da sviluppare in parallelo. Si congela l'interfaccia tra le parti, non l'interno: come un modulo implementa la sua facciata è affare di chi lo costruisce, entro i pattern dell'esemplare.

Le voci che dipendono dall'incremento (dettaglio dei moduli, contratti API, stabilità, revisione) si richiudono a ogni incremento; i dati si progettano una volta per tutte le funzionalità, e gli elementi che servono solo a incrementi futuri restano nello schema marcati dalla loro traccia.

Sorgenti: `moduli/<modulo>.toml`, `dati/dati.toml`, `sequenze/<PC-n>.md`, e i contratti in `contracts/`.

Indice: Moduli (5.01–5.04, 5.10, 5.11) · Dati (5.05.1–5.05.4, 5.05, 5.06) · Contratti (5.07, 5.09, 5.15, 5.16) · Sequenze (5.08) · Sicurezza (5.12) · Stabilità e revisione (5.13, 5.14).

## Moduli

**5.01** Ogni storia ha il `modulo` che la orchestra e i moduli che `tocca`; lo script controlla che nessuna resti senza. Una storia che attraversa più moduli la orchestra quello che ne possiede l'esito, e gli altri li usa tramite facciate o eventi.

**5.02** Ogni modulo dell'incremento ha il suo `moduli/<modulo>.toml`:

- `[[facciata]]`: le operazioni che offre agli altri moduli, con `firma`, `semantica` (cosa restituisce, quali effetti), `errori` del catalogo e `traccia`. È un contratto: lo scheletro la crea con un'implementazione finta, e ogni modulo si costruisce contro gli altri senza aspettarli. Lo script verifica che ogni dipendenza sincrona trovi una facciata.
- `[[eventi]]`: per la comunicazione asincrona, nome, `dati`, `consumatori`; ogni dipendenza asincrona ha un evento consumato da chi sta a valle.
- `[[componenti]]`: le parti interne con una responsabilità ciascuna, quando non sono ovvie dall'archetipo.
- `[[porte]]`: i confini verso altri moduli e verso l'esterno, ciascuno con il suo `finto` per i test (5.11).

**5.03** `[[pattern]]` solo dove risolvono un problema presente, con il problema scritto: un pattern senza problema è complessità che l'esemplare replicherà in ogni modulo.

**5.04** `[[algoritmi]]` dove la soluzione non è ovvia: il problema, la soluzione, la complessità valutata sui volumi della tavola (5.05.1). Un algoritmo quadratico su 50 righe non è un problema; su 50.000 sì.

**5.10** `[[transazioni]]` per le operazioni che scrivono più cose insieme o competono tra loro: il confine della transazione, l'isolamento, cosa succede con due richieste concorrenti, l'idempotenza. Tra moduli non si allungano le transazioni: se due moduli devono restare coerenti, saga o outbox, e l'ADR lo dice. `ST-concorrenza` dà le regole comuni.

**5.11** Testabilità: ogni dipendenza esterna dietro una porta con un finto, il tempo e la casualità iniettabili, nessuno stato globale implicito. È ciò che permette agli oracoli, scritti prima del codice, di eseguire il modulo da solo.

## Dati

Il metodo classico della progettazione logica: dallo schema concettuale (3.07) allo schema logico, passando per i numeri che giustificano ogni scelta. In `dati/dati.toml` le tavole e le decisioni, in `contracts/schema.toml` il risultato. Si fa per tutte le entità e relazioni, non solo per l'incremento.

### 5.05.1 Tavola dei volumi

`[[volumi]]` per ogni entità e relazione: `concetto` (`entita:…` o `relazione:…`), `volume` in istanze nell'orizzonte scelto, `crescita`, e la `fonte` (i requisiti sui dati) o il `calcolo` da cui viene. I volumi delle relazioni si ricavano da quelli delle entità e dalle cardinalità medie.

### 5.05.2 Tavola degli accessi

`[[accessi]]` per ogni operazione frequente o critica che le storie implicano: `operazione`, `tipo` (interattiva o batch), `frequenza` e `per` (ora, giorno…), la `traccia` verso storie e RNF, e il `cammino` sullo schema concettuale, passo per passo, con il concetto attraversato, il numero di `accessi` e il tipo, lettura `L` o scrittura `S`. I `filtri` sono le colonne su cui l'operazione seleziona. Il costo di un'operazione è la somma degli accessi pesata per la frequenza, con le scritture che valgono il doppio: è il numero che decide le scelte successive.

### 5.05.3 Ristrutturazione

Lo schema concettuale si trasforma in uno schema traducibile, con una decisione registrata in `[[ristrutturazione]]` per ogni punto, con il `motivo` e gli `accessi` che lo giustificano:

- **ridondanze**: ogni attributo derivato si tiene o si toglie confrontando il costo delle letture che risparmia con quello delle scritture che lo aggiornano;
- **generalizzazioni**: accorpamento dei figli nel padre, del padre nei figli, o sostituzione con relazioni, secondo come gli accessi leggono le entità;
- **partizionamenti e accorpamenti** di entità e relazioni, quando gli accessi leggono separatamente parti di un concetto, o sempre insieme due concetti;
- **identificatori principali**: per ogni entità con più identificatori, quale diventa la chiave; e se usare una chiave surrogata, e perché.

Lo script pretende una decisione per ogni generalizzazione, attributo derivato ed entità con più identificatori.

### 5.05.4 Traduzione e normalizzazione

`contracts/schema.toml`: ogni tabella dichiara il `modulo` proprietario e i concetti che traduce (`da`); ogni colonna l'attributo da cui nasce o la sua traccia; le chiavi esterne la relazione che traducono e le azioni referenziali (restrict, cascade, set-null, no-action). Le regole di traduzione sono quelle classiche: un'entità diventa una tabella; una relazione molti-a-molti una tabella con le chiavi dei partecipanti; uno-a-molti una chiave esterna dal lato "molti"; uno-a-uno una chiave esterna con vincolo d'unicità dal lato con partecipazione obbligatoria. Gli identificatori esterni diventano chiavi composte o chiavi esterne nella chiave.

Si verifica la forma normale di ogni tabella, e la si dichiara in `normalizzazione`: almeno la terza, o un `motivo` per scendere sotto, che di solito è una ridondanza decisa alla 5.05.3. I vincoli d'integrità che lo schema concettuale lasciava alle regole diventano, dove possono, `controlli` sulla tabella: ciò che il database garantisce non lo deve garantire ogni modulo.

Le chiavi esterne tra tabelle di moduli diversi portano il `motivo`: proteggono l'integrità, ma accoppiano i moduli, e un modulo non scrive mai le tabelle di un altro. Le tabelle che servono alla piattaforma e non al dominio (audit, code) sono `piattaforma = true` e citano la strategia che le richiede.

### 5.05 Schema fisico

Tipi concreti del database scelto, vincoli, e gli `indici` derivati dagli accessi: ogni indice cita gli accessi che lo giustificano, e ogni colonna su cui un accesso filtra è la prima colonna di un indice, di una chiave o di un vincolo d'unicità. Lo script verifica entrambe le direzioni. Le liste sono sempre paginate: è una regola del contratto, non una scelta di chi costruisce. Così i problemi classici dell'esercizio — query senza indice, elenchi illimitati — si chiudono in progettazione.

### 5.06 Migrazioni

`ST-migrazioni`: lo schema cambia con migrazioni compatibili con il rilascio progressivo, in due tempi (expand/contract): prima si aggiunge senza togliere, poi il codice passa al nuovo, poi si toglie il vecchio. Le migrazioni dell'incremento le scrive lo scheletro da `schema.toml`, con i soli elementi dell'incremento corrente.

## Contratti

**5.07 API.** `contracts/openapi.json` (o AsyncAPI per gli eventi esposti), nella versione decisa nello stack. Ogni operazione ha `operationId`, `x-modulo`, `x-storie`, `x-errori` con i codici del catalogo, almeno una risposta 4xx, ed esempi realistici per ogni risposta, errori compresi: gli esempi diventano i mock, e un mock che mostra solo dati felici fa costruire un'interfaccia senza stati vuoti e d'errore. Ogni lista porta `x-lista` e i parametri di paginazione dichiarati in `info.x-paginazione`; ogni operazione che farebbe danni se ripetuta dichiara l'idempotenza; versionamento e limiti di frequenza seguono le strategie. Le operazioni senza accesso sono dichiarate pubbliche con `security: []`, e sono le sole fuori dalla matrice: ogni altra nomina in `x-autorizzazione` la regola `risorsa.azione` che la consente, e lo script lo pretende. Senza quel legame la corrispondenza tra operazioni e regole la inventerebbe chi costruisce. Lo script avvisa per ogni storia dell'incremento senza operazioni.

**5.09 Errori.** `contracts/errori.toml`: un `codice` per errore con la `categoria` (cosa si recupera, cosa si propaga), lo stato `http`, se è `recuperabile`, il livello di `log`, e con un'interfaccia la chiave del testo che l'utente vede; più `[[validazioni]]`, una regola per campo con l'errore che produce. È la fonte unica per backend e frontend. `ST-errori` dice il formato della risposta: se lo stack non ne ha uno, uno standard come Problem Details evita di inventarlo (`FONTI.md`).

**5.15 Matrice delle autorizzazioni.** `contracts/autorizzazioni.toml`, in TOML perché lo legge lo script e lo applica il kernel condiviso:

- **negazione per default**: `predefinito = "nega"`;
- **i ruoli sono gli attori**, gli stakeholder con `usa = true`, né uno di più né uno di meno;
- **una regola per risorsa e azione**, con i ruoli che `consenti` e la `traccia` verso la storia o la minaccia che la chiede; una risorsa è un'entità, o una voce di `risorse` per ciò che entità non è, come la sessione. Ogni regola la applica almeno un'operazione (`x-autorizzazione`), altrimenti è un avviso;
- **le condizioni di proprietà esplicite**, nominate in `[condizioni]` e legate al ruolo a cui si applicano: "il cliente legge i *propri* interventi" è la regola che, dimenticata, lascia leggere quelli altrui cambiando un id nell'URL, il difetto d'accesso più comune;
- **il controllo vive nel backend**: nascondere un bottone è esperienza d'uso, non autorizzazione.

Ogni regola genera test in entrambe le direzioni, e ogni condizione il test con la risorsa di un altro.

**5.16 Configurazione.** `contracts/configurazione.toml`: le variabili con gli ambienti in cui servono e il default se c'è, e i nomi dei segreti con la rotazione. Mai i valori.

## 5.08 Sequenze dei percorsi critici

Per ogni percorso critico, `sequenze/<PC-n>.md` con le operazioni API e le facciate che attraversa nel frontmatter, e un `sequenceDiagram` Mermaid attraverso API, kernel e moduli. È qui che si vede se le facciate reggono il percorso: una chiamata che nessuna facciata offre è una lacuna del dettaglio.

## 5.12 Sicurezza verificata su ASVS

Per ogni classe di rischio si sceglie il livello di OWASP ASVS, nella versione stabile, che è un deperibile (`FONTI.md`): di solito il livello 1 per i moduli standard di un'app interna, il 2 per i moduli ad alto rischio o per un'app esposta, il 3 dove la criticità lo impone. Ogni modulo ha in `[sicurezza]` il suo `asvs` e i `requisiti` del livello che lo riguardano, scritti come regole verificabili: diventano regole della matrice, errori del catalogo, casi degli oracoli. Le contromisure del threat model (4.11) si ritrovano qui.

## Stabilità e revisione

**5.13** I contratti sono abbastanza stabili per sviluppare in parallelo quando nessuno dei controlli di schema, indici, API, errori, matrice, configurazione e dettaglio ha errori, e nessuna storia dell'incremento ha bisogno di un'operazione o di una facciata che non c'è.

**5.14** Un `reviewer` che non ha scritto il dettaglio lo rilegge per l'incremento: storie contro operazioni e facciate, accessi contro indici, matrice contro storie e minacce, errori contro criteri. I findings si correggono dove stanno.

## Gate

Il brief: lo schema logico con le decisioni della ristrutturazione che pesano di più, gli indici e gli accessi che li giustificano, le facciate tra i moduli, le operazioni dell'incremento, la matrice con le condizioni di proprietà, i livelli ASVS, l'esito della revisione. Da qui il dettaglio è ciò che i costruttori leggeranno: ogni lacuna diventerà una domanda in costruzione, o peggio un'interpretazione.
