"""Local filesystem stand-in for the S3 document store.

Mirrors the S3 layout from ARCHITECTURE.md so the same code shape would port to
boto3 later:

    {root}/workbooks/{workbook_id}/
        v{timestamp}/{metadata.json, validation.json, draft.md, refined.md}
        published/{current.md, manifest.json}
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class LocalDocStore:
    def __init__(self, root: str | Path = "output/docs") -> None:
        self.root = Path(root)

    def _workbook_dir(self, workbook_id: str) -> Path:
        return self.root / "workbooks" / workbook_id

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def save_version(
        self,
        workbook_id: str,
        metadata: dict,
        draft_md: str,
        refined_md: str,
        validation: dict,
        version: Optional[str] = None,
    ) -> Path:
        version = version or f"v{self._timestamp()}"
        version_dir = self._workbook_dir(workbook_id) / version
        version_dir.mkdir(parents=True, exist_ok=True)

        (version_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
        (version_dir / "validation.json").write_text(
            json.dumps(validation, indent=2) + "\n", encoding="utf-8"
        )
        (version_dir / "draft.md").write_text(draft_md, encoding="utf-8")
        (version_dir / "refined.md").write_text(refined_md, encoding="utf-8")
        return version_dir

    def publish(
        self,
        workbook_id: str,
        markdown: str,
        version: str,
        editor: str = "pipeline",
        tableau_updated_at: Optional[str] = None,
    ) -> Path:
        published_dir = self._workbook_dir(workbook_id) / "published"
        published_dir.mkdir(parents=True, exist_ok=True)
        (published_dir / "current.md").write_text(markdown, encoding="utf-8")
        manifest = {
            "workbook_id": workbook_id,
            "version": version,
            "editor": editor,
            "published_at": self._timestamp(),
            "tableau_updated_at": tableau_updated_at,
        }
        (published_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        return published_dir

    def list_workbooks(self) -> list[str]:
        base = self.root / "workbooks"
        if not base.exists():
            return []
        return sorted(p.name for p in base.iterdir() if p.is_dir())

    def get_published_doc(self, workbook_id: str) -> Optional[str]:
        path = self._workbook_dir(workbook_id) / "published" / "current.md"
        return path.read_text(encoding="utf-8") if path.exists() else None

    def get_manifest(self, workbook_id: str) -> Optional[dict]:
        path = self._workbook_dir(workbook_id) / "published" / "manifest.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
