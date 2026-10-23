<!-- Generato da app-blueprint (progetto.py viste): non modificare a mano. Le sorgenti sono in docs/progettazione/ e contracts/. -->

# Schema logico

Generato da contracts/schema.toml: tabelle, chiavi e chiavi esterne.

```mermaid
erDiagram
  ACCOUNT {
    char(26) id PK
    varchar(254) email UK
    varchar(20) ruolo
    varchar(20) stato
    smallint tentativi_falliti
    varchar(255) password_hash "null"
    varchar(512) secondo_fattore "null"
    timestamptz creato_il
  }
  AUDIT {
    char(26) id PK
    timestamptz avvenuto_il
    char(26) account_id
    varchar(40) azione
    varchar(40) risorsa
    char(26) risorsa_id
  }
  CLIENTI {
    char(26) id PK
    varchar(100) nome
    varchar(100) cognome
    char(16) codice_fiscale UK
    varchar(254) email
    char(26) account_id FK,UK "null"
  }
  CODA {
    bigint id PK
    text contenuto
    smallint tentativi
    timestamptz disponibile_dal
  }
  FATTURE {
    char(26) id PK
    smallint anno UK
    integer numero UK
    char(26) intervento_id FK,UK
    timestamptz emessa_il
    bigint totale_centesimi
  }
  INTERVENTI {
    char(26) id PK
    varchar(16) codice UK
    char(26) veicolo_id FK
    text descrizione
    varchar(20) stato
    timestamptz aperto_il
    timestamptz chiuso_il "null"
    date data_prevista "null"
    integer versione
  }
  NUMERATORI_FATTURE {
    smallint anno PK
    integer ultimo_numero
  }
  PREVENTIVI {
    char(26) id PK
    char(26) intervento_id FK,UK
    varchar(20) stato
    timestamptz approvato_il "null"
    char(26) approvato_da "null"
    integer versione
  }
  RIGHE_FATTURA {
    char(26) id PK
    char(26) fattura_id FK,UK
    smallint numero UK
    varchar(200) descrizione
    numeric(8_2) quantita
    integer prezzo_unitario_centesimi
    numeric(4_2) aliquota_iva
    bigint importo_centesimi
  }
  RIGHE_PREVENTIVO {
    char(26) id PK
    char(26) preventivo_id FK,UK
    smallint numero UK
    varchar(20) codice_voce
    varchar(200) descrizione
    varchar(12) tipo
    numeric(8_2) quantita
    integer prezzo_unitario_centesimi
    numeric(4_2) aliquota_iva
  }
  VEICOLI {
    char(26) id PK
    varchar(10) targa UK
    varchar(60) marca
    varchar(60) modello
    date scadenza_revisione "null"
    date promemoria_inviato_il "null"
    char(26) cliente_id FK
  }
  VOCI_LISTINO {
    char(26) id PK
    varchar(20) codice UK
    varchar(200) descrizione
    varchar(12) tipo
    integer prezzo_centesimi
    numeric(4_2) aliquota_iva
    smallint durata_standard_minuti "null"
    varchar(40) codice_fornitore "null"
  }
  CLIENTI |o--o| ACCOUNT : "account_id"
  FATTURE |o--|| INTERVENTI : "intervento_id"
  INTERVENTI }o--|| VEICOLI : "veicolo_id"
  PREVENTIVI |o--|| INTERVENTI : "intervento_id"
  RIGHE_FATTURA }o--|| FATTURE : "fattura_id"
  RIGHE_PREVENTIVO }o--|| PREVENTIVI : "preventivo_id"
  VEICOLI }o--|| CLIENTI : "cliente_id"
```

| tabella | modulo | forma normale | traduce |
|---|---|---|---|
| account | accessi | BCNF | entita:account |
| audit |  | BCNF |  |
| clienti | clienti | BCNF | entita:cliente |
| coda |  | BCNF |  |
| fatture | fatture | BCNF | entita:fattura, relazione:intervento-fattura |
| interventi | interventi | BCNF | entita:intervento |
| numeratori_fatture | fatture | BCNF | entita:fattura |
| preventivi | interventi | BCNF | entita:preventivo, relazione:intervento-preventivo |
| righe_fattura | fatture | BCNF | entita:riga_fattura, relazione:fattura-righe |
| righe_preventivo | interventi | BCNF | entita:riga_preventivo, relazione:preventivo-righe |
| veicoli | veicoli | BCNF | entita:veicolo |
| voci_listino | prezzi | BCNF | entita:voce_listino, entita:manodopera, entita:ricambio |
