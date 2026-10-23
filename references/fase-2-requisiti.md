# Fase 2 — Ingegneria dei requisiti

Produce l'inventario completo di ciò che l'app deve fare, per tutti gli incrementi, e la specifica verificabile di ciò che fa l'incremento corrente. È la fase da cui dipende la promessa del metodo: gli schemi si progettano una volta, bene, solo se tutte le funzionalità sono sul tavolo prima di disegnarli. Le voci 2.02, 2.07 e 2.10 si ripetono a ogni incremento, per le storie che l'incremento costruisce.

Sorgenti: `requisiti/requisiti.toml`, `requisiti/storie.toml` (o `storie-<area>.toml`), `dominio/glossario.toml`, i vincoli in `prodotto.toml`. La vista `viste/srs.md` presenta tutto come una specifica dei requisiti da leggere, e `viste/tracciabilita.md` è la matrice di tracciabilità: si generano, non si scrivono.

Ordine utile: raccolta (2.01) e glossario (2.13), poi storie (2.02) e trasversali (2.14), qualità (2.03–2.05), conformità (2.06), priorità (2.09), percorsi critici (2.15), conflitti (2.08), e alla fine revisione (2.07), validazione (2.10) e baseline (2.11).

## 2.01 Raccolta

Da ogni stakeholder rilevante, con la tecnica che il contesto consente: intervista per chi decide, osservazione o analisi dei documenti per il processo attuale (i fogli, i moduli, le fatture vere), workshop quando gli stakeholder si contraddicono, prototipo quando l'utente non sa descrivere ciò che vuole ma lo riconosce vedendolo. Ogni requisito porta la sua `fonte`: lo script segnala uno stakeholder d'interesse alto che non è fonte di nulla, cioè qualcuno che nessuno ha ascoltato.

## 2.13 Glossario

Un termine per concetto, lo stesso in dati, API, codice e interfaccia, con la `definizione` e i sinonimi da `evitare`. Si scrive prima delle storie perché le storie lo usano: lo script segnala un sinonimo vietato nel titolo di una storia. Alla 3.02 il glossario diventa il linguaggio ubiquo del modello.

## 2.02 Storie e criteri

L'inventario copre tutte le funzionalità di tutti gli incrementi; i criteri sono obbligatori per le storie dell'incremento corrente e benvenuti per le altre.

- **Aree**: `[[aree]]` con un prefisso di 2–5 maiuscole; l'id di una storia è `<AREA>-n`, stabile per sempre.
- **Una storia** ha titolo, `attore` (uno stakeholder con `usa = true`), `priorita`, `incremento`, `fonte`, e la `traccia` verso gli obiettivi che serve. Ha la forma INVEST: indipendente, negoziabile, di valore, stimabile, piccola, verificabile.
- **I criteri** sono *dato / quando / allora* con dati concreti, e coprono la variante principale e almeno un caso d'errore: lo script avvisa sotto i due criteri. "L'operatore registra un cliente con codice fiscale RSSMRA80A01H501U" è verificabile; "l'operatore registra un cliente" no. Ogni criterio diventerà un test d'accettazione, scritto da chi non costruisce.
- **Entità e moduli** non si scrivono adesso: `entita`, `modulo` e `tocca` li aggiunge la fase 3, quando il modello esiste, ed è la prova che lo spiega (3.09).

## 2.14 Funzionalità trasversali

Le funzionalità che nessuno chiede e tutti si aspettano. `[trasversali]` in `requisiti.toml` ha una chiave per ciascuna, e ogni chiave elenca le storie che la coprono o i non-obiettivi che la escludono:

- `autenticazione`: registrazione, accesso, uscita, recupero e cambio della password, verifica dell'email, secondo fattore, scadenza della sessione;
- `account-e-profilo`, `utenti-e-ruoli`, `amministrazione`, `audit` consultabile;
- `notifiche` e preferenze, `ricerca`, `import-export`;
- `privacy`: i diritti degli interessati;
- `pagine-di-servizio`: errore, manutenzione, pagine legali;
- `onboarding-e-aiuto`.

Lo script rifiuta una chiave vuota: una funzionalità trasversale dimenticata è la lacuna più comune di una progettazione, e la si scopre di solito in costruzione.

## 2.03 Le caratteristiche di qualità

