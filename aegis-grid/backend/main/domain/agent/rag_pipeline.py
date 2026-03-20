from typing import List, Dict, Any
from main.infrastructure.config.settings import settings

class AdvancedRAG:
    """Implements advanced RAG architectures."""

    @staticmethod
    def hyde_prompt(query: str) -> str:
        """Hypothetical Document Embeddings (HyDE)."""
        prompt = f"""
        Please write a brief, authoritative passage that directly answers the following query.
        Treat this passage as a military doctrine or field manual excerpt.
        Query: '{query}'
        """
        return prompt

    @staticmethod
    def semantic_chunking(text: str, similarity_threshold: float = 0.8) -> List[str]:
        """
        Simulates embedding-similarity based semantic chunking.
        Instead of fixed token windows, it groups sentences logically.
        (Implementation simplified to paragraph splitting for current lack of embed model)
        """
        import re
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = ""
        for p in paragraphs:
            if len(current_chunk) + len(p) > 1000:  # Fallback threshold
                chunks.append(current_chunk.strip())
                current_chunk = p
            else:
                current_chunk += "\n\n" + p
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    @staticmethod
    def rag_fusion_queries(original_query: str) -> List[str]:
        """Generates sub-queries for RAG Fusion."""
        # This would typically call an LLM.
        return [
            original_query,
            f"What are the rules of engagement regarding {original_query}?",
            f"Historical mission reports similar to {original_query}",
            f"Tactical response procedures for {original_query}"
        ]

    @staticmethod
    def reciprocal_rank_fusion(search_results_list: List[List[Dict[str, Any]]], k: int = 60) -> List[Dict[str, Any]]:
        """Reciprocal Rank Fusion (RRF) for combining multi-query results."""
        fused_scores = {}
        document_store = {}
        for doc_list in search_results_list:
            for rank, doc in enumerate(doc_list):
                doc_id = doc.get('id', str(hash(str(doc))))
                if doc_id not in fused_scores:
                    fused_scores[doc_id] = 0
                    document_store[doc_id] = doc
                fused_scores[doc_id] += 1 / (rank + k)

        sorted_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        final_docs = []
        for doc_id, score in sorted_results:
            d = document_store[doc_id].copy()
            d['rrf_score'] = score
            final_docs.append(d)
        return final_docs

    @staticmethod
    def context_compression(context: str, query: str) -> str:
        """Simulates extracting only highly relevant sentences from chunks."""
        sentences = context.split('. ')
        # Mock logic: keeping sentences that contain words from query
        query_words = set(query.lower().split())
        compressed = [s for s in sentences if any(w in s.lower() for w in query_words)]
        if not compressed:
            return context[:200] + "..." # Fallback
        return ". ".join(compressed) + "."
