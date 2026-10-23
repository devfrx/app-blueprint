# Punti, fasi e gate

Il protocollo con cui si lavora la checklist: dove inizia e dove finisce ogni punto e ogni fase, cosa prova che una voce è chiusa, come si ripete per incremento, come si cambia ciò che è già chiuso. I comandi che lo eseguono scrivono al posto della sessione, così ciò che dicono i file e ciò che è successo non divergono.

Indice: Sessioni · Punti · Evidenze · Fasi e gate · Revisioni · Domande e spike · Incrementi · Modifiche · decision-map · Passaggio a parallel-build.

## Sessioni

- **Avvio**: `session-resume` se c'è un handoff, poi `progetto.py stato`, e basta. Lo stato dice scheda, punto aperto, registro, frontiera, domande, mappe aperte ed esito della verifica; il resto si legge per id quando serve (`struttura.md`, *Leggere*).
- **Se la verifica ha errori** all'avvio, si correggono prima di aprire un punto: un errore lasciato indietro diventa la premessa sbagliata del lavoro successivo.
- **Fine**: `session-handoff` alla fine di una fase, o prima che il contesto si saturi. L'handoff è breve, perché lo stato è già nei file: dice il ragionamento in corso, la domanda aperta e il passo successivo, non ciò che `progetto.py stato` ristampa.
- **Commit** a ogni chiusura, con il messaggio `progettazione: <voce> <cosa>`; in un ambiente effimero anche il push, se l'utente l'ha permesso alla voce 0.01.

## Punti

Un punto è il lavoro su una voce. Ha un inizio e una fine espliciti, sempre:

1. **Inizio**: `progetto.py apri <voce>`. Registra il punto in `stato.toml`, porta la fase a `in-corso` (o `riaperto`) e stampa "Inizio punto …" con il fascio della voce: dove vive l'evidenza, i controlli che dovranno passare, le sorgenti da leggere.
2. **Lavoro**: si segue la sezione della voce nella reference della fase, si decide con l'utente (`decisioni.md`), si scrivono le sorgenti.
3. **Fine**: `progetto.py chiudi <voce> --evidenza …`. Prima di scrivere esegue i controlli della voce e verifica che le evidenze esistano: se qualcosa non passa non scrive nulla ed elenca cosa correggere. Poi registra la chiusura, rigenera le viste, stampa gli avvisi dei controlli (non bloccano, ma si leggono adesso), "Fine punto …" e la frontiera.
4. **Commit**.

Regole:

- **Un punto alla volta.** Si lascia un punto aperto solo se lo blocca una domanda registrata (`Q-n` con `punto` uguale alla voce), e allora `apri` accetta un altro punto.
- **La frontiera propone, l'utente dispone.** `stato` elenca le voci applicabili aperte della fase più bassa le cui dipendenze sono chiuse; l'ordine di lavoro si può cambiare, e `apri` avvisa se una dipendenza è ancora aperta.
- **Una voce chiusa non si riapre con `apri`**: si riapre con una modifica.
- **Più voci, un artefatto**: quando un lavoro chiude più voci (le quattro del metodo dei dati, per esempio), ognuna si chiude con il suo comando, con l'evidenza che la riguarda.

## Evidenze

L'evidenza è ciò che un revisore apre per vedere che la voce è soddisfatta:

- un percorso, relativo alla radice o a `docs/progettazione/`, con un'eventuale ancora: `requisiti/storie.toml`, `prodotto/visione.md#problema`;
- un id: `REV-6`, `ADR-0004`, `DEP-3`, `RK-2`;
- un tag: `tag:progettazione/gate-2-2026-10-10`;
- un URL, per ciò che vive fuori dal repo.

Lo script verifica che percorsi e id esistano, non che dicano il vero: quello lo dicono i controlli della voce, per ciò che si può controllare, e le revisioni per il resto. Una chiusura come non applicabile non ha evidenze ma un motivo (`profili.md`, *Esclusioni*).

## Fasi e gate

- **Inizio**: quando si apre il suo primo punto. La fase 6 corre intrecciata alle fasi 2–5: le sue voci entrano nella frontiera dalla fase 2, perché la UX scopre requisiti e i requisiti cambiano la UX.
- **Fine**, in quest'ordine:
  1. tutte le voci applicabili chiuse: `progetto.py checklist --fase N`;
  2. `progetto.py verifica --gate N` senza errori, e con i suoi avvisi letti: sono anche quelli dei controlli delle voci della fase, che la verifica ordinaria non ripete;
  3. controlli trasversali passati in rassegna: `progetto.py checklist --trasversali`, una riga d'esito per voce nella nota del registro;
  4. il brief del gate presentato all'utente;
  5. l'approvazione esplicita dell'utente, e solo allora `progetto.py approva N --da <chi approva> --note "<trasversali, in breve>"`;
  6. commit, e il tag che `approva` stampa.
- **Il brief del gate** sta in una schermata, nella conversazione: le decisioni difficili da invertire della fase, ciascuna con l'alternativa scartata e il suo ADR; le esclusioni con il motivo; assunzioni, rischi e debito nuovi; cosa guardare per primo, cioè dove un errore costerebbe di più; l'esito della verifica. Il rischio di un gate è l'approvazione senza lettura: il brief rende la lettura breve e mirata.
- **`approva` non approva al posto dell'utente**: registra un'approvazione già data. Senza un sì esplicito la fase resta `in-corso`.

Il registro non può mentire: una fase superata con voci aperte è un errore di `verifica`, qualunque sia la causa.

## Revisioni

Le revisioni stanno in `[[revisioni]]` di `registri.toml`, con tipo, oggetto, revisore, data, incremento ed esito; quella di prontezza porta anche `p0` e `p1`, la prova di decidibilità `domande`. Chi le fa:

