+++
percorso = "PC-1"
operazioni = ["accedi", "verificaSecondoFattore", "apriIntervento", "aggiungiRigaPreventivo", "approvaPreventivo", "chiudiIntervento", "emettiFattura"]
facciate = ["veicoli.veicolo", "prezzi.voce", "prezzi.totali", "interventi.interventoChiuso"]
+++
# PC-1 — intervento completo

Dall'accesso alla fattura, attraverso le facciate. Ogni freccia verso un modulo è una chiamata di facciata; il kernel applica la matrice prima di ogni operazione.

```mermaid
sequenceDiagram
  actor O as Operatore
  actor R as Responsabile
  participant API as API e kernel
  participant INT as interventi
  participant VEI as veicoli
  participant PRZ as prezzi
  participant FAT as fatture
  O->>API: accedi
  API-->>O: sessione aperta
  O->>API: apriIntervento(veicolo, descrizione)
  API->>INT: apri
  INT->>VEI: veicolo(id)
  VEI-->>INT: riassunto
  INT-->>API: intervento in accettazione, preventivo vuoto
  O->>API: aggiungiRigaPreventivo(MAN-ORA, 2)
  API->>INT: aggiungi riga
  INT->>PRZ: voce(MAN-ORA)
  INT->>PRZ: totali(righe)
  PRZ-->>INT: 183,00 €
  R->>API: accedi + verificaSecondoFattore
  R->>API: approvaPreventivo(versione)
  API->>INT: approva
  INT-->>API: intervento in lavorazione
  O->>API: chiudiIntervento(versione)
  API->>INT: chiudi (R-1)
  R->>API: emettiFattura(intervento)
  API->>FAT: emetti
  FAT->>INT: interventoChiuso(id)
  FAT->>PRZ: totali(righe)
  FAT-->>API: fattura 42/2026
```
