# Fase 0 — Precondizioni

Prepara ciò che le fasi successive danno per scontato: un repo che conserva il lavoro, sotto-agenti che vedono ciò che è stato deciso e hanno le skill giuste, lo stato della progettazione da cui ogni sessione riparte. Ogni voce è una condizione verificabile, non un passo da ricordare: dopo un riavvio la fase si riesegue, e ciò che è già vero si chiude subito.

I fatti su Claude Code citati qui sono in `FONTI.md`, con la data della verifica. Se la versione in uso si comporta diversamente, si rilegge la documentazione invece di adattare il controllo a memoria.

## 0.05 prima di tutto: lo stato

Senza stato non c'è checklist, quindi questa voce si fa per prima, anche se ha il numero più alto:

```bash
python <cartella della skill>/scripts/progetto.py inizia --progetto "<nome>" --responsabile "<chi approva i gate>"
python <cartella della skill>/scripts/progetto.py stato
```

`inizia` crea `stato.toml`, `gate.toml` e `registri.toml` in `docs/progettazione/` e genera le viste. Il responsabile è chi approva i gate: di solito l'utente stesso, con il nome con cui comparirà come stakeholder. Da qui ogni punto si apre e si chiude con i comandi di `gate.md`; la 0.05 si chiude con `--evidenza stato.toml gate.toml registri.toml`.

## 0.01 Repo e persistenza

- **Repo git con almeno un commit** e il branch d'integrazione attivo, di solito `main`. Se il repo non esiste, si crea con l'utente.
- **Persistenza.** Versionato non vuol dire salvato: in un ambiente effimero, come una sessione cloud, ciò che non è committato e pushato si perde a fine sessione. Si chiede una volta all'utente se l'ambiente è effimero e se si può pushare dopo ogni chiusura. Senza il permesso non si pusha: il rischio si dice, non si aggira.
- Evidenza: l'URL del remoto, o `.git` per un repo solo locale, con `--nota` sul branch e sul permesso di push.

## 0.02 File di lavoro e worktree

- **`.build/` esclusa da git**, in `.git/info/exclude`: è il posto dei file di lavoro di una sessione, come i brief di `parallel-build`.
- **`.claude/worktrees/` in `.gitignore`**, come consiglia la documentazione di Claude Code.
- **`worktree.baseRef` a `"head"`** in `.claude/settings.json`:

  ```json
  { "worktree": { "baseRef": "head" } }
  ```

  I sotto-agenti isolati in un worktree, cioè `reviewer` e costruttori, partono per default dal branch di default del remoto, non dalla HEAD locale: senza questa impostazione rivedrebbero o costruirebbero sul progetto di ieri. Anche con l'impostazione vedono solo ciò che è committato: si committa prima di lanciarli.

## 0.03 Agenti

1. **Installa.** Copia le definizioni da `assets/agenti/` in `.claude/agents/` del progetto e committale: `researcher`, `reviewer`, `test-author`, `backend-builder`, `frontend-builder`. La progettazione usa `researcher`, `reviewer` e i costruttori per gli spike; la costruzione li usa tutti.
2. **Riavvia, se serve.** Claude Code vede in pochi secondi un agente nuovo in una cartella `.claude/agents/` che esisteva all'avvio della sessione, ma non una cartella creata dopo: in quel caso chiedi il riavvio subito, finché il contesto è quasi vuoto, poi riesegui la fase.
3. **Sonda.** Una skill precaricata che manca viene saltata con un solo avviso nel log di debug, e l'agente lavora senza. Lancia ogni tipo di agente con questo compito: "Senza usare strumenti, per ogni skill precaricata nel tuo contesto riporta il nome e la prima frase dopo il titolo principale". Confronta le frasi con le skill: un elenco di nomi non basta, perché si ricostruisce anche senza averle. Se una manca, correggi il nome nella copia del progetto (alcuni ambienti espongono le skill con un prefisso, come `anthropic-skills:`) e ripeti.
4. Evidenza: `.claude/agents/`, con `--nota` sull'esito della sonda.

**Senza agenti di progetto**, se l'ambiente non carica `.claude/agents/` o la sessione non si può riavviare: sotto-agenti generici con il corpo della definizione in testa al brief, e la nota della chiusura dice che strumenti e skill precaricate non sono garantiti. Senza sotto-agenti, ricerca e revisioni si fanno in sequenza nella sessione, dichiarandolo nelle revisioni; la prova di decidibilità invece non si può fare, perché la sessione conosce già le risposte, e la 7.14 si chiude come non applicabile con questo motivo, da far approvare all'utente.

## 0.04 Convenzioni del repo

In un repo nuovo valgono i percorsi del metodo (`struttura.md`), e l'evidenza è la nota che lo dice. Se il repo ha già percorsi o formati per ADR, diagrammi o contratti, si decide con l'utente: migrare al layout del metodo, che lo script sa verificare, o non usare il metodo così com'è. Le convenzioni del codice — linguaggio, stile, test — non si decidono qui: si rilevano se esistono e si fissano alla 7.07.

## Gate

Il brief è breve: repo e permesso di push, agenti e sonda, eventuali ripieghi dichiarati. Con l'approvazione dell'utente, `progetto.py approva 0 --da <chi approva>`.
