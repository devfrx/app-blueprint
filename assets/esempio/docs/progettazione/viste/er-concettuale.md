<!-- Generato da app-blueprint (progetto.py viste): non modificare a mano. Le sorgenti sono in docs/progettazione/ e contracts/. -->

# Schema E/R concettuale

Generato da dominio/entita.toml. Notazione a zampa di gallina: il simbolo accanto a un'entità dice quante sue istanze partecipano per ogni istanza dell'altra. Gli identificatori principali sono marcati PK, gli altri UK.

```mermaid
erDiagram
  ACCOUNT {
    email email PK
    enumerazione ruolo
    enumerazione stato
    intero tentativi_falliti
    testo password "facoltativo"
    testo secondo_fattore "facoltativo"
    istante creato_il
  }
  CLIENTE {
    testo nome
    testo cognome
    codice_fiscale codice_fiscale PK
    email email
  }
  FATTURA {
    intero anno PK
    intero numero PK
    istante emessa_il
    denaro totale "derivato"
  }
  INTERVENTO {
    testo codice PK
    testo descrizione
    enumerazione stato
    istante aperto_il
    istante chiuso_il "facoltativo"
    data data_prevista "facoltativo"
  }
  MANODOPERA {
    intero durata_standard "facoltativo"
  }
  PREVENTIVO {
    enumerazione stato
    istante approvato_il "facoltativo"
    denaro totale "derivato"
  }
  RICAMBIO {
    testo codice_fornitore "facoltativo"
  }
  RIGA_FATTURA {
    intero numero PK
    testo descrizione
    decimale quantita
    denaro prezzo_unitario
    decimale aliquota_iva
    denaro importo
  }
  RIGA_PREVENTIVO {
    intero numero PK
    testo codice_voce
    testo descrizione
    enumerazione tipo
    decimale quantita
    denaro prezzo_unitario
    decimale aliquota_iva
  }
  VEICOLO {
    targa targa PK
    testo marca
    testo modello
    data scadenza_revisione "facoltativo"
    data promemoria_inviato_il "facoltativo"
  }
  VOCE_LISTINO {
    testo codice PK
    testo descrizione
    denaro prezzo
    decimale aliquota_iva
  }
  CLIENTE |o--o| ACCOUNT : "accede-con"
  CLIENTE ||--o{ VEICOLO : "possiede"
  FATTURA ||--|{ RIGA_FATTURA : "contiene"
  INTERVENTO ||--o| FATTURA : "chiuso-da"
  INTERVENTO ||--|| PREVENTIVO : "ha"
  PREVENTIVO ||--o{ RIGA_PREVENTIVO : "contiene"
  VEICOLO ||--o{ INTERVENTO : "riceve"
  VOCE_LISTINO ||--o{ RIGA_PREVENTIVO : "prezza"
  VOCE_LISTINO ||--o| MANODOPERA : "è un (totale, esclusiva)"
  VOCE_LISTINO ||--o| RICAMBIO : "è un (totale, esclusiva)"
```

## Proprietari

| entità | modulo | descrizione |
|---|---|---|
| account | accessi | L'accesso di una persona a Officina. |
| cliente | clienti | Chi porta i veicoli in officina e riceve le fatture. |
| fattura | fatture | Documento emesso per un intervento chiuso; immutabile (R-3). |
| intervento | interventi | Il lavoro su un veicolo, dall'accettazione alla chiusura. |
| manodopera | prezzi | Voce di listino prezzata a ore. |
| preventivo | interventi | Le righe di un intervento; uno per intervento. |
| ricambio | prezzi | Voce di listino prezzata a pezzo. |
| riga_fattura | fatture | Copia di una riga del preventivo approvato all'emissione. |
| riga_preventivo | interventi | Una voce del listino nel preventivo, con i valori del momento. |
| veicolo | veicoli | Un mezzo di un cliente. |
| voce_listino | prezzi | Una prestazione o un ricambio con prezzo e aliquota. |
