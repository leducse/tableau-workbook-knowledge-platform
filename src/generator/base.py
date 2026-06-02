"""Generator interface for the two-pass documentation step.

Both the local mock and the Bedrock-backed implementation conform to this
interface, so the pipeline is agnostic to which one runs.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass


@dataclass
class GenerationResult:
    draft: str
    refined: str
    backend: str


class DocGenerator(abc.ABC):
    """Two-pass markdown generator: draft, then refine against metadata."""

    name: str = "base"

    @abc.abstractmethod
    def draft(self, metadata: dict) -> str:
        """Pass 1 — produce a human-readable markdown draft from metadata."""

    @abc.abstractmethod
    def refine(self, draft: str, metadata: dict) -> str:
        """Pass 2 — refine the draft, grounding it against metadata."""

    def generate(self, metadata: dict) -> GenerationResult:
        draft = self.draft(metadata)
        refined = self.refine(draft, metadata)
        return GenerationResult(draft=draft, refined=refined, backend=self.name)
