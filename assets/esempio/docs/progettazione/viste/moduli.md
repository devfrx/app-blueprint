<!-- Generato da app-blueprint (progetto.py viste): non modificare a mano. Le sorgenti sono in docs/progettazione/ e contracts/. -->

# Moduli e context map

Generata da dominio/moduli.toml. Una freccia va dal modulo a valle a quello da cui dipende.

```mermaid
flowchart LR
  subgraph anagrafiche [anagrafiche — supporto]
    clienti["clienti<br/>crud, rischio standard"]
    veicoli["veicoli<br/>crud, rischio standard"]
  end
  subgraph fatturazione [fatturazione — supporto]
    fatture["fatture<br/>crud, rischio alto"]
  end
  subgraph identita [identita — generico]
    accessi["accessi<br/>workflow, rischio alto"]
  end
  subgraph officina [officina — core]
    interventi["interventi<br/>workflow, rischio standard"]
    prezzi["prezzi<br/>motore, rischio alto"]
  end
  clienti -->|cliente-fornitore, sincrona| accessi
  fatture -->|cliente-fornitore, sincrona| interventi
  fatture -->|conformista, sincrona| prezzi
  interventi -->|conformista, sincrona| prezzi
  interventi -->|cliente-fornitore, sincrona| veicoli
  veicoli -->|cliente-fornitore, sincrona| clienti
```

| modulo | responsabilità | entità possedute |
|---|---|---|
| accessi | Ciclo di vita degli account, accesso, secondo fattore, inviti e recupero; nessuna regola di dominio dell'officina. | account |
| clienti | Anagrafica dei clienti e collegamento al loro account. | cliente |
| fatture | Emissione, numerazione e PDF delle fatture. | fattura, riga_fattura |
| interventi | Interventi e preventivi, con le loro macchine a stati. | intervento, preventivo, riga_preventivo |
| prezzi | Listino e motore dei prezzi: l'unico posto dove si calcolano i totali (R-2). | manodopera, ricambio, voce_listino |
| veicoli | Veicoli dei clienti e loro proprietario. | veicolo |
