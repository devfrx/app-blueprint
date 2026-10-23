# Ricerca e decisioni

Le decisioni si prendono su evidenza letta al momento, non su ciò che si ricorda (`decision-principles`). La ricerca si delega e si parallelizza perché è lettura; la decisione resta all'utente.

Indice: Come si parla con l'utente · Ricerca · Presentare una decisione · Dove finisce una decisione · Deperibili · Spike.

## Come si parla con l'utente

**Deroga dichiarata a `dev-communication`.** `dev-communication` chiede la domanda minima necessaria, e regge quando la direzione è nota. Nel prodotto, nei requisiti e nelle decisioni la direzione è proprio ciò che manca: le domande sono la produzione, non attrito. Qui si incalza, con domande concrete e le opzioni già individuate, usando lo strumento di domanda a opzioni se l'ambiente lo offre. Una risposta vaga su un requisito misurabile non si registra come requisito: è debito che sembra un asset.

Due confini:

- **Non chiedere ciò che puoi verificare.** Versioni, compatibilità, maturità di una libreria: risponde un `researcher`, non l'utente.
- **Fuori da prodotto, requisiti e decisioni** `dev-communication` torna in vigore senza deroghe.

Se l'utente non sa dare un numero, proponi intervalli plausibili e fai scegliere: il numero scelto è un'assunzione, registrata come tale (`A-n`), mai un numero inventato al suo posto.

## Ricerca

Un `researcher` per decisione aperta, tutti nello stesso turno. Il protocollo e il formato del dossier sono nella sua definizione; il brief gli dà solo la domanda in una frase, i requisiti che la governano citati per id, i vincoli e le decisioni già prese, le opzioni già escluse e perché.

**Un dossier è una dichiarazione.** Prima di presentare la decisione, un secondo `researcher`, che non l'ha scritto, apre le fonti delle affermazioni su cui poggia la raccomandazione e dice quali reggono. Se il dossier non regge, si rilancia la ricerca sul punto preciso invece di correggerlo a memoria. Un dossier che torna a mani vuote è un risultato: si decide con meno evidenza, e l'ADR lo dichiara.

Non si ricerca ciò che un vincolo ha già deciso, come uno stack imposto: si registra come vincolo, con la sua fonte.

## Presentare una decisione

Con la domanda e i requisiti che la governano, le opzioni reali con i trade-off in poche righe, la raccomandazione e il perché, e la sua classe:

- **difficile da invertire**, se tornare indietro butta lavoro già fatto (framework, database, modello d'autenticazione, confini dei moduli, modello dei dati): si presenta da sola;
- **reversibile**, se il cambio resta contenuto: si presenta insieme alle altre reversibili, e l'utente le conferma con una risposta.

Dopo ogni decisione si ricontrolla la coerenza con le precedenti: l'hosting vincola il database, l'autenticazione vincola il frontend. Una decisione che ne contraddice una presa si espone, non si risolve in silenzio. Uno scostamento dallo stato dell'arte si dichiara nell'ADR e al gate, e lo accetta l'utente.

## Dove finisce una decisione

- **Difficile da invertire → un ADR** in `docs/adr/NNNN-<titolo>.md`, nel formato di `design-docs`, al massimo una pagina: contesto, alternative scartate con il motivo in una riga, decisione, conseguenze comprese le negative accettate, e *Fonti* quando poggia su fonti esterne, citate con il loro `DEP-n`. Un ADR registra il perché: ciò che la decisione comporta va nelle sorgenti, che citano l'ADR (una strategia con `adr`, un RNF con `indirizzato_da`). Se una decisione cade, l'ADR diventa `Superseded` e se ne scrive uno nuovo.
- **Reversibile → una riga dove si applica**: una strategia in `architettura.toml` se è trasversale, un campo della sorgente se riguarda un elemento.
- **Decisioni che si scelgono insieme**, perché le alternative sono pacchetti, sono un ADR solo.

Di solito un'app ha da cinque a dieci ADR: la scelta make/buy (1.06), lo stack, lo stile architetturale, il modello dei dati se non è ovvio, la sicurezza, il rilascio, e il motore se c'è.

## Deperibili

Ogni fatto che scade — versione, finestra di supporto, advisory, deprecazione, standard in revisione — è un `[[deperibili]]` in `registri.toml`, con la fonte e `verificato_il`. Gli ADR e le sorgenti lo citano per id, così la data vive in un posto solo. Al congelamento un `researcher` li riverifica tutti (7.15): `progetto.py congela` rifiuta un deperibile verificato prima della data del congelamento.

## Spike

Uno spike verifica con il codice un'assunzione la cui caduta cambierebbe un contratto o un ADR: la libreria regge il volume? il servizio esterno è idempotente? Ciò che si risolve leggendo la documentazione è ricerca.

1. Finché è aperto, lo spike è una domanda `Q-n` con il `criterio` di successo misurabile e il punto che blocca.
2. Lo esegue un `backend-builder` o un `frontend-builder` in un worktree, con un brief che dice che è uno spike e che il codice è usa e getta, e dà domanda e criterio. La risposta torna con la prova: comando, misura, output.
3. L'esito va nell'ADR che dipendeva dall'assunzione, o nella sorgente; la domanda si toglie e il ramo dello spike si cancella. La voce 4.14 si chiude con gli ADR che riportano gli esiti.

Se l'assunzione cade, si torna alla decisione con l'utente prima di specificare altro: contratti scritti su un'assunzione falsa si scrivono due volte.
