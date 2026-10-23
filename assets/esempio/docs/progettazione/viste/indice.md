<!-- Generato da app-blueprint (progetto.py viste): non modificare a mano. Le sorgenti sono in docs/progettazione/ e contracts/. -->

# Indice della progettazione

Una riga per elemento: id, descrizione, incremento in cui serve, sorgente. Il dettaglio si legge per id: `progetto.py mostra <id>`.

## obiettivi

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| OB-1 | L'officina gestisce preventivi, interventi e fatture solo con Officina, senza fogli di calcolo. | 1 | docs/progettazione/prodotto/prodotto.toml |
| OB-2 | Emettere una fattura costa meno tempo e nessuna trascrizione. | 1 | docs/progettazione/prodotto/prodotto.toml |
| OB-3 | I clienti seguono lo stato dei propri interventi senza telefonare. | 1 | docs/progettazione/prodotto/prodotto.toml |

## stakeholder

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| cliente | Segue lo stato dei propri interventi. | 1 | docs/progettazione/prodotto/prodotto.toml |
| commercialista | Riceve le fatture in PDF dal responsabile. Non usa Officina, ma il suo lavoro dipende da come le … | 1 | docs/progettazione/prodotto/prodotto.toml |
| consulente-privacy | Professionista che rivede informativa e registro dei trattamenti prima del lancio. | 1 | docs/progettazione/prodotto/prodotto.toml |
| operatore | Accetta i veicoli, apre e chiude gli interventi, compila i preventivi, registra clienti e veicoli. | 1 | docs/progettazione/prodotto/prodotto.toml |
| responsabile | Titolare dell'officina: approva i preventivi, emette le fatture, gestisce gli account. | 1 | docs/progettazione/prodotto/prodotto.toml |
| sviluppatore | Sviluppatore PHP a tempo parziale: manterrà l'app, ne gestisce il VPS e la sicurezza. | 1 | docs/progettazione/prodotto/prodotto.toml |

## sistemi

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| sito | Sito dell'officina sullo stesso VPS: non si integra, ma ne condivide le risorse. | 1 | docs/progettazione/prodotto/prodotto.toml |
| smtp | Servizio di posta dell'officina, via SMTP: inviti e recupero della password. | 1 | docs/progettazione/prodotto/prodotto.toml |

## non_obiettivi

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| NO-1 | Registrazione autonoma: gli account li crea il responsabile, o nascono con il cliente. | 1 | docs/progettazione/prodotto/prodotto.toml |
| NO-2 | Cambio della password dall'interno: si usa il recupero (ACC-3). | 1 | docs/progettazione/prodotto/prodotto.toml |
| NO-3 | Profilo modificabile dall'utente: nome ed email li corregge il responsabile. | 1 | docs/progettazione/prodotto/prodotto.toml |
| NO-4 | Audit consultabile dall'interfaccia: le azioni su preventivi e fatture si registrano e si consult… | 1 | docs/progettazione/prodotto/prodotto.toml |
| NO-5 | Notifiche oltre a invito, recupero della password e, nel secondo incremento, promemoria di revisi… | 1 | docs/progettazione/prodotto/prodotto.toml |
| NO-6 | Import da altri gestionali: clienti e veicoli si inseriscono a mano. | 1 | docs/progettazione/prodotto/prodotto.toml |
| NO-7 | Richieste privacy self-service: le evade il responsabile con la procedura del runbook (ADR-0005). | 1 | docs/progettazione/prodotto/prodotto.toml |
| NO-8 | Onboarding guidato e aiuto in linea: gli utenti sono pochi e imparano di persona. | 1 | docs/progettazione/prodotto/prodotto.toml |
| NO-9 | Invio delle fatture ai sistemi fiscali: lo fa il commercialista, che le riceve in PDF. | 1 | docs/progettazione/prodotto/prodotto.toml |
| NO-10 | App mobile nativa: l'interfaccia web è responsiva. | 1 | docs/progettazione/prodotto/prodotto.toml |

## vincoli

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| V-1 | Esercizio su un solo VPS, già in uso per il sito dell'officina. | 1 | docs/progettazione/prodotto/prodotto.toml |
| V-2 | Budget d'esercizio: il VPS esistente, nessun servizio a pagamento in più. | 1 | docs/progettazione/prodotto/prodotto.toml |
| V-3 | Manutenzione affidata a uno sviluppatore PHP a tempo parziale. | 1 | docs/progettazione/prodotto/prodotto.toml |
| V-4 | Interfaccia solo in italiano. | 1 | docs/progettazione/prodotto/prodotto.toml |
| V-5 | Dati personali dei clienti (nome, codice fiscale, email, targhe): minimizzazione, informativa, re… | 1 | docs/progettazione/prodotto/prodotto.toml |
| V-6 | Numerazione progressiva per anno senza buchi e conservazione delle fatture per il periodo di legg… | 1 | docs/progettazione/prodotto/prodotto.toml |
| V-7 | Nessun obbligo di legge sull'accessibilità per un gestionale interno; il livello AA è un requisit… | 1 | docs/progettazione/prodotto/prodotto.toml |

## aree

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| ACC | Accessi | 1 | docs/progettazione/requisiti/requisiti.toml |
| CLI | Clienti | 1 | docs/progettazione/requisiti/requisiti.toml |
| FAT | Fatture | 1 | docs/progettazione/requisiti/requisiti.toml |
| INT | Interventi e preventivi | 1 | docs/progettazione/requisiti/requisiti.toml |
| PRZ | Prezzi | 1 | docs/progettazione/requisiti/requisiti.toml |
| VEI | Veicoli | 1 | docs/progettazione/requisiti/requisiti.toml |

