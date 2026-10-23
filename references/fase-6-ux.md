# Fase 6 — Progettazione UX/UI

Con l'innesco `ui`: chi usa l'app, come si orienta, come appare ogni schermata in ogni stato, con quali parole, e con quale accessibilità. Corre intrecciata alle fasi 2–5, perché la UX scopre requisiti e i requisiti cambiano la UX: personas e journey nutrono le storie, l'architettura dell'informazione cresce con il modello, le schermate si scrivono insieme alle operazioni API che le servono. Le sue voci entrano nella frontiera dalla fase 2; il gate si approva quando sono chiuse, di solito insieme alla fase 5.

La direzione visiva, i mockup e la verifica nel browser seguono `frontend-craft`, che resta la regola per tutto ciò che è interfaccia; qui si dice cosa la progettazione deve fissare perché la costruzione non debba decidere.

Sorgenti: `ux/ux.toml` (personas, sezioni, rotte, schermate), `ux/design-system.toml`, `ux/testi.toml`, `ux/utenti.md`, i mockup in `docs/design/mockups/`. Le voci 6.03, 6.05, 6.06, 6.07, 6.08 e 6.10 si richiudono a ogni incremento, per le schermate che l'incremento costruisce.

## 6.01 Utenti e percorsi

Una ricerca proporzionata al profilo: un'osservazione al posto di lavoro e qualche conversazione per un progetto personale o pubblicabile, interviste e test per un prodotto pubblico. `[[personas]]` una per attore, con descrizione e obiettivi concreti; in `utenti.md` il ragionamento e i journey dei percorsi critici, in Mermaid. Una persona senza un'osservazione dietro è un'assunzione, e si dichiara.

## 6.02 Architettura dell'informazione

`[[sezioni]]` con i ruoli che le vedono, e `[[rotte]]` con il percorso, la schermata e i ruoli; ogni schermata ha una rotta. La terminologia dell'interfaccia è quella del glossario: un utente che legge "commessa" dove il modello dice "intervento" è un utente che non trova le cose.

## 6.04 Design system

Con `frontend-craft`: brief, ipotesi concreta di direzione visiva, conferma dell'utente, poi i token (colore, tipografia, spaziatura, forma, fuoco) e i componenti condivisi con varianti, stati e accessibilità, in `design-system.toml`. Oppure l'adozione motivata di un design system esistente, con il suo ADR (`adozione`). Lo scheletro porta token e componenti nella shell dell'interfaccia: i costruttori li usano, non li inventano.

## 6.05 Schermate

Una voce per schermata in `[[schermate]]`, ed è un contratto quanto un'API:

- il `modulo` che la possiede: il suo frontend la costruisce, anche quando mostra dati o azioni di altri moduli, che chiama attraverso il contratto API. Una schermata, un proprietario: così nessuna finisce in due task, e nessun costruttore decide chi monta il bottone di un altro;
- `scopo`, `ruoli`, le `storie` che serve, il `pattern` se ne segue uno;
- i `dati`, cioè le operazioni API che la alimentano;
- le `azioni`, ciascuna con i ruoli, l'operazione e il **nome accessibile**: oracoli e test end-to-end, scritti prima del codice, cercano gli elementi per ruolo e per nome, quindi il nome si fissa qui. Un test che non trova il bottone segnala anche un problema di accessibilità. I ruoli di un'azione stanno dentro quelli che la regola della sua operazione consente: un bottone offerto a chi riceverebbe un rifiuto è un errore;
- i `testi`, per chiave;
- gli `stati`: caricamento, vuoto, errore, parziale, successo, permesso negato. Ciascuno descritto, o `non-applicabile:` con il motivo. Lo script pretende tutti e sei: lo stato vuoto e quello d'errore sono i primi che una costruzione dimentica.

Lo script avvisa per ogni storia dell'incremento senza schermata.

## 6.03 Mockup

Mockup HTML self-contained in `docs/design/mockups/`, con `frontend-craft`, per i pattern di schermata, per le schermate dei percorsi critici e per quelle fuori pattern; le altre schermate restano voci del contratto, costruite sul pattern del loro esemplare. Ogni percorso critico ha almeno una schermata con il mockup, e il campo `mockup` della schermata lo collega. Un mockup mostra anche gli stati che contano, non solo quello felice.

## 6.07 Testi e microcopy

`ux/testi.toml`, una chiave per testo: titoli, etichette, aiuti, conferme, e i messaggi d'errore che il catalogo degli errori cita con `utente`. Un messaggio d'errore dice cosa è successo e cosa fare adesso, nella lingua del glossario, senza colpe e senza codici interni. I testi sono un contratto perché i test li cercano e perché tradurli dopo tocca ogni stringa.

## 6.09 Dispositivi e lingue

`ST-i18n` dice lingue, formati di date, numeri e valute, fusi, e se le lingue cresceranno; il design system dice i dispositivi e i punti di rottura. Aggiungere una lingua dopo costa ogni stringa: si decide adesso anche quando la risposta è "solo italiano".

## 6.10 Revisione euristica

Un `reviewer` rilegge mockup e voci delle schermate con le dieci euristiche di usabilità (visibilità dello stato, corrispondenza con il mondo reale, controllo e libertà, coerenza e standard, prevenzione degli errori, riconoscere invece di ricordare, flessibilità, design essenziale, aiuto a riconoscere e correggere gli errori, aiuto e documentazione), e riporta i problemi con la gravità. Viene prima del test con utenti reali, perché costa poco e trova i problemi ovvi.

## 6.06 Accessibilità

Il livello del profilo, di solito WCAG 2.2 AA (`FONTI.md`), applicato al design: contrasto dei token, focus visibile, ordine di tabulazione, nomi accessibili, errori annunciati, aree di tocco, nessuna informazione affidata al solo colore. Un `reviewer` lo verifica su mockup, design system e schermate; i criteri automatizzabili diventano controlli nei test d'interfaccia (la prova dell'RNF di accessibilità).

## 6.08 Usabilità con utenti reali

Con un'esposizione pubblica: test sui prototipi con utenti veri, i compiti dei percorsi critici, i problemi principali risolti prima del congelamento. Per un progetto pubblicabile è nel debito di pubblicazione.

## Gate

Il brief: le personas, la mappa delle sezioni, i mockup dei percorsi critici, le schermate con gli stati più delicati, i testi d'errore, il livello d'accessibilità e gli esiti delle revisioni. È spesso il gate in cui l'utente vede per la prima volta l'app: conviene mostrare i mockup, non descriverli.
