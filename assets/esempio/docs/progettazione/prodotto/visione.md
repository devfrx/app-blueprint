+++
fase = 1
+++
# Officina — visione

## Problema

L'officina gestisce preventivi, interventi e fatture con fogli di calcolo e un registro cartaceo. Lo stesso dato si scrive tre volte: nel preventivo, nel foglio dei lavori, nella fattura. Gli errori di trascrizione arrivano fino alle fatture, la numerazione si corregge a mano e i clienti telefonano per sapere a che punto è il loro veicolo.

## Contesto

- **Processo attuale**: l'operatore accetta il veicolo e scrive il preventivo su un foglio; il responsabile lo approva a voce; a lavori finiti il responsabile ricopia le righe in un modello di fattura e la manda in PDF al commercialista, che la trasmette ai sistemi fiscali.
- **Sistemi**: un VPS già in uso per il sito dell'officina; un servizio di posta via SMTP. Nessun gestionale da sostituire: i dati storici restano nei fogli.
- **Soluzioni esistenti**: i gestionali per officine valutati sono confrontati in ADR-0001.

## Perimetro

Dentro: clienti e veicoli, interventi con preventivo approvato, motore dei prezzi, fatture numerate e in PDF, accesso con ruoli, area del cliente per seguire i propri interventi. Fuori: i non-obiettivi in `prodotto.toml`; in particolare l'invio ai sistemi fiscali, che resta del commercialista.

## Fattibilità

- **Tecnica**: un'app web su un solo VPS regge i volumi di RD-1…RD-4 (analisi in `architettura/analisi.md`).
- **Economica**: nessun costo d'esercizio oltre il VPS esistente (V-2); lo sviluppo lo fanno agenti, la manutenzione uno sviluppatore PHP a tempo parziale (V-3).
- **Operativa**: tre ruoli, pochi utenti, formazione di persona.
- **Legale**: dati personali dei clienti (GDPR) e obblighi fiscali sulle fatture (V-5, V-6).
- **Temporale**: nessuna scadenza imposta.
