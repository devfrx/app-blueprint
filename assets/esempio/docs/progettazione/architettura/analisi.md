+++
fase = 4
rnf = ["RNF-1", "RNF-2", "RNF-5"]
+++
# Analisi quantitative

I numeri vengono dalle tavole di `dati/dati.toml` e dagli RNF; dove sono stime, lo dichiara l'assunzione A-1.

## Capacità

- Righe dopo cinque anni: circa 50.000 interventi e preventivi, 250.000 righe di preventivo, 50.000 fatture con 250.000 righe; tutto sotto i 2 GB su disco con gli indici.
- Crescita: circa 10.000 interventi all'anno; nessuna tabella chiede partizionamento nell'orizzonte di cinque anni.

## Prestazioni

- AC-1, l'elenco degli interventi aperti, è l'operazione più frequente: 200 al giorno, al massimo 20 utenti contemporanei. Con l'indice su (stato, aperto_il) la prima pagina legge 25 righe di interventi, veicoli e clienti: decine di millisecondi, sotto il budget di 300 ms di RNF-1.
- AC-3, l'emissione della fattura, serializza sul numeratore dell'anno: a 30 emissioni al giorno l'attesa sul blocco è trascurabile.

## Costi infrastrutturali

Zero oltre il VPS (V-2): la memoria resta sotto 1 GB con un processo PHP-FPM a 8 worker, un worker della coda e PostgreSQL con 256 MB di shared_buffers (RNF-5, da misurare su staging).

## Affidabilità

Un solo nodo: la disponibilità è quella del VPS. RNF-2 si regge sul backup notturno (RPO 24 h) e su un ripristino di circa un'ora, più la ricreazione del VPS dallo script di provisioning: dentro le 4 h di RTO.
