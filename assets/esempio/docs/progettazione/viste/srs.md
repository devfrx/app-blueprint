<!-- Generato da app-blueprint (progetto.py viste): non modificare a mano. Le sorgenti sono in docs/progettazione/ e contracts/. -->

# Specifica dei requisiti — Officina

Vista generata dalle sorgenti dei requisiti: per leggerla, non per modificarla.

## Obiettivi

- **OB-1** L'officina gestisce preventivi, interventi e fatture solo con Officina, senza fogli di calcolo. — metrica: Quota degli interventi del mese gestiti in Officina; valore atteso: 100% dal secondo mese d'uso.
- **OB-2** Emettere una fattura costa meno tempo e nessuna trascrizione. — metrica: Minuti tra la chiusura dell'intervento e l'emissione della fattura; valore atteso: Meno di 2 minuti al 90° percentile.
- **OB-3** I clienti seguono lo stato dei propri interventi senza telefonare. — metrica: Telefonate per chiedere lo stato, a settimana; valore atteso: -50% entro tre mesi.

## Stakeholder e attori

- **cliente** (attore; utente): Segue lo stato dei propri interventi.
- **commercialista** (non usa il prodotto; esterno): Riceve le fatture in PDF dal responsabile. Non usa Officina, ma il suo lavoro dipende da come le fatture sono numerate.
- **consulente-privacy** (non usa il prodotto; legale): Professionista che rivede informativa e registro dei trattamenti prima del lancio.
- **operatore** (attore; utente): Accetta i veicoli, apre e chiude gli interventi, compila i preventivi, registra clienti e veicoli.
- **responsabile** (attore; utente, committente): Titolare dell'officina: approva i preventivi, emette le fatture, gestisce gli account.
- **sviluppatore** (non usa il prodotto; sviluppo, esercizio, sicurezza): Sviluppatore PHP a tempo parziale: manterrà l'app, ne gestisce il VPS e la sicurezza.

## Perimetro

Non-obiettivi:

- **NO-1** Registrazione autonoma: gli account li crea il responsabile, o nascono con il cliente.
- **NO-2** Cambio della password dall'interno: si usa il recupero (ACC-3).
- **NO-3** Profilo modificabile dall'utente: nome ed email li corregge il responsabile.
- **NO-4** Audit consultabile dall'interfaccia: le azioni su preventivi e fatture si registrano e si consultano dal database.
- **NO-5** Notifiche oltre a invito, recupero della password e, nel secondo incremento, promemoria di revisione; nessuna preferenza di notifica.
- **NO-6** Import da altri gestionali: clienti e veicoli si inseriscono a mano.
- **NO-7** Richieste privacy self-service: le evade il responsabile con la procedura del runbook (ADR-0005).
- **NO-8** Onboarding guidato e aiuto in linea: gli utenti sono pochi e imparano di persona.
- **NO-9** Invio delle fatture ai sistemi fiscali: lo fa il commercialista, che le riceve in PDF.
- **NO-10** App mobile nativa: l'interfaccia web è responsiva.

## Vincoli

- **V-1** (tecnico) Esercizio su un solo VPS, già in uso per il sito dell'officina.
- **V-2** (budget) Budget d'esercizio: il VPS esistente, nessun servizio a pagamento in più.
- **V-3** (competenze) Manutenzione affidata a uno sviluppatore PHP a tempo parziale.
- **V-4** (organizzativo) Interfaccia solo in italiano.
- **V-5** (conformita) Dati personali dei clienti (nome, codice fiscale, email, targhe): minimizzazione, informativa, registro dei trattamenti e diritti degli interessati, secondo il GDPR.
- **V-6** (conformita) Numerazione progressiva per anno senza buchi e conservazione delle fatture per il periodo di legge: i dettagli si verificano con il commercialista.
- **V-7** (conformita) Nessun obbligo di legge sull'accessibilità per un gestionale interno; il livello AA è un requisito di qualità (RNF-3). Non rientra nel Cyber Resilience Act né nell'AI Act: nessuna messa sul mercato, nessuna funzione di IA.

## Requisiti funzionali

### Accessi

- **ACC-1** L'operatore accede ed esce — attore operatore, priorità must, incremento 1.
  - *Dato* l'account attivo mario@officina.test con la sua password, *quando* accede, *allora* vede l'elenco degli interventi aperti.
  - *Dato* quattro tentativi falliti per mario@officina.test, *quando* il quinto fallisce, *allora* riceve account-bloccato, e solo il responsabile può sbloccarlo (ACC-7).
  - *Dato* l'operatore dentro Officina, *quando* esce, *allora* la sessione termina e ogni pagina interna chiede di nuovo l'accesso.
