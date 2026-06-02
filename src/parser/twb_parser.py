"""Parse Tableau workbook XML (`.twb`) or packaged workbooks (`.twbx`).

The parser produces a normalized, in-memory representation of the workbook
structure. Layout/visual noise is intentionally ignored; only the elements
needed for documentation are retained.
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

_BRACKET = re.compile(r"^\[(.*)\]$")


def _strip_brackets(value: str) -> str:
    match = _BRACKET.match(value.strip())
    return match.group(1) if match else value.strip()


@dataclass
class CalculatedField:
    internal_name: str
    name: str
    formula: str
    datasource: str
    datatype: Optional[str] = None


@dataclass
class Parameter:
    internal_name: str
    name: str
    datatype: str
    default: Optional[str] = None
    domain: Optional[str] = None


@dataclass
class DataSource:
    internal_name: str
    name: str
    connection: Optional[str] = None
    tables: list[str] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)


@dataclass
class Worksheet:
    name: str
    datasources: list[str] = field(default_factory=list)
    referenced_columns: set[str] = field(default_factory=set)


@dataclass
class Dashboard:
    name: str
    sheets: list[str] = field(default_factory=list)


@dataclass
class ParsedWorkbook:
    title: str
    version: Optional[str]
    data_sources: list[DataSource] = field(default_factory=list)
    calculated_fields: list[CalculatedField] = field(default_factory=list)
    parameters: list[Parameter] = field(default_factory=list)
    worksheets: list[Worksheet] = field(default_factory=list)
    dashboards: list[Dashboard] = field(default_factory=list)


def _read_twb_xml(path: Path) -> bytes:
    """Return the raw `.twb` XML bytes from a `.twb` or `.twbx` file."""
    if path.suffix.lower() == ".twbx":
        with zipfile.ZipFile(path) as archive:
            twb_names = [n for n in archive.namelist() if n.lower().endswith(".twb")]
            if not twb_names:
                raise ValueError(f"No .twb entry found inside packaged workbook: {path}")
            return archive.read(twb_names[0])
    return path.read_bytes()


def _is_parameter_source(ds_elem: ET.Element) -> bool:
    return ds_elem.get("name") == "Parameters" or ds_elem.get("caption") == "Parameters"


def _parse_parameters(ds_elem: ET.Element) -> list[Parameter]:
    params: list[Parameter] = []
    for col in ds_elem.findall("column"):
        if col.get("param-domain-type") is None:
            continue
        params.append(
            Parameter(
                internal_name=col.get("name", ""),
                name=col.get("caption") or _strip_brackets(col.get("name", "")),
                datatype=col.get("datatype", "string"),
                default=_clean_value(col.get("value")),
                domain=col.get("param-domain-type"),
            )
        )
    return params


def _clean_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value.strip().strip('"')


def _parse_data_source(ds_elem: ET.Element) -> tuple[DataSource, list[CalculatedField]]:
    internal_name = ds_elem.get("name", "")
    caption = ds_elem.get("caption") or internal_name
    connection_class = None
    tables: list[str] = []

    connection = ds_elem.find("connection")
    if connection is not None:
        named = connection.find(".//named-connection/connection")
        if named is not None:
            connection_class = named.get("class")
        for relation in connection.findall(".//relation"):
            if relation.get("type") == "table" and relation.get("name"):
                tables.append(relation.get("name"))

    regular_fields: list[str] = []
    calcs: list[CalculatedField] = []
    for col in ds_elem.findall("column"):
        calc = col.find("calculation")
        caption_or_name = col.get("caption") or _strip_brackets(col.get("name", ""))
        if calc is not None and calc.get("formula"):
            calcs.append(
                CalculatedField(
                    internal_name=col.get("name", ""),
                    name=caption_or_name,
                    formula=calc.get("formula", "").strip(),
                    datasource=caption,
                    datatype=col.get("datatype"),
                )
            )
        else:
            regular_fields.append(caption_or_name)

    return (
        DataSource(
            internal_name=internal_name,
            name=caption,
            connection=connection_class,
            tables=tables,
            fields=regular_fields,
        ),
        calcs,
    )


def _parse_worksheet(ws_elem: ET.Element) -> Worksheet:
    name = ws_elem.get("name", "")
    datasources: list[str] = []
    for ds in ws_elem.findall(".//view/datasources/datasource"):
        caption = ds.get("caption") or ds.get("name")
        if caption:
            datasources.append(caption)

    referenced: set[str] = set()
    for inst in ws_elem.findall(".//column-instance"):
        column = inst.get("column")
        if column:
            referenced.add(column)
    for col in ws_elem.findall(".//datasource-dependencies/column"):
        ref = col.get("name")
        if ref:
            referenced.add(ref)

    return Worksheet(name=name, datasources=datasources, referenced_columns=referenced)


def _parse_dashboard(db_elem: ET.Element, worksheet_names: set[str]) -> Dashboard:
    name = db_elem.get("name", "")
    sheets: list[str] = []
    for zone in db_elem.findall(".//zone"):
        zone_name = zone.get("name")
        if zone_name and zone_name in worksheet_names and zone_name not in sheets:
            sheets.append(zone_name)
    return Dashboard(name=name, sheets=sheets)


def parse_workbook(path: str | Path) -> ParsedWorkbook:
    """Parse a `.twb` or `.twbx` file into a :class:`ParsedWorkbook`."""
    path = Path(path)
    xml_bytes = _read_twb_xml(path)
    root = ET.fromstring(xml_bytes)

    data_sources: list[DataSource] = []
    calculated_fields: list[CalculatedField] = []
    parameters: list[Parameter] = []

    # Only the workbook-level <datasources> block; worksheet views also contain
    # <datasources> references that must not be treated as real data sources.
    top_level = root.find("datasources")
    for ds_elem in top_level.findall("datasource") if top_level is not None else []:
        if _is_parameter_source(ds_elem):
            parameters.extend(_parse_parameters(ds_elem))
            continue
        data_source, calcs = _parse_data_source(ds_elem)
        data_sources.append(data_source)
        calculated_fields.extend(calcs)

    worksheets = [_parse_worksheet(ws) for ws in root.findall(".//worksheets/worksheet")]
    worksheet_names = {ws.name for ws in worksheets}
    dashboards = [
        _parse_dashboard(db, worksheet_names)
        for db in root.findall(".//dashboards/dashboard")
    ]

    title = path.stem
    return ParsedWorkbook(
        title=title,
        version=root.get("version"),
        data_sources=data_sources,
        calculated_fields=calculated_fields,
        parameters=parameters,
        worksheets=worksheets,
        dashboards=dashboards,
    )