## storie

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| ACC-1 | L'operatore accede ed esce | 1 | docs/progettazione/requisiti/storie.toml |
| ACC-2 | Il responsabile crea l'account di un operatore | 1 | docs/progettazione/requisiti/storie.toml |
| ACC-3 | L'operatore recupera la password | 1 | docs/progettazione/requisiti/storie.toml |
| ACC-4 | Il responsabile accede con un secondo fattore | 1 | docs/progettazione/requisiti/storie.toml |
| ACC-5 | Il cliente attiva l'account dall'invito | 1 | docs/progettazione/requisiti/storie.toml |
| ACC-6 | Il cliente consulta l'informativa privacy e le pagine di servizio | 1 | docs/progettazione/requisiti/storie.toml |
| ACC-7 | Il responsabile sblocca un account bloccato | 1 | docs/progettazione/requisiti/storie.toml |
| CLI-1 | L'operatore registra un cliente | 1 | docs/progettazione/requisiti/storie.toml |
| CLI-2 | L'operatore cerca i clienti per nome | 2 | docs/progettazione/requisiti/storie.toml |
| FAT-1 | Il responsabile emette la fattura di un intervento chiuso | 1 | docs/progettazione/requisiti/storie.toml |
| FAT-2 | Il responsabile esporta in CSV le fatture del mese | 2 | docs/progettazione/requisiti/storie.toml |
| FAT-3 | Il responsabile scarica il PDF di una fattura per il commercialista | 1 | docs/progettazione/requisiti/storie.toml |
| INT-1 | L'operatore apre un intervento su un veicolo | 1 | docs/progettazione/requisiti/storie.toml |
| INT-2 | Il responsabile approva il preventivo | 1 | docs/progettazione/requisiti/storie.toml |
| INT-3 | Il cliente vede lo stato del proprio intervento | 1 | docs/progettazione/requisiti/storie.toml |
| INT-4 | L'operatore chiude l'intervento a lavori finiti | 1 | docs/progettazione/requisiti/storie.toml |
| INT-5 | L'operatore compila il preventivo | 1 | docs/progettazione/requisiti/storie.toml |
| INT-6 | L'operatore consulta l'elenco degli interventi aperti | 1 | docs/progettazione/requisiti/storie.toml |
| PRZ-1 | Il responsabile aggiorna il listino dall'interfaccia | 2 | docs/progettazione/requisiti/storie.toml |
| VEI-1 | L'operatore associa un veicolo a un cliente | 1 | docs/progettazione/requisiti/storie.toml |
| VEI-2 | Il cliente riceve un promemoria quando la revisione del veicolo sta per scadere | 2 | docs/progettazione/requisiti/storie.toml |

## percorsi

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| PC-1 | intervento completo | 1 | docs/progettazione/requisiti/requisiti.toml |
| PC-2 | il cliente segue il suo intervento | 1 | docs/progettazione/requisiti/requisiti.toml |

## rnf

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| RNF-1 |  | 1 | docs/progettazione/requisiti/requisiti.toml |
| RNF-2 |  | 1 | docs/progettazione/requisiti/requisiti.toml |
| RNF-3 |  | 1 | docs/progettazione/requisiti/requisiti.toml |
| RNF-4 |  | 1 | docs/progettazione/requisiti/requisiti.toml |
| RNF-5 |  | 1 | docs/progettazione/requisiti/requisiti.toml |
| RNF-6 |  | 1 | docs/progettazione/requisiti/requisiti.toml |
| RNF-7 |  | 1 | docs/progettazione/requisiti/requisiti.toml |

## requisiti_dati

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| RD-1 |  | 1 | docs/progettazione/requisiti/requisiti.toml |
| RD-2 |  | 1 | docs/progettazione/requisiti/requisiti.toml |
| RD-3 |  | 1 | docs/progettazione/requisiti/requisiti.toml |
| RD-4 |  | 1 | docs/progettazione/requisiti/requisiti.toml |

## conflitti

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| CO-1 | L'operatore vorrebbe approvare da solo i preventivi sotto i 100 €. | 1 | docs/progettazione/requisiti/requisiti.toml |

## glossario

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| account | L'accesso di una persona a Officina, con un ruolo; nasce invitato e diventa attivo con l'attivazi… | 1 | docs/progettazione/dominio/glossario.toml |
| cliente | La persona che porta i veicoli in officina e riceve le fatture. | 1 | docs/progettazione/dominio/glossario.toml |
| fattura | Il documento emesso per un intervento chiuso, con numero progressivo per anno; una volta emessa n… | 1 | docs/progettazione/dominio/glossario.toml |
| intervento | Il lavoro su un veicolo, dall'accettazione alla chiusura. Ha un preventivo e, chiuso, può avere u… | 1 | docs/progettazione/dominio/glossario.toml |
| manodopera | Voce di listino prezzata a ore. | 1 | docs/progettazione/dominio/glossario.toml |
| motore dei prezzi | La logica unica che calcola imponibile, IVA e totale di preventivi e fatture. | 1 | docs/progettazione/dominio/glossario.toml |
| preventivo | Le righe di manodopera e ricambi di un intervento; il totale lo calcola il motore dei prezzi. | 1 | docs/progettazione/dominio/glossario.toml |
| ricambio | Voce di listino prezzata a pezzo. | 1 | docs/progettazione/dominio/glossario.toml |
| riga di fattura | Copia di una riga del preventivo approvato al momento dell'emissione. | 1 | docs/progettazione/dominio/glossario.toml |
| riga di preventivo | Una voce del listino con quantità, prezzo e aliquota al momento dell'inserimento. | 1 | docs/progettazione/dominio/glossario.toml |
| veicolo | Un mezzo di un cliente, identificato dalla targa. | 1 | docs/progettazione/dominio/glossario.toml |
| voce di listino | Una prestazione o un ricambio con il suo prezzo e la sua aliquota IVA. | 1 | docs/progettazione/dominio/glossario.toml |

