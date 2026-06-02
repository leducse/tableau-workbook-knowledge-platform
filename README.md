# Tableau Workbook Knowledge Platform

**Former internal name:** Project Prism

**Status:** Spec only — not yet implemented.

Turns Tableau workbooks into **curated, field-trusted documentation**: extract
workbook metadata, generate markdown with Amazon Bedrock, human-edit via a
web UI, store in S3, and expose content to agents through MCP-style retrieval.

## Why this name

Tableau dashboards are often what the **field actually uses**—so they are the
practical source of truth for metrics and business rules, even when warehouse
schemas and Confluence are scattered. This platform makes that truth **structured,
accurate, and queryable**.

## Documents

| File | Purpose |
|------|---------|
| [`MVP_SPEC.md`](MVP_SPEC.md) | AWS MVP build spec (portfolio demo) |
| [`REQUIREMENTS.md`](REQUIREMENTS.md) | Full requirements — pipeline, UI, MCP, governance |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | End-to-end flow and component diagram |

## Related work (out of scope for this repo)

**Tableau → QuickSight migration** (genAI calc/view conversion, Q topics, deploy
validation) is a **separate project**—same Tableau extract step, different
downstream. Spec when ready: `tableau-quicksight-migration-assistant` (working title).

## Disclaimer

Portfolio/demo implementation uses **sample workbooks and synthetic metadata**.
No production Tableau Server credentials or customer dashboards in this repo.
