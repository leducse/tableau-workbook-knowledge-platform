"""Amazon Bedrock-backed generator (optional, guarded).

This path is only used when ``DOC_GENERATOR=bedrock``. It imports ``boto3``
lazily so the local demo never requires AWS dependencies or credentials. The
two passes mirror the spec: draft from metadata, then refine the draft while
fact-checking it against the same metadata.
"""

from __future__ import annotations

import json
import os

from .base import DocGenerator

_DEFAULT_MODEL = "anthropic.claude-3-5-sonnet-20241022-v2:0"

_DRAFT_PROMPT = """You are a BI documentation writer. Using ONLY the workbook
metadata JSON below, write clear markdown documentation describing the
workbook's purpose, data sources, calculated fields (with formulas), parameters
and dashboards. Do not invent field names or metrics.

Workbook metadata:
```json
{metadata}
```
"""

_REFINE_PROMPT = """You are a BI documentation editor. Refine the DRAFT markdown
below so it is accurate and well structured. Use the metadata JSON as the source
of truth: every calculated field and parameter name must match the metadata, and
remove any claim not supported by it. Enforce these sections: Purpose,
Metrics & Calculated Fields, Parameters, Data Sources, Dashboards & Dependencies.

Metadata JSON:
```json
{metadata}
```

DRAFT:
{draft}
"""


class BedrockGenerator(DocGenerator):
    name = "bedrock"

    def __init__(self, model_id: str | None = None, region: str | None = None) -> None:
        self.model_id = model_id or os.environ.get("BEDROCK_MODEL_ID", _DEFAULT_MODEL)
        self.region = region or os.environ.get("AWS_REGION", "us-east-1")
        self._client = None

    def _bedrock(self):
        if self._client is None:
            import boto3  # imported lazily; only required for the Bedrock path

            self._client = boto3.client("bedrock-runtime", region_name=self.region)
        return self._client

    def _invoke(self, prompt: str) -> str:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        }
        response = self._bedrock().invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
        )
        payload = json.loads(response["body"].read())
        return "".join(block.get("text", "") for block in payload.get("content", []))

    def draft(self, metadata: dict) -> str:
        return self._invoke(_DRAFT_PROMPT.format(metadata=json.dumps(metadata, indent=2)))

    def refine(self, draft: str, metadata: dict) -> str:
        prompt = _REFINE_PROMPT.format(
            metadata=json.dumps(metadata, indent=2), draft=draft
        )
        return self._invoke(prompt)
