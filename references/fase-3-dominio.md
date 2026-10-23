# Fase 3 — Analisi e modellazione del dominio

Costruisce il modello che spiega tutte le funzionalità: concetti, relazioni, regole, cicli di vita, e i confini dentro cui ciascuno vive. È la progettazione concettuale classica — schema E/R, dizionario dei dati, vincoli non esprimibili nello schema — unita alla progettazione strategica del domain-driven design, che trasforma i confini del linguaggio in confini dei moduli. Si fa una volta, per tutti gli incrementi.

Sorgenti: `dominio/` — `glossario.toml`, `regole.toml`, `moduli.toml`, `entita.toml`, `stati.toml`, `processi/<id>.md`. Le viste `er-concettuale.md`, `stati.md` e `moduli.md` sono i diagrammi, generati.

## 3.07 Lo schema concettuale

La voce centrale della fase, e quella da cui dipendono dati, contratti e moduli. Si costruisce dai requisiti con una strategia mista: prima uno schema scheletro con i concetti principali delle storie e dei requisiti sui dati, poi lo si raffina area per area, integrando i pezzi e risolvendo i conflitti di nome e di struttura.

- **Entità**: i concetti con esistenza autonoma e istanze da distinguere. Ognuna ha il `termine` del glossario, la `descrizione` (è il dizionario dei dati), gli `attributi` e almeno un identificatore. Un nome che non ha attributi propri e vive solo legato a un altro concetto è di solito un attributo; un attributo che ha attributi suoi o partecipa a relazioni è un'entità.
- **Attributi**: `nome`, `dominio` concettuale (testo, email, intero, decimale, denaro, data, istante, booleano, enumerazione, o un dominio del progetto come codice fiscale o targa), `descrizione`; `obbligatorio = false`, `multiplo = true` (multivalore), `composto = [i componenti]`, `derivato` dove vale; multivalori e composti si risolvono alla ristrutturazione (5.05.3). Un attributo derivato si dichiara come tale: decidere se memorizzarlo è una scelta della ristrutturazione (5.05.3), non del modello. Nessun tipo fisico, nessuna chiave artificiale: lo schema è indipendente dalla tecnologia.
- **Identificatori**: liste di attributi; `relazione:<id>` dentro un identificatore per l'identificazione esterna, quando un'entità si distingue solo attraverso un'altra (la riga 3 *di quel* preventivo).
- **Relazioni**: `nome` (un verbo), `partecipanti` con le cardinalità `min` 0 o 1 e `max` 1 o `"N"`, cioè quante volte ogni istanza di quell'entità partecipa; gli attributi della relazione se ne ha; la `traccia` verso le storie. Una relazione con più di due partecipanti si modella come tale e non si spezza in coppie: perderebbe il suo significato.
- **Generalizzazioni**: padre, figli, `copertura` totale o parziale, `disgiunzione` esclusiva o sovrapposta. Le proprietà comuni stanno nel padre; i figli ne ereditano anche l'identificatore.
- **Proprietario**: ogni entità ha il suo `modulo`, uno solo. Si assegna dopo la 3.03, ed è la regola che rende il lavoro parallelizzabile: gli altri moduli passano dalla sua facciata.

Qualità da verificare prima di chiudere: correttezza (i costrutti sono usati come vuole il modello), completezza (ogni dato dei requisiti è da qualche parte), leggibilità, minimalità (nessuna ridondanza non dichiarata). Ciò che lo schema non sa dire va nelle regole.

## 3.01 e 3.08 Regole, invarianti, eccezioni

`regole.toml`: `R-n` con `tipo` regola, invariante o eccezione, il `testo`, le `entita` coinvolte, la `traccia`. Una regola dice cosa è ammesso ("si chiude solo con il preventivo approvato"); un invariante cosa resta sempre vero ("i totali li calcola solo il motore"); un'eccezione il caso limite di business e cosa succede allora. Gli oracoli le proveranno una a una, quindi ognuna dev'essere verificabile da un test. I casi limite si cercano storia per storia: cosa succede con zero, con il massimo, con due operazioni insieme, con un dato già usato, a cavallo dell'anno.

## 3.02 Linguaggio ubiquo

Il glossario diventa il linguaggio del modello: ogni entità usa un termine del glossario, e lo script lo verifica; i nomi delle relazioni e degli stati sono quelli che usa chi lavora nel dominio. Un termine tecnico che l'esperto non riconosce è un segnale: o il modello è sbagliato, o manca una parola nel glossario.

## 3.03 e 3.04 Sottodomini, moduli e context map

- **Sottodomini** classificati: `core` (ciò che distingue il prodotto, dove si investe il progetto migliore), `supporto` (necessario ma non distintivo), `generico` (risolto da altri: autenticazione, posta, pagamenti, spesso comprato o preso da una libreria).
- **Bounded context**: i confini dentro cui un termine ha un significato solo. Ogni bounded context è un modulo — un solo confine da progettare, possedere e verificare — con la sua `responsabilita` in una riga. Un modulo grande quanto un'app è un confine mancato; venti moduli per venti entità sono confini inventati.
- **Context map**: `[[dipendenze]]` da un modulo `a_valle` a quello `a_monte` da cui dipende, con il `tipo` di relazione (cliente-fornitore, conformista, anticorruzione, servizio aperto, linguaggio pubblicato, kernel condiviso, partnership). Le dipendenze vanno in una sola direzione: lo script rifiuta i cicli, che renderebbero impossibile costruire un modulo prima dell'altro. La `comunicazione`, sincrona o asincrona, si decide alla 4.04.

## 3.05 Processi

I processi principali in `processi/<id>.md`, con il frontmatter (`id`, `titolo`, `tipo`, `storie`, `entita`) e un diagramma Mermaid: diagramma di attività per un flusso con passaggi di mano, casi d'uso per le interazioni di un attore, Event Storming per un dominio pieno di eventi. Si modellano i processi che attraversano più storie o più ruoli, non ogni storia.

## 3.06 Macchine a stati

Ogni entità con un ciclo di vita ha la sua macchina in `stati.toml`: `stati`, `iniziale`, `finali`, e le `transizioni` con l'evento, i `ruoli` che possono scatenarle, la `guardia` se c'è, la `traccia`. Le transizioni elencate sono le sole ammesse: tutte le altre sono vietate, e la vista le elenca perché gli oracoli le provino. Lo script controlla che ogni stato sia raggiungibile.

## 3.09 Il modello alla prova delle storie

Ogni storia, di ogni incremento, riceve le `entita` che usa, il `modulo` che la orchestra e i moduli che `tocca`. Poi un `reviewer` fa il walkthrough: storia per storia, criterio per criterio, segue il percorso nel modello — quali entità si leggono e si scrivono, quali transizioni, quali regole — e riporta dove il modello non basta o si contraddice. Un modello che spiega le storie dell'incremento 1 ma non quelle del 3 costringerà a rifare lo schema proprio quando ci sono dati veri.

## 3.10 Approvazione degli esperti

L'utente, e gli esperti di dominio che indica, rileggono il modello attraverso le viste generate e i processi: riconoscono i loro concetti, le loro regole, i loro stati? La revisione registra chi ha approvato e cosa è cambiato.

## Gate

Il brief: lo schema E/R e i moduli con i loro proprietari, le regole più delicate, le macchine a stati, gli esiti del walkthrough e dell'approvazione. Da qui le entità, le relazioni e i confini dei moduli sono la base di dati, contratti e piano: cambiarli dopo è una modifica con un impatto largo.
