# Demo Workbook

> Auto-generated draft documentation for Tableau workbook `demo-workbook`.

## Overview

This workbook surfaces 3 worksheet(s) across 2 dashboard(s), built on 1 data source(s). It is intended as the field-trusted reference for the metrics and business rules defined below.

## Data Sources

- **Sales** — connection: `redshift`, tables: pipeline

## Calculated Fields

### ARR YTD

- **Formula:** `SUM([arr])`
- **Data source:** Sales
- **Used on sheets:** Summary, Trend

### Win Rate

- **Formula:** `SUM([won]) / SUM([opportunities])`
- **Data source:** Sales
- **Used on sheets:** Summary

### Region In Scope

- **Formula:** `[region] = [Parameters].[Parameter 1]`
- **Data source:** Sales
- **Used on sheets:** Pipeline Detail


## Parameters

- **Region** (string) — default: `NA`
- **Target ARR** (number) — default: `1000000`

## Dashboards

- **Executive Summary** — sheets: Summary, Trend
- **Pipeline Operations** — sheets: Pipeline Detail
