# Tableau Workbook Knowledge Platform

**Former internal name:** Project Prism

**Status:** MVP built — runnable locally with **no AWS credentials**. The Amazon
Bedrock generation step is **mocked locally** (template-based markdown); a
guarded Bedrock implementation path is included behind an env var.

Turns Tableau workbooks into **curated, field-trusted documentation**: extract
workbook metadata, generate markdown with Amazon Bedrock, human-edit via a
web UI, store in S3, and expose content to agents through MCP-style retrieval.

## Quick start (local demo, ~2 minutes)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_pipeline.py
```

This parses the sanitized sample workbook and runs the full pipeline:

```text
samples/demo_workbook.twb
  → parse TWB/TWBX XML
  → condense to metadata.json (data sources, calc fields, params, sheets, dashboards)
  → generate draft markdown (Bedrock pass 1 — MOCKED locally)
  → refine + ground against metadata (Bedrock pass 2 — MOCKED locally)
  → rule-based validator (calc/param/datasource/section coverage)
  → store versioned artifacts + publish (local filesystem stand-in for S3)
  → query via MCP-style tools (list_workbooks / get_workbook_doc / search_docs)
```

### Generated demo artifacts (committed)

| Path | What |
|------|------|
| `output/metadata.json` | Condensed workbook metadata |
| `output/draft.md` | Pass 1 draft |
| `output/refined.md` | Pass 2 refined, published doc |
| `output/validation.json` | Rule-based validation report (all green) |
| `output/docs/workbooks/demo-workbook/` | S3-style versioned + published layout |

### Query the published docs (MCP-style read tools)

```bash
python -m src.mcp_server.server list_workbooks
python -m src.mcp_server.server get_workbook_doc --workbook-id demo-workbook
python -m src.mcp_server.server search_docs --query "win rate region"
```

## Bedrock path (optional, guarded)

The generation step is behind a `DocGenerator` interface. The default
`local-mock` implementation requires **no AWS**. To use real Bedrock:

```bash
pip install boto3
export DOC_GENERATOR=bedrock
pip install -e ../libs/portfolio_aws   # or: pip install git+https://github.com/leducse/portfolio-aws-lib.git
export PORTFOLIO_SECRET_ARN=arn:aws:secretsmanager:...  # from CDK output after deploy
# Or set BEDROCK_MODEL_ID only (uses default region from AWS profile)
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
python scripts/run_pipeline.py
```

`boto3` is imported lazily and only on this path, so the local demo never needs
it (see `src/generator/bedrock.py`).

## Source layout

```text
src/
  parser/      TWB/TWBX XML → normalized structure
  condenser/   normalized structure → minimal metadata.json
  generator/   two-pass docs: mock (Jinja2) + Bedrock-guarded, behind one interface
  validator/   rule-based grounding checks (no model)
  storage/     local filesystem stand-in for the S3 doc store
  retrieval/   keyword search over published docs
  mcp_server/  MCP-style read tools (list / get / search) over published docs
scripts/
  run_pipeline.py   end-to-end local pipeline runner
samples/
  demo_workbook.twb sanitized, hand-authored sample workbook
```

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

**Tableau → QuickSight migration** is a separate repo:
[`tableau-quicksight-migration-assistant`](../tableau-quicksight-migration-assistant/)
(same Tableau extract step, different downstream).

## Disclaimer

Portfolio/demo implementation uses **sample workbooks and synthetic metadata**.
No production Tableau Server credentials or customer dashboards in this repo.
