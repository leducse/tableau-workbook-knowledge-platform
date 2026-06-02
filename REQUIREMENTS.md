# Requirements — Tableau Workbook Knowledge Platform

> Replaces scattered documentation with **Tableau-grounded, human-curated
> knowledge** that agents and engineers can query.

---

## 1. Problem

- Business rules and metric definitions are scattered (warehouse, wikis, tribal knowledge).
- **Tableau workbooks** are what the field trusts and uses daily.
- Manual documentation takes **4–8 hours per workbook** and goes stale.
- GenAI on raw TWB/XML alone **hallucinates** field names and calc logic.

## 2. Goals

| Goal | Success signal |
|------|----------------|
| Extract structured metadata from Tableau workbooks | JSON schema covers calcs, params, datasources, sheets |
| Generate accurate markdown documentation | Second-pass Bedrock + validation; &lt;5% structural errors |
| Human-curated source of truth | Edited markdown in S3 is canonical version |
| Agent access | MCP (or RAG) searches approved doc corpus |
| Operational efficiency | ~5 minutes automated draft vs hours manual |

## 3. Pipeline (target state)

```text
Tableau REST API
    → download workbook (.twbx / .twb)
    → parse TWB → condensed JSON (essential metadata only)
    → Bedrock pass 1: draft markdown
    → Bedrock pass 2: refine / fact-check against JSON
    → S3: canonical markdown (+ JSON artifact)
    → optional: index for MCP retrieval
Web UI: review and edit markdown → publish back to S3
MCP tool: search / get_document(workbook_id)
```

## 4. Functional requirements

### 4.1 Ingestion

| ID | Requirement |
|----|-------------|
| R1 | Authenticate to Tableau Server via REST API (PAT or connected app). |
| R2 | Download workbook by ID or URL; support `.twb` inside `.twbx`. |
| R3 | Parse XML into normalized JSON: worksheets, dashboards, calculated fields, parameters, filters, data connections. |
| R4 | Strip noise (layout XML, binary) — JSON is **LLM-sized**, not full TWB. |

### 4.2 Generation

| ID | Requirement |
|----|-------------|
| R5 | Pass 1 (Bedrock): draft markdown — purpose, metrics, calcs, dependencies, datasources. |
| R6 | Pass 2 (Bedrock): refine using JSON only — fix names, flag unsupported claims, structured sections. |
| R7 | Validation checks: every calc name in markdown exists in JSON; parameters listed match source. |
| R8 | Store artifacts: `metadata.json`, `draft.md`, `published.md` (versioned) in S3. |

### 4.3 Human curation (source of truth)

| ID | Requirement |
|----|-------------|
| R9 | Web UI lists workbooks and documentation status (draft / published / stale). |
| R10 | Editor loads `published.md` (or draft); user saves → new S3 version. |
| R11 | **Published** version is what MCP and downstream systems read. |
| R12 | Optional: trigger re-ingest when Tableau workbook updated (stale badge). |

### 4.4 Agent access

| ID | Requirement |
|----|-------------|
| R13 | MCP tools: `list_workbooks`, `get_workbook_doc`, `search_docs` (keyword or embedding). |
| R14 | Responses cite workbook id + doc version + section. |
| R15 | Compatible with governed data-access MCP pattern (read-only S3/docs). |

## 5. Non-goals (v1)

- Replacing Tableau as the analytics UI.
- Full QuickSight migration (separate project).
- Real-time sync on every view refresh.
- Auto-publish without human review on first rollout.

## 6. AWS services (production target)

| Service | Role |
|---------|------|
| Lambda | Tableau fetch, parse, Bedrock orchestration |
| Step Functions | Optional multi-step generate pipeline |
| Amazon Bedrock | Draft + refine passes |
| S3 | JSON, markdown, versioned docs |
| API Gateway + Cognito | Web UI + API |
| DynamoDB | Workbook registry, status, version pointers |
| OpenSearch / Bedrock KB | Optional semantic search for MCP |

## 7. Quality & governance

- Two-pass generation is **mandatory** (draft ≠ publish).
- Validation report stored alongside markdown (discrepancy list).
- Audit: who published, when, which Tableau workbook version.
- PII: do not embed row-level data from Tableau extracts in docs.

## 8. Metrics (from prior delivery)

| Metric | Target |
|--------|--------|
| Time to first draft | ~5 minutes per workbook |
| Human review to publish | ~30–60 minutes (vs days to reverse-engineer) |
| Structural error rate post-validation | &lt;2% (calc/field name mismatches) |

---

*Requirements v1.0 — aligns with former Project Prism scope + MCP + editorial UI.*
