# Fonti verificate

I fatti che scadono e che la skill cita, con la fonte letta e la data della lettura. Un progetto non li copia: li riverifica al momento e li registra nei suoi `[[deperibili]]`. Se una data qui è vecchia, si rilegge la fonte prima di usarla.

## Standard e norme

| Fatto | Fonte | Verificato il |
|---|---|---|
| ISO/IEC 25010:2023 (edizione 2, pubblicata il 2023-11-15, sostituisce la 25010:2011) definisce il modello di qualità del prodotto con nove caratteristiche: idoneità funzionale, efficienza prestazionale, compatibilità, capacità di interazione, affidabilità, sicurezza, manutenibilità, flessibilità, safety | [ISO](https://www.iso.org/standard/78176.html) | 2026-10-23 |
| WCAG 2.2 è la versione corrente delle WCAG 2: Recommendation W3C del 5 ottobre 2023, aggiornata il 12 dicembre 2024; è anche ISO/IEC 40500:2025. WCAG 3 è una bozza | [W3C WAI](https://www.w3.org/WAI/standards-guidelines/wcag/) | 2026-10-23 |
| OWASP ASVS 5.0.0, pubblicato il 30 maggio 2025, è la versione stabile, con tre livelli di verifica | [OWASP ASVS](https://asvs.owasp.org/); [SoftwareMill](https://softwaremill.com/whats-new-in-asvs-5-0/) | 2026-10-23 |
| RFC 9457, Problem Details for HTTP APIs: Proposed Standard, luglio 2023, sostituisce RFC 7807; nessuna RFC successiva la aggiorna | [RFC Editor](https://www.rfc-editor.org/info/rfc9457) | 2026-10-23 |
| OpenAPI: la serie 3.2 è la più recente pubblicata (3.2.1, 10 settembre 2026); AsyncAPI: 3.1.0. La versione da usare la decide il supporto degli strumenti scelti | [OpenAPI](https://spec.openapis.org/oas/v3.2); [AsyncAPI](https://www.asyncapi.com/docs/reference/specification/latest) | 2026-10-23 |
| Cyber Resilience Act, Regolamento (UE) 2024/2847: obblighi di segnalazione dall'11 settembre 2026, applicazione piena dall'11 dicembre 2027; il software libero e open source non fornito nell'ambito di un'attività commerciale ne è escluso | [CMS](https://cms.law/en/aut/legal-updates/ready-respond-report-the-cyber-resilience-act-s-reporting-regime-is-here) | 2026-10-23 |
| AI Act, Regolamento (UE) 2024/1689, come modificato dal Regolamento (UE) 2026/1744 (AI Omnibus, in vigore dal 27 luglio 2026): obblighi di trasparenza dal 2 agosto 2026; obblighi per i sistemi ad alto rischio dell'allegato III dal 2 dicembre 2027, per quelli dell'allegato I dal 2 agosto 2028 | [National Law Review](https://natlawreview.com/article/eu-digital-omnibus-ai-enters-force); [Addleshaw Goddard](https://www.addleshawgoddard.com/en/insights/insights-briefings/2026/technology/eu-ai-act-ai-omnibus-formally-adopted/) | 2026-10-23 |

Le due righe sulle norme UE poggiano su fonti secondarie autorevoli: per un obbligo concreto la verifica la fa `compliance-docs` sul testo ufficiale.

## Claude Code

| Fatto | Fonte | Verificato il |
|---|---|---|
| I sotto-agenti non possono fare domande all'utente: `AskUserQuestion` è tolto dai loro strumenti | [Sub-agents](https://code.claude.com/docs/en/sub-agents) | 2026-10-23 |
| Le definizioni in `.claude/agents/` si ricaricano in pochi secondi; serve un riavvio se la cartella non esisteva all'avvio della sessione | [Sub-agents](https://code.claude.com/docs/en/sub-agents) | 2026-10-23 |
| Una skill elencata in `skills` che manca viene saltata con un avviso nel solo log di debug | [Sub-agents](https://code.claude.com/docs/en/sub-agents) | 2026-10-23 |
| Al massimo 20 sotto-agenti concorrenti per default, modificabile con `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | [Sub-agents](https://code.claude.com/docs/en/sub-agents) | 2026-10-23 |
| `isolation: worktree` esegue un sotto-agente in un worktree temporaneo, che parte dal branch di default del remoto salvo `worktree.baseRef = "head"`; `.claude/worktrees/` va in `.gitignore` | [Worktrees](https://code.claude.com/docs/en/worktrees) | 2026-10-23 |
| Un sotto-agente in un worktree prende i file d'istruzione con cui parte dalla conversazione principale, non dal suo worktree; sotto `.claude/worktrees/` non carica nemmeno il `CLAUDE.md` della radice del worktree | [Worktrees](https://code.claude.com/docs/en/worktrees) | 2026-10-23 |
| Una regola di deny `Bash(…)` nelle impostazioni vale per la conversazione principale e per i sotto-agenti; `disallowedTools` con uno specificatore toglie l'intero strumento | [Sub-agents](https://code.claude.com/docs/en/sub-agents) | 2026-10-23 |
| Gli hook nel frontmatter di un sotto-agente valgono solo mentre quel sotto-agente è attivo; per un agente di progetto girano solo dopo l'accettazione della fiducia nella cartella, e una sessione `-p` non conta | [Sub-agents](https://code.claude.com/docs/en/sub-agents); [Hooks](https://code.claude.com/docs/en/hooks) | 2026-10-23 |
| Un hook `PreToolUse` che esce con 2 blocca la chiamata, e il suo stderr è il motivo che l'agente riceve | [Hooks](https://code.claude.com/docs/en/hooks) | 2026-10-23 |
