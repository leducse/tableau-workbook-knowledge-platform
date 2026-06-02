"""Amazon Bedrock-backed generator (optional, guarded).

Uses ``portfolio_aws.BedrockConverse`` (Converse API) when ``PORTFOLIO_SECRET_ARN``
or ``BEDROCK_MODEL_ID`` is set. Install the shared lib::

    pip install -e ../../libs/portfolio_aws

Set ``DOC_GENERATOR=bedrock``. Credentials come from your AWS profile or instance
role — never from git.
"""

from __future__ import annotations

import json
import os

from .base import DocGenerator

_DRAFT_SYSTEM = "You are a BI documentation writer. Use only the provided metadata."
_DRAFT_USER = """Write markdown documentation for this Tableau workbook metadata.
Include: Purpose, Metrics & Calculated Fields, Parameters, Data Sources, Dashboards.
Do not invent fields.

Metadata JSON:
{metadata}
"""

_REFINE_SYSTEM = "You are a BI documentation editor. Ground every claim in the metadata."
_REFINE_USER = """Refine the draft. Remove unsupported claims. Keep sections:
Purpose, Metrics & Calculated Fields, Parameters, Data Sources, Dashboards.

Metadata:
{metadata}

Draft:
{draft}
"""


class BedrockGenerator(DocGenerator):
    name = "bedrock"

    def __init__(self) -> None:
        try:
            from portfolio_aws import BedrockConverse, load_config
        except ImportError as exc:
            raise ImportError(
                "Bedrock path requires portfolio_aws. From repo root run:\n"
                "  pip install -e ../libs/portfolio_aws\n"
                "Then set PORTFOLIO_SECRET_ARN (after CDK deploy) or BEDROCK_MODEL_ID."
            ) from exc
        self._load_config = load_config
        self._BedrockConverse = BedrockConverse
        self._llm = None

    def _client(self):
        if self._llm is None:
            config = self._load_config(require_secret=bool(os.environ.get("PORTFOLIO_SECRET_ARN")))
            self._llm = self._BedrockConverse(config)
        return self._llm

    def draft(self, metadata: dict) -> str:
        meta = json.dumps(metadata, indent=2)
        return self._client().complete(
            _DRAFT_USER.format(metadata=meta),
            system=_DRAFT_SYSTEM,
        ).text

    def refine(self, draft: str, metadata: dict) -> str:
        meta = json.dumps(metadata, indent=2)
        return self._client().complete(
            _REFINE_USER.format(metadata=meta, draft=draft),
            system=_REFINE_SYSTEM,
        ).text