- **ACC-2** Il responsabile crea l'account di un operatore — attore responsabile, priorità must, incremento 1.
  - *Dato* nessun account per luca@officina.test, *quando* il responsabile lo crea con il ruolo operatore, *allora* l'account è invitato e parte l'email con il link d'attivazione.
  - *Dato* un account per luca@officina.test, *quando* il responsabile lo crea di nuovo, *allora* riceve account-esistente e nessuna email parte.
- **ACC-3** L'operatore recupera la password — attore operatore, priorità must, incremento 1.
  - *Dato* l'account attivo mario@officina.test, *quando* chiede il recupero, *allora* riceve un link valido una sola volta per 60 minuti.
  - *Dato* nessun account per ignoto@officina.test, *quando* chiede il recupero, *allora* vede la stessa conferma del caso precedente, e nessuna email parte.
- **ACC-4** Il responsabile accede con un secondo fattore — attore responsabile, priorità must, incremento 1.
  - *Dato* il responsabile con il secondo fattore attivo, *quando* accede con password e codice corretto, *allora* entra.
  - *Dato* il responsabile con il secondo fattore attivo, *quando* inserisce un codice già usato, *allora* riceve codice-non-valido.
- **ACC-5** Il cliente attiva l'account dall'invito — attore cliente, priorità must, incremento 1.
  - *Dato* l'invito valido per mario.rossi@example.test, *quando* apre il link e sceglie una password di 12 caratteri, *allora* l'account è attivo e il cliente entra; lo stesso vale per l'invito di un operatore.
  - *Dato* un link d'invito già usato, *quando* lo riapre, *allora* riceve link-non-valido.
  - *Dato* l'invito valido, *quando* sceglie una password di 8 caratteri, *allora* riceve password-debole e l'account resta invitato.
- **ACC-6** Il cliente consulta l'informativa privacy e le pagine di servizio — attore cliente, priorità must, incremento 1.
  - *Dato* la pagina d'attivazione, *quando* il cliente apre il link all'informativa, *allora* legge l'informativa senza dover accedere.
  - *Dato* un indirizzo inesistente, *quando* lo apre, *allora* vede la pagina 'non trovata' con il link alla pagina iniziale.
- **ACC-7** Il responsabile sblocca un account bloccato — attore responsabile, priorità must, incremento 1.
  - *Dato* mario@officina.test bloccato dopo cinque tentativi, *quando* il responsabile lo sblocca, *allora* l'account torna attivo con zero tentativi falliti.
  - *Dato* un account attivo, *quando* un operatore prova a sbloccarlo, *allora* riceve non-autorizzato.

### Clienti

- **CLI-1** L'operatore registra un cliente — attore operatore, priorità must, incremento 1.
  - *Dato* nessun cliente con codice fiscale RSSMRA80A01H501U, *quando* l'operatore registra Mario Rossi con quel codice e l'email mario.rossi@example.test, *allora* il cliente esiste e ha un account invitato.
  - *Dato* un cliente con codice fiscale RSSMRA80A01H501U, *quando* l'operatore ne registra un altro con lo stesso codice, *allora* riceve cliente-duplicato e nulla viene creato.
  - *Dato* nessun cliente, *quando* l'operatore registra il codice fiscale RSSMRA80A01H501X, *allora* riceve codice-fiscale-non-valido.
- **CLI-2** L'operatore cerca i clienti per nome — attore operatore, priorità should, incremento 2.

### Fatture

- **FAT-1** Il responsabile emette la fattura di un intervento chiuso — attore responsabile, priorità must, incremento 1.
  - *Dato* un intervento chiuso, e l'ultima fattura del 2026 con numero 41, *quando* il responsabile emette la fattura, *allora* nasce la fattura 42/2026 con le righe e il totale del preventivo approvato.
  - *Dato* un intervento in lavorazione, *quando* il responsabile prova a fatturarlo, *allora* riceve intervento-non-chiuso.
  - *Dato* un intervento già fatturato, *quando* il responsabile prova a fatturarlo di nuovo, *allora* riceve fattura-esistente e nessun numero viene consumato.
- **FAT-2** Il responsabile esporta in CSV le fatture del mese — attore responsabile, priorità could, incremento 2.
- **FAT-3** Il responsabile scarica il PDF di una fattura per il commercialista — attore responsabile, priorità must, incremento 1.
  - *Dato* la fattura 42/2026, *quando* il responsabile ne scarica il PDF, *allora* riceve un PDF con numero, data, righe, imponibile, IVA e totale uguali alla fattura.
  - *Dato* la stessa fattura, *quando* un operatore prova a scaricarla, *allora* riceve non-autorizzato.