Le nove caratteristiche della ISO/IEC 25010:2023 (`FONTI.md`), tutte in `[[qualita]]` con `rilevanza` e `motivo`, anche quelle non pertinenti: idoneità funzionale, efficienza prestazionale, compatibilità, capacità di interazione, affidabilità, sicurezza, manutenibilità, flessibilità, safety. Scartarne una per iscritto è una decisione; dimenticarla no.

## 2.04 Requisiti non funzionali

Ogni caratteristica di rilevanza alta ha almeno un RNF, e una di rilevanza media di solito anche. Un RNF è uno scenario misurabile: *quando* `stimolo`, *in* `contesto`, *il sistema* `risposta` *entro* `misura`, con la `prova` che lo verificherà, o la dichiarazione che in locale non si verifica. "Veloce" non è un RNF; "la prima pagina dell'elenco in 300 ms al 95° percentile con 20 utenti e 50.000 interventi" sì. Un numero che l'utente sceglie senza misure è un'assunzione (`assunzione = "A-n"`). Il campo `indirizzato_da` si compila in fase 4, con le decisioni che lo soddisfano.

## 2.05 Dati, interfacce, vincoli

`[[requisiti_dati]]` per ogni concetto con volume, crescita, conservazione e qualità attesa: sono l'ingresso della tavola dei volumi (5.05.1) e delle analisi quantitative (4.12). Le interfacce sono i `[[sistemi]]` della fase 1; i vincoli nuovi si aggiungono a `[[vincoli]]`.

## 2.06 Conformità

Un vincolo `conformita` per ogni obbligo, con la `norma`; se non ce ne sono, lo si scrive come vincolo. Con gli inneschi lo script si aspetta di vedere nominati il GDPR (`dati-personali`), il Cyber Resilience Act (`mercato-ue`) e l'AI Act (`ia`); l'accessibilità per i servizi ai consumatori nell'UE ha le sue norme. La valutazione giuridica è di `compliance-docs`, e gli obblighi correnti si verificano al momento: le date che il metodo conosce sono in `FONTI.md`, verificate in un giorno preciso.

## 2.09 Priorità

`metodo_priorita` dichiara il metodo e i suoi valori (MoSCoW, o un altro), e ogni storia ne ha uno. La priorità decide l'`incremento` di ogni storia: l'incremento 1 è il primo che dà valore utilizzabile, non il più facile da costruire. Le storie `wont` restano nell'inventario: dicono cosa si è scelto di non fare.

## 2.15 Percorsi critici

Le sequenze di storie che, se si rompono, rendono l'app inutile: `[[percorsi]]` con le storie in ordine, accesso compreso. Diventano i diagrammi di sequenza della 5.08 e i test end-to-end del piano.

## 2.08 Conflitti

Con un'esposizione da pubblicabile in su, o un committente: dove due stakeholder vogliono cose incompatibili, `[[conflitti]]` con chi, su cosa e come si è risolto, e chi ha deciso.

## 2.07 Revisione dei requisiti

Un `reviewer` rilegge le storie dell'incremento, i RNF e i requisiti sui dati contro le caratteristiche di un buon requisito: necessario, non ambiguo, singolo, verificabile, coerente con gli altri, fattibile. In più: criteri senza caso d'errore, termini fuori glossario, storie che ne nascondono due. I findings si correggono; la revisione si registra (`gate.md`, *Revisioni*).

## 2.10 Validazione

Con gli stakeholder, non con un agente: un walkthrough delle storie dell'incremento e dei percorsi critici, o un prototipo per ciò che sulla carta non si capisce. La domanda è "è questo che serve?", non "è scritto bene?". La revisione registra chi ha validato e cosa è cambiato.

## 2.11 e 2.12 Baseline e tracciabilità

La baseline dei requisiti è il tag del gate: da lì ogni cambio passa dalla procedura delle modifiche di `gate.md`, uguale per tutti i progetti. La matrice di tracciabilità è `viste/tracciabilita.md`: si genera dalle tracce, e si completa da sola man mano che le fasi successive aggiungono entità, moduli, operazioni, schermate e test.

## Gate

Il brief: quante storie per area e per incremento, le funzionalità trasversali escluse e perché, le caratteristiche di qualità rilevanti con i loro RNF, gli obblighi di conformità, i percorsi critici, gli esiti di revisione e validazione. La domanda all'utente è una: questo inventario contiene tutto ciò che l'app dovrà fare, anche dopo il primo incremento?
