<!-- Generato da app-blueprint (progetto.py viste): non modificare a mano. Le sorgenti sono in docs/progettazione/ e contracts/. -->

# Checklist dei gate

Esposizione **pubblicabile**, criticità **media**, inneschi: ui, dati-personali, denaro, integrazioni. Incremento corrente: **1**; ↻ segna le voci che si richiudono a ogni incremento, e per loro vale la chiusura dell'incremento corrente.

## 0. Precondizioni

**Gate:** Il repo conserva il lavoro, i sotto-agenti vedono ciò che è committato e hanno le skill giuste.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 0.01 | fatta | Repo git con il branch d'integrazione attivo; in un ambiente effimero il lavoro si pusha a ogni chiusura, con il permesso dell'utente | tag:progettazione/gate-0-2026-10-05 |
| 0.02 | fatta | `.build/` esclusa da git, `.claude/worktrees/` ignorata, `worktree.baseRef` impostato a "head" | tag:progettazione/gate-0-2026-10-05 |
| 0.03 | fatta | Agenti installati in `.claude/agents/` e provati con la sonda, oppure ripiego dichiarato | tag:progettazione/gate-0-2026-10-05 |
| 0.04 | fatta | Convenzioni del repo rilevate: percorsi e formati già in uso per ADR, design e contratti | tag:progettazione/gate-0-2026-10-05 |
| 0.05 | fatta | Stato della progettazione inizializzato: stato.toml, gate.toml e registri.toml dall'esempio, senza congelamento | stato.toml, gate.toml, registri.toml |

## 1. Avvio, analisi del problema e fattibilità

**Gate:** C'è una decisione formale di procedere, fondata su obiettivi misurabili e su un perimetro scritto.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 1.01 | fatta | Problema descritto senza riferimenti a una soluzione | prodotto/visione.md#problema |
| 1.02 | fatta | Obiettivi misurabili, ciascuno con metrica e valore atteso | OB-1, OB-2, OB-3 |
| 1.03 | fatta | Stakeholder identificati, inclusi esercizio, sicurezza e legale, con interesse e influenza | prodotto/prodotto.toml#stakeholder |
| 1.04 | fatta | Contesto analizzato: processi attuali, sistemi da integrare, soluzioni esistenti | prodotto/visione.md#contesto, sistema:smtp, sistema:sito |
| 1.05 | fatta | Fattibilità valutata su tutti gli assi: tecnica, economica (sviluppo ed esercizio), operativa, legale, temporale | prodotto/prodotto.toml#fattibilita, prodotto/visione.md#fattibilita |
| 1.06 | fatta | Alternative make, buy, riuso e SaaS confrontate, con la scelta motivata | ADR-0001 |
| 1.07 | non-applicabile | Se commissionato o acquistato: contratto, proprietà intellettuale, criteri di accettazione e livelli di servizio definiti | condizione falsa per la scheda (quando: innesco commissionato) |
| 1.08 | fatta | Scope e non-scope scritti | prodotto/visione.md#perimetro, NO-1 |
| 1.09 | fatta | Vincoli raccolti: budget, scadenze, tecnologie imposte, competenze disponibili | V-1, V-2, V-3, V-4 |
| 1.10 | fatta | Registro dei rischi aperto con i rischi iniziali | RK-1, RK-2, RK-3 |
| 1.11 | fatta | Stima d'ordine di grandezza, con l'incertezza dichiarata | prodotto/prodotto.toml#stima |
| 1.12 | fatta | Decisione go/no-go registrata | stato.toml#registro |
| 1.13 | fatta | Scheda compilata: esposizione, criticità, inneschi, modello di processo | stato.toml#scheda |
| 1.14 | fatta | Verdetto d'ingresso espresso: nebbia, fuori-metodo, incremento-unico o incrementi | stato.toml#scheda |

## 2. Ingegneria dei requisiti

