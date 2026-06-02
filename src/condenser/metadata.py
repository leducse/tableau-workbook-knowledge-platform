"""Condense a :class:`ParsedWorkbook` into the minimal `metadata.json` schema.

The condensed form is the only workbook context handed to the generator, so it
deliberately drops layout XML and keeps just the fields the documentation
needs: data sources, calculated fields, parameters, worksheets and dashboards.
"""

from __future__ import annotations

import re
from typing import Optional

from ..parser import ParsedWorkbook

_SLUG = re.compile(r"[^a-z0-9]+")
_DATATYPE_MAP = {
    "real": "number",
    "integer": "number",
    "string": "string",
    "boolean": "boolean",
    "date": "date",
    "datetime": "datetime",
}


def workbook_id_from_title(title: str) -> str:
    slug = _SLUG.sub("-", title.lower()).strip("-")
    return slug or "workbook"


def _normalize_type(datatype: Optional[str]) -> str:
    if not datatype:
        return "string"
    return _DATATYPE_MAP.get(datatype, datatype)


def _sheets_using(internal_name: str, workbook: ParsedWorkbook) -> list[str]:
    return [ws.name for ws in workbook.worksheets if internal_name in ws.referenced_columns]


def condense(workbook: ParsedWorkbook, workbook_id: Optional[str] = None) -> dict:
    """Return the condensed metadata dictionary for ``workbook``."""
    title = workbook.title.replace("_", " ").replace("-", " ").title()
    wb_id = workbook_id or workbook_id_from_title(workbook.title)

    data_sources = [
        {
            "name": ds.name,
            "connection": ds.connection or "unknown",
            "tables": ds.tables,
            "fields": ds.fields,
        }
        for ds in workbook.data_sources
    ]

    calculated_fields = [
        {
            "name": calc.name,
            "formula": calc.formula,
            "data_source": calc.datasource,
            "used_on_sheets": _sheets_using(calc.internal_name, workbook),
        }
        for calc in workbook.calculated_fields
    ]

    parameters = [
        {
            "name": param.name,
            "type": _normalize_type(param.datatype),
            "default": param.default,
        }
        for param in workbook.parameters
    ]

    dashboards = [
        {"name": db.name, "sheets": db.sheets} for db in workbook.dashboards
    ]

    return {
        "workbook_id": wb_id,
        "title": title,
        "version": workbook.version,
        "data_sources": data_sources,
        "calculated_fields": calculated_fields,
        "parameters": parameters,
        "worksheets": [ws.name for ws in workbook.worksheets],
        "dashboards": dashboards,
    }