## regole

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| R-1 | Un intervento si chiude solo con il preventivo approvato. | 1 | docs/progettazione/dominio/regole.toml |
| R-2 | I totali di preventivi e fatture li calcola solo il motore dei prezzi: righe, IVA per aliquota, a… | 1 | docs/progettazione/dominio/regole.toml |
| R-3 | Le fatture hanno un numero progressivo per anno, senza buchi; una fattura emessa non si cancella … | 1 | docs/progettazione/dominio/regole.toml |
| R-4 | Un veicolo ha al massimo un intervento non chiuso. | 1 | docs/progettazione/dominio/regole.toml |
| R-5 | Una fattura emessa a cavallo della mezzanotte del 31 dicembre prende l'anno della data di emissio… | 1 | docs/progettazione/dominio/regole.toml |
| R-6 | Dopo cinque tentativi d'accesso falliti l'account si blocca; lo sblocca solo il responsabile, e i… | 1 | docs/progettazione/dominio/regole.toml |
| R-7 | Il codice fiscale è valido e unico per cliente. | 1 | docs/progettazione/dominio/regole.toml |
| R-8 | La targa si normalizza (maiuscole, senza spazi) ed è unica. | 1 | docs/progettazione/dominio/regole.toml |
| R-9 | Una riga con quantità zero o negativa è rifiutata; un preventivo approvato non accetta righe nuove. | 1 | docs/progettazione/dominio/regole.toml |

## sottodomini

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| anagrafiche | Clienti e veicoli. | 1 | docs/progettazione/dominio/moduli.toml |
| fatturazione | Fatture numerate, immutabili e in PDF. | 1 | docs/progettazione/dominio/moduli.toml |
| identita | Account, accesso, ruoli. | 1 | docs/progettazione/dominio/moduli.toml |
| officina | Interventi, preventivi e prezzi: il lavoro che distingue l'officina. | 1 | docs/progettazione/dominio/moduli.toml |

## moduli

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| accessi | Ciclo di vita degli account, accesso, secondo fattore, inviti e recupero; nessuna regola di domin… | 1 | docs/progettazione/dominio/moduli.toml |
| clienti | Anagrafica dei clienti e collegamento al loro account. | 1 | docs/progettazione/dominio/moduli.toml |
| fatture | Emissione, numerazione e PDF delle fatture. | 1 | docs/progettazione/dominio/moduli.toml |
| interventi | Interventi e preventivi, con le loro macchine a stati. | 1 | docs/progettazione/dominio/moduli.toml |
| prezzi | Listino e motore dei prezzi: l'unico posto dove si calcolano i totali (R-2). | 1 | docs/progettazione/dominio/moduli.toml |
| veicoli | Veicoli dei clienti e loro proprietario. | 1 | docs/progettazione/dominio/moduli.toml |

## dipendenze

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| clienti>accessi |  | 1 | docs/progettazione/dominio/moduli.toml |
| fatture>interventi |  | 1 | docs/progettazione/dominio/moduli.toml |
| fatture>prezzi |  | 1 | docs/progettazione/dominio/moduli.toml |
| interventi>prezzi |  | 1 | docs/progettazione/dominio/moduli.toml |
| interventi>veicoli |  | 1 | docs/progettazione/dominio/moduli.toml |
| veicoli>clienti |  | 1 | docs/progettazione/dominio/moduli.toml |

## entita

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| account | L'accesso di una persona a Officina. | 1 | docs/progettazione/dominio/entita.toml |
| cliente | Chi porta i veicoli in officina e riceve le fatture. | 1 | docs/progettazione/dominio/entita.toml |
| fattura | Documento emesso per un intervento chiuso; immutabile (R-3). | 1 | docs/progettazione/dominio/entita.toml |
| intervento | Il lavoro su un veicolo, dall'accettazione alla chiusura. | 1 | docs/progettazione/dominio/entita.toml |
| manodopera | Voce di listino prezzata a ore. | 1 | docs/progettazione/dominio/entita.toml |
| preventivo | Le righe di un intervento; uno per intervento. | 1 | docs/progettazione/dominio/entita.toml |
| ricambio | Voce di listino prezzata a pezzo. | 1 | docs/progettazione/dominio/entita.toml |
| riga_fattura | Copia di una riga del preventivo approvato all'emissione. | 1 | docs/progettazione/dominio/entita.toml |
| riga_preventivo | Una voce del listino nel preventivo, con i valori del momento. | 1 | docs/progettazione/dominio/entita.toml |
| veicolo | Un mezzo di un cliente. | 1 | docs/progettazione/dominio/entita.toml |
| voce_listino | Una prestazione o un ricambio con prezzo e aliquota. | 1 | docs/progettazione/dominio/entita.toml |

## generalizzazioni

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| voce-listino-tipo |  | 1 | docs/progettazione/dominio/entita.toml |

## relazioni

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| account-cliente | accede-con | 1 | docs/progettazione/dominio/entita.toml |
| cliente-veicolo | possiede | 1 | docs/progettazione/dominio/entita.toml |
| fattura-righe | contiene | 1 | docs/progettazione/dominio/entita.toml |
| intervento-fattura | chiuso-da | 1 | docs/progettazione/dominio/entita.toml |
| intervento-preventivo | ha | 1 | docs/progettazione/dominio/entita.toml |
| preventivo-righe | contiene | 1 | docs/progettazione/dominio/entita.toml |
| veicolo-intervento | riceve | 1 | docs/progettazione/dominio/entita.toml |
| voce-riga | prezza | 1 | docs/progettazione/dominio/entita.toml |

