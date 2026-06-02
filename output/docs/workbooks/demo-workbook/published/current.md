---
workbook_id: demo-workbook
title: Demo Workbook
generated_by: local-mock
data_sources: 1
calculated_fields: 3
parameters: 2
---

# Demo Workbook

Curated documentation for Tableau workbook `demo-workbook`. Every metric and
business rule below is grounded in the parsed workbook metadata.

## Purpose

Demo Workbook provides a single, field-trusted view of the metrics tracked in this
workbook. It draws on 1 data source(s) and exposes
3 calculated field(s) across
3 worksheet(s).

## Metrics & Calculated Fields
| Field | Formula | Used on |
|-------|---------|---------|
| `ARR YTD` | `SUM([arr])` | Summary, Trend |
| `Win Rate` | `SUM([won]) / SUM([opportunities])` | Summary |
| `Region In Scope` | `[region] = [Parameters].[Parameter 1]` | Pipeline Detail |

## Parameters
| Parameter | Type | Default |
|-----------|------|---------|
| `Region` | string | `NA` |
| `Target ARR` | number | `1000000` |

## Data Sources

- **Sales** (`redshift`) — tables: pipeline

## Dashboards & Dependencies

- **Executive Summary** — sheets: Summary, Trend
- **Pipeline Operations** — sheets: Pipeline Detail

## Worksheets

- Summary
- Trend
- Pipeline Detail
