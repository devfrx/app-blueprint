# Profilo, applicabilità e verdetto

La checklist non si pota a mano: la scheda del progetto dice quali voci valgono, e lo script lo calcola. Dosare il rigore sul profilo è il criterio di proporzione di `decision-principles` reso verificabile: un gestionale per sé non merita il rigore di un servizio pubblico che muove denaro, ma la differenza si scrive, non si improvvisa voce per voce.

Indice: La scheda · Applicabilità · Pubblicabile e debito di pubblicazione · Esclusioni · Verdetto d'ingresso · Senza tempo.

## La scheda

`[scheda]` in `stato.toml`. `progetto.py inizia` la crea con progetto, responsabile, avvio e incremento; il resto si compila alla voce 1.13, quando problema, stakeholder e contesto sono noti (le sue dipendenze), e il verdetto alla 1.14.

| Campo | Valori | Domanda che lo decide |
|---|---|---|
| `esposizione` | `personale` < `pubblicabile` < `pubblico` | Chi la userà? Solo l'autore o chi lui sceglie; potrebbe diventare pubblica; nasce pubblica |
| `criticita` | `bassa` < `media` < `alta` < `regolamentata` | Cosa costa un errore? Un fastidio; lavoro perso o denaro modesto; danni economici, legali o alla sicurezza; una norma di settore impone la verifica |
| `inneschi` | vedi sotto | Quali fatti, a prescindere dal profilo, chiamano voci in più |
| `processo` | `cascata`, `v`, `iterativo`, `agile`, `ibrido` | Come si alternano progettazione e costruzione: con il metodo è di solito `ibrido`, progettazione completa e costruzione per incrementi |
| `verdetto` | `nebbia`, `fuori-metodo`, `incremento-unico`, `incrementi` | Vedi *Verdetto d'ingresso* |
| `costruzione` | `parallela`, `seriale` | Si decide alla voce 7.12 |

Gli inneschi, con la loro definizione, sono in testa al catalogo (`assets/checklist.toml`): `ui`, `api-pubblica`, `dati-personali`, `dati-particolari`, `denaro`, `integrazioni`, `migrazione-dati`, `ia`, `mercato-ue`, `commissionato`, `multitenant`. Un innesco è un fatto, non una valutazione: con dati personali o mercato UE la valutazione giuridica la fa `compliance-docs`, e gli obblighi correnti si verificano al momento.

Nel dubbio tra due livelli si sceglie quello più alto e si scrive perché nella nota del registro della fase 1: abbassarlo dopo costa una riga, alzarlo dopo costa le voci saltate.

## Applicabilità

Ogni voce del catalogo ha una condizione `quando`, valutata sulla scheda:

- `sempre`;
- `esposizione OP livello`, `criticita OP livello`, con `OP` tra `>=`, `<=`, `==`, `>`, `<`;
- `innesco nome`;
- `non` davanti a un termine, `e` e `o` tra i termini, con `e` che lega più di `o` e senza parentesi.

Per un progetto una voce è:

- **applicabile**: si lavora e si chiude;
- **rinviata**: vedi sotto;
- **non applicabile**: la condizione è falsa, e non si scrive nulla;
- **fuori catena**: fasi 13–15, che nessuna skill esegue per ora.

`progetto.py checklist --fase N` stampa le voci di una fase con il loro stato, `viste/checklist.md` tutte, con il motivo di ogni esclusione calcolata.

Cambiare la scheda cambia le voci che valgono. Se rende applicabili voci di fasi già superate, il registro non è più vero e `verifica` lo dice: il cambio di profilo è una modifica, e si gestisce come tale (`gate.md`).

## Pubblicabile e debito di pubblicazione

La maggior parte dei progetti personali potrebbe un giorno diventare pubblica. `pubblicabile` serve a non pagare oggi l'esercizio di un servizio pubblico senza precludersi di diventarlo:

- **le voci di progetto** (`natura = "progetto"`) si valutano come per un'app pubblica, perché sono difficili da invertire: modello dei dati, autenticazione, autorizzazioni, threat model, analisi quantitative;
- **le voci di esercizio** (`natura = "esercizio"`) che varrebbero solo per un'app pubblica diventano **rinviate**: test di usabilità con utenti reali, SBOM, monitoraggio e reperibilità, hypercare. Non si chiudono: formano il debito di pubblicazione, elencato in `viste/debito-pubblicazione.md`.

Passare da `pubblicabile` a `pubblico` riapre tutte le voci rinviate: è il prezzo della pubblicazione, noto fin dall'inizio, e nessuna di esse richiede di riprogettare.

## Esclusioni

Una voce applicabile che nel progetto non ha senso si chiude come non applicabile, con il motivo:

```bash
progetto.py chiudi 4.12 --non-applicabile --motivo "Un solo utente su un VPS: capacità e costi non sono un rischio"
```

- Il motivo dice perché la voce non serve *a questo progetto*, non che non c'era tempo.
- Da criticità `alta` in su un'esclusione porta anche chi l'ha approvata, `--approvato <nome>`, e ad approvarla è l'utente: lo script lo pretende.
- Un'esclusione resta visibile nella checklist con il suo motivo, e al gate si rilegge.

## Verdetto d'ingresso

Si esprime sempre, alla voce 1.14, anche nel caso normale: rende esplicito che il metodo è una scelta.

- **`nebbia`**: la destinazione non sta in una frase verificabile, le storie che contano cambiano a ogni risposta, due stakeholder vogliono cose incompatibili e nessuno sa chi decide, o un'area chiede studio su più sessioni. Si apre `decision-map` per la parte nebbiosa (`gate.md`, *decision-map*) e si riprende da qui a mappa chiusa.
- **`fuori-metodo`**: l'app sta in una sessione, con una manciata di storie e meno di tre moduli con confini propri; si costruisce con `dev-discipline`, senza piano. È un'euristica: il costo fisso del metodo (scheletro, oracoli, esemplari, rientri) supera il guadagno del parallelismo. La progettazione delle fasi 1–5 resta utile anche così, e si può fermare lì.
- **`incremento-unico`**: tutte le storie si costruiscono in un incremento.
- **`incrementi`**: le storie non stanno in un'ondata di costruzione, i task superano il limite di sotto-agenti concorrenti, o un valore utilizzabile arriva prima costruendo una parte. L'inventario e la progettazione restano complete; le storie portano l'incremento in cui si costruiscono (`gate.md`, *Incrementi*).

## Senza tempo

Il metodo non ha durate: ogni fase finisce quando il suo gate è verde, non quando scade un tempo, e nessuna voce si chiude perché "non c'è tempo". Se l'utente dà una scadenza, la scadenza riduce lo scope, cioè le storie dell'incremento, mai il rigore delle voci che valgono; e lo si dice prima di cominciare. Le stime della fase 1 e della 7 misurano il lavoro, non lo comprimono.