**Gate:** I requisiti di tutte le funzionalità sono inventariati, quelli dell'incremento corrente prioritizzati, verificabili e approvati.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 2.01 | fatta | Requisiti raccolti da tutti gli stakeholder rilevanti, con tecniche adatte al contesto | requisiti/storie.toml, REV-1 |
| 2.02 ↻ | fatta | Requisiti funzionali specificati come user story con criteri di accettazione: l'inventario copre tutte le funzionalità di tutti gli incrementi, i criteri quelle dell'incremento corrente | requisiti/storie.toml |
| 2.03 | fatta | Le nove caratteristiche di qualità della ISO/IEC 25010:2023 passate in rassegna; quelle rilevanti scelte e motivate | requisiti/requisiti.toml#qualita |
| 2.04 | fatta | Ogni requisito non funzionale quantificato con uno scenario misurabile: stimolo, contesto, risposta, misura | RNF-1, RNF-2, RNF-3, RNF-4, RNF-5, RNF-6, RNF-7 |
| 2.05 | fatta | Vincoli, interfacce e requisiti sui dati documentati (volumi, crescita, conservazione, qualità) | RD-1, RD-2, RD-3, RD-4, V-1, sistema:smtp |
| 2.06 | fatta | Requisiti di conformità identificati: privacy (GDPR), accessibilità, sicurezza dei prodotti (Cyber Resilience Act), IA (AI Act), norme di settore | V-5, V-6, V-7 |
| 2.07 ↻ | fatta | Ogni requisito necessario, non ambiguo, singolo, verificabile, coerente e fattibile | REV-1 |
| 2.08 | fatta | Conflitti tra stakeholder risolti e registrati | CO-1 |
| 2.09 | fatta | Priorità assegnate con un metodo esplicito | requisiti/requisiti.toml#metodo_priorita |
| 2.10 ↻ | fatta | Requisiti validati con gli stakeholder tramite revisione, prototipo o walkthrough | REV-2 |
| 2.11 | fatta | Baseline e procedura di gestione delle modifiche definite | tag:progettazione/gate-2-2026-10-10 |
| 2.12 | fatta | Matrice di tracciabilità avviata | viste/tracciabilita.md |
| 2.13 | fatta | Glossario condiviso | dominio/glossario.toml |
| 2.14 | fatta | Funzionalità trasversali passate in rassegna, ognuna con le sue storie o tra i non-obiettivi | requisiti/requisiti.toml#trasversali |
| 2.15 | fatta | Percorsi critici individuati: le sequenze di storie che, se si rompono, rendono l'app inutile | PC-1, PC-2 |

## 3. Analisi e modellazione del dominio

**Gate:** Il modello spiega tutte le funzionalità senza contraddizioni e l'utente lo riconosce come proprio.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 3.01 | fatta | Modello di dominio con concetti, relazioni, invarianti e regole di business | dominio/entita.toml, dominio/regole.toml |
| 3.02 | fatta | Linguaggio ubiquo allineato al glossario e usato sia dai tecnici sia dagli esperti | dominio/glossario.toml |
| 3.03 | fatta | Sottodomini classificati (core, di supporto, generici) e bounded context individuati: ogni bounded context è un modulo | dominio/moduli.toml |
| 3.04 | fatta | Context map delle relazioni tra i contesti | viste/moduli.md |
| 3.05 | fatta | Processi principali modellati: casi d'uso, diagrammi di attività o Event Storming | processo:ciclo-intervento, processo:accesso-e-attivazione |
| 3.06 | fatta | Ogni entità con un ciclo di vita modellata come macchina a stati, con transizioni ammesse e vietate | dominio/stati.toml, viste/stati.md |
| 3.07 | fatta | Modello concettuale dei dati, indipendente dalla tecnologia: entità, attributi, identificatori, generalizzazioni, relazioni con cardinalità, dizionario dei dati | dominio/entita.toml, viste/er-concettuale.md |
| 3.08 | fatta | Casi limite ed eccezioni di business documentati | R-5, R-6, R-9 |
| 3.09 | fatta | Modello provato su tutte le storie, senza contraddizioni | REV-3 |
| 3.10 | fatta | Modello rivisto e approvato dagli esperti di dominio | REV-4 |

## 4. Progettazione architetturale

