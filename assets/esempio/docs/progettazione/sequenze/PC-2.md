+++
percorso = "PC-2"
operazioni = ["registraCliente", "associaVeicolo", "attivaAccount", "dettaglioIntervento"]
facciate = ["accessi.creaAccountInvitato", "clienti.esiste", "veicoli.proprietarioAccount", "clienti.accountDi"]
+++
# PC-2 — il cliente segue il suo intervento

La condizione di proprietà della matrice è il punto delicato: per leggere un intervento il kernel chiede a interventi, che chiede a veicoli, che chiede a clienti l'account del proprietario. Se non coincide con chi chiede, la risposta è non-trovato, senza indizi che l'intervento esista (MI-1).

```mermaid
sequenceDiagram
  actor O as Operatore
  actor C as Cliente
  participant API as API e kernel
  participant CLI as clienti
  participant ACC as accessi
  participant VEI as veicoli
  participant INT as interventi
  O->>API: registraCliente(Mario Rossi)
  API->>CLI: registra
  CLI->>ACC: creaAccountInvitato(email, cliente)
  ACC-->>CLI: account invitato, invito in coda
  O->>API: associaVeicolo(cliente, AB123CD)
  API->>VEI: associa
  VEI->>CLI: esiste(cliente)
  C->>API: attivaAccount(token, password)
  API->>ACC: attiva
  C->>API: dettaglioIntervento(id)
  API->>INT: leggi(id)
  INT->>VEI: proprietarioAccount(veicolo)
  VEI->>CLI: accountDi(cliente)
  CLI-->>VEI: account
  VEI-->>INT: account
  alt l'account è di chi chiede
    INT-->>API: intervento con il preventivo
  else di un altro cliente
    INT-->>API: non-trovato
  end
```
