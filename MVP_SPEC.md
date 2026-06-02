# MVP Spec — Portfolio Demo

> Build a **credible, small demo** of the documentation pipeline—not full
> Tableau Server integration unless you have a test site.

---

## MVP scope

| In | Out |
|----|-----|
| Parse **sample `.twb`** from repo | Production Tableau PAT / all workbooks |
| Condensed `metadata.json` | Full workbook XML in prompts |
| Bedrock draft + refine (2 Lambda calls or 1 Step Function) | Usage analytics from Redshift |
| S3 versioned markdown | OpenSearch / Bedrock KB (optional stretch) |
| Minimal **React or static** editor UI | Full auth/RBAC |
| MCP: `get_workbook_doc` + `list_workbooks` | Semantic search |
| Rule-based validator | ML quality scorer |

---

## Repo layout (when built)

```text
tableau-workbook-knowledge-platform/
├── README.md
├── MVP_SPEC.md
├── samples/
│   └── demo_workbook.twb          # sanitized sample
├── src/
│   ├── parser/                    # TWB → metadata.json
│   ├── generator/                 # Bedrock draft + refine
│   ├── validator/
│   ├── api/                       # Lambda handlers
│   └── mcp_server/                # read published docs from S3
├── web/                           # simple editor (Vite + React)
├── infra/cdk/                     # S3, Lambda, API GW, Cognito (minimal)
└── scripts/
    └── run_local_pipeline.py      # no AWS for quick demo
```

---

## AWS MVP stack

| Service | Use |
|---------|-----|
| **S3** | `metadata.json`, `refined.md`, `published/current.md` |
| **Lambda** | parse, generate, validate, API CRUD |
| **Bedrock** | Claude — draft and refine prompts |
| **API Gateway** | `GET/PUT /workbooks/{id}/doc` |
| **Cognito** | Single demo user (optional; API key ok for MVP) |

Skip Step Functions unless you want one extra slide in the demo.

---

## `metadata.json` schema (minimal)

```json
{
  "workbook_id": "demo-sales",
  "title": "Regional Sales Overview",
  "data_sources": [{ "name": "Sales", "connection": "redshift", "tables": ["pipeline"] }],
  "calculated_fields": [
    { "name": "ARR YTD", "formula": "SUM([arr])", "used_on_sheets": ["Summary"] }
  ],
  "parameters": [{ "name": "Region", "type": "string", "default": "NA" }],
  "dashboards": [{ "name": "Executive Summary", "sheets": ["Summary", "Trend"] }]
}
```

---

## Demo script (5 minutes)

1. Run `run_local_pipeline.py` on `samples/demo_workbook.twb` → show `metadata.json`.
2. Trigger Bedrock → show `refined.md` + `validation.json` (all green).
3. Open web UI → edit one paragraph → save to S3 `published/current.md`.
4. MCP `get_workbook_doc("demo-sales")` returns published text only.
5. Mention production: Tableau REST + org-wide registry + link to MCP query governance.

---

## Implementation order

1. TWB parser + sample workbook + unit tests  
2. Bedrock prompts (draft/refine) + validator  
3. S3 layout + local script  
4. CDK minimal deploy  
5. Tiny web editor  
6. MCP reader  

**Estimate:** ~2 weeks part-time.

---

## Success criteria

- [ ] Parser extracts calcs/params from sample TWB  
- [ ] Two Bedrock passes produce markdown that passes validator  
- [ ] UI can overwrite `published/current.md`  
- [ ] MCP returns published doc only  
- [ ] README 30-minute local demo path works  

---

*MVP v1.0 — Tableau Workbook Knowledge Platform (formerly Project Prism)*