**Gate:** Ogni attributo di qualità prioritario ha una decisione che lo indirizza e un modo per verificarlo; i rischi tecnici maggiori sono ridotti o accettati.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 4.01 | fatta | Driver architetturali elencati: funzionalità chiave, attributi di qualità prioritari, vincoli | DR-1, DR-2, DR-3, DR-4 |
| 4.02 | fatta | Stile architetturale scelto, con i compromessi accettati scritti | ADR-0003 |
| 4.03 | fatta | Componenti definiti con responsabilità, proprietà esclusiva dei dati e dipendenze in una sola direzione | dominio/moduli.toml |
| 4.04 | fatta | Interfacce e contratti tra componenti definiti: sincroni o asincroni, formati, versioning | dominio/moduli.toml, ST-versionamento |
| 4.05 | fatta | Architettura dei dati definita: storage per ogni bisogno, modello di consistenza, partizionamento, replica, conservazione | ST-dati |
| 4.06 | fatta | Obiettivi RPO e RTO fissati, con una strategia di backup coerente | RNF-2, ST-backup |
| 4.07 | fatta | Integrazioni esterne definite, incluso il comportamento quando il sistema esterno non risponde | integrazione:smtp |
| 4.08 | fatta | Strategie trasversali decise: autenticazione e autorizzazione, errori, osservabilità, configurazione, caching, concorrenza, segreti, audit, internazionalizzazione | architettura/architettura.toml#strategie |
| 4.09 | fatta | Meccanismi di resilienza scelti: timeout, retry con backoff e jitter, circuit breaker, idempotenza, degrado controllato | ST-resilienza |
| 4.10 | fatta | Vista di deployment: ambienti, infrastruttura, rete, scalabilità, infrastruttura come codice | architettura/architettura.md, ambiente:produzione |
| 4.11 | fatta | Threat model su flussi di dati e confini di fiducia, con le contromisure | architettura/minacce.toml |
| 4.12 | fatta | Analisi quantitative svolte: capacità, prestazioni, costi infrastrutturali, affidabilità | architettura/analisi.md |
| 4.13 | fatta | Tecnologie scelte su criteri espliciti: maturità, supporto e licenza, competenze, lock-in, costo totale | ADR-0002, DEP-1, DEP-2, DEP-3 |
| 4.14 | fatta | Incognite principali ridotte con spike o proof of concept, con gli esiti documentati | RK-2, ADR-0002 |
| 4.15 | fatta | Architettura valutata contro gli scenari di qualità con una revisione strutturata (es. ATAM) | architettura/valutazione.md, REV-5 |
| 4.16 | fatta | Ogni attributo di qualità prioritario ha almeno una decisione che lo indirizza e un modo per verificarlo | viste/tracciabilita.md |
| 4.17 | fatta | Un ADR per ogni decisione significativa: contesto, alternative, scelta, conseguenze | ADR-0001, ADR-0002, ADR-0003, ADR-0004, ADR-0005, ADR-0006 |
| 4.18 | fatta | Diagrammi (C4 o 4+1) versionati come testo accanto al codice | architettura/architettura.md, viste/contesto.md, viste/moduli.md |
| 4.19 | fatta | Rischi tecnici residui accettati esplicitamente, ciascuno con un responsabile | RK-2, RK-4, RK-5 |

## 5. Progettazione di dettaglio