## macchine

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| account |  | 1 | docs/progettazione/dominio/stati.toml |
| intervento |  | 1 | docs/progettazione/dominio/stati.toml |
| preventivo |  | 1 | docs/progettazione/dominio/stati.toml |

## processi

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| accesso-e-attivazione | Caso d'uso: dall'invito al primo accesso | 1 | docs/progettazione/dominio/processi/accesso-e-attivazione.md |
| ciclo-intervento | Ciclo di un intervento, dall'accettazione alla fattura | 1 | docs/progettazione/dominio/processi/ciclo-intervento.md |

## driver

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| DR-1 |  | 1 | docs/progettazione/architettura/architettura.toml |
| DR-2 |  | 1 | docs/progettazione/architettura/architettura.toml |
| DR-3 |  | 1 | docs/progettazione/architettura/architettura.toml |
| DR-4 |  | 1 | docs/progettazione/architettura/architettura.toml |

## strategie

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| ST-accessibilita | WCAG 2.2 AA con frontend-craft: componenti del design system accessibili, nomi accessibili nel co… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-audit | Tabella di audit append-only per approvazioni, emissioni e sblocchi: chi, cosa, quando, id della … | 1 | docs/progettazione/architettura/architettura.toml |
| ST-autenticazione | Sessione lato server con i flussi del framework: attivazione dall'invito, accesso, uscita, recupe… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-autorizzazione | Il kernel applica contracts/autorizzazioni.toml a ogni operazione, con negazione per default e co… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-backup | Dump notturno cifrato con 30 giorni di storico presso il fornitore del VPS; ripristino provato a … | 1 | docs/progettazione/architettura/architettura.toml |
| ST-cache | Nessuna cache applicativa: gli indici di AC-1 bastano a RNF-1. Cache HTTP solo sugli asset statici. | 1 | docs/progettazione/architettura/architettura.toml |
| ST-ci-cd | CI su GitHub Actions con i comandi del piano e i gate di supply chain; rilascio manuale su stagin… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-concorrenza | Blocco ottimistico con colonna versione su preventivi e interventi; blocco pessimistico sulla rig… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-configurazione | Variabili d'ambiente elencate in contracts/configurazione.toml; un file per ambiente fuori dal re… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-dati | Un solo database relazionale (PostgreSQL); consistenza forte con transazioni locali; nessun parti… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-denaro | Importi in interi di centesimi con la valuta; arrotondamento al centesimo per riga, metà per ecce… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-errori | Problem Details (RFC 9457) con il codice del catalogo nel campo type; un solo gestore al confine … | 1 | docs/progettazione/architettura/architettura.toml |
| ST-i18n | Solo italiano (V-4), ma ogni testo dell'interfaccia passa da una chiave di ux/testi.toml; formati… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-identificatori | Chiavi primarie surrogate ULID per tutte le tabelle; i codici leggibili (codice dell'intervento, … | 1 | docs/progettazione/architettura/architettura.toml |
| ST-migrazioni | Migrazioni in avanti, solo additive in un rilascio (expand); le rimozioni in un rilascio successi… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-osservabilita | Log JSON strutturati con id di richiesta, senza dati personali (solo id); endpoint di salute; met… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-paginazione | Paginazione a cursore con i parametri cursore e limite, 25 elementi per default, 100 al massimo. | 1 | docs/progettazione/architettura/architettura.toml |
| ST-qualita-codice | Trunk-based su main con rami brevi; Pint e PHPStan per il backend, ESLint, Prettier e vue-tsc per… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-resilienza | Email inviate da una coda con 3 tentativi, backoff esponenziale e jitter; timeout di 10 s verso S… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-segreti | Segreti solo nelle variabili d'ambiente del VPS, nomi in contracts/configurazione.toml; token d'i… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-tempo | Istanti in UTC nel database, Europe/Rome nell'interfaccia e per l'anno delle fatture (R-5); le da… | 1 | docs/progettazione/architettura/architettura.toml |
| ST-versionamento | API interna al frontend, versione nel percorso (/api/v1); nessuna API pubblica; un cambio incompa… | 1 | docs/progettazione/architettura/architettura.toml |

## ambienti

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| locale | Sviluppo e test, compresi gli agenti di parallel-build. | 1 | docs/progettazione/architettura/architettura.toml |
| produzione | Esercizio. | 1 | docs/progettazione/architettura/architettura.toml |
| staging | Prova di rilascio, di ripristino e di carico. | 1 | docs/progettazione/architettura/architettura.toml |

## integrazioni

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| smtp |  | 1 | docs/progettazione/architettura/architettura.toml |

## confini

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| app-database | Dall'applicazione al database. | 1 | docs/progettazione/architettura/minacce.toml |
| app-email | Dall'applicazione al servizio email. | 1 | docs/progettazione/architettura/minacce.toml |
| browser-app | Da internet all'applicazione. | 1 | docs/progettazione/architettura/minacce.toml |

## flussi

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| FL-1 | Accesso con credenziali e secondo fattore. | 1 | docs/progettazione/architettura/minacce.toml |
| FL-2 | Il cliente legge il proprio intervento. | 1 | docs/progettazione/architettura/minacce.toml |
| FL-3 | Approvazione dei preventivi ed emissione delle fatture. | 1 | docs/progettazione/architettura/minacce.toml |
| FL-4 | Invio degli inviti e dei link di recupero. | 1 | docs/progettazione/architettura/minacce.toml |

