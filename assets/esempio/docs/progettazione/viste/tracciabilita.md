<!-- Generato da app-blueprint (progetto.py viste): non modificare a mano. Le sorgenti sono in docs/progettazione/ e contracts/. -->

# Matrice di tracciabilità

Dalle storie al progetto e ai test che le provano. Gli esiti non stanno qui: li dà la suite, che porta l'id della storia nel nome di ogni test, e la voce 11.06 si chiude con il suo rapporto.

| storia | inc. | priorità | entità | modulo (tocca) | operazioni API | schermate | oracoli | end-to-end |
|---|---|---|---|---|---|---|---|---|
| ACC-1 | 1 | must | account | accessi | accedi, esci | accesso, interventi-aperti | O-accessi | X-intervento-completo |
| ACC-2 | 1 | must | account | accessi | creaAccount, elencoAccount | account | O-accessi |  |
| ACC-3 | 1 | must | account | accessi | chiediRecuperoPassword, impostaPasswordDaRecupero | recupero-password | O-accessi |  |
| ACC-4 | 1 | must | account | accessi | accedi, verificaSecondoFattore | accesso | O-accessi | X-intervento-completo |
| ACC-5 | 1 | must | account | accessi | attivaAccount | attivazione | O-accessi | X-cliente-segue-intervento |
| ACC-6 | 1 | must | account | accessi |  | attivazione, informativa, non-trovato | O-accessi |  |
| ACC-7 | 1 | must | account | accessi | elencoAccount, sbloccaAccount | account | O-accessi |  |
| CLI-1 | 1 | must | cliente, account | clienti (accessi) | dettaglioCliente, elencoClienti, registraCliente | cliente-scheda, clienti | O-clienti | X-cliente-segue-intervento |
| CLI-2 | 2 | should | cliente | clienti | cercaClienti | clienti |  |  |
| FAT-1 | 1 | must | fattura, riga_fattura, intervento, preventivo, riga_preventivo | fatture (interventi, prezzi) | emettiFattura | fattura, intervento | O-fatture | X-intervento-completo |
| FAT-2 | 2 | could | fattura, riga_fattura | fatture | esportaFatture | esportazione-fatture |  |  |
| FAT-3 | 1 | must | fattura, riga_fattura | fatture | dettaglioFattura, pdfFattura | fattura | O-fatture |  |
| FAT-4 |  | wont |  |  |  |  |  |  |
| INT-1 | 1 | must | intervento, preventivo, veicolo | interventi (veicoli) | apriIntervento | cliente-scheda, intervento | O-interventi | X-intervento-completo |
| INT-2 | 1 | must | preventivo, intervento, riga_preventivo | interventi (prezzi) | approvaPreventivo | intervento | O-interventi | X-intervento-completo |
| INT-3 | 1 | must | intervento, preventivo, riga_preventivo, veicolo, cliente | interventi (veicoli) | dettaglioIntervento | area-cliente-intervento | O-interventi | X-cliente-segue-intervento |
| INT-4 | 1 | must | intervento, preventivo | interventi | chiudiIntervento | intervento | O-interventi | X-intervento-completo |
| INT-5 | 1 | must | preventivo, riga_preventivo, voce_listino, manodopera, ricambio | interventi (prezzi) | aggiungiRigaPreventivo, dettaglioIntervento, elencoVociListino | intervento | O-interventi | X-intervento-completo |
| INT-6 | 1 | must | intervento, veicolo, cliente | interventi (veicoli) | elencoInterventiAperti | interventi-aperti | O-interventi |  |
| PRZ-1 | 2 | should | voce_listino, manodopera, ricambio | prezzi | aggiornaVoceListino | listino |  |  |
| VEI-1 | 1 | must | veicolo, cliente | veicoli (clienti) | associaVeicolo, dettaglioCliente, elencoVeicoliCliente | cliente-scheda | O-veicoli | X-cliente-segue-intervento |
| VEI-2 | 2 | should | veicolo, cliente | veicoli (clienti) |  |  |  |  |

## Requisiti non funzionali

| RNF | caratteristica | indirizzato da | prova |
|---|---|---|---|
| RNF-1 | efficienza-prestazionale | AC-1, ST-cache, ADR-0003 | Test di carico su staging con dati sintetici prima del rilascio: in locale non si verifica. |
| RNF-2 | affidabilita | ST-backup, ADR-0006 | Ripristino dal backup notturno provato su staging seguendo il runbook. |
| RNF-3 | capacita-di-interazione | ST-accessibilita | Controllo automatico dell'accessibilità nei test d'interfaccia, più la lente UI della revisione. |
| RNF-4 | sicurezza | ST-autorizzazione, ADR-0005, MI-1 | Test di autorizzazione dalla matrice; mutation testing sui moduli ad alto rischio; revisione di sicurezza approfondita. |
| RNF-5 | compatibilita | ADR-0003, ST-dati | Misura su staging durante il test di carico di RNF-1. |
| RNF-6 | manutenibilita | ADR-0003, ST-qualita-codice | Test di manutenibilità alla chiusura della costruzione. |
| RNF-7 | idoneita-funzionale | ADR-0004, ST-denaro | Suite di conformità del motore con i 40 casi, più test basati su proprietà degli invarianti. |

## Obiettivi

| obiettivo | storie che lo servono |
|---|---|
| OB-1 | ACC-1, ACC-2, CLI-1, INT-1, INT-2, INT-4, INT-5, INT-6, VEI-1 |
| OB-2 | FAT-1, FAT-3, INT-5 |
| OB-3 | ACC-5, CLI-1, INT-3 |
