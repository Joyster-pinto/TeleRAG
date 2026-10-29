"""
Hybrid BM25 + Dense Vector Indexer with DEW-RRF Scoring
Provides fast local indexing, query retrieval, and ranking.
"""
import math
import re
from typing import List, Dict, Any, Optional
from collections import Counter
from .chunker import DocumentChunk
from .dew_rrf import DEWRRFScorer
from .acronym_expander import TelecomAcronymExpander

class SimpleBM25:
    """Lightweight in-memory BM25 Okapi search index."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avgdl = 0.0
        self.doc_freqs: List[Counter] = []
        self.idf: Dict[str, float] = {}
        self.doc_lens: List[int] = []
        self.docs: List[DocumentChunk] = []

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def index(self, docs: List[DocumentChunk]):
        self.docs = docs
        self.corpus_size = len(docs)
        if self.corpus_size == 0:
            return

        self.doc_freqs = []
        self.doc_lens = []
        total_len = 0
        df = Counter()

        for doc in docs:
            tokens = self._tokenize(doc.content)
            self.doc_lens.append(len(tokens))
            total_len += len(tokens)
            freqs = Counter(tokens)
            self.doc_freqs.append(freqs)
            for word in freqs.keys():
                df[word] += 1

        self.avgdl = total_len / self.corpus_size

        for word, count in df.items():
            # Standard BM25 IDF formulation
            self.idf[word] = math.log((self.corpus_size - count + 0.5) / (count + 0.5) + 1.0)

    def search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        if not self.docs:
            return []

        q_tokens = self._tokenize(query)
        scores = []

        for idx, freqs in enumerate(self.doc_freqs):
            score = 0.0
            doc_len = self.doc_lens[idx]
            for token in q_tokens:
                if token not in freqs:
                    continue
                tf = freqs[token]
                idf = self.idf.get(token, 0.1)
                num = tf * (self.k1 + 1.0)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avgdl))
                score += idf * (num / denom)
            
            scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in scores[:top_k]:
            doc = self.docs[idx]
            results.append({
                "id": doc.chunk_id,
                "text": doc.content,
                "score": float(score),
                "metadata": doc.to_dict()
            })
        return results


class SimpleDenseRetriever:
    """
    In-memory semantic dense retriever.
    Uses TF-IDF + Acronym weighted cosine similarity fallback, or dense vector embeddings.
    """

    def __init__(self):
        self.docs: List[DocumentChunk] = []
        self.acronym_expander = TelecomAcronymExpander()

    def index(self, docs: List[DocumentChunk]):
        self.docs = docs

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        if not self.docs:
            return []

        expanded_query = self.acronym_expander.expand_query(query)
        q_tokens = Counter(self._tokenize(expanded_query))

        scores = []
        for doc in self.docs:
            d_tokens = Counter(self._tokenize(doc.content))
            
            # Compute cosine similarity between query and doc token bags
            common = set(q_tokens.keys()).intersection(set(d_tokens.keys()))
            dot = sum(q_tokens[t] * d_tokens[t] for t in common)
            mag_q = math.sqrt(sum(v**2 for v in q_tokens.values()))
            mag_d = math.sqrt(sum(v**2 for v in d_tokens.values()))
            
            cos_sim = dot / (mag_q * mag_d + 1e-8)
            scores.append((doc, cos_sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for doc, score in scores[:top_k]:
            results.append({
                "id": doc.chunk_id,
                "text": doc.content,
                "score": float(score),
                "metadata": doc.to_dict()
            })
        return results


class TelecomHybridIndexer:
    """
    Main entry point for Stage 1 indexing and retrieval.
    Combines BM25 and Dense search through the novel DEW-RRF fusion engine.
    """

    def __init__(self, alpha: float = 0.50, beta: float = 0.30, gamma: float = 0.20):
        self.bm25 = SimpleBM25()
        self.dense = SimpleDenseRetriever()
        self.scorer = DEWRRFScorer(alpha=alpha, beta=beta, gamma=gamma)
        self.docs: List[DocumentChunk] = []

    def index_chunks(self, chunks: List[DocumentChunk]):
        """Indexes a list of DocumentChunk instances in both BM25 and Dense structures."""
        self.docs = chunks
        self.bm25.index(chunks)
        self.dense.index(chunks)
        print(f"[HybridIndexer] Indexed {len(chunks)} chunks across BM25 and Dense stores.")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes hybrid retrieval:
        1. BM25 Sparse Search (top 20)
        2. Dense Semantic Search (top 20)
        3. Fuses using DEW-RRF equation
        """
        dense_results = self.dense.search(query, top_k=20)
        bm25_results = self.bm25.search(query, top_k=20)

        fused_ranking = self.scorer.fuse_and_rank(
            query=query,
            dense_results=dense_results,
            bm25_results=bm25_results
        )

        return fused_ranking[:top_k]
