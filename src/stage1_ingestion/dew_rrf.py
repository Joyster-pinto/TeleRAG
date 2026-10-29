"""
Domain Evidence-Weighted Reciprocal Rank Fusion (DEW-RRF) Scoring Engine
Novel mathematical ranking function combining Score-Calibrated RRF, Cross-Encoder Deep Attention,
and 3GPP Technical Evidence Overlap E(q, d).
"""
from typing import List, Dict, Any, Optional
import numpy as np
from .acronym_expander import TelecomAcronymExpander

class DEWRRFScorer:
    """
    Computes the Domain Evidence-Weighted Reciprocal Rank Fusion (DEW-RRF) score:
    DEW-RRF(q, d) = α * [ (w_D * C_D(q, d)) / (k + r_D(d)) + (w_B * C_B(q, d)) / (k + r_B(d)) ] + β * C_CE(q, d) + γ * E(q, d)
    
    Subject to:
    α + β + γ = 1
    w_D + w_B = 1
    """

    def __init__(
        self,
        alpha: float = 0.50,
        beta: float = 0.30,
        gamma: float = 0.20,
        w_dense: float = 0.55,
        w_bm25: float = 0.45,
        k_constant: int = 60
    ):
        assert abs((alpha + beta + gamma) - 1.0) < 1e-4, "alpha + beta + gamma must equal 1.0"
        assert abs((w_dense + w_bm25) - 1.0) < 1e-4, "w_dense + w_bm25 must equal 1.0"
        
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.w_D = w_dense
        self.w_B = w_bm25
        self.k = k_constant
        self.acronym_expander = TelecomAcronymExpander()

    def _min_max_normalize(self, scores: List[float]) -> List[float]:
        """Normalizes raw scores to [0, 1] range."""
        if not scores:
            return []
        arr = np.array(scores, dtype=float)
        s_min, s_max = np.min(arr), np.max(arr)
        if s_max - s_min < 1e-8:
            return [1.0] * len(scores)
        norm = (arr - s_min) / (s_max - s_min)
        return norm.tolist()

    def fuse_and_rank(
        self,
        query: str,
        dense_results: List[Dict[str, Any]],  # List of {id, text, score, metadata}
        bm25_results: List[Dict[str, Any]],   # List of {id, text, score, metadata}
        cross_encoder_scores: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Merges dense and BM25 candidate results using the DEW-RRF formulation.
        Returns a sorted list of documents ranked by composite DEW-RRF score.
        """
        all_doc_ids = set()
        dense_map = {}
        bm25_map = {}

        # 1. Process Dense Results
        dense_raw_scores = [r["score"] for r in dense_results] if dense_results else []
        dense_norm_scores = self._min_max_normalize(dense_raw_scores)
        for rank, (r, n_score) in enumerate(zip(dense_results, dense_norm_scores), start=1):
            doc_id = r["id"]
            all_doc_ids.add(doc_id)
            dense_map[doc_id] = {
                "rank": rank,
                "score_raw": r["score"],
                "score_norm": n_score,
                "text": r.get("text", ""),
                "metadata": r.get("metadata", {})
            }

        # 2. Process BM25 Results
        bm25_raw_scores = [r["score"] for r in bm25_results] if bm25_results else []
        bm25_norm_scores = self._min_max_normalize(bm25_raw_scores)
        for rank, (r, n_score) in enumerate(zip(bm25_results, bm25_norm_scores), start=1):
            doc_id = r["id"]
            all_doc_ids.add(doc_id)
            bm25_map[doc_id] = {
                "rank": rank,
                "score_raw": r["score"],
                "score_norm": n_score,
                "text": r.get("text", ""),
                "metadata": r.get("metadata", {})
            }

        # 3. Calculate Cross-Encoder Normalized Scores
        ce_map = {}
        if cross_encoder_scores:
            ce_vals = list(cross_encoder_scores.values())
            ce_norm = self._min_max_normalize(ce_vals)
            for k, val in zip(cross_encoder_scores.keys(), ce_norm):
                ce_map[k] = val

        # 4. Compute DEW-RRF score for each unique candidate
        scored_candidates = []
        for doc_id in all_doc_ids:
            # Extract doc text and metadata
            doc_text = ""
            doc_meta = {}
            if doc_id in dense_map:
                doc_text = dense_map[doc_id]["text"]
                doc_meta = dense_map[doc_id]["metadata"]
            elif doc_id in bm25_map:
                doc_text = bm25_map[doc_id]["text"]
                doc_meta = bm25_map[doc_id]["metadata"]

            # Dense Term: (w_D * C_D) / (k + r_D)
            if doc_id in dense_map:
                r_D = dense_map[doc_id]["rank"]
                C_D = dense_map[doc_id]["score_norm"]
                dense_term = (self.w_D * C_D) / (self.k + r_D)
            else:
                r_D = 999
                C_D = 0.0
                dense_term = 0.0

            # BM25 Term: (w_B * C_B) / (k + r_B)
            if doc_id in bm25_map:
                r_B = bm25_map[doc_id]["rank"]
                C_B = bm25_map[doc_id]["score_norm"]
                bm25_term = (self.w_B * C_B) / (self.k + r_B)
            else:
                r_B = 999
                C_B = 0.0
                bm25_term = 0.0

            # Stage 1 Score-Weighted Term
            first_stage_score = self.alpha * (dense_term + bm25_term)

            # Cross-Encoder Term
            C_CE = ce_map.get(doc_id, 0.5)  # Default neutral score if not evaluated
            ce_term = self.beta * C_CE

            # Domain Evidence Match Term: E(q, d)
            E_qd = self.acronym_expander.get_evidence_overlap(query, doc_text, doc_meta)
            evidence_term = self.gamma * E_qd

            # Total DEW-RRF Composite Score
            dew_rrf_score = first_stage_score + ce_term + evidence_term

            scored_candidates.append({
                "id": doc_id,
                "text": doc_text,
                "metadata": doc_meta,
                "dew_rrf_score": float(dew_rrf_score),
                "dense_rank": r_D,
                "bm25_rank": r_B,
                "dense_norm_score": C_D,
                "bm25_norm_score": C_B,
                "cross_encoder_score": C_CE,
                "evidence_match_score": E_qd,
                "components": {
                    "first_stage_weighted_rrf": float(first_stage_score),
                    "cross_encoder_weighted": float(ce_term),
                    "evidence_weighted": float(evidence_term)
                }
            })

        # Sort descending by DEW-RRF score
        scored_candidates.sort(key=lambda x: x["dew_rrf_score"], reverse=True)
        return scored_candidates