**Gate:** Ogni requisito in scope è assegnato a un modulo e i contratti sono abbastanza stabili per sviluppare in parallelo.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 5.01 | fatta | Ogni requisito in scope assegnato a un componente | requisiti/storie.toml |
| 5.02 ↻ | fatta | Responsabilità interne dei componenti definite: alta coesione, basso accoppiamento, information hiding | moduli/accessi.toml, moduli/clienti.toml, moduli/veicoli.toml, moduli/interventi.toml, moduli/prezzi.toml, moduli/fatture.toml |
| 5.03 ↻ | fatta | Pattern usati solo dove risolvono un problema presente, con il motivo scritto | moduli/prezzi.toml, moduli/accessi.toml |
| 5.04 ↻ | fatta | Algoritmi e strutture dati scelti, con la complessità valutata sui volumi previsti | moduli/prezzi.toml, moduli/fatture.toml, moduli/veicoli.toml |
| 5.05 | fatta | Schema dati logico e fisico: chiavi, vincoli di integrità, indici derivati dalle query reali | contracts/schema.toml |
| 5.05.1 | fatta | Tavola dei volumi: entità e relazioni con il numero stimato di istanze e la crescita | dati/dati.toml#volumi |
| 5.05.2 | fatta | Tavola degli accessi: per ogni operazione frequente, frequenza, concetti attraversati, letture e scritture | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10 |
| 5.05.3 | fatta | Ristrutturazione dello schema concettuale: ridondanze, generalizzazioni, partizionamenti e accorpamenti, identificatori principali, decisi sui numeri delle tavole | dati/dati.toml#ristrutturazione |
| 5.05.4 | fatta | Traduzione nel modello logico e normalizzazione, con ogni denormalizzazione motivata | contracts/schema.toml, viste/er-logico.md |
| 5.06 | fatta | Migrazioni di schema compatibili con il rilascio progressivo (expand/contract) | ST-migrazioni |
| 5.07 ↻ | fatta | Contratti API formalizzati (OpenAPI o AsyncAPI): errori, paginazione, idempotenza, versioning, limiti di frequenza | contracts/openapi.json, viste/api.md |
| 5.08 | fatta | Flussi critici descritti con diagrammi di sequenza | sequenza:PC-1, sequenza:PC-2 |
| 5.09 | fatta | Tassonomia degli errori: cosa si recupera, cosa si propaga, cosa vede l'utente, cosa si registra | contracts/errori.toml, ST-errori |
| 5.10 ↻ | fatta | Concorrenza e transazioni progettate: isolamento, race condition, saga o outbox se distribuite | moduli/interventi.toml, moduli/fatture.toml, ST-concorrenza |
| 5.11 ↻ | fatta | Testabilità garantita: dipendenze iniettabili, confini esterni isolati | moduli/accessi.toml, moduli/clienti.toml, moduli/veicoli.toml, moduli/interventi.toml, moduli/prezzi.toml, moduli/fatture.toml |
| 5.12 ↻ | fatta | Requisiti di sicurezza verificati su un catalogo come OWASP ASVS | moduli/accessi.toml, moduli/clienti.toml, moduli/veicoli.toml, moduli/interventi.toml, moduli/prezzi.toml, moduli/fatture.toml, DEP-4 |
| 5.13 ↻ | fatta | Contratti abbastanza stabili da permettere lo sviluppo in parallelo | contracts/schema.toml, contracts/openapi.json, contracts/autorizzazioni.toml, contracts/errori.toml |
| 5.14 ↻ | fatta | Design revisionato da qualcuno che non l'ha scritto | REV-6 |
| 5.15 | fatta | Matrice delle autorizzazioni completa: negazione per default, un ruolo per attore, condizioni di proprietà esplicite | contracts/autorizzazioni.toml |
| 5.16 | fatta | Configurazione definita: variabili e nomi dei segreti, mai i valori | contracts/configurazione.toml |

## 6. Progettazione UX/UI

**Gate:** I flussi prioritari reggono la revisione di usabilità del profilo e rispettano i criteri di accessibilità. Corre intrecciata alle fasi 2–5.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 6.01 | fatta | Ricerca utente svolta; personas e user journey documentati | ux/utenti.md, persona:giulia, persona:marco, persona:anna |
| 6.02 | fatta | Architettura dell'informazione definita: struttura, navigazione, terminologia | ux/ux.toml#sezioni |
| 6.03 ↻ | fatta | Wireframe e prototipi dei flussi prioritari | docs/design/mockups/accesso.html, docs/design/mockups/interventi.html, docs/design/mockups/intervento.html, docs/design/mockups/area-cliente.html, docs/design/mockups/fattura.html |
| 6.04 | fatta | Design system con token e componenti, oppure adozione motivata di uno esistente | ux/design-system.toml |
| 6.05 ↻ | fatta | Ogni schermata progettata in tutti gli stati: vuoto, caricamento, errore, parziale, successo, permessi insufficienti | ux/ux.toml#schermate |
| 6.06 ↻ | fatta | Criteri WCAG 2.2 di livello AA, o del livello richiesto, applicati al design | REV-8 |
| 6.07 ↻ | fatta | Messaggi d'errore e microcopy che dicono cosa è successo e cosa fare | ux/testi.toml |
| 6.08 ↻ | rinviata | Test di usabilità sui prototipi con utenti reali; problemi principali risolti | voce di esercizio rinviata al passaggio al pubblico (quando: innesco ui e esposizione >= pubblico) |
| 6.09 | fatta | Varianti per dispositivo e internazionalizzazione considerate | ST-i18n |
| 6.10 ↻ | fatta | Revisione euristica di usabilità dei mockup, prima di quella con utenti reali | REV-7 |

## 7. Pianificazione della realizzazione

