# ADR-0003: Monolite modulare con cinque moduli e un motore

- **Status:** Accepted
- **Date:** 2026-10-14
- **Deciders:** responsabile, sviluppatore

## Context

RNF-1 e RNF-5 si soddisfano su un solo VPS, e nessun requisito misurato chiede deploy separati (DR-1). I moduli devono potersi costruire in parallelo senza toccarsi (DR-4).

- **Servizi separati:** rete, deploy multipli e consistenza distribuita, senza un requisito che li giustifichi.

## Decision

Un solo deployabile con i moduli di dominio/moduli.toml, ciascuno in app/Moduli/<Modulo> e resources/js/moduli/<modulo>. I moduli si parlano solo tramite le facciate dei progetti di dettaglio; le dipendenze vanno in una sola direzione e sono fitness function eseguite da `fitness`. Contenitori e deployment sono in architettura/architettura.md.

## Consequences

- Positive: un deploy, transazioni locali, confini verificati dalla build.
- Negative (accettate): estrarre un modulo è un lavoro a sé; i moduli condividono il database, con un solo modulo proprietario per tabella.
