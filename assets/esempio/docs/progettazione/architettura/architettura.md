+++
fase = 4
+++
# Architettura di Officina

Il contesto (chi usa il sistema, con quali sistemi esterni dialoga) e il grafo dei moduli sono viste generate: `viste/contesto.md` e `viste/moduli.md`. Qui stanno le viste che nessuna sorgente può generare: container e deployment. Il perché delle scelte è negli ADR.

## Container

Un solo deployabile (ADR-0003): l'app Laravel serve l'API e le pagine Vue con Inertia; un worker dello stesso codice consuma la coda delle email.

```mermaid
flowchart LR
  op([Operatore e responsabile]) -->|HTTPS| web
  cl([Cliente]) -->|HTTPS| web
  subgraph officina [Officina — un deployabile]
    web[App web<br/>Laravel, Vue, Inertia]
    worker[Worker della coda<br/>stesso codice]
  end
  web --> db[(PostgreSQL)]
  worker --> db
  worker -->|SMTP| mail[Servizio email]
```

## Deployment

Lo stesso VPS del sito (V-1), dietro il proxy inverso che già esiste. Staging è un secondo utente con un secondo database sullo stesso VPS: prova rilascio, ripristino e carico senza costi in più (V-2). L'infrastruttura è descritta come codice da uno script di provisioning versionato nel repo.

```mermaid
flowchart TB
  internet((Internet)) --> proxy[Proxy inverso del VPS]
  subgraph vps [VPS dell'officina]
    proxy --> sito[Sito]
    proxy --> prod[Officina produzione<br/>app e worker]
    proxy --> stag[Officina staging<br/>app e worker]
    prod --> dbp[(PostgreSQL produzione)]
    stag --> dbs[(PostgreSQL staging)]
  end
  prod -. dump notturno cifrato .-> backup[(Spazio di backup del fornitore)]
```

Scalabilità: verticale, nel limite di RNF-5; nessuna replica (ST-dati). Rete: solo il proxy esposto; database in ascolto su localhost.
