# ADR-0005: Sicurezza e accessi

- **Status:** Accepted
- **Date:** 2026-10-15
- **Deciders:** responsabile, sviluppatore, consulente-privacy

## Context

Officina tratta dati personali dei clienti e denaro. Dal threat model (architettura/minacce.toml): il rischio maggiore è un cliente che legge gli interventi altrui (MI-1), poi un operatore che approva o fattura al posto del responsabile (MI-3).

- **Accesso delegato a un fornitore d'identità:** toglie la gestione delle password, ma è un servizio esterno in più per tre ruoli e poche decine di account.

## Decision

- Autenticazione a sessione con i flussi del framework, come in ST-autenticazione; secondo fattore per il responsabile.
- Autorizzazioni nel kernel, da contracts/autorizzazioni.toml, con negazione per default e la condizione di proprietà sugli interventi del cliente.
- Livello di verifica OWASP ASVS: il 2 per accessi, prezzi e fatture, l'1 per gli altri moduli, nella versione stabile al congelamento.
- Dati personali minimizzati, mai nei log, dati di test sintetici; informativa e registro dei trattamenti con compliance-docs, da far rivedere al consulente prima del lancio. Le richieste degli interessati le evade il responsabile con la procedura del runbook (NO-7).

## Consequences

- Positive: le minacce principali diventano test di autorizzazione e casi d'errore del contratto.
- Negative (accettate): Officina gestisce le password, e quindi il loro ciclo di vita; gli operatori non hanno il secondo fattore (RK-4).

## Fonti

- DEP-4 nei registri.
