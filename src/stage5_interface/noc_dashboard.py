"""
Stage 5: Response Synthesis & Explainable User Interface
Implements the 6 sequential blocks of Stage 5 from the TeleRAG 2.0 Architecture Diagram:
1. Multi-Agent Consensus (Aggregates findings from all invoked agents)
2. Chain-of-Thought Reasoning Trace (Step-by-step reasoning with evidence references)
3. 3GPP Evidence & Citations (Clickable TS & clause references for verification)
4. Actionable Remediation (Root cause summary + recommended actions)
5. TeleMCP Standard Export (Structured output export: JSON/YAML)
6. Explainable NOC User Interface (Root Cause [What & Why], 3GPP Evidence, Recommended Actions [How], Verification Status & Confidence)
"""
import json
from src.stage4_verification.consensus import ConsensusSynthesisBundle


class ExplainableNOCInterface:
    """Renders Stage 5 Response Synthesis & Explainable NOC User Interface."""

    def render_diagnostic_report(self, bundle: ConsensusSynthesisBundle) -> str:
        lines = []
        lines.append("=" * 94)
        lines.append("  TeleRAG 2.0 — STAGE 5: RESPONSE SYNTHESIS & EXPLAINABLE NOC USER INTERFACE")
        lines.append("=" * 94)

        # Stage 2 & Stage 4->Stage 2 Feedback Summary
        lines.append(f"\n[STAGE 2 & 4 FLOW SUMMARY]")
        lines.append(f"  • Input Query / Log   : {bundle.dag_plan.original_input[:105]}")
        lines.append(f"  • Intent & DAG Layers : {bundle.dag_plan.intent_type} -> {', '.join(bundle.dag_plan.active_layers)}")
        lines.append(f"  • Feedback Re-routes  : {bundle.total_iterations} (Stage 4 -> Stage 2 -> Stage 3)")
        if bundle.feedback_history:
            for fb in bundle.feedback_history:
                lines.append(f"    ⟲ [Loop {fb['iteration']}] {fb['loop_path']}:")
                lines.append(f"      \"{fb['critique']}\"")

        # 1. Multi-Agent Consensus
        lines.append(f"\n[1] MULTI-AGENT CONSENSUS (Aggregated Findings from Stage 3 Domain Agents)")
        lines.append(f"  {bundle.executive_rca_summary}")

        # 2. Chain-of-Thought Reasoning Trace
        lines.append(f"\n[2] CHAIN-OF-THOUGHT REASONING TRACE (Step-by-Step Evidence Trace)")
        for idx, step in enumerate(bundle.combined_cot_trace, start=1):
            lines.append(f"  {idx:02d}. {step}")

        # 3. 3GPP Evidence & Citations
        ver = bundle.verification_report
        lines.append(
            f"\n[3] 3GPP EVIDENCE & CITATIONS (Faithfulness: {ver.citation_faithfulness_score*100:.1f}% | Verified={ver.is_verified})"
        )
        seen = set()
        for cit in ver.verified_clauses:
            key = (cit["doc_id"], cit["section_id"])
            if key in seen:
                continue
            seen.add(key)
            lines.append(
                f"  • [{cit['doc_id']} ({cit['release']}) §{cit['section_id']} — {cit['section_title']}] "
                f"| DEW-RRF Score: {cit['dew_rrf_score']:.4f} | Evidence E(q,d): {cit['evidence_match_score']:.2f}"
            )

        # 4. Actionable Remediation
        lines.append(
            f"\n[4] ACTIONABLE REMEDIATION (Root Cause Summary + Recommended SON Actions)"
        )
        if bundle.son_evaluation.son_remediation_plan:
            lines.append(
                "  " + json.dumps(bundle.son_evaluation.son_remediation_plan, indent=2).replace("\n", "\n  ")
            )

        # 5. TeleMCP Standard Export
        lines.append(f"\n[5] TELEMCP STANDARD EXPORT (Structured JSON/YAML Output)")
        export_preview = {
            "protocol_version": bundle.telemcp_export.get("protocol_version"),
            "verified_3gpp_compliant": bundle.telemcp_export.get("verified_3gpp_compliant"),
            "feedback_loops_executed": bundle.telemcp_export.get("feedback_loops_executed"),
            "confidence_scores": (
                ver.verified_package.confidence_scores if ver.verified_package else {}
            )
        }
        lines.append("  " + json.dumps(export_preview, indent=2).replace("\n", "\n  "))

        # 6. Explainable NOC User Interface Summary Panel
        lines.append(f"\n[6] EXPLAINABLE NOC USER INTERFACE PANEL")
        lines.append(f"  • Root Cause (What & Why)         : {bundle.agent_outputs[0].root_cause_diagnosis if bundle.agent_outputs else 'N/A'}")
        lines.append(f"  • 3GPP Evidence (Citations)       : {', '.join(f'{c[0]} §{c[1]}' for c in sorted(seen))}")
        lines.append(f"  • Recommended Actions (How)       : {bundle.son_evaluation.son_remediation_plan.get('validated_parameters', {})}")
        lines.append(
            f"  • Verification Status & Confidence: VERIFIED={ver.is_verified} | "
            f"Faithfulness={ver.citation_faithfulness_score*100:.1f}% | Bounds Compliance={ver.parameter_compliance_score*100:.1f}%"
        )
        lines.append("=" * 94)
        return "\n".join(lines)