## minacce

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| MI-1 | Un cliente legge l'intervento di un altro cambiando l'id nell'URL. | 1 | docs/progettazione/architettura/minacce.toml |
| MI-2 | Credenziali indovinate o riusate da altri siti. | 1 | docs/progettazione/architettura/minacce.toml |
| MI-3 | Un operatore approva un preventivo o emette una fattura. | 1 | docs/progettazione/architettura/minacce.toml |
| MI-4 | Un link d'invito o di recupero intercettato viene riusato. | 1 | docs/progettazione/architettura/minacce.toml |
| MI-5 | Chi ha emesso o approvato nega di averlo fatto. | 1 | docs/progettazione/architettura/minacce.toml |
| MI-6 | Raffiche di tentativi d'accesso saturano il VPS condiviso. | 1 | docs/progettazione/architettura/minacce.toml |
| MI-7 | Un importo viene alterato tra preventivo e fattura. | 1 | docs/progettazione/architettura/minacce.toml |

## volumi

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| entita:account |  | 1 | docs/progettazione/dati/dati.toml |
| entita:cliente |  | 1 | docs/progettazione/dati/dati.toml |
| entita:fattura |  | 1 | docs/progettazione/dati/dati.toml |
| entita:intervento |  | 1 | docs/progettazione/dati/dati.toml |
| entita:manodopera |  | 1 | docs/progettazione/dati/dati.toml |
| entita:preventivo |  | 1 | docs/progettazione/dati/dati.toml |
| entita:ricambio |  | 1 | docs/progettazione/dati/dati.toml |
| entita:riga_fattura |  | 1 | docs/progettazione/dati/dati.toml |
| entita:riga_preventivo |  | 1 | docs/progettazione/dati/dati.toml |
| entita:veicolo |  | 1 | docs/progettazione/dati/dati.toml |
| entita:voce_listino |  | 1 | docs/progettazione/dati/dati.toml |
| relazione:account-cliente |  | 1 | docs/progettazione/dati/dati.toml |
| relazione:cliente-veicolo |  | 1 | docs/progettazione/dati/dati.toml |
| relazione:fattura-righe |  | 1 | docs/progettazione/dati/dati.toml |
| relazione:intervento-fattura |  | 1 | docs/progettazione/dati/dati.toml |
| relazione:intervento-preventivo |  | 1 | docs/progettazione/dati/dati.toml |
| relazione:preventivo-righe |  | 1 | docs/progettazione/dati/dati.toml |
| relazione:veicolo-intervento |  | 1 | docs/progettazione/dati/dati.toml |
| relazione:voce-riga |  | 1 | docs/progettazione/dati/dati.toml |

## accessi

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| AC-1 | Elenco degli interventi aperti, prima pagina | 1 | docs/progettazione/dati/dati.toml |
| AC-2 | Il cliente apre il proprio intervento | 1 | docs/progettazione/dati/dati.toml |
| AC-3 | Emissione di una fattura | 1 | docs/progettazione/dati/dati.toml |
| AC-4 | Accesso con email e password | 1 | docs/progettazione/dati/dati.toml |
| AC-5 | Totale del preventivo mostrato a ogni riga aggiunta | 1 | docs/progettazione/dati/dati.toml |
| AC-6 | Lettura di una fattura, a schermo o in PDF | 1 | docs/progettazione/dati/dati.toml |
| AC-7 | Ricerca dei clienti per cognome | 2 | docs/progettazione/dati/dati.toml |
| AC-8 | Promemoria delle revisioni in scadenza | 2 | docs/progettazione/dati/dati.toml |
| AC-9 | Veicoli di un cliente, nella sua scheda | 1 | docs/progettazione/dati/dati.toml |
| AC-10 | Apertura di un intervento con il controllo dell'intervento già aperto (R-4) | 1 | docs/progettazione/dati/dati.toml |

