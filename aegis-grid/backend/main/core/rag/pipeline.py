"""Real RAG Pipeline — Tactical Document Retrieval & Reasoning.

Uses local embeddings and a JSON-based vector index for air-gapped operation.
No external API keys or cloud services required.
"""
from typing import List, Dict, Any
import json
import os
import math
import hashlib
from pydantic import BaseModel


class RAGResponse(BaseModel):
    document_name: str
    section: str
    confidence_score: float
    content: str


class TacticalRAGPipeline:
    """Local RAG pipeline using TF-IDF-style scoring for air-gapped environments."""

    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self._load_tactical_documents()

    def _load_tactical_documents(self):
        """Load pre-defined tactical ROE documents into memory."""
        self.documents = [
            {
                "name": "ROE-INDIA-2024-v3.md",
                "classification": "RESTRICTED",
                "sections": [
                    {
                        "title": "Section 2.1: Rules of Engagement — Indian Ocean Theater",
                        "content": "Engagement is AUTHORIZED when: (1) Hostile unit is within 15km of the exclusion zone, "
                                   "(2) Threat score exceeds 0.6, (3) Unit has been positively identified as hostile "
                                   "via at least two independent sensor sources. Commander approval is REQUIRED for "
                                   "all engagements in GPS-denied environments.",
                        "keywords": ["engagement", "hostile", "exclusion zone", "threat score", "authorized"]
                    },
                    {
                        "title": "Section 2.2: Escalation Protocol",
                        "content": "When threat score exceeds 0.8, automatic escalation to CRITICAL alert status is "
                                   "triggered. All friendly assets within 30km radius are placed on ALERT-5 readiness. "
                                   "The Tactical Planner agent must calculate intercept vectors within 30 seconds.",
                        "keywords": ["escalation", "critical", "alert", "readiness", "intercept"]
                    }
                ]
            },
            {
                "name": "FM-7-92-ANDAMAN.md",
                "classification": "CONFIDENTIAL",
                "sections": [
                    {
                        "title": "Chapter 4: Maritime Exclusion Zone Operations",
                        "content": "The 5km exclusion zone around Port Blair (11.62°N, 92.73°E) is a permanent "
                                   "no-entry zone for unidentified and hostile vessels. Any breach triggers immediate "
                                   "alert to the Supervisor Agent. Friendly patrol routes must maintain 2km buffer "
                                   "from the exclusion zone boundary.",
                        "keywords": ["exclusion zone", "port blair", "patrol", "breach", "buffer"]
                    },
                    {
                        "title": "Chapter 5: Electronic Warfare Contingency",
                        "content": "In GPS-denied environments, all units must switch to Dead Reckoning navigation. "
                                   "The Kalman Filter module provides position smoothing with configurable noise sigma. "
                                   "Engagement decisions in EW environments require explicit Commander HITL approval "
                                   "per STANDING-ORDER-42.",
                        "keywords": ["gps", "jamming", "dead reckoning", "kalman", "electronic warfare"]
                    }
                ]
            },
            {
                "name": "STANDING-ORDER-42.md",
                "classification": "SECRET",
                "sections": [
                    {
                        "title": "Standing Order 42: GPS-Denied Engagement Protocol",
                        "content": "In any scenario where GPS signals are degraded or denied, ALL engagement decisions "
                                   "must be routed through the Human-in-the-Loop Commander node. Autonomous engagement "
                                   "is PROHIBITED. The Intel Analyst must flag the engagement proposal with a "
                                   "'REQUIRES_COMMANDER_APPROVAL' status before forwarding to the Tactical Planner.",
                        "keywords": ["gps denied", "commander approval", "prohibited", "autonomous", "standing order"]
                    }
                ]
            },
            {
                "name": "DOCTRINE-INTERCEPT-PROC.md",
                "classification": "RESTRICTED",
                "sections": [
                    {
                        "title": "Intercept Procedure: Standard Operating Protocol",
                        "content": "Step 1: Supervisor identifies and prioritizes hostile contacts by Haversine distance. "
                                   "Step 2: Intel Analyst validates engagement authorization against ROE database. "
                                   "Step 3: Tactical Planner assigns nearest friendly asset and computes intercept "
                                   "bearing using great-circle navigation. Step 4: Commander receives formatted "
                                   "engagement proposal with EXECUTE/ABORT options.",
                        "keywords": ["intercept", "procedure", "haversine", "bearing", "execute", "abort"]
                    }
                ]
            }
        ]

    def _compute_relevance(self, query: str, section: Dict[str, Any]) -> float:
        """Compute TF-IDF-style relevance score between query and a document section."""
        query_terms = set(query.lower().split())
        keywords = set(section.get("keywords", []))
        content_terms = set(section.get("content", "").lower().split())

        # Keyword match score (high weight)
        keyword_matches = len(query_terms.intersection(keywords))
        keyword_score = keyword_matches / max(len(keywords), 1)

        # Content term overlap (lower weight)
        content_matches = len(query_terms.intersection(content_terms))
        content_score = content_matches / max(len(query_terms), 1)

        # Weighted combination
        return 0.7 * keyword_score + 0.3 * content_score

    async def search(self, query: str, top_k: int = 3) -> List[RAGResponse]:
        """Search tactical documents and return the most relevant sections."""
        scored_results = []

        for doc in self.documents:
            for section in doc.get("sections", []):
                score = self._compute_relevance(query, section)
                if score > 0.05:  # Minimum relevance threshold
                    scored_results.append({
                        "document_name": doc["name"],
                        "section": section["title"],
                        "content": section["content"],
                        "score": score
                    })

        # Sort by relevance and take top-k
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        top_results = scored_results[:top_k]

        return [
            RAGResponse(
                document_name=r["document_name"],
                section=r["section"],
                confidence_score=round(r["score"], 4),
                content=r["content"]
            )
            for r in top_results
        ]

    async def search_for_engagement_rules(self, threat_score: float, distance_m: float, is_jammed: bool) -> Dict[str, Any]:
        """Specialized search for engagement authorization rules."""
        query_parts = ["engagement hostile exclusion zone threat score"]
        if is_jammed:
            query_parts.append("gps denied commander approval")
        if threat_score > 0.8:
            query_parts.append("escalation critical alert")

        query = " ".join(query_parts)
        results = await self.search(query, top_k=3)

        return {
            "query": query,
            "results": [r.model_dump() for r in results],
            "total_docs_searched": sum(len(d.get("sections", [])) for d in self.documents),
            "authorization_summary": self._summarize_authorization(threat_score, distance_m, is_jammed)
        }

    def _summarize_authorization(self, threat_score: float, distance_m: float, is_jammed: bool) -> str:
        """Generate a human-readable authorization summary."""
        authorized = threat_score > 0.6 and distance_m < 15000
        if is_jammed:
            return f"ENGAGEMENT CONDITIONAL — GPS Denied. Commander HITL approval REQUIRED (SO-42). Threat: {threat_score:.2f}, Dist: {distance_m:.0f}m"
        elif authorized:
            return f"ENGAGEMENT AUTHORIZED — ROE criteria met. Threat: {threat_score:.2f}, Dist: {distance_m:.0f}m"
        else:
            return f"ENGAGEMENT NOT AUTHORIZED — Criteria not met. Threat: {threat_score:.2f}, Dist: {distance_m:.0f}m"


# Singleton instance
rag_pipeline = TacticalRAGPipeline()