**Gate:** Il progetto è congelato con il piano validato, e un walking skeleton gira end-to-end in un ambiente simile alla produzione.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 7.01 ↻ | fatta | Lavoro scomposto in task e ondate, con dipendenze e percorso critico | piano/piano.toml |
| 7.02 ↻ | fatta | Stime prodotte con un metodo dichiarato e con l'incertezza esplicita | piano/piano.toml#stima |
| 7.03 | fatta | Roadmap, milestone e piano dei rilasci, con il primo incremento di valore (MVP) identificato | piano/piano.toml#incrementi |
| 7.04 ↻ | fatta | Team e ownership dei moduli assegnati | piano/piano.toml#task |
| 7.05 | fatta | Strategia di test scritta: livelli, tipi, ambienti, dati di test, automazione, criteri di ingresso e uscita, tecniche di progettazione dei casi | piano/test.toml |
| 7.06 | fatta | DoD di incremento adottata e condivisa | viste/checklist.md#dod |
| 7.07 | fatta | Repository, strategia di branching, linter, formatter e analisi statica decisi | ST-qualita-codice, ADR-0002 |
| 7.08 | fatta | Pipeline CI/CD progettata | ST-ci-cd |
| 7.09 | aperta | Ambienti disponibili: sviluppo, test, staging, produzione, secondo il profilo |  |
| 7.10 | aperta | Walking skeleton che attraversa tutti gli strati dell'architettura |  |
| 7.11 ↻ | fatta | Registro dei rischi aggiornato | registri.toml#rischi |
| 7.12 ↻ | fatta | Modalità di costruzione decisa: parallela con parallel-build, o seriale in una sessione | stato.toml#scheda |
| 7.13 ↻ | fatta | Revisione di prontezza senza P0 né P1 | REV-9 |
| 7.14 ↻ | fatta | Prova di decidibilità senza domande: un reviewer prepara la costruzione di ogni esemplare con i soli file del repo | REV-10 |
| 7.15 ↻ | fatta | Riferimenti deperibili riverificati alla data del congelamento | DEP-1, DEP-2, DEP-3, DEP-4, DEP-5, DEP-6 |
| 7.16 ↻ | fatta | Pre-mortem svolto: ogni causa plausibile corretta o accettata come rischio con il suo segnale | REV-11 |
| 7.17 ↻ | fatta | Progetto congelato: brief del gate letto, approvazione dell'utente, tag progettazione/incremento-N-<data> | stato.toml#congelamento |

## 8. Implementazione

**Gate:** Ogni task del perimetro ha superato la DoD di incremento e i controlli sull'intera base di codice sono verdi.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 8.01 ↻ | aperta | Ogni incremento del perimetro ha superato la DoD di incremento |  |
| 8.02 ↻ | aperta | Linter, formatter e analisi statica attivi in pipeline su tutto il codice |  |
| 8.03 ↻ | aperta | Nessun problema bloccante aperto da SAST e SCA |  |
| 8.04 ↻ | aperta | Licenze di tutte le dipendenze verificate e compatibili |  |
| 8.05 ↻ | rinviata | SBOM (CycloneDX o SPDX) aggiornata all'ultima build | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico o innesco mercato-ue) |
| 8.06 ↻ | aperta | Verifica automatica dei segreti attiva; nessun segreto nel repository |  |
| 8.07 ↻ | aperta | Build riproducibile da qualunque commit |  |
| 8.08 ↻ | aperta | Feature flag temporanei rimossi o con una data di rimozione |  |
| 8.09 ↻ | aperta | Registro del debito tecnico aggiornato e rivisto |  |
| 8.10 ↻ | aperta | Documentazione tecnica allineata al codice |  |
| 8.11 ↻ | aperta | Oracoli scritti prima del codice da chi non costruisce, rossi per la ragione giusta |  |
| 8.12 ↻ | aperta | Esemplari approvati dall'utente e prova a secco superata prima dell'ondata di costruzione |  |
| 8.13 ↻ | aperta | Elenco dei moduli in attesa vuoto: nessun oracolo escluso dalla suite |  |

## 9. Integrazione

