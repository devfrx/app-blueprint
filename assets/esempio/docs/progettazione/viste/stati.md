<!-- Generato da app-blueprint (progetto.py viste): non modificare a mano. Le sorgenti sono in docs/progettazione/ e contracts/. -->

# Macchine a stati

Generate da dominio/stati.toml. Le transizioni non elencate sono vietate: gli oracoli lo provano.

## account (stato)

```mermaid
stateDiagram-v2
  [*] --> invitato
  invitato --> attivo : attivazione dall'invito con una password valida
  attivo --> bloccato : quinto tentativo d'accesso fallito
  bloccato --> attivo : sblocco [responsabile]
```

Transizioni vietate: invitato → bloccato; attivo → invitato; bloccato → invitato.

## intervento (stato)

```mermaid
stateDiagram-v2
  [*] --> accettazione
  accettazione --> lavorazione : approvazione del preventivo [responsabile]
  lavorazione --> chiuso : chiusura a lavori finiti [operatore, responsabile]
  chiuso --> [*]
```

Transizioni vietate: accettazione → chiuso; lavorazione → accettazione; chiuso → accettazione; chiuso → lavorazione.

## preventivo (stato)

```mermaid
stateDiagram-v2
  [*] --> bozza
  bozza --> bozza : aggiunta di una riga [operatore, responsabile]
  bozza --> approvato : approvazione [responsabile]
  approvato --> [*]
```

Transizioni vietate: approvato → bozza.
