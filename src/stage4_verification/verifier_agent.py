"""
Stage 4: ★ 3GPP Citation & Guardrail Verifier (Proposed Novelty)
Implements the exact 3 sequential blocks in the TeleRAG 2.0 Architecture Diagram:
1. CITATION GROUNDING CHECK:
   Verifies that cited 3GPP TS, section & clause actually exist in the indexed document tree.
   Prevents hallucinated citations.
2. PARAMETER BOUNDS ENFORCER:
   Checks SON/optimization parameters against 3GPP/O-RAN standardized valid ranges & operator policies.
   Prevents unsafe actions.
3. VERIFIED & TRUSTED RESPONSE PACKAGE:
   Outputs Validated Citations, Verified Parameters, and Confidence Scores.
   If any check fails, triggers the Stage 4 -> Stage 2 Feedback Loop (Verifier Feedback / Re-routing for Re-evaluation).
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple
from src.stage1_ingestion.chunker import DocumentChunk
from src.stage3_specialists.agents import AgentDiagnosisOutput


@dataclass
class VerifiedResponsePackage:
    """Block 3 of Stage 4: Verified & Trusted Response Package."""
    validated_citations: List[Dict[str, Any]]
    verified_parameters: Dict[str, Any]
    confidence_scores: Dict[str, float]


@dataclass
class VerificationReport:
    """Output of Stage 4 (3GPP Citation & Guardrail Verifier)."""
    is_verified: bool
    citation_faithfulness_score: float
    parameter_compliance_score: float
    verified_clauses: List[Dict[str, Any]]
    verified_package: Optional[VerifiedResponsePackage] = None
    violations: List[str] = field(default_factory=list)
    violation_critique: Optional[str] = None
    target_agent_type: Optional[str] = None
    verifier_trace: List[str] = field(default_factory=list)


class GuardrailVerifierAgent:
    """
    Stage 4: 3GPP Citation & Guardrail Verifier (Proposed Novelty).
    Enforces:
    1. Citation Grounding Check
    2. Parameter Bounds Enforcer (3GPP valid ranges + Operator ANR/MLB policies)
    3. Verified & Trusted Response Package generation (or Stage 4 -> Stage 2 Feedback Loop)
    """

    VALID_TTT_MS = {0, 40, 64, 80, 100, 128, 160, 256, 320, 480, 512, 640, 1024, 1280, 2560, 5120}
    VALID_T304_MS = {50, 100, 150, 200, 500, 1000, 2000, 10000}
    VALID_ALPHA = {0.0, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}

    def __init__(self, indexed_chunks: List[DocumentChunk]):
        self.document_tree: Set[Tuple[str, str]] = set()
        self.spec_to_doc_id: Dict[str, str] = {}

        for ch in indexed_chunks:
            self.document_tree.add((ch.doc_id, ch.section_id))
            self.spec_to_doc_id[ch.spec_number] = ch.doc_id

    # ------------------------------------------------------------------
    # Block 1: Citation Grounding Check
    # ------------------------------------------------------------------
    def citation_grounding_check(
        self,
        agent_outputs: List[AgentDiagnosisOutput]
    ) -> Tuple[List[Dict[str, Any]], List[str], float, Optional[str]]:
        verified_clauses: List[Dict[str, Any]] = []
        violations: List[str] = []
        violating_agent: Optional[str] = None
        total_citations = 0
        valid_citations = 0

        for out in agent_outputs:
            for cit in out.cited_clauses:
                total_citations += 1
                doc_id = cit.get("doc_id", "")
                sec_id = cit.get("section_id", "")

                if (doc_id, sec_id) in self.document_tree:
                    valid_citations += 1
                    verified_clauses.append(cit)
                else:
                    violating_agent = out.agent_type
                    violations.append(
                        f"CITATION_HALLUCINATION: Clause '{doc_id} §{sec_id}' cited by {out.agent_name} does not exist in the indexed 3GPP/O-RAN Document Tree."
                    )

        faithfulness = (valid_citations / total_citations) if total_citations > 0 else 1.0
        return verified_clauses, violations, faithfulness, violating_agent

    # ------------------------------------------------------------------
    # Block 2: Parameter Bounds Enforcer
    # ------------------------------------------------------------------
    def parameter_bounds_enforcer(
        self,
        agent_outputs: List[AgentDiagnosisOutput],
        incident_payload: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], List[str], float, Optional[str]]:
        kpi = (incident_payload or {}).get("kpi_snapshot", {})
        neigh_prb = float(kpi.get("neighbor_PRB_utilization_percent", 50.0))
        neighbor_id = (incident_payload or {}).get("neighbor_cell_id", "gNB_Neighbor_02")

        violations: List[str] = []
        violating_agent: Optional[str] = None
        verified_params: Dict[str, Any] = {}
        total_params = 0
        valid_params = 0

        for out in agent_outputs:
            params = out.proposed_parameters
            for p_name, p_val in params.items():
                total_params += 1
                is_param_ok = True

                if p_name == "CIO_dB":
                    val = float(p_val)
                    hys = float(params.get("Hysteresis_dB", 2.0))
                    ttt = int(params.get("TTT_ms", 160))

                    if not (-24.0 <= val <= 24.0):
                        is_param_ok = False
                        violations.append(
                            f"PARAMETER_OUT_OF_BOUNDS: CIO_dB={val} dB violates 3GPP TS 38.331 §5.5.4.4 legal range [-24.0 dB, +24.0 dB]."
                        )
                    elif abs((val * 2.0) - round(val * 2.0)) > 1e-4:
                        is_param_ok = False
                        violations.append(
                            f"INVALID_STEP_SIZE: CIO_dB={val} dB violates 3GPP TS 38.331 §5.5.4.4 discrete step size of 0.5 dB."
                        )
                    elif neigh_prb > 85.0 and val > 2.0:
                        is_param_ok = False
                        violations.append(
                            f"OPERATOR_POLICY_MLB_VIOLATION: Target neighbor cell {neighbor_id} PRB utilization is {neigh_prb}% (> 85% limit in 3GPP TS 28.541 §4.3.1), so CIO={val:+.1f} dB will cause neighbor congestion collapse and Event A3 Ping-Pong handovers (Hys={hys} dB, TTT={ttt} ms)."
                        )

                elif p_name == "Hysteresis_dB":
                    val = float(p_val)
                    if not (0.0 <= val <= 15.0) or abs((val * 2.0) - round(val * 2.0)) > 1e-4:
                        is_param_ok = False
                        violations.append(
                            f"PARAMETER_OUT_OF_BOUNDS: Hysteresis_dB={val} dB violates TS 38.331 §5.5.4.4 range [0, 15 dB] (step 0.5 dB)."
                        )

                elif p_name == "TTT_ms":
                    if int(p_val) not in self.VALID_TTT_MS:
                        is_param_ok = False
                        violations.append(
                            f"INVALID_ENUM_VALUE: TTT_ms={p_val} ms is not a valid 3GPP TS 38.331 TimeToTrigger value."
                        )

                elif p_name == "T304_ms":
                    if int(p_val) not in self.VALID_T304_MS:
                        is_param_ok = False
                        violations.append(
                            f"INVALID_ENUM_VALUE: T304_ms={p_val} ms is not a valid 3GPP TS 38.331 §5.3.5.3 Timer T304 value."
                        )

                elif p_name == "RET_tilt_deg":
                    val = float(p_val)
                    if not (0.0 <= val <= 10.0):
                        is_param_ok = False
                        violations.append(
                            f"PARAMETER_OUT_OF_BOUNDS: RET_tilt_deg={val} deg exceeds 3GPP TS 28.541 §4.3.1 maximum downtilt limit of 10.0 deg."
                        )

                elif p_name == "P0_PUSCH_dBm":
                    val = float(p_val)
                    if not (-202.0 <= val <= 24.0):
                        is_param_ok = False
                        violations.append(
                            f"PARAMETER_OUT_OF_BOUNDS: P0_PUSCH_dBm={val} dBm violates 3GPP TS 38.213 §7.1 range [-202, +24 dBm]."
                        )

                elif p_name == "PUSCH_alpha":
                    if float(p_val) not in self.VALID_ALPHA:
                        is_param_ok = False
                        violations.append(
                            f"INVALID_ENUM_VALUE: PUSCH_alpha={p_val} is not in TS 38.213 §7.1 allowed set {sorted(list(self.VALID_ALPHA))}."
                        )

                if is_param_ok:
                    valid_params += 1
                    verified_params[p_name] = p_val
                else:
                    violating_agent = out.agent_type if out.agent_type != "SON_OPTIMIZATION" else "MOBILITY_RRC"

        compliance = (valid_params / total_params) if total_params > 0 else 1.0
        return verified_params, violations, compliance, violating_agent

    # ------------------------------------------------------------------
    # Full Stage 4 Verification & Trusted Package Builder
    # ------------------------------------------------------------------
    def verify_outputs(
        self,
        agent_outputs: List[AgentDiagnosisOutput],
        incident_payload: Optional[Dict[str, Any]] = None
    ) -> VerificationReport:
        verified_clauses, cit_violations, faithfulness, cit_agent = self.citation_grounding_check(agent_outputs)
        verified_params, param_violations, param_compliance, param_agent = self.parameter_bounds_enforcer(
            agent_outputs, incident_payload=incident_payload
        )

        all_violations = cit_violations + param_violations
        violating_agent = cit_agent or param_agent
        is_verified = (len(all_violations) == 0)
        trace: List[str] = []

        if is_verified:
            avg_dew_score = (
                sum(float(c.get("dew_rrf_score", 0.0)) for c in verified_clauses) / max(1, len(verified_clauses))
            )
            package = VerifiedResponsePackage(
                validated_citations=verified_clauses,
                verified_parameters=verified_params,
                confidence_scores={
                    "citation_faithfulness": round(faithfulness, 4),
                    "parameter_compliance": round(param_compliance, 4),
                    "mean_dew_rrf_confidence": round(avg_dew_score, 4)
                }
            )
            trace.append(
                f"[Stage 4: 3GPP Citation & Guardrail Verifier] PASSED Block 1 (Citation Grounding: {faithfulness*100:.1f}%) & Block 2 (Parameter Bounds Enforcer: {param_compliance*100:.1f}%) -> Built Verified & Trusted Response Package."
            )
            critique = None
        else:
            package = None
            critique = (
                f"[STAGE 4 -> STAGE 2 FEEDBACK LOOP (Verifier Re-routing to {violating_agent or 'MOBILITY_RRC'})] "
                + " | ".join(all_violations)
                + " Re-evaluate using bounded CIO <= +2.0 dB (0.5 dB step), Hysteresis >= 2.0 dB, TTT >= 256 ms, and verified 3GPP clauses."
            )
            trace.append(critique)

        return VerificationReport(
            is_verified=is_verified,
            citation_faithfulness_score=faithfulness,
            parameter_compliance_score=param_compliance,
            verified_clauses=verified_clauses,
            verified_package=package,
            violations=all_violations,
            violation_critique=critique,
            target_agent_type=violating_agent,
            verifier_trace=trace
        )