**Gate:** Il sistema integrato si installa e funziona in un ambiente di test simile alla produzione.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 9.01 ↻ | aperta | Strategia di integrazione esplicita, continua o per incrementi, senza "big bang" |  |
| 9.02 ↻ | aperta | Test di integrazione con dipendenze reali o containerizzate verdi |  |
| 9.03 ↻ | aperta | Contract test tra moduli e verso l'API verdi |  |
| 9.04 ↻ | aperta | Integrazioni con sistemi terzi provate in sandbox, comprese le risposte d'errore |  |
| 9.05 ↻ | aperta | Differenze tra ambienti documentate e gestite in configurazione |  |
| 9.06 ↻ | non-applicabile | Migrazione dei dati provata su una copia realistica, con verifica di integrità e riconciliazione | condizione falsa per la scheda (quando: innesco migrazione-dati) |
| 9.07 ↻ | aperta | Installazione e avvio riusciti in un ambiente simile alla produzione |  |
| 9.08 ↻ | aperta | Percorsi critici end-to-end verdi sull'app integrata |  |

## 10. Verifica

**Gate:** I criteri di uscita della strategia di test sono soddisfatti e nessun difetto bloccante è aperto.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 10.01 ↻ | aperta | Revisioni o ispezioni svolte su requisiti, design e codice |  |
| 10.02 ↻ | aperta | Analisi statica completa, senza problemi bloccanti |  |
| 10.03 ↻ | non-applicabile | Metodi formali applicati alle parti critiche, dove previsti | condizione falsa per la scheda (quando: criticita >= regolamentata) |
| 10.04 ↻ | aperta | Casi di test funzionali progettati con tecniche sistematiche: classi di equivalenza, valori limite, tabelle di decisione, transizioni di stato |  |
| 10.05 ↻ | aperta | Test di sistema ed end-to-end sui flussi prioritari verdi |  |
| 10.06 ↻ | aperta | Regressione automatizzata verde |  |
| 10.07 ↻ | rinviata | Prestazioni verificate contro gli scenari della fase 2: carico, stress, durata, picchi | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico o criticita >= alta) |
| 10.08 ↻ | aperta | Sicurezza verificata con SAST, DAST e analisi delle dipendenze; fuzzing e penetration test dove previsti |  |
| 10.09 ↻ | aperta | Failover e ripristino da backup provati davvero |  |
| 10.10 ↻ | aperta | Compatibilità, accessibilità, installazione e aggiornamento verificati |  |
| 10.11 ↻ | aperta | Efficacia dei test valutata oltre la copertura, per esempio con mutation testing sulle parti critiche |  |
| 10.12 ↻ | aperta | Difetti residui non bloccanti accettati esplicitamente |  |
| 10.13 ↻ | aperta | Cause radice dei difetti ricorrenti analizzate |  |

## 11. Validazione e accettazione

**Gate:** L'utente accetta formalmente e, se previsto dal profilo, chi gestirà il sistema dà il via libera operativo.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 11.01 ↻ | aperta | Test di accettazione utente (UAT) svolti sui criteri della fase 2, esiti registrati |  |
| 11.02 ↻ | rinviata | Accettazione operativa (OAT) svolta da chi gestirà il sistema: backup, monitoraggio, ripristino, runbook | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico) |
| 11.03 ↻ | rinviata | Alfa, beta o pilota con utenti reali; feedback gestito | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico) |
| 11.04 ↻ | aperta | Conformità verificata: privacy, accessibilità, sicurezza, contratti, norme di settore |  |
| 11.05 ↻ | non-applicabile | Valutazione di conformità o certificazione ottenuta, dove richiesta | voce di esercizio rinviata al passaggio al pubblico (quando: criticita >= regolamentata o innesco mercato-ue) |
| 11.06 ↻ | aperta | Tracciabilità chiusa: ogni requisito ha almeno un test e un esito |  |
| 11.07 ↻ | aperta | Gli obiettivi misurabili della fase 1 hanno un modo di essere misurati in esercizio |  |
| 11.08 ↻ | aperta | Verbale di accettazione firmato |  |

## 12. Rilascio e transizione in esercizio

