#!/usr/bin/env python3
"""Run the local documentation pipeline end-to-end on a sample workbook.

    parse .twb -> condense metadata.json -> generate (draft + refine)
    -> validate -> store version -> publish -> query via MCP tools

Runs with no AWS credentials by default (local mock generator). Set
``DOC_GENERATOR=bedrock`` to use the Amazon Bedrock path instead.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.condenser import condense
from src.generator import get_generator
from src.mcp_server import call_tool
from src.parser import parse_workbook
from src.retrieval import DocRetriever
from src.storage import LocalDocStore
from src.validator import validate


def run(workbook_path: Path, docs_root: Path, output_root: Path, backend: str | None) -> int:
    print(f"[1/6] Parsing workbook: {workbook_path}")
    parsed = parse_workbook(workbook_path)

    print("[2/6] Condensing metadata")
    metadata = condense(parsed)
    workbook_id = metadata["workbook_id"]
    print(
        f"      workbook_id={workbook_id} "
        f"data_sources={len(metadata['data_sources'])} "
        f"calcs={len(metadata['calculated_fields'])} "
        f"params={len(metadata['parameters'])} "
        f"worksheets={len(metadata['worksheets'])} "
        f"dashboards={len(metadata['dashboards'])}"
    )

    generator = get_generator(backend)
    print(f"[3/6] Generating documentation (backend={generator.name})")
    result = generator.generate(metadata)

    print("[4/6] Validating refined document")
    report = validate(result.refined, metadata)
    status = "PASS" if report.passed else "FAIL"
    print(f"      validation: {status} "
          f"({report.to_dict()['summary']['passed']}/{report.to_dict()['summary']['total']} checks)")
    for check in report.checks:
        if not check.passed:
            for detail in check.details:
                print(f"        - {check.id}: {detail}")

    print("[5/6] Storing artifacts")
    store = LocalDocStore(docs_root)
    version = "vDEMO"
    version_dir = store.save_version(
        workbook_id=workbook_id,
        metadata=metadata,
        draft_md=result.draft,
        refined_md=result.refined,
        validation=report.to_dict(),
        version=version,
    )
    if report.passed:
        store.publish(workbook_id, result.refined, version=version)
        print(f"      published -> {store.root}/workbooks/{workbook_id}/published/current.md")
    else:
        print("      not published (validation failed)")
    print(f"      version dir -> {version_dir}")

    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    (output_root / "draft.md").write_text(result.draft, encoding="utf-8")
    (output_root / "refined.md").write_text(result.refined, encoding="utf-8")
    (output_root / "validation.json").write_text(
        json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8"
    )
    print(f"      demo artifacts -> {output_root}/(metadata.json, draft.md, refined.md, validation.json)")

    print("[6/6] Querying via MCP-style tools")
    retriever = DocRetriever(store)
    print("      list_workbooks:", json.dumps(call_tool("list_workbooks", retriever=retriever)))
    hits = call_tool("search_docs", {"query": "win rate region"}, retriever=retriever)
    print("      search_docs('win rate region'):", json.dumps(hits))
    doc = call_tool("get_workbook_doc", {"workbook_id": workbook_id}, retriever=retriever)
    preview = (doc or {}).get("content", "").splitlines()[:1]
    print(f"      get_workbook_doc('{workbook_id}') -> {preview[0] if preview else '(none)'}")

    return 0 if report.passed else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workbook",
        default=str(REPO_ROOT / "samples" / "demo_workbook.twb"),
        help="Path to a .twb or .twbx workbook.",
    )
    parser.add_argument("--docs-root", default=str(REPO_ROOT / "output" / "docs"))
    parser.add_argument("--output-root", default=str(REPO_ROOT / "output"))
    parser.add_argument(
        "--backend",
        default=None,
        help="Generator backend: 'mock' (default) or 'bedrock'. "
        "Falls back to the DOC_GENERATOR env var.",
    )
    args = parser.parse_args()

    exit_code = run(
        workbook_path=Path(args.workbook),
        docs_root=Path(args.docs_root),
        output_root=Path(args.output_root),
        backend=args.backend,
    )
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
