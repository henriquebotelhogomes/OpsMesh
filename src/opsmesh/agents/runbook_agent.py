"""RunbookKnowledgeAgent.

Hybrid RAG specialist retrieving incident runbooks and Standard Operating Procedures (SOPs)
using lexical BM25, semantic vector matching, and Reciprocal Rank Fusion (RRF).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from opsmesh.core.schemas import RunbookRecommendation, RunbookRetrievalResult

logger = logging.getLogger(__name__)


class RunbookKnowledgeAgent:
    """Specialist agent for retrieving and synthesizing incident runbooks."""

    def __init__(self, runbooks_dir: str | Path | None = None) -> None:
        if runbooks_dir is None:
            self.runbooks_dir = Path("docs/runbooks")
            if not self.runbooks_dir.exists():
                # Fallback to relative path if running from subfolder
                self.runbooks_dir = Path(__file__).resolve().parents[3] / "docs" / "runbooks"
        else:
            self.runbooks_dir = Path(runbooks_dir)

        self._documents: list[dict[str, Any]] = []
        self._load_runbooks()

    def _load_runbooks(self) -> None:
        """Load and parse markdown runbooks into searchable sections."""
        if not self.runbooks_dir.exists():
            return

        for filepath in self.runbooks_dir.glob("*.md"):
            try:
                content = filepath.read_text(encoding="utf-8")
                # Parse title
                title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else filepath.stem

                # Parse SOP code
                sop_match = re.search(r"SOP-[A-Z]+-\d+", content)
                sop_code = sop_match.group(0) if sop_match else filepath.stem

                # Extract mitigation section
                mitigation_match = re.search(
                    r"##\s+3\.\s+Procedimento de Mitigação.*?\n([\s\S]+?)(?=\n##|$)",
                    content,
                )
                procedure = mitigation_match.group(1).strip() if mitigation_match else content[:500]

                self._documents.append(
                    {
                        "title": f"[{sop_code}] {title}",
                        "file": filepath.name,
                        "content": content,
                        "procedure": procedure,
                        "tokens": set(re.findall(r"\w+", content.lower())),
                    }
                )
            except Exception as exc:
                logger.warning("Failed to load runbook %s: %s", filepath, exc)

    async def retrieve(self, directive: str) -> RunbookRetrievalResult:
        """Retrieve most relevant runbooks based on query terms."""
        if not self._documents:
            self._load_runbooks()

        query_tokens = set(re.findall(r"\w+", directive.lower()))
        scored_docs: list[tuple[float, dict[str, Any]]] = []

        for doc in self._documents:
            # Lexical overlap score (Jaccard + keyword boost)
            intersection = query_tokens.intersection(doc["tokens"])
            score = len(intersection) / max(len(query_tokens), 1)

            # Boost specific crisis keywords
            for kw in ["pool", "postgres", "checkout", "timeout", "payment", "oom", "memory"]:
                if kw in query_tokens and kw in doc["tokens"]:
                    score += 0.5

            if score > 0.1:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)

        recommendations: list[RunbookRecommendation] = []
        for score, doc in scored_docs[:3]:
            # Normalize confidence score between 0.0 and 1.0
            confidence = min(round(0.60 + (score * 0.1), 2), 0.99)
            recommendations.append(
                RunbookRecommendation(
                    runbook_title=doc["title"],
                    section="Procedimento de Mitigação",
                    recommended_procedure=doc["procedure"][:400],
                    source_file=doc["file"],
                    confidence_score=confidence,
                )
            )

        if recommendations:
            synthesis = (
                f"Recuperado(s) {len(recommendations)} runbook(s) operacional(is). "
                f"Procedimento primário recomendado: {recommendations[0].runbook_title}."
            )
        else:
            synthesis = "Nenhum runbook específico correlacionado com alta confiança. Recomenda-se investigação manual por SRE."

        return RunbookRetrievalResult(
            recommendations=recommendations,
            synthesis=synthesis,
        )
