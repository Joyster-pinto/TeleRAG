"""
Stage 5: Target KPI & Ablation Study Benchmark Evaluator
Evaluates:
1. Mean Reciprocal Rank (MRR >= 78%)
2. Top-5 Clause Recall (>= 88%)
3. TeleQnA Multiple-Choice Accuracy (>= 82%)
4. Citation Faithfulness & Parameter Bounds Compliance (>= 92%)
5. Ablation Study: Standard RRF vs. DEW-RRF
"""
from typing import Dict, List, Any


class TeleRAGBenchmarkEvaluator:
    """Computes quantitative retrieval, QnA, and closed-loop verification metrics."""

    def __init__(self, pipeline):
        self.pipeline = pipeline

    def evaluate_all_kpis(self) -> Dict[str, Any]:
        teleqna_items = self.pipeline.data_loader.load_teleqna_dataset()
        alarms = self.pipeline.data_loader.load_telemetry_alarms()

        # 1. Evaluate Retrieval (MRR & Top-5 Recall) and TeleQnA Accuracy
        reciprocal_ranks_dew = []
        reciprocal_ranks_std = []
        top5_hits_dew = 0
        correct_mcq = 0

        raw_teleqna_path = self.pipeline.data_loader.fetcher.raw_teleqna_dir + "/teleqna_benchmark.json"
        import json
        with open(raw_teleqna_path, "r", encoding="utf-8") as f:
            raw_qna = json.load(f)

        for raw_item, q_item in zip(raw_qna, teleqna_items):
            target_doc = raw_item.get("target_doc_id")
            target_sec = raw_item.get("target_section_id")

            # DEW-RRF Retrieval
            ranked_dew = self.pipeline.tools.dew_rrf_retriever(q_item.question, top_k=5)
            rank_pos = 0
            for idx, r in enumerate(ranked_dew, start=1):
                meta = r.get("metadata", {})
                if meta.get("doc_id") == target_doc and meta.get("section_id") == target_sec:
                    rank_pos = idx
                    break

            if rank_pos > 0:
                reciprocal_ranks_dew.append(1.0 / rank_pos)
                top5_hits_dew += 1
            else:
                reciprocal_ranks_dew.append(0.0)

            # Standard RRF (Ablation Baseline: pure rank 1/(60+r) without score weighting or E(q,d))
            dense_res = self.pipeline.indexer.dense.search(q_item.question, top_k=20)
            bm25_res = self.pipeline.indexer.bm25.search(q_item.question, top_k=20)
            std_scores: Dict[str, float] = {}
            meta_map: Dict[str, Dict[str, Any]] = {}
            for r_idx, r in enumerate(dense_res, start=1):
                std_scores[r["id"]] = std_scores.get(r["id"], 0.0) + (1.0 / (60.0 + r_idx))
                meta_map[r["id"]] = r.get("metadata", {})
            for r_idx, r in enumerate(bm25_res, start=1):
                std_scores[r["id"]] = std_scores.get(r["id"], 0.0) + (1.0 / (60.0 + r_idx))
                meta_map[r["id"]] = r.get("metadata", {})

            std_sorted = sorted(std_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            std_rank_pos = 0
            for idx, (cid, _) in enumerate(std_sorted, start=1):
                m = meta_map.get(cid, {})
                if m.get("doc_id") == target_doc and m.get("section_id") == target_sec:
                    std_rank_pos = idx
                    break
            reciprocal_ranks_std.append((1.0 / std_rank_pos) if std_rank_pos > 0 else 0.0)

            # TeleQnA MCQ End-to-End Pipeline Execution
            bundle = self.pipeline.run_teleqna_item(q_item)
            pred_opt = bundle.agent_outputs[0].selected_mcq_option if bundle.agent_outputs else None
            if pred_opt == q_item.correct_answer:
                correct_mcq += 1

        # 2. Evaluate Incident Triage, Multi-Tier Self-Correction & Citation Faithfulness
        faithfulness_scores = []
        compliance_scores = []
        self_correction_count = 0

        for alarm in alarms:
            bundle = self.pipeline.run_incident_triage(alarm)
            faithfulness_scores.append(bundle.verification_report.citation_faithfulness_score)
            compliance_scores.append(bundle.verification_report.parameter_compliance_score)
            if bundle.total_iterations > 0:
                self_correction_count += 1

        n_q = max(1, len(teleqna_items))
        mrr_dew = sum(reciprocal_ranks_dew) / n_q
        mrr_std = sum(reciprocal_ranks_std) / n_q
        recall_top5 = top5_hits_dew / n_q
        teleqna_acc = correct_mcq / n_q
        avg_faithfulness = sum(faithfulness_scores) / max(1, len(faithfulness_scores))
        avg_compliance = sum(compliance_scores) / max(1, len(compliance_scores))

        return {
            "MRR_DEW_RRF_percent": round(mrr_dew * 100, 2),
            "MRR_Standard_RRF_percent": round(mrr_std * 100, 2),
            "Top5_Recall_percent": round(recall_top5 * 100, 2),
            "TeleQnA_Accuracy_percent": round(teleqna_acc * 100, 2),
            "Citation_Faithfulness_percent": round(avg_faithfulness * 100, 2),
            "SON_Parameter_Compliance_percent": round(avg_compliance * 100, 2),
            "Self_Correction_Interceptions": self_correction_count,
            "targets_met": {
                "MRR >= 78%": mrr_dew >= 0.78,
                "Top5_Recall >= 88%": recall_top5 >= 0.88,
                "TeleQnA_Accuracy >= 82%": teleqna_acc >= 0.82,
                "Faithfulness >= 92%": avg_faithfulness >= 0.92
            }
        }