## ristrutturazione

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| generalizzazione-listino | Accorpamento dei figli nel padre: una tabella voci_listino con il tipo e le colonne facoltative d… | 1 | docs/progettazione/dati/dati.toml |
| identificatori-surrogati | Chiave primaria surrogata ULID per tutte le tabelle; codice, targa, codice fiscale, email e (anno… | 1 | docs/progettazione/dati/dati.toml |
| totale-fattura | Memorizzato all'emissione e mai aggiornato. | 1 | docs/progettazione/dati/dati.toml |
| totale-preventivo | Non memorizzato: lo calcola il motore dei prezzi a ogni lettura. | 1 | docs/progettazione/dati/dati.toml |
| voce-riga-copiata | Nessuna chiave esterna verso il listino: la riga copia codice, descrizione, tipo, prezzo e aliquo… | 1 | docs/progettazione/dati/dati.toml |

## tabelle

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| account | account | 1 | contracts/schema.toml |
| audit | audit | 1 | contracts/schema.toml |
| clienti | clienti | 1 | contracts/schema.toml |
| coda | coda | 1 | contracts/schema.toml |
| fatture | fatture | 1 | contracts/schema.toml |
| interventi | interventi | 1 | contracts/schema.toml |
| numeratori_fatture | numeratori_fatture | 1 | contracts/schema.toml |
| preventivi | preventivi | 1 | contracts/schema.toml |
| righe_fattura | righe_fattura | 1 | contracts/schema.toml |
| righe_preventivo | righe_preventivo | 1 | contracts/schema.toml |
| veicoli | veicoli | 1 | contracts/schema.toml |
| voci_listino | voci_listino | 1 | contracts/schema.toml |

## api

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| accedi | Accede con email e password | 1 | contracts/openapi.json |
| aggiornaVoceListino | Aggiorna una voce di listino | 2 | contracts/openapi.json |
| aggiungiRigaPreventivo | Aggiunge una riga dal listino | 1 | contracts/openapi.json |
| approvaPreventivo | Approva il preventivo | 1 | contracts/openapi.json |
| apriIntervento | Apre un intervento | 1 | contracts/openapi.json |
| associaVeicolo | Associa un veicolo al cliente | 1 | contracts/openapi.json |
| attivaAccount | Attiva l'account dall'invito | 1 | contracts/openapi.json |
| cercaClienti | Cerca i clienti per nome | 2 | contracts/openapi.json |
| chiediRecuperoPassword | Chiede il link di recupero | 1 | contracts/openapi.json |
| chiudiIntervento | Chiude l'intervento | 1 | contracts/openapi.json |
| creaAccount | Crea un account e invia l'invito | 1 | contracts/openapi.json |
| dettaglioCliente | Legge un cliente | 1 | contracts/openapi.json |
| dettaglioFattura | Legge una fattura | 1 | contracts/openapi.json |
| dettaglioIntervento | Legge un intervento; per il cliente solo il proprio, altrimenti non-trovato | 1 | contracts/openapi.json |
| elencoAccount | Elenca gli account | 1 | contracts/openapi.json |
| elencoClienti | Elenca i clienti | 1 | contracts/openapi.json |
| elencoInterventiAperti | Elenca gli interventi aperti | 1 | contracts/openapi.json |
| elencoVeicoliCliente | Elenca i veicoli di un cliente | 1 | contracts/openapi.json |
| elencoVociListino | Elenca le voci di listino | 1 | contracts/openapi.json |
| emettiFattura | Emette la fattura di un intervento chiuso | 1 | contracts/openapi.json |
| esci | Esce | 1 | contracts/openapi.json |
| esportaFatture | Esporta in CSV le fatture di un mese | 2 | contracts/openapi.json |
| impostaPasswordDaRecupero | Imposta la password dal link di recupero | 1 | contracts/openapi.json |
| pdfFattura | Scarica il PDF di una fattura | 1 | contracts/openapi.json |
| registraCliente | Registra un cliente | 1 | contracts/openapi.json |
| sbloccaAccount | Sblocca un account | 1 | contracts/openapi.json |
| verificaSecondoFattore | Verifica il codice TOTP | 1 | contracts/openapi.json |

## facciata

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| accessi.creaAccountInvitato | creaAccountInvitato | 1 | docs/progettazione/moduli/accessi.toml |
| clienti.accountDi | accountDi | 1 | docs/progettazione/moduli/clienti.toml |
| clienti.esiste | esiste | 1 | docs/progettazione/moduli/clienti.toml |
| interventi.interventoChiuso | interventoChiuso | 1 | docs/progettazione/moduli/interventi.toml |
| prezzi.totali | totali | 1 | docs/progettazione/moduli/prezzi.toml |
| prezzi.voce | voce | 1 | docs/progettazione/moduli/prezzi.toml |
| veicoli.proprietarioAccount | proprietarioAccount | 1 | docs/progettazione/moduli/veicoli.toml |
| veicoli.veicolo | veicolo | 1 | docs/progettazione/moduli/veicoli.toml |

## errori

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| account-bloccato |  | 1 | contracts/errori.toml |
| account-esistente |  | 1 | contracts/errori.toml |
| cliente-duplicato |  | 1 | contracts/errori.toml |
| codice-fiscale-non-valido |  | 1 | contracts/errori.toml |
| codice-non-valido |  | 1 | contracts/errori.toml |
| conflitto-di-versione |  | 1 | contracts/errori.toml |
| credenziali-non-valide |  | 1 | contracts/errori.toml |
| errore-interno |  | 1 | contracts/errori.toml |
| fattura-esistente |  | 1 | contracts/errori.toml |
| intervento-gia-aperto |  | 1 | contracts/errori.toml |
| intervento-non-chiuso |  | 1 | contracts/errori.toml |
| link-non-valido |  | 1 | contracts/errori.toml |
| non-autenticato |  | 1 | contracts/errori.toml |
| non-autorizzato |  | 1 | contracts/errori.toml |
| non-trovato |  | 1 | contracts/errori.toml |
| password-debole |  | 1 | contracts/errori.toml |
| preventivo-approvato |  | 1 | contracts/errori.toml |
| preventivo-non-approvato |  | 1 | contracts/errori.toml |
| preventivo-vuoto |  | 1 | contracts/errori.toml |
| quantita-non-valida |  | 1 | contracts/errori.toml |
| troppe-richieste |  | 1 | contracts/errori.toml |
| validazione |  | 1 | contracts/errori.toml |
| veicolo-duplicato |  | 1 | contracts/errori.toml |

## matrice

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| account.crea |  | 1 | contracts/autorizzazioni.toml |
| account.leggi |  | 1 | contracts/autorizzazioni.toml |
| account.sblocca |  | 1 | contracts/autorizzazioni.toml |
| cliente.cerca |  | 2 | contracts/autorizzazioni.toml |
| cliente.crea |  | 1 | contracts/autorizzazioni.toml |
| cliente.leggi |  | 1 | contracts/autorizzazioni.toml |
| fattura.emetti |  | 1 | contracts/autorizzazioni.toml |
| fattura.esporta |  | 2 | contracts/autorizzazioni.toml |
| fattura.leggi |  | 1 | contracts/autorizzazioni.toml |
| intervento.chiudi |  | 1 | contracts/autorizzazioni.toml |
| intervento.crea |  | 1 | contracts/autorizzazioni.toml |
| intervento.elenca |  | 1 | contracts/autorizzazioni.toml |
| intervento.leggi |  | 1 | contracts/autorizzazioni.toml |
| preventivo.approva |  | 1 | contracts/autorizzazioni.toml |
| preventivo.modifica |  | 1 | contracts/autorizzazioni.toml |
| veicolo.crea |  | 1 | contracts/autorizzazioni.toml |
| veicolo.leggi |  | 1 | contracts/autorizzazioni.toml |
| voce_listino.leggi |  | 1 | contracts/autorizzazioni.toml |
| voce_listino.modifica |  | 2 | contracts/autorizzazioni.toml |

## sequenze

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| PC-1 | PC-1 | 1 | docs/progettazione/sequenze/PC-1.md |
| PC-2 | PC-2 | 1 | docs/progettazione/sequenze/PC-2.md |

## personas

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| anna | Cliente occasionale, apre il link dal telefono. | 1 | docs/progettazione/ux/ux.toml |
| giulia | Operatrice d'accettazione, al banco con il telefono che squilla; usa il PC dell'officina. | 1 | docs/progettazione/ux/ux.toml |
| marco | Titolare: approva tra un lavoro e l'altro, spesso dal telefono. | 1 | docs/progettazione/ux/ux.toml |

## sezioni

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| amministrazione | Amministrazione | 1 | docs/progettazione/ux/ux.toml |
| area-cliente | I miei interventi | 1 | docs/progettazione/ux/ux.toml |
| lavoro | Lavoro | 1 | docs/progettazione/ux/ux.toml |

## rotte

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| /* | /* | 1 | docs/progettazione/ux/ux.toml |
| /accesso | /accesso | 1 | docs/progettazione/ux/ux.toml |
| /account | /account | 1 | docs/progettazione/ux/ux.toml |
| /area-cliente/interventi/{id} | /area-cliente/interventi/{id} | 1 | docs/progettazione/ux/ux.toml |
| /attivazione/{token} | /attivazione/{token} | 1 | docs/progettazione/ux/ux.toml |
| /clienti | /clienti | 1 | docs/progettazione/ux/ux.toml |
| /clienti/{id} | /clienti/{id} | 1 | docs/progettazione/ux/ux.toml |
| /fatture/esportazione | /fatture/esportazione | 1 | docs/progettazione/ux/ux.toml |
| /fatture/{id} | /fatture/{id} | 1 | docs/progettazione/ux/ux.toml |
| /informativa | /informativa | 1 | docs/progettazione/ux/ux.toml |
| /interventi | /interventi | 1 | docs/progettazione/ux/ux.toml |
| /interventi/{id} | /interventi/{id} | 1 | docs/progettazione/ux/ux.toml |
| /listino | /listino | 1 | docs/progettazione/ux/ux.toml |
| /recupero-password | /recupero-password | 1 | docs/progettazione/ux/ux.toml |

## schermate

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| accesso | Accedere con email e password, e con il codice per il responsabile. | 1 | docs/progettazione/ux/ux.toml |
| account | Creare gli account degli operatori e sbloccare quelli bloccati. | 1 | docs/progettazione/ux/ux.toml |
| area-cliente-intervento | Il cliente vede stato, preventivo e data prevista del proprio intervento. | 1 | docs/progettazione/ux/ux.toml |
| attivazione | Scegliere la password e attivare l'account dall'invito. | 1 | docs/progettazione/ux/ux.toml |
| cliente-scheda | Dati del cliente, i suoi veicoli, l'apertura di un intervento. | 1 | docs/progettazione/ux/ux.toml |
| clienti | Trovare un cliente o registrarne uno nuovo. | 1 | docs/progettazione/ux/ux.toml |
| esportazione-fatture | Esportare in CSV le fatture di un mese per il commercialista. | 2 | docs/progettazione/ux/ux.toml |
| fattura | Vedere una fattura emessa e scaricarne il PDF. | 1 | docs/progettazione/ux/ux.toml |
| informativa | Leggere l'informativa privacy senza accedere. | 1 | docs/progettazione/ux/ux.toml |
| interventi-aperti | Vedere gli interventi non chiusi, i più vecchi per primi. | 1 | docs/progettazione/ux/ux.toml |
| intervento | Seguire un intervento: preventivo, approvazione, chiusura, fattura. | 1 | docs/progettazione/ux/ux.toml |
| listino | Aggiornare prezzi e descrizioni del listino. | 2 | docs/progettazione/ux/ux.toml |
| non-trovato | Dire che la pagina non esiste e riportare alla pagina iniziale. | 1 | docs/progettazione/ux/ux.toml |
| recupero-password | Chiedere il link di recupero e impostare una nuova password. | 1 | docs/progettazione/ux/ux.toml |

## livelli

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| accessibilita | WCAG 2.2 AA sui percorsi critici (RNF-3). | 1 | docs/progettazione/piano/test.toml |
| accettazione | Un test per ogni criterio delle storie, con l'id della storia nel nome. | 1 | docs/progettazione/piano/test.toml |
| autorizzazione | Dalla matrice: chi è consentito passa, chi non lo è riceve l'errore previsto; per ogni condizione… | 1 | docs/progettazione/piano/test.toml |
| contratto | Ogni risposta validata contro contracts/openapi.json, errori e paginazione compresi. | 1 | docs/progettazione/piano/test.toml |
| e2e | I percorsi critici PC-1 e PC-2 sull'app integrata, per ruolo e nome accessibile. | 1 | docs/progettazione/piano/test.toml |
| mutazioni | La forza dei test sui moduli ad alto rischio: accessi, prezzi, fatture. | 1 | docs/progettazione/piano/test.toml |
| prestazioni | RNF-1 e RNF-5 sotto carico. | 1 | docs/progettazione/piano/test.toml |
| proprieta | Gli invarianti del motore dei prezzi e della numerazione delle fatture. | 1 | docs/progettazione/piano/test.toml |
| unita | La logica interna di ogni modulo, oltre agli oracoli: la scrive chi costruisce. | 1 | docs/progettazione/piano/test.toml |

## incrementi

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| 1 |  | 1 | docs/progettazione/piano/piano.toml |
| 2 |  | 1 | docs/progettazione/piano/piano.toml |

## task

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| C-accessi-be |  | 1 | docs/progettazione/piano/piano.toml |
| C-accessi-fe |  | 1 | docs/progettazione/piano/piano.toml |
| C-fatture-be |  | 1 | docs/progettazione/piano/piano.toml |
| C-fatture-fe |  | 1 | docs/progettazione/piano/piano.toml |
| C-veicoli-be |  | 1 | docs/progettazione/piano/piano.toml |
| C-veicoli-fe |  | 1 | docs/progettazione/piano/piano.toml |
| E-clienti |  | 1 | docs/progettazione/piano/piano.toml |
| E-interventi |  | 1 | docs/progettazione/piano/piano.toml |
| M-prezzi |  | 1 | docs/progettazione/piano/piano.toml |
| O-accessi |  | 1 | docs/progettazione/piano/piano.toml |
| O-clienti |  | 1 | docs/progettazione/piano/piano.toml |
| O-fatture |  | 1 | docs/progettazione/piano/piano.toml |
| O-interventi |  | 1 | docs/progettazione/piano/piano.toml |
| O-prezzi |  | 1 | docs/progettazione/piano/piano.toml |
| O-veicoli |  | 1 | docs/progettazione/piano/piano.toml |
| X-cliente-segue-intervento |  | 1 | docs/progettazione/piano/piano.toml |
| X-intervento-completo |  | 1 | docs/progettazione/piano/piano.toml |

## rischi

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| RK-1 | L'officina continua a usare i fogli di calcolo accanto a Officina. | 1 | docs/progettazione/registri.toml |
| RK-2 | La libreria PDF non genera 50 fatture in meno di 2 secondi sul VPS. | 1 | docs/progettazione/registri.toml |
| RK-3 | Un incidente del fornitore del VPS colpisce insieme server e backup. | 1 | docs/progettazione/registri.toml |
| RK-4 | Le credenziali di un operatore, senza secondo fattore, vengono indovinate o riusate. | 1 | docs/progettazione/registri.toml |
| RK-5 | Raffiche di richieste saturano il VPS condiviso con il sito. | 1 | docs/progettazione/registri.toml |

## assunzioni

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| A-1 | I 20 utenti contemporanei e i 50.000 interventi in cinque anni sono una stima del responsabile. | 1 | docs/progettazione/registri.toml |

## debito

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| DEB-1 | Il backup sta presso lo stesso fornitore del VPS. | 1 | docs/progettazione/registri.toml |

## deperibili

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| DEP-1 | Laravel: versione stabile e finestra di supporto | 1 | docs/progettazione/registri.toml |
| DEP-2 | Vue: versione stabile e politica dei rilasci | 1 | docs/progettazione/registri.toml |
| DEP-3 | PostgreSQL: versione stabile e fine del supporto | 1 | docs/progettazione/registri.toml |
| DEP-4 | OWASP ASVS: versione stabile e livelli di verifica | 1 | docs/progettazione/registri.toml |
| DEP-5 | OpenAPI: versione della specifica supportata dagli strumenti scelti | 1 | docs/progettazione/registri.toml |
| DEP-6 | Problem Details for HTTP APIs (RFC 9457): stato e sostituzioni | 1 | docs/progettazione/registri.toml |

## revisioni

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| REV-1 | Storie, RNF e requisiti sui dati, sui criteri della ISO/IEC/IEEE 29148 | 1 | docs/progettazione/registri.toml |
| REV-2 | Requisiti dell'incremento 1, con il walkthrough dei percorsi critici | 1 | docs/progettazione/registri.toml |
| REV-3 | Il modello concettuale provato su tutte le storie, compresi gli incrementi futuri | 1 | docs/progettazione/registri.toml |
| REV-4 | Modello di dominio, glossario, macchine a stati | 1 | docs/progettazione/registri.toml |
| REV-5 | Valutazione dell'architettura contro gli scenari di qualità | 1 | docs/progettazione/registri.toml |
| REV-6 | Progetto di dettaglio dei moduli, schema, contratti | 1 | docs/progettazione/registri.toml |
| REV-7 | Mockup dei percorsi critici, con frontend-craft | 1 | docs/progettazione/registri.toml |
| REV-8 | Mockup e contratto UI sui criteri WCAG 2.2 AA | 1 | docs/progettazione/registri.toml |
| REV-9 | Tutta la progettazione, con la checklist del catalogo e un reviewer per modulo ad alto rischio | 1 | docs/progettazione/registri.toml |
| REV-10 | Costruzione degli esemplari clienti e interventi e del motore prezzi, con i soli file del repo | 1 | docs/progettazione/registri.toml |
| REV-11 | Immaginando la costruzione fallita | 1 | docs/progettazione/registri.toml |

## modifiche

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| MOD-1 | Il cliente paga la fattura online dall'area cliente. | 1 | docs/progettazione/registri.toml |

## adr

| id | descrizione | inc. | sorgente |
|---|---|---|---|
| ADR-0001 | ADR-0001: Costruire Officina invece di adottare un gestionale | 1 | docs/adr/0001-costruire-officina.md |
| ADR-0002 | ADR-0002: Laravel, Vue con Inertia e PostgreSQL | 1 | docs/adr/0002-stack-laravel-vue-postgresql.md |
| ADR-0003 | ADR-0003: Monolite modulare con cinque moduli e un motore | 1 | docs/adr/0003-monolite-modulare.md |
| ADR-0004 | ADR-0004: Un motore dei prezzi costruito, unico calcolatore dei totali | 1 | docs/adr/0004-motore-dei-prezzi.md |
| ADR-0005 | ADR-0005: Sicurezza e accessi | 1 | docs/adr/0005-sicurezza-e-accessi.md |
| ADR-0006 | ADR-0006: Rilascio ed esercizio sul VPS dell'officina | 1 | docs/adr/0006-rilascio-ed-esercizio.md |