**Gate:** L'app è rilasciata secondo il profilo; con un'esposizione pubblica, a fine hypercare le metriche sono stabili e non ci sono incidenti bloccanti aperti.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 12.01 ↻ | rinviata | Pipeline di rilascio automatizzata, con artefatti immutabili e firmati e provenienza verificabile | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico o innesco mercato-ue) |
| 12.02 ↻ | rinviata | Strategia di rilascio scelta (blue/green, canary, rolling) con criteri di arresto | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico) |
| 12.03 ↻ | rinviata | Rollback provato, migrazioni di schema comprese | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico o criticita >= alta) |
| 12.04 ↻ | non-applicabile | Migrazione dei dati e cut-over pianificati e provati | condizione falsa per la scheda (quando: innesco migrazione-dati) |
| 12.05 ↻ | rinviata | Monitoraggio e alert attivi prima del go-live | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico) |
| 12.06 ↻ | rinviata | Runbook, reperibilità e catena di escalation pronti | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico) |
| 12.07 ↻ | rinviata | Utenti e supporto formati; documentazione utente pubblicata | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico) |
| 12.08 ↻ | rinviata | Note di rilascio e comunicazione agli stakeholder inviate | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico) |
| 12.09 ↻ | rinviata | Periodo di hypercare definito, con i responsabili | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico) |
| 12.10 ↻ | rinviata | Metriche stabili e nessun incidente bloccante a fine hypercare | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico) |
| 12.11 ↻ | aperta | README e runbook coprono avvio, test, deploy, rollback e ripristino da backup |  |

## 13. Esercizio (periodica)

**Gate:** A ogni controllo periodico gli SLO risultano rispettati entro l'error budget.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 13.01 | fuori-catena | SLI e SLO definiti; eventuali SLA coerenti con gli SLO | fasi 13–15: fuori dalla catena |
| 13.02 | fuori-catena | Error budget misurato e usato nelle decisioni di rilascio | fasi 13–15: fuori dalla catena |
| 13.03 | fuori-catena | Dashboard e alert sui sintomi percepiti dall'utente, senza alert rumorosi | fasi 13–15: fuori dalla catena |
| 13.04 | fuori-catena | Postmortem senza colpe per ogni incidente rilevante, con azioni correttive tracciate | fasi 13–15: fuori dalla catena |
| 13.05 | fuori-catena | Problemi ricorrenti analizzati; modifiche gestite con un processo | fasi 13–15: fuori dalla catena |
| 13.06 | fuori-catena | Dipendenze monitorate per vulnerabilità; patch applicate nei tempi stabiliti | fasi 13–15: fuori dalla catena |
| 13.07 | non-applicabile | Se è un prodotto con elementi digitali sul mercato UE: procedura di segnalazione del Cyber Resilience Act pronta (preallerta entro 24 ore, notifica entro 72), con un responsabile della decisione | voce di esercizio rinviata al passaggio al pubblico (quando: innesco mercato-ue) |
| 13.08 | fuori-catena | Capacità e costi sotto controllo, con una previsione | fasi 13–15: fuori dalla catena |
| 13.09 | fuori-catena | Ultima prova di ripristino da backup riuscita entro la cadenza stabilita | fasi 13–15: fuori dalla catena |
| 13.10 | non-applicabile | Esercitazione di disaster recovery svolta | voce di esercizio rinviata al passaggio al pubblico (quando: esposizione >= pubblico e criticita >= alta) |
| 13.11 | fuori-catena | Feedback e metriche d'uso raccolti e portati nel backlog | fasi 13–15: fuori dalla catena |

## 14. Manutenzione ed evoluzione (periodica)

**Gate:** Ogni modifica supera, in scala ridotta, i gate delle fasi che tocca.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 14.01 | fuori-catena | Ogni modifica ripercorre analisi d'impatto, requisiti, design, implementazione, verifica e rilascio, in proporzione alla sua dimensione | fasi 13–15: fuori dalla catena |
| 14.02 | fuori-catena | Modifiche classificate (correttiva, adattiva, perfettiva, preventiva) per vedere dove va l'impegno | fasi 13–15: fuori dalla catena |
| 14.03 | fuori-catena | Registro del debito tecnico rivisto, con un budget esplicito per ripagarlo | fasi 13–15: fuori dalla catena |
| 14.04 | fuori-catena | Dipendenze e runtime lontani dal fine vita; piano di aggiornamento per quelli vicini | fasi 13–15: fuori dalla catena |
| 14.05 | fuori-catena | Fitness function automatiche a protezione delle proprietà architetturali chiave | fasi 13–15: fuori dalla catena |
| 14.06 | fuori-catena | Piano di sostituzione graduale per le parti legacy (es. strangler fig) | fasi 13–15: fuori dalla catena |
| 14.07 | fuori-catena | Versionamento semantico e politica di deprecazione applicati | fasi 13–15: fuori dalla catena |
| 14.08 | fuori-catena | Diagrammi, ADR e documentazione allineati allo stato corrente del sistema | fasi 13–15: fuori dalla catena |