### Interventi e preventivi

- **INT-1** L'operatore apre un intervento su un veicolo — attore operatore, priorità must, incremento 1.
  - *Dato* il veicolo AB123CD senza interventi aperti, *quando* l'operatore apre un intervento per il cambio dei freni, *allora* l'intervento INT-2026-0001 è in accettazione con un preventivo vuoto.
  - *Dato* un intervento aperto su AB123CD, *quando* l'operatore ne apre un secondo, *allora* riceve intervento-gia-aperto (R-4).
- **INT-2** Il responsabile approva il preventivo — attore responsabile, priorità must, incremento 1.
  - *Dato* un preventivo con manodopera da 90,00 € (2 h a 45,00 €) e pastiglie da 60,00 €, IVA 22%, *quando* il responsabile lo approva, *allora* il totale è 183,00 € e l'intervento passa in lavorazione.
  - *Dato* lo stesso preventivo, *quando* un operatore prova ad approvarlo, *allora* riceve non-autorizzato e il preventivo resta in bozza.
  - *Dato* un preventivo senza righe, *quando* il responsabile prova ad approvarlo, *allora* riceve preventivo-vuoto.
- **INT-3** Il cliente vede lo stato del proprio intervento — attore cliente, priorità must, incremento 1.
  - *Dato* Mario Rossi con un intervento in lavorazione, *quando* lo apre, *allora* vede stato, preventivo approvato e data prevista.
  - *Dato* l'intervento di un altro cliente, *quando* Mario Rossi ne apre l'indirizzo, *allora* riceve non-trovato, senza indizi che esista.
- **INT-4** L'operatore chiude l'intervento a lavori finiti — attore operatore, priorità must, incremento 1.
  - *Dato* l'intervento su AB123CD in lavorazione, con il preventivo approvato, *quando* l'operatore lo chiude, *allora* l'intervento è chiuso e si può fatturare.
  - *Dato* un intervento in accettazione, con il preventivo in bozza, *quando* l'operatore prova a chiuderlo, *allora* riceve preventivo-non-approvato (R-1).
- **INT-5** L'operatore compila il preventivo — attore operatore, priorità must, incremento 1.
  - *Dato* l'intervento su AB123CD in accettazione, *quando* l'operatore aggiunge 2 h di manodopera a 45,00 € e le pastiglie da 60,00 € del listino, *allora* il preventivo mostra 183,00 € IVA compresa, calcolati dal motore dei prezzi.
  - *Dato* lo stesso intervento, *quando* l'operatore aggiunge una riga con quantità 0, *allora* riceve quantita-non-valida e il preventivo non cambia.
  - *Dato* un preventivo approvato, *quando* l'operatore prova ad aggiungere una riga, *allora* riceve preventivo-approvato.
- **INT-6** L'operatore consulta l'elenco degli interventi aperti — attore operatore, priorità must, incremento 1.
  - *Dato* 30 interventi aperti e 5 chiusi, *quando* l'operatore apre l'elenco, *allora* vede i 25 aperti più vecchi per primi, con targa, cliente e stato, e il collegamento alla pagina successiva.
  - *Dato* nessun intervento aperto, *quando* apre l'elenco, *allora* vede lo stato vuoto con il comando per aprirne uno.

### Prezzi

- **PRZ-1** Il responsabile aggiorna il listino dall'interfaccia — attore responsabile, priorità should, incremento 2.

### Veicoli

- **VEI-1** L'operatore associa un veicolo a un cliente — attore operatore, priorità must, incremento 1.
  - *Dato* il cliente Mario Rossi e nessun veicolo con targa AB123CD, *quando* l'operatore gli associa ab 123 cd, *allora* il veicolo AB123CD compare tra quelli del cliente.
  - *Dato* la targa AB123CD già associata, *quando* l'operatore la associa a un altro cliente, *allora* riceve veicolo-duplicato.
- **VEI-2** Il cliente riceve un promemoria quando la revisione del veicolo sta per scadere — attore cliente, priorità should, incremento 2.

## Requisiti di qualità

- **affidabilita** — rilevanza alta: Le fatture emesse non si possono perdere.
- **capacita-di-interazione** — rilevanza alta: Deve essere più comodo dei fogli, o non verrà usata (RK-1).
- **compatibilita** — rilevanza media: Coesiste con il sito sullo stesso VPS (V-1).
- **efficienza-prestazionale** — rilevanza media: Pochi utenti, ma l'elenco degli interventi si consulta di continuo.
- **flessibilita** — rilevanza bassa: Un solo ambiente d'esercizio, nessun porting previsto.
- **idoneita-funzionale** — rilevanza alta: Un totale sbagliato in fattura è un danno economico e fiscale.
- **manutenibilita** — rilevanza alta: La manterrà uno sviluppatore a tempo parziale che non l'ha scritta (V-3).
- **safety** — rilevanza non-pertinente: Nessuna funzione mette a rischio persone o beni.
- **sicurezza** — rilevanza alta: Dati personali dei clienti e denaro.

