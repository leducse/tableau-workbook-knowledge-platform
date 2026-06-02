"""Rule-based validator for generated documentation.

Runs after the refine pass (no model required). It checks that the markdown is
grounded in the condensed metadata: calculated fields and parameters are
covered, and the expected structural sections are present.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

_REQUIRED_SECTIONS = [
    "Purpose",
    "Metrics & Calculated Fields",
    "Parameters",
    "Data Sources",
    "Dashboards",
]


@dataclass
class Check:
    id: str
    description: str
    passed: bool
    details: list[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    workbook_id: str
    passed: bool
    checks: list[Check]

    def to_dict(self) -> dict:
        return {
            "workbook_id": self.workbook_id,
            "passed": self.passed,
            "summary": {
                "total": len(self.checks),
                "passed": sum(1 for c in self.checks if c.passed),
                "failed": sum(1 for c in self.checks if not c.passed),
            },
            "checks": [asdict(c) for c in self.checks],
        }


def _check_calc_coverage(markdown: str, metadata: dict) -> Check:
    missing = [c["name"] for c in metadata.get("calculated_fields", []) if c["name"] not in markdown]
    return Check(
        id="calc_coverage",
        description="Every calculated field in metadata appears in the document.",
        passed=not missing,
        details=[f"missing calculated field: {name}" for name in missing],
    )


def _check_param_coverage(markdown: str, metadata: dict) -> Check:
    missing = [p["name"] for p in metadata.get("parameters", []) if p["name"] not in markdown]
    return Check(
        id="param_coverage",
        description="Every parameter in metadata appears in the document.",
        passed=not missing,
        details=[f"missing parameter: {name}" for name in missing],
    )


def _check_sections(markdown: str) -> Check:
    missing = [section for section in _REQUIRED_SECTIONS if section not in markdown]
    return Check(
        id="required_sections",
        description="Document contains the required structural sections.",
        passed=not missing,
        details=[f"missing section: {section}" for section in missing],
    )


def _check_datasource_coverage(markdown: str, metadata: dict) -> Check:
    missing = [d["name"] for d in metadata.get("data_sources", []) if d["name"] not in markdown]
    return Check(
        id="datasource_coverage",
        description="Every data source in metadata appears in the document.",
        passed=not missing,
        details=[f"missing data source: {name}" for name in missing],
    )


def validate(markdown: str, metadata: dict) -> ValidationReport:
    """Validate ``markdown`` against the condensed ``metadata``."""
    checks = [
        _check_sections(markdown),
        _check_calc_coverage(markdown, metadata),
        _check_param_coverage(markdown, metadata),
        _check_datasource_coverage(markdown, metadata),
    ]
    return ValidationReport(
        workbook_id=metadata.get("workbook_id", "unknown"),
        passed=all(c.passed for c in checks),
        checks=checks,
    )