## 15. Dismissione

**Gate:** Nessun dato orfano, nessun accesso residuo, nessun costo residuo.

| voce | stato | testo | evidenza o motivo |
|---|---|---|---|
| 15.01 | fuori-catena | Piano di dismissione approvato | fasi 13–15: fuori dalla catena |
| 15.02 | fuori-catena | Utenti avvisati con preavviso adeguato; data di fine supporto pubblicata | fasi 13–15: fuori dalla catena |
| 15.03 | fuori-catena | Utenti e dati migrati verso il sistema successivo, con completezza verificata | fasi 13–15: fuori dalla catena |
| 15.04 | fuori-catena | Dati soggetti a obblighi di conservazione archiviati, con la data di scadenza | fasi 13–15: fuori dalla catena |
| 15.05 | fuori-catena | Altri dati cancellati in modo sicuro, con evidenza | fasi 13–15: fuori dalla catena |
| 15.06 | fuori-catena | Infrastruttura spenta; nessuna risorsa ancora attiva o fatturata | fasi 13–15: fuori dalla catena |
| 15.07 | fuori-catena | Credenziali, certificati, chiavi API, accessi e integrazioni revocati | fasi 13–15: fuori dalla catena |
| 15.08 | fuori-catena | Contratti e licenze chiusi | fasi 13–15: fuori dalla catena |
| 15.09 | fuori-catena | Documentazione e lezioni apprese archiviate | fasi 13–15: fuori dalla catena |

## Controlli trasversali

Si rivedono a ogni gate; l'esito va nella nota del registro.

| voce | stato | testo |
|---|---|---|
| T.01 | applicabile | Registro dei rischi aggiornato; ogni rischio ha un responsabile |
| T.02 | applicabile | Decisioni significative della fase registrate in ADR |
| T.03 | applicabile | Codice, configurazione, infrastruttura e documentazione versionati; il contenuto di ogni release è ricostruibile |
| T.04 | applicabile | Modifiche ai requisiti passate dal controllo delle modifiche, con analisi d'impatto |
| T.05 | applicabile | Il processo seguito è quello dichiarato (verifica di assicurazione qualità) |
| T.06 | applicabile | Metriche di prodotto e di delivery raccolte, per esempio le metriche DORA |
| T.07 | applicabile | Documentazione per chi sviluppa, chi gestisce e chi usa allineata allo stato corrente |
| T.08 | applicabile | Attività di sicurezza previste per la fase svolte (secure SDLC) |
| T.09 | applicabile | Conformità ricontrollata: privacy (DPIA se il rischio è elevato), accessibilità, licenze, norme di settore, Cyber Resilience Act e AI Act se applicabili |

## DoD di incremento

La applica parallel-build a ogni rientro (task) e alla chiusura dell'incremento.

| voce | stato | testo |
|---|---|---|
| D.01 (task) | applicabile | Criteri di accettazione soddisfatti e verificati |
| D.02 (task) | applicabile | Codice conforme alle convenzioni; linter e formatter verdi |
| D.03 (task) | applicabile | Test unitari e di integrazione scritti e verdi |
| D.04 (incremento) | applicabile | Regressione verde in pipeline |
| D.05 (incremento) | applicabile | Code review completata |
| D.06 (task) | applicabile | Nessun nuovo problema bloccante da SAST e SCA |
| D.07 (task) | applicabile | Nessun segreto nel codice; configurazione esternalizzata |
| D.08 (task) | applicabile | Log, metriche e tracce per il nuovo comportamento, senza dati personali o segreti |
| D.09 (incremento) | applicabile | Funzionalità incomplete dietro feature flag |
| D.10 (task) | applicabile | Contratti API e schema dati aggiornati; migrazioni compatibili all'indietro |
| D.11 (task) | applicabile | Documentazione aggiornata: tecnica, utente, ADR e diagrammi se la modifica li tocca |
| D.12 (task) | applicabile | Tracciabilità aggiornata tra requisito e test |
| D.13 (task) | applicabile | Debito tecnico introdotto registrato, non nascosto |
| D.14 (incremento) | applicabile | Incremento deployabile, o già deployato in staging |
| D.15 (incremento) | applicabile | Accettato dal product owner |