- **RNF-1** (efficienza-prestazionale) Quando 20 utenti consultano insieme l'elenco degli interventi aperti, in 50.000 interventi in archivio, esercizio normale sul VPS condiviso, il sistema restituisce la prima pagina dell'elenco entro 300 ms al 95° percentile. Prova: Test di carico su staging con dati sintetici prima del rilascio: in locale non si verifica.
- **RNF-2** (affidabilita) Quando il server va perso, in un incidente del fornitore del VPS, il sistema Officina torna operativa dal backup entro RTO di 4 h e RPO di 24 h. Prova: Ripristino dal backup notturno provato su staging seguendo il runbook.
- **RNF-3** (capacita-di-interazione) Quando un utente percorre i percorsi critici da tastiera o con un lettore di schermo, in browser recenti, desktop e mobile, il sistema completa ogni passo entro nessuna violazione WCAG 2.2 di livello AA. Prova: Controllo automatico dell'accessibilità nei test d'interfaccia, più la lente UI della revisione.
- **RNF-4** (sicurezza) Quando un utente prova un'operazione o una risorsa fuori dal suo perimetro, in qualsiasi ruolo, compreso chi cambia un id nell'URL, il sistema nega con l'errore previsto dal catalogo entro 100% delle regole della matrice e delle condizioni di proprietà. Prova: Test di autorizzazione dalla matrice; mutation testing sui moduli ad alto rischio; revisione di sicurezza approfondita.
- **RNF-5** (compatibilita) Quando il carico di RNF-1, in il VPS condiviso con il sito, il sistema Officina resta nei suoi limiti di risorse entro al massimo 1 GB di RAM e metà della CPU. Prova: Misura su staging durante il test di carico di RNF-1.
- **RNF-6** (manutenibilita) Quando uno sviluppatore che non conosce il progetto deve aggiungere un modulo crud, in solo la documentazione del repo, senza aiuto, il sistema lo aggiunge seguendo i pattern dell'esemplare entro nessuna domanda e nessuna deviazione dai pattern nella prova. Prova: Test di manutenibilità alla chiusura della costruzione.
- **RNF-7** (idoneita-funzionale) Quando il motore dei prezzi calcola un preventivo o una fattura, in la tabella di 40 casi d'esempio fornita dal commercialista, il sistema produce imponibile, IVA e totale entro uguali al centesimo in tutti i casi. Prova: Suite di conformità del motore con i 40 casi, più test basati su proprietà degli invarianti.

## Requisiti sui dati

- **RD-1** intervento: volume 50.000 in archivio dopo cinque anni, crescita circa 10.000 all'anno, conservazione quanto le fatture a cui sono legati.
- **RD-2** cliente: volume 5.000, crescita circa 800 all'anno, conservazione finché il cliente è attivo; poi cancellazione su richiesta, salvo i dati che le fatture devono conservare.
- **RD-3** fattura: volume 10.000 all'anno, crescita lineare con gli interventi, conservazione il periodo di legge, da verificare con il commercialista (V-6).
- **RD-4** veicolo: volume 6.000, crescita circa 900 all'anno, conservazione quanto il cliente.

## Glossario

- **account**: L'accesso di una persona a Officina, con un ruolo; nasce invitato e diventa attivo con l'attivazione.
- **cliente**: La persona che porta i veicoli in officina e riceve le fatture.
- **fattura**: Il documento emesso per un intervento chiuso, con numero progressivo per anno; una volta emessa non cambia.
- **intervento**: Il lavoro su un veicolo, dall'accettazione alla chiusura. Ha un preventivo e, chiuso, può avere una fattura.
- **manodopera**: Voce di listino prezzata a ore.
- **motore dei prezzi**: La logica unica che calcola imponibile, IVA e totale di preventivi e fatture.
- **preventivo**: Le righe di manodopera e ricambi di un intervento; il totale lo calcola il motore dei prezzi.
- **ricambio**: Voce di listino prezzata a pezzo.
- **riga di fattura**: Copia di una riga del preventivo approvato al momento dell'emissione.
- **riga di preventivo**: Una voce del listino con quantità, prezzo e aliquota al momento dell'inserimento.
- **veicolo**: Un mezzo di un cliente, identificato dalla targa.
- **voce di listino**: Una prestazione o un ricambio con il suo prezzo e la sua aliquota IVA.
