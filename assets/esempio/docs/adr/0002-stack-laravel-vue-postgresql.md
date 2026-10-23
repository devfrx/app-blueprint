# ADR-0002: Laravel, Vue con Inertia e PostgreSQL

- **Status:** Accepted
- **Date:** 2026-10-14
- **Deciders:** responsabile, sviluppatore

## Context

Lo sviluppatore che manterrà l'app conosce PHP (V-3); il VPS ospita già PHP-FPM (V-1). Il metodo chiede codice generabile dal contratto, test per modulo, fitness function e test isolati in parallelo.

| Criterio | Laravel + Vue/Inertia | Symfony + React | Node (NestJS) + Vue |
|---|---|---|---|
| Maturità e supporto | finestre di supporto pubblicate (DEP-1, DEP-2) | buona | buona |
| Licenze | MIT | MIT | MIT |
| Competenze del manutentore | sì | in parte | no |
| Lock-in | basso | basso | basso |
| Costo totale | nessun servizio in più | nessun servizio in più | runtime Node in più sul VPS |

PostgreSQL contro MySQL: indici parziali per R-4, vincoli di controllo e blocchi di riga per la numerazione (R-3); la versione stabile e il suo supporto sono in DEP-3. Il contratto API è OpenAPI 3.1 (DEP-5), il formato degli errori RFC 9457 (DEP-6).

Spike sulla libreria PDF (RK-2): criterio, 50 fatture d'esempio in meno di 2 s sul VPS. Esito: 0,8 s con la libreria scelta, che entra tra le dipendenze del lockfile.

## Decision

Useremo Laravel con Vue 3 e Inertia, PostgreSQL, PHPUnit con Pest, Vitest, Playwright; Deptrac per i confini tra moduli; la libreria PDF dello spike. Gli oracoli vivono in tests/Oracoli/, fuori dalle cartelle dei moduli: è una divergenza voluta dalla convenzione di Laravel, che li terrebbe accanto al codice.

## Consequences

- Positive: lo stack che il manutentore conosce; un solo runtime sul VPS.
- Negative (accettate): Inertia lega frontend e backend nello stesso deployabile, coerente con ADR-0003.

## Fonti

- DEP-1, DEP-2, DEP-3, DEP-5 e DEP-6 nei registri.
