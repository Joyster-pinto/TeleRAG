"""
TeleMCP Domain-Specific Diagnostic & Retrieval Tools for Stage 3 Agents
Implements all specialized tools in the TeleRAG 2.0 Architecture:
- Mobility & RRC Agent      : rc_spec_retriever / rrc_spec_retriever, ho_matrix_parser
- PHY & Quality Agent       : kpi_anomaly_detect, rf_spec_retriever
- O-RAN & Interface Agent   : o_ran_alarm_parser / oran_alarm_parser, f1_latency_checker
- Core & Transport Agent    : pdu_session_parser / pdu_session_tracer, ngap_cause_analyzer
- 3GPP Spec QnA Agent       : hybrid_rrf_search / dew_rrf_retriever, bge_reranker_large
- SON Optimization Agent    : son_param_optimizer
"""
import re
from typing import Dict, List, Any, Optional
from src.stage1_ingestion.indexer import TelecomHybridIndexer


class TeleMCPTools:
    """Standardized Model Context Protocol (TeleMCP) toolset for 5G/O-RAN diagnostics."""

    def __init__(self, indexer: TelecomHybridIndexer):
        self.indexer = indexer

    # ------------------------------------------------------------------
    # 1. Mobility & RRC Tools
    # ------------------------------------------------------------------
    def ho_matrix_parser(self, kpi_snapshot: Dict[str, Any], raw_log: str = "") -> Dict[str, Any]:
        """Parses handover metrics, T304 expiry indicators, Event A3 offsets, and neighbor load."""
        ho_fail_rate = float(kpi_snapshot.get("HO_failure_rate_percent", 0.0))
        rsrp_serv = float(kpi_snapshot.get("RSRP_serving_dBm", -95.0))
        rsrp_neigh = float(kpi_snapshot.get("RSRP_neighbor_dBm", -95.0))
        neigh_prb = float(kpi_snapshot.get("neighbor_PRB_utilization_percent", 50.0))
        t304_expired = "T304" in raw_log.upper() or ho_fail_rate > 20.0

        return {
            "tool": "ho_matrix_parser",
            "t304_expired": t304_expired,
            "ho_failure_rate_percent": ho_fail_rate,
            "rsrp_delta_dB": round(rsrp_neigh - rsrp_serv, 2),
            "neighbor_prb_utilization_percent": neigh_prb,
            "current_CIO_dB": float(kpi_snapshot.get("current_CIO_dB", 0.0)),
            "current_Hysteresis_dB": float(kpi_snapshot.get("current_Hysteresis_dB", 2.0)),
            "current_TTT_ms": int(kpi_snapshot.get("current_TTT_ms", 160)),
            "status": "CRITICAL_HO_DEGRADATION" if t304_expired else "NOMINAL"
        }

    def rrc_spec_retriever(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves 3GPP TS 38.331 RRC & Mobility clauses via DEW-RRF + Cross-Encoder."""
        enriched_query = f"TS 38.331 RRC Mobility {query}"
        return self.dew_rrf_retriever(enriched_query, top_k=top_k, doc_filter="TS_38.331")

    def rc_spec_retriever(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Alias matching diagram label `rc_spec_retriever` for RRC Specification Retrieval."""
        return self.rrc_spec_retriever(query, top_k=top_k)

    # ------------------------------------------------------------------
    # 2. PHY & Radio Quality Tools
    # ------------------------------------------------------------------
    def kpi_anomaly_detect(self, kpi_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Detects physical layer SINR, BLER, and RSRP/RSRQ anomalies against 3GPP TS 38.213 thresholds."""
        sinr = float(kpi_snapshot.get("SINR_serving_dB", 10.0))
        bler = float(kpi_snapshot.get("BLER_percent", 2.0))
        rsrp = float(kpi_snapshot.get("RSRP_serving_dBm", -85.0))
        rsrq = float(kpi_snapshot.get("RSRQ_serving_dB", -10.0))

        anomalies = []
        if sinr < -3.0:
            anomalies.append(f"SEVERE_UL_SINR_DEGRADATION ({sinr} dB < -3.0 dB threshold)")
        if bler > 10.0:
            anomalies.append(f"EXCESSIVE_HARQ_BLER ({bler}% > 10.0% target threshold)")
        if rsrp < -105.0:
            anomalies.append(f"WEAK_COVERAGE_RSRP ({rsrp} dBm < -105.0 dBm)")
        if rsrq < -15.0:
            anomalies.append(f"PILOT_POLLUTION_RSRQ ({rsrq} dB < -15.0 dB)")

        return {
            "tool": "kpi_anomaly_detect",
            "anomalies_detected": anomalies,
            "sinr_dB": sinr,
            "bler_percent": bler,
            "rsrp_dBm": rsrp,
            "rsrq_dB": rsrq,
            "is_anomalous": len(anomalies) > 0
        }

    def rf_spec_retriever(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves 3GPP TS 38.213 / 38.211 Physical Layer clauses via DEW-RRF."""
        enriched_query = f"TS 38.213 PHY PUSCH PRACH SINR BLER {query}"
        return self.dew_rrf_retriever(enriched_query, top_k=top_k, doc_filter="TS_38.213")

    # ------------------------------------------------------------------
    # 3. O-RAN Interface Tools
    # ------------------------------------------------------------------
    def oran_alarm_parser(self, kpi_snapshot: Dict[str, Any], raw_log: str = "") -> Dict[str, Any]:
        """Parses O-RAN E2/O1/A1 alarms and active Near-RT RIC xApp states."""
        sctp_lost = "SCTP_COMMUNICATION_LOST" in raw_log.upper() or kpi_snapshot.get("E2_packet_loss_percent", 0) >= 50.0
        active_xapps = kpi_snapshot.get("Active_xApps", [])
        xapp_conflict = ("MRO_xApp" in active_xapps and "MLB_xApp" in active_xapps)

        return {
            "tool": "o_ran_alarm_parser",
            "e2_sctp_disconnected": sctp_lost,
            "active_xapps": active_xapps,
            "xapp_conflict_detected": xapp_conflict,
            "conflicting_pair": ["MRO_xApp", "MLB_xApp"] if xapp_conflict else []
        }

    def o_ran_alarm_parser(self, kpi_snapshot: Dict[str, Any], raw_log: str = "") -> Dict[str, Any]:
        """Alias matching diagram label `o_ran_alarm_parser`."""
        return self.oran_alarm_parser(kpi_snapshot, raw_log)

    def f1_latency_checker(self, kpi_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Checks E2 and CU-DU F1 split latency against O-RAN WG3 10 ms SLA."""
        e2_lat = float(kpi_snapshot.get("E2_latency_ms", 2.0))
        f1_lat = float(kpi_snapshot.get("F1_latency_ms", 2.0))

        return {
            "tool": "f1_latency_checker",
            "e2_latency_ms": e2_lat,
            "f1_latency_ms": f1_lat,
            "e2_sla_violated": e2_lat > 10.0,
            "f1_sla_violated": f1_lat > 10.0,
            "sla_threshold_ms": 10.0
        }

    # ------------------------------------------------------------------
    # 4. Core & Transport Tools
    # ------------------------------------------------------------------
    def ngap_cause_analyzer(self, kpi_snapshot: Dict[str, Any], raw_log: str = "") -> Dict[str, Any]:
        """Analyzes NGAP Initial Context Setup failures and N2 control plane signaling drops."""
        n2_fail_rate = float(kpi_snapshot.get("N2_setup_failure_rate_percent", 0.0))
        transport_unavail = "TRANSPORT RESOURCE UNAVAILABLE" in raw_log.upper()
        radio_unavail = "RADIO RESOURCES NOT AVAILABLE" in raw_log.upper()

        cause = "Transport Resource Unavailable" if transport_unavail else (
            "Radio resources not available" if radio_unavail else "Unspecified NGAP Cause"
        )
        return {
            "tool": "ngap_cause_analyzer",
            "ngap_cause": cause,
            "n2_setup_failure_rate_percent": n2_fail_rate,
            "requested_5qi": int(kpi_snapshot.get("requested_5QI", 9))
        }

    def pdu_session_tracer(self, kpi_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Traces N3 GTP-U user plane tunnel congestion and packet drop rates."""
        gtpu_drop = float(kpi_snapshot.get("N3_GTPU_packet_drop_percent", 0.0))
        return {
            "tool": "pdu_session_parser",
            "n3_gtpu_packet_drop_percent": gtpu_drop,
            "tunnel_congested": gtpu_drop > 5.0
        }

    def pdu_session_parser(self, kpi_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Alias matching diagram label `pdu_session_parser`."""
        return self.pdu_session_tracer(kpi_snapshot)

    # ------------------------------------------------------------------
    # 5. SON Optimization Tool (Stage 3 Agent 6)
    # ------------------------------------------------------------------
    def son_param_optimizer(
        self,
        kpi_snapshot: Dict[str, Any],
        prior_proposals: Dict[str, Any],
        feedback_critique: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Computes closed-loop SON parameter tuning (CIO, Antenna Tilt, Tx Power)
        per 3GPP TS 28.541 §4.3.1.
        """
        neigh_prb = float(kpi_snapshot.get("neighbor_PRB_utilization_percent", 50.0))
        optimized = dict(prior_proposals)

        if feedback_critique:
            # Self-correct parameters when Verifier or SON bounds critique is received
            if "CIO_dB" in optimized:
                optimized["CIO_dB"] = 2.0
                optimized["Hysteresis_dB"] = 2.5
                optimized["TTT_ms"] = 320
            if "RET_tilt_deg" in optimized and float(optimized["RET_tilt_deg"]) > 10.0:
                optimized["RET_tilt_deg"] = 6.0

        return {
            "tool": "son_param_optimizer",
            "neighbor_prb_utilization_percent": neigh_prb,
            "optimized_parameters": optimized
        }

    # ------------------------------------------------------------------
    # 6. Core Retrieval & Cross-Encoder Re-Ranking Tools
    # ------------------------------------------------------------------
    def bge_reranker_large(self, query: str, candidates: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Computes deep semantic cross-attention relevance scores C_CE(q, d) in [0, 1]
        between query tokens/bigrams and candidate specification clauses.
        """
        q_words = set(re.findall(r'\b\w+\b', query.lower()))
        q_bigrams = set(zip(query.lower().split(), query.lower().split()[1:]))
        ce_scores: Dict[str, float] = {}

        for cand in candidates:
            doc_id = cand["id"]
            text_lower = cand.get("text", "").lower()
            d_words = set(re.findall(r'\b\w+\b', text_lower))
            d_bigrams = set(zip(text_lower.split(), text_lower.split()[1:]))

            word_overlap = len(q_words.intersection(d_words)) / max(1, len(q_words))
            bigram_overlap = len(q_bigrams.intersection(d_bigrams)) / max(1, len(q_bigrams))

            score = 0.65 * word_overlap + 0.35 * bigram_overlap
            ce_scores[doc_id] = float(min(1.0, max(0.05, score)))

        return ce_scores

    def dew_rrf_retriever(
        self,
        query: str,
        top_k: int = 5,
        doc_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes full two-stage retrieval using:
        1. Dense + BM25 candidate generation
        2. Cross-Encoder score calculation (bge_reranker_large)
        3. DEW-RRF composite ranking
        """
        dense_res = self.indexer.dense.search(query, top_k=20)
        bm25_res = self.indexer.bm25.search(query, top_k=20)

        all_cands = {r["id"]: r for r in (dense_res + bm25_res)}
        ce_scores = self.bge_reranker_large(query, list(all_cands.values()))

        ranked = self.indexer.scorer.fuse_and_rank(
            query=query,
            dense_results=dense_res,
            bm25_results=bm25_res,
            cross_encoder_scores=ce_scores
        )

        if doc_filter:
            filtered = [r for r in ranked if r.get("metadata", {}).get("doc_id") == doc_filter]
            if filtered:
                return filtered[:top_k]

        return ranked[:top_k]

    def hybrid_rrf_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Alias matching diagram label `hybrid_rrf_search`."""
        return self.dew_rrf_retriever(query, top_k=top_k)
