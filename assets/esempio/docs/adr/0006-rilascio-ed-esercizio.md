# ADR-0006: Rilascio ed esercizio sul VPS dell'officina

- **Status:** Accepted
- **Date:** 2026-10-15
- **Deciders:** responsabile, sviluppatore

## Context

RNF-2 chiede RTO di 4 h e RPO di 24 h; V-2 esclude servizi a pagamento in più. Il progetto è pubblicabile: le voci di esercizio per un'app pubblica (canary, hypercare, SLO) sono nel debito di pubblicazione.

- **Backup presso un secondo fornitore:** riduce RK-3, ma ha un costo che V-2 esclude oggi.

## Decision

Staging e produzione sullo stesso VPS, con utenti e database separati; rilascio manuale dello stesso artefatto di CI prima su staging e poi in produzione; dump notturno cifrato con 30 giorni di storico presso il fornitore del VPS; ripristino provato su staging a ogni rilascio, seguendo il runbook.

## Consequences

- Positive: costo zero; ripristino provato davvero, non solo descritto.
- Negative (accettate): backup presso lo stesso fornitore (DEB-1, RK-3).
