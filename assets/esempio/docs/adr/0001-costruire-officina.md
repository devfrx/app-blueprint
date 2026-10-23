# ADR-0001: Costruire Officina invece di adottare un gestionale

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** responsabile, sviluppatore

## Context

Gli obiettivi OB-1…OB-3 chiedono preventivi, interventi e fatture in un solo strumento, con un'area per i clienti, senza costi d'esercizio in più (V-2).

- **Gestionale per officine in abbonamento:** completo, ma il canone mensile viola V-2 e l'area cliente non c'è nei piani di base.
- **Gestionale installato:** licenza una tantum, ma niente area cliente e dati in un formato chiuso.
- **Fogli di calcolo migliorati:** costo zero, ma restano le trascrizioni che OB-1 e OB-2 vogliono eliminare.

## Decision

Costruiremo Officina: un'app web su misura, sul VPS esistente, progettata con app-blueprint e costruita con parallel-build. Vince perché è l'unica opzione che copre l'area cliente senza un canone.

## Consequences

- Positive: nessun costo d'esercizio in più; dati dell'officina in un database suo.
- Negative (accettate): la manutenzione è a carico dello sviluppatore a tempo parziale (V-3, RNF-6).
