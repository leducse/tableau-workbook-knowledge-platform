"""MCP-style read tools over the published document corpus.

This is a thin, dependency-free stand-in for an MCP server. It exposes the
read-only tools from the spec (``list_workbooks``, ``get_workbook_doc``,
``search_docs``) over the published docs only, plus a small CLI for the demo.
"""

from __future__ import annotations

import argparse
import json

from ..retrieval import DocRetriever

TOOLS = [
    {
        "name": "list_workbooks",
        "description": "List published workbook documents and their versions.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_workbook_doc",
        "description": "Return the published markdown document for a workbook id.",
        "input_schema": {
            "type": "object",
            "properties": {"workbook_id": {"type": "string"}},
            "required": ["workbook_id"],
        },
    },
    {
        "name": "search_docs",
        "description": "Keyword search across published workbook documents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
]


def call_tool(name: str, arguments: dict | None = None, retriever: DocRetriever | None = None):
    arguments = arguments or {}
    retriever = retriever or DocRetriever()

    if name == "list_workbooks":
        return retriever.list_workbooks()
    if name == "get_workbook_doc":
        return retriever.get_workbook_doc(arguments["workbook_id"])
    if name == "search_docs":
        return retriever.search_docs(arguments["query"], int(arguments.get("limit", 5)))
    raise ValueError(f"Unknown tool: {name!r}")


def _main() -> None:
    parser = argparse.ArgumentParser(description="MCP-style doc reader (demo CLI).")
    parser.add_argument("tool", choices=[t["name"] for t in TOOLS])
    parser.add_argument("--workbook-id")
    parser.add_argument("--query")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--docs-root", default="output/docs")
    args = parser.parse_args()

    from ..storage import LocalDocStore

    retriever = DocRetriever(LocalDocStore(args.docs_root))
    arguments: dict = {}
    if args.workbook_id:
        arguments["workbook_id"] = args.workbook_id
    if args.query:
        arguments["query"] = args.query
        arguments["limit"] = args.limit

    result = call_tool(args.tool, arguments, retriever=retriever)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _main()
