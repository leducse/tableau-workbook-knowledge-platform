"""Keyword retrieval over the published document corpus.

Reads only ``published/current.md`` for each workbook (the human-approved
version), matching the governed, read-only access pattern the MCP layer uses.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..storage import LocalDocStore

_WORD = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _WORD.findall(text.lower())


@dataclass
class SearchHit:
    workbook_id: str
    version: str | None
    score: int
    snippet: str

    def to_dict(self) -> dict:
        return {
            "workbook_id": self.workbook_id,
            "version": self.version,
            "score": self.score,
            "snippet": self.snippet,
        }


class DocRetriever:
    def __init__(self, store: LocalDocStore | None = None) -> None:
        self.store = store or LocalDocStore()

    def list_workbooks(self) -> list[dict]:
        results = []
        for workbook_id in self.store.list_workbooks():
            manifest = self.store.get_manifest(workbook_id) or {}
            results.append(
                {
                    "workbook_id": workbook_id,
                    "version": manifest.get("version"),
                    "published": self.store.get_published_doc(workbook_id) is not None,
                }
            )
        return results

    def get_workbook_doc(self, workbook_id: str) -> dict | None:
        markdown = self.store.get_published_doc(workbook_id)
        if markdown is None:
            return None
        manifest = self.store.get_manifest(workbook_id) or {}
        return {
            "workbook_id": workbook_id,
            "version": manifest.get("version"),
            "content": markdown,
        }

    def search_docs(self, query: str, limit: int = 5) -> list[dict]:
        terms = set(_tokenize(query))
        if not terms:
            return []

        hits: list[SearchHit] = []
        for workbook_id in self.store.list_workbooks():
            markdown = self.store.get_published_doc(workbook_id)
            if markdown is None:
                continue
            tokens = _tokenize(markdown)
            score = sum(tokens.count(term) for term in terms)
            if score == 0:
                continue
            manifest = self.store.get_manifest(workbook_id) or {}
            hits.append(
                SearchHit(
                    workbook_id=workbook_id,
                    version=manifest.get("version"),
                    score=score,
                    snippet=self._snippet(markdown, terms),
                )
            )

        hits.sort(key=lambda h: h.score, reverse=True)
        return [hit.to_dict() for hit in hits[:limit]]

    @staticmethod
    def _snippet(markdown: str, terms: set[str], width: int = 160) -> str:
        lowered = markdown.lower()
        for term in terms:
            idx = lowered.find(term)
            if idx != -1:
                start = max(0, idx - width // 2)
                end = min(len(markdown), idx + width // 2)
                return markdown[start:end].strip().replace("\n", " ")
        return markdown[:width].strip().replace("\n", " ")
