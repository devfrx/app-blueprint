# Fase 1 — Avvio, analisi del problema e fattibilità

Trasforma un'idea in una decisione formale di procedere, fondata su un problema descritto, obiettivi misurabili e un perimetro scritto. Tutto ciò che qui resta vago, le fasi successive lo interpreteranno: per questo si incalza finché ogni voce è precisa (`decisioni.md`, *Come si parla con l'utente*). Non è un questionario da somministrare per intero: si salta ciò che l'utente ha già detto e si approfondisce dove le risposte aprono questioni.

Sorgenti: `prodotto/visione.md` per il ragionamento, `prodotto/prodotto.toml` per ciò che altri citano per id, `registri.toml` per i rischi, `stato.toml` per scheda e verdetto. Formati: `progetto.py formato <tipo>`.

## 1.01 Il problema

In `visione.md`, sezione *Problema*: chi ha il problema, cosa succede oggi, con quale frequenza e quale costo. Senza nominare la soluzione: "serve un'app che…" descrive una soluzione, "lo stesso dato si scrive tre volte e gli errori arrivano in fattura" descrive un problema. Se il problema non si riesce a dire senza la soluzione, è il primo segnale di nebbia (`profili.md`, *Verdetto*).

## 1.03 Gli stakeholder

Chi usa l'app, chi ne dipende senza usarla, chi la paga, chi la gestirà, chi ne risponde per sicurezza e legge. Per ciascuno `categorie`, `interesse` e `influenza`: la griglia potere-interesse dice chi coinvolgere nelle decisioni e chi informare.

- **`usa = true`** per chi usa il prodotto: ogni attore sarà un ruolo della matrice delle autorizzazioni, e dimenticarne uno qui è un buco di sicurezza dopo.
- **Esercizio, sicurezza e legale** si nominano anche quando sono la stessa persona dell'autore: lo script lo pretende, perché altrimenti le loro domande non le fa nessuno.

## 1.02 Gli obiettivi

Ogni obiettivo ha `testo`, `metrica`, `valore` atteso e `misura`, cioè come si misurerà davvero. "Risparmiare tempo" non è un obiettivo; "meno di 2 minuti tra la chiusura dell'intervento e la fattura, al 90° percentile" sì. Gli obiettivi tornano alla 11.07, che chiede come si misurano in esercizio, e le storie li citano nella `traccia`.

## 1.04 Il contesto

In `visione.md`, sezione *Contesto*: il processo attuale, i sistemi con cui l'app dovrà dialogare (`[[sistemi]]`, con `integrazione = true` per quelli con cui scambia dati), le soluzioni esistenti. Le soluzioni esistenti sono l'ingresso della 1.06.

## 1.08 Perimetro e non-obiettivi

In `visione.md`, sezione *Perimetro*, cosa sta dentro in una frase per area; in `[[non_obiettivi]]` ciò che consapevolmente non si fa, ciascuno con il motivo. Un non-obiettivo vale quanto un requisito: alla 2.14 copre le funzionalità trasversali che non si costruiscono, e protegge lo scope da ciò che "sembrerebbe ovvio" aggiungere.

## 1.09 I vincoli

`[[vincoli]]` con tipo, testo e `fonte`: hosting imposto, budget d'esercizio, competenze di chi manterrà l'app, scadenze, tecnologie imposte, norme. Un vincolo di conformità porta la `norma`. Un vincolo che decide una scelta (uno stack imposto) evita la ricerca su quella scelta: la decisione è già presa, e il vincolo è la sua fonte.

## 1.05 La fattibilità

Sui cinque assi, in `[fattibilita]` una riga ciascuno e in `visione.md` il ragionamento: tecnica (si può fare con la tecnologia e le competenze disponibili?), economica (sviluppo ed esercizio, contro il valore degli obiettivi), operativa (chi la userà e la gestirà ce la fa?), legale (norme, contratti, licenze), temporale (scadenze, se ci sono). Un asse non fattibile si dice subito: è la ragione più economica per non procedere.

## 1.06 Make, buy, riuso, SaaS

Prima di progettare un'app si verifica che non convenga comprarla, riusarla o abbonarsi. Un `researcher` per le soluzioni esistenti, con i criteri che vengono dagli obiettivi e dai vincoli (`decisioni.md`). La scelta è il primo ADR, ed è difficile da invertire. Se vince un'alternativa al costruire, il metodo si ferma qui, e lo si dice: la progettazione di un'app che non si costruirà è lavoro buttato.

## 1.07 Commissionato

Con l'innesco `commissionato`: contratto, proprietà intellettuale, criteri di accettazione e livelli di servizio si scrivono come vincoli con la fonte nel contratto. I criteri di accettazione contrattuali diventano la base della 11.01 e della 11.08: si scrivono adesso perché le storie dovranno soddisfarli.

## 1.10 I rischi iniziali

`[[rischi]]` in `registri.toml`, con tipo, probabilità, impatto, risposta, stato e responsabile. All'avvio servono almeno quelli di prodotto (nessuno la userà, il problema era un altro), tecnici (le incognite note), di progetto (competenze, tempo), di sicurezza e conformità. Il registro si aggiorna a ogni gate (T.01): un rischio accettato porta il `segnale` che lo farà emergere.

## 1.11 La stima d'ordine di grandezza

In `[stima]`: l'`ordine` (aree funzionali, moduli e storie probabili, incrementi), l'`incertezza` dichiarata e la `base` su cui poggia. Misura la dimensione del lavoro, non una durata: serve al verdetto e al go, e la 7.02 la sostituisce con una stima dal piano. Con una scadenza dell'utente, la stima dice quanto scope ci sta (`profili.md`, *Senza tempo*).

## 1.13 e 1.14 Scheda e verdetto

Con problema, stakeholder e contesto noti si compila la scheda, e con perimetro e stima si esprime il verdetto: `profili.md`. Sono le due voci che decidono quali altre valgono, quindi si ricontrollano con l'utente prima di chiuderle.

## 1.12 Go o no-go

La decisione è dell'utente, dopo il quadro di 1.05, 1.06, 1.10 e 1.11. Si registra nella nota della chiusura, con le condizioni se è un go condizionato:

```bash
progetto.py chiudi 1.12 --evidenza prodotto/visione.md#fattibilita ADR-0001 --nota "Go: …"
```

Un no-go chiude la progettazione: si scrive il motivo nella nota, si approva il gate con quella nota, e ci si ferma.

## Gate

Il brief: il problema in due righe, gli obiettivi con le metriche, il perimetro con i non-obiettivi più significativi, la fattibilità per asse, la scelta della 1.06, i rischi principali, scheda e verdetto, il go. Il passaggio da qui alla fase 2 cambia natura al lavoro: da cosa e perché a cosa esattamente, per tutte le funzionalità.
