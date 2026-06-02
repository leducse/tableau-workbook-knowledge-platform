"""Select a generator implementation based on environment configuration.

Defaults to the local mock so the demo runs with no AWS access. Set
``DOC_GENERATOR=bedrock`` to use the Amazon Bedrock path.
"""

from __future__ import annotations

import os

from .base import DocGenerator
from .mock import MockGenerator


def get_generator(backend: str | None = None) -> DocGenerator:
    backend = (backend or os.environ.get("DOC_GENERATOR", "mock")).strip().lower()
    if backend in ("mock", "local", "local-mock"):
        return MockGenerator()
    if backend == "bedrock":
        from .bedrock import BedrockGenerator

        return BedrockGenerator()
    raise ValueError(f"Unknown DOC_GENERATOR backend: {backend!r}")
