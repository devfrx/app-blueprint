<!-- Generato da app-blueprint (progetto.py viste): non modificare a mano. Le sorgenti sono in docs/progettazione/ e contracts/. -->

# Operazioni API

Generato da contracts/openapi.json.

## accessi

| operazione | metodo e percorso | storie | errori |
|---|---|---|---|
| accedi | POST /api/v1/sessione | ACC-1, ACC-4 | credenziali-non-valide, account-bloccato, troppe-richieste |
| attivaAccount | POST /api/v1/attivazioni/{token} | ACC-5 | link-non-valido, password-debole |
| chiediRecuperoPassword | POST /api/v1/recupero-password | ACC-3 | troppe-richieste |
| creaAccount | POST /api/v1/account | ACC-2 | account-esistente, validazione, non-autorizzato |
| elencoAccount | GET /api/v1/account | ACC-2, ACC-7 | non-autorizzato |
| esci | DELETE /api/v1/sessione | ACC-1 | non-autenticato |
| impostaPasswordDaRecupero | POST /api/v1/recupero-password/{token} | ACC-3 | link-non-valido, password-debole |
| sbloccaAccount | POST /api/v1/account/{id}/sblocco | ACC-7 | non-autorizzato, non-trovato |
| verificaSecondoFattore | POST /api/v1/sessione/secondo-fattore | ACC-4 | codice-non-valido, troppe-richieste |

## clienti

| operazione | metodo e percorso | storie | errori |
|---|---|---|---|
| cercaClienti | GET /api/v1/clienti/ricerca | CLI-2 | validazione, non-autorizzato |
| dettaglioCliente | GET /api/v1/clienti/{id} | CLI-1, VEI-1 | non-trovato, non-autorizzato |
| elencoClienti | GET /api/v1/clienti | CLI-1 | non-autorizzato |
| registraCliente | POST /api/v1/clienti | CLI-1 | cliente-duplicato, codice-fiscale-non-valido, validazione, non-autorizzato |

## fatture

| operazione | metodo e percorso | storie | errori |
|---|---|---|---|
| dettaglioFattura | GET /api/v1/fatture/{id} | FAT-3 | non-trovato, non-autorizzato |
| emettiFattura | POST /api/v1/interventi/{id}/fattura | FAT-1 | intervento-non-chiuso, fattura-esistente, non-trovato, non-autorizzato |
| esportaFatture | GET /api/v1/fatture/esportazione | FAT-2 | validazione, non-autorizzato |
| pdfFattura | GET /api/v1/fatture/{id}/pdf | FAT-3 | non-trovato, non-autorizzato |

## interventi

| operazione | metodo e percorso | storie | errori |
|---|---|---|---|
| aggiungiRigaPreventivo | POST /api/v1/interventi/{id}/preventivo/righe | INT-5 | quantita-non-valida, preventivo-approvato, conflitto-di-versione, non-trovato, non-autorizzato |
| approvaPreventivo | POST /api/v1/interventi/{id}/preventivo/approvazione | INT-2 | preventivo-vuoto, conflitto-di-versione, non-trovato, non-autorizzato |
| apriIntervento | POST /api/v1/interventi | INT-1 | intervento-gia-aperto, non-trovato, validazione, non-autorizzato |
| chiudiIntervento | POST /api/v1/interventi/{id}/chiusura | INT-4 | preventivo-non-approvato, conflitto-di-versione, non-trovato, non-autorizzato |
| dettaglioIntervento | GET /api/v1/interventi/{id} | INT-3, INT-5 | non-trovato, non-autorizzato |
| elencoInterventiAperti | GET /api/v1/interventi | INT-6 | non-autorizzato |

## prezzi

| operazione | metodo e percorso | storie | errori |
|---|---|---|---|
| aggiornaVoceListino | PUT /api/v1/listino/{codice} | PRZ-1 | validazione, non-trovato, non-autorizzato |
| elencoVociListino | GET /api/v1/listino | INT-5 | non-autorizzato |

## veicoli

| operazione | metodo e percorso | storie | errori |
|---|---|---|---|
| associaVeicolo | POST /api/v1/clienti/{id}/veicoli | VEI-1 | veicolo-duplicato, validazione, non-trovato, non-autorizzato |
| elencoVeicoliCliente | GET /api/v1/clienti/{id}/veicoli | VEI-1 | non-trovato, non-autorizzato |
