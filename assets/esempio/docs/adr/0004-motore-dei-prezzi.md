# ADR-0004: Un motore dei prezzi costruito, unico calcolatore dei totali

- **Status:** Accepted
- **Date:** 2026-10-15
- **Deciders:** responsabile, sviluppatore

## Context

Preventivi e fatture devono avere gli stessi totali al centesimo (R-2, RNF-7), e interventi e fatture li calcolerebbero entrambi.

- **Libreria di calcolo esistente:** nessuna copre l'arrotondamento per riga che usa il commercialista.
- **Calcolo in ciascun modulo:** due implementazioni che prima o poi divergono.

## Decision

Il modulo prezzi è un motore: una funzione pura `totali(righe)` in aritmetica intera sui centesimi, con la facciata in moduli/prezzi.toml come API versionata. Lo costruisce la sessione nell'ondata motore, prima degli esemplari, contro una suite di conformità con i 40 casi del commercialista e test basati su proprietà.

## Consequences

- Positive: un solo posto dove sbagliare, e una suite che lo prova.
- Negative (accettate): interventi e fatture dipendono da prezzi; un cambio di regola fiscale tocca il motore e la sua suite.