- un `reviewer`, sotto-agente che non ha scritto ciò che rivede, per requisiti (2.07), walkthrough del modello (3.09), architettura (4.15), dettaglio (5.14), revisione euristica (6.10), accessibilità (6.06), prontezza (7.13) e decidibilità (7.14). Il brief gli dà il tipo, la checklist della reference della fase, la scala P0–P3 e cosa leggere, per id;
- l'utente e gli stakeholder per la validazione dei requisiti (2.10), l'approvazione del modello (3.10), l'usabilità con utenti reali (6.08) e, in costruzione, l'accettazione (11.01, 11.08) e quella operativa (11.02);
- l'utente con la sessione per il pre-mortem (7.16).

Scala dei findings: **P0** rende la costruzione impossibile o sbagliata; **P1** è una lacuna che un costruttore colmerebbe indovinando; **P2** un'incoerenza che non cambia ciò che si costruisce; **P3** rifinitura. I findings si correggono dove stanno, non in un documento a parte; la revisione registra l'esito in una riga. I `reviewer` lavorano in un worktree e vedono solo ciò che è committato: si committa prima di lanciarli.

## Domande e spike

Una domanda che blocca un punto è un `[[domande]]` in `registri.toml`, con il punto che blocca. Si chiude togliendola, quando la risposta è scritta dove si applica. Uno spike è una domanda che solo il codice risolve, e porta il `criterio` di successo misurabile (`decisioni.md`, *Spike*). Il congelamento esige zero domande.

## Incrementi

Le voci il cui lavoro dipende dall'incremento corrente si richiudono a ogni incremento (`↻` in `stato` e nella checklist): criteri delle storie, contratti e schermate dell'incremento, dettaglio dei suoi moduli, revisioni, piano, congelamento, e tutte le voci delle fasi 8–12. Le loro chiusure portano l'incremento, e il registro ha una riga per incremento delle fasi che le contengono. Tutto il resto — prodotto, inventario dei requisiti, dominio, architettura, dati — si progetta una volta, per tutte le funzionalità, e cambia solo con una modifica.

Aprire l'incremento successivo, a costruzione dell'incremento corrente chiusa:

1. `[scheda].incremento` aumenta di uno, con un commit `progettazione: apre l'incremento N`. Le voci per incremento si riaprono da sole, e la frontiera riparte dalla 2.02.
2. Si lavorano le voci riaperte: i criteri delle storie del nuovo incremento, la loro revisione e validazione, il dettaglio dei moduli e i contratti che l'incremento rende completi, le schermate, il piano.
3. Ciò che il nuovo incremento costringe a cambiare in elementi già costruiti — una colonna, una facciata — è una modifica, con l'analisi d'impatto.
4. Congelamento e passaggio a `parallel-build`, come per il primo.

Spostare una storia da un incremento all'altro è una decisione di scope: si fa con l'utente, e se tocca l'incremento congelato è una modifica.

## Modifiche

Una modifica cambia ciò che una chiusura dà per vero: un requisito nuovo o diverso, una decisione rovesciata, un finding della costruzione, un cambio di profilo. Una correzione che non cambia ciò che si costruisce, come un refuso in una descrizione, non lo è.

1. **Impatto**: `progetto.py impatto <id>` per ogni elemento toccato.
2. **Registrazione**: un `[[modifiche]]` in `registri.toml` con descrizione, motivo, data, `impatto` (gli id) e `riapre` (le voci da rifare), `esito = "proposta"`.
3. **Decisione**: all'utente, con ciò che cambia, ciò che si riapre e il costo. Se la respinge, `esito = "respinta"` con una nota: la traccia resta.
4. **Applicazione**: `esito = "approvata"`, `approvato_da`, poi `progetto.py modifica MOD-n`. Le chiusure con data anteriore delle voci elencate non valgono più, e le fasi superate che le contengono tornano `riaperto` nel registro.
5. **Lavoro**: le voci riaperte si lavorano come punti, e le fasi si riapprovano.

Una modifica approvata dopo il congelamento lo annulla sempre, anche senza nominarlo: il congelamento certifica il progetto di quel giorno. Durante la costruzione `parallel-build` ferma i task toccati, e l'incremento si ricongela prima di riprendere.

## decision-map

`decision-map` si usa per la nebbia vera, in qualunque punto: una domanda che richiede studio su più sessioni, o una destinazione che non sta in una frase verificabile.

1. La domanda diventa `Q-n` con il punto che blocca, e la mappa si apre con `decision-map`. Nelle *Note* della mappa si scrive che alla chiusura si torna ad `app-blueprint` al punto `<voce>`, senza emettere issue d'implementazione.
2. La mappa si registra in `stato.toml`, così ogni avvio la vede:

   ```toml
   [[mappe]]
   punto = "4.13"
   link = "https://github.com/<proprietario>/<repo>/issues/<n>"
   ```

3. A mappa chiusa: gli ADR scritti dalla mappa si adottano e si citano, senza riscriverli; la risposta va dove si applica; `Q-n` e la riga di `[[mappe]]` si tolgono; il punto si riprende.

Gli altri punti, se non dipendono dalla domanda, proseguono intanto.

## Passaggio a parallel-build

`progetto.py congela` chiude la progettazione dell'incremento (`fase-7-pianificazione.md`). Da lì la frontiera mostra le voci di `parallel-build`: ambienti e scheletro (7.09, 7.10), poi le fasi 8–12, sullo stesso registro e con gli stessi comandi. `parallel-build` legge la progettazione per id, e il brief di ogni task è la sua procedura più `progetto.py fascio --task <id>`.
