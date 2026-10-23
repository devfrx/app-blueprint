+++
fase = 4
revisione = "REV-5"
+++
# Valutazione dell'architettura

Una revisione in stile ATAM, proporzionata al progetto: per ogni scenario di qualità di rilevanza alta, le decisioni che lo indirizzano, i punti sensibili, i compromessi e i rischi. L'ha svolta un reviewer che non ha scritto l'architettura (REV-5).

| Scenario | Decisioni | Punti sensibili | Compromessi | Rischi |
|---|---|---|---|---|
| RNF-7 totali corretti | ADR-0004, ST-denaro | arrotondamento per riga | nessuno | basso: suite di conformità sui 40 casi |
| RNF-4 autorizzazioni | ADR-0005, ST-autorizzazione | condizione di proprietà sugli interventi | una richiesta in più per risolvere il proprietario tramite veicoli | basso |
| RNF-2 ripristino | ST-backup, ADR-0006 | backup presso lo stesso fornitore | costo zero contro un rischio di fornitore | accettato: DEB-1, RK-3 |
| RNF-6 manutenibilità | ADR-0003, ST-qualita-codice | confini tra moduli | regole Deptrac da mantenere | basso |
| RNF-3 accessibilità | ST-accessibilita | componenti del design system | nessuno | basso |

Esito: nessun rischio non accettato; il punto più sensibile è la numerazione delle fatture sotto concorrenza (ST-concorrenza), coperto da un test di proprietà nel modulo fatture.
