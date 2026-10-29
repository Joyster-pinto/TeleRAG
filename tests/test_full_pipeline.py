"""
Comprehensive End-to-End Test Suite for Stages 1 through 5 of TeleRAG 2.0
Tests the exact flow from the TeleRAG 2.0 Architecture Diagram:
- Stage 1: Knowledge Ingestion, Metadata Enrichment & Hybrid DEW-RRF + BGE Reranker Retrieval
- Stage 2: Supervisor / Dispatcher Agent (Acronym Normalizer -> Intent & Layer Classifier -> DAG Delegator -> Agent Router)
- Stage 3: All 6 Specialized Domain Agents (Mobility/RRC, PHY/Quality, O-RAN, Core/Transport, Spec QnA, SON Optimization)
- Stage 4: 3GPP Citation & Guardrail Verifier (1. Citation Grounding Check -> 2. Parameter Bounds Enforcer -> 3. Verified Package + Stage 4 -> Stage 2 Feedback Loop)
- Stage 5: Response Synthesis & Explainable NOC User Interface (Multi-Agent Consensus -> CoT Trace -> 3GPP Evidence -> Actionable Remediation -> TeleMCP Export -> Explainable UI)
"""
import unittest
from src.pipeline import TeleRAG2Pipeline
from src.stage3_specialists.agents import AgentDiagnosisOutput


class TestTeleRAG2FullPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pipeline = TeleRAG2Pipeline()

    def test_stage2_supervisor_dag_decomposition_and_6_agents(self):
        # 1. Spec QnA Intent
        plan_qna = self.pipeline.supervisor.classify_and_decompose(
            "What is the valid range of CIO in TS 38.331 Event A3?",
            is_mcq=True
        )
        self.assertEqual(plan_qna.intent_type, "SPEC_QNA")
        self.assertIn("SPEC_QNA", plan_qna.active_layers)
        self.assertFalse(plan_qna.requires_son_optimization)

        # 2. Multi-Layer Cascade Incident Intent (includes SON_OPTIMIZATION as 6th Stage 3 Agent)
        plan_multi = self.pipeline.supervisor.classify_and_decompose(
            "Alarm: Handover failure T304 expiry on RRC with severe PUSCH uplink SINR degradation and E2 SCTP disconnect."
        )
        self.assertEqual(plan_multi.intent_type, "MULTI_LAYER_INCIDENT")
        self.assertIn("MOBILITY_RRC", plan_multi.active_layers)
        self.assertIn("PHY_QUALITY", plan_multi.active_layers)
        self.assertIn("ORAN_INTERFACE", plan_multi.active_layers)
        self.assertIn("SON_OPTIMIZATION", plan_multi.active_layers)
        self.assertTrue(plan_multi.requires_son_optimization)

    def test_stage3_all_6_specialist_agents(self):
        alarms = self.pipeline.data_loader.load_telemetry_alarms()
        for alarm in alarms:
            bundle = self.pipeline.run_incident_triage(alarm)
            self.assertTrue(len(bundle.agent_outputs) >= 2)  # Domain Agent + SON Optimization Agent
            self.assertTrue(bundle.verification_report.is_verified)
            self.assertIsNotNone(bundle.verification_report.verified_package)

    def test_stage4_to_stage2_feedback_loop_rerouting(self):
        # Incident 1 has neighbor_PRB_utilization_percent = 91.5% (>85%), triggering Stage 4 -> Stage 2 -> Stage 3 Feedback Loop
        alarms = self.pipeline.data_loader.load_telemetry_alarms()
        handover_alarm = alarms[0]
        bundle = self.pipeline.run_incident_triage(handover_alarm)

        # Verify Stage 4 -> Stage 2 feedback loop executed and re-routed through Supervisor Agent
        self.assertGreaterEqual(bundle.total_iterations, 1)
        self.assertTrue(bundle.dag_plan.rerouted_from_verifier)
        self.assertEqual(bundle.feedback_history[0]["tier"], "STAGE_4_TO_STAGE_2_VERIFIER_FEEDBACK")
        final_params = bundle.verification_report.verified_package.verified_parameters
        self.assertLessEqual(final_params["CIO_dB"], 2.0)
        self.assertGreaterEqual(final_params["TTT_ms"], 256)

    def test_stage4_citation_and_parameter_guardrail_rejection(self):
        # Simulate a hallucinated 3GPP section and out-of-bounds CIO parameter (+28.3 dB)
        bad_output = AgentDiagnosisOutput(
            agent_type="MOBILITY_RRC",
            agent_name="Mobility & RRC Agent",
            root_cause_diagnosis="Test invalid output",
            chain_of_thought=["Step 1"],
            cited_clauses=[{
                "doc_id": "TS_38.331",
                "spec_number": "38.331",
                "release": "Rel-17",
                "section_id": "99.99.99",  # Nonexistent clause
                "section_title": "Hallucinated Clause",
                "dew_rrf_score": 0.5,
                "evidence_match_score": 0.0,
                "snippet": "Fake snippet"
            }],
            proposed_parameters={
                "CIO_dB": 28.3,          # Violates [-24, +24] and 0.5 dB step
                "RET_tilt_deg": 15.0     # Violates <= 10.0 deg
            }
        )
        report = self.pipeline.verifier_agent.verify_outputs([bad_output])
        self.assertFalse(report.is_verified)
        self.assertIsNone(report.verified_package)
        self.assertEqual(report.citation_faithfulness_score, 0.0)
        self.assertEqual(report.parameter_compliance_score, 0.0)
        self.assertTrue(any("CITATION_HALLUCINATION" in v for v in report.violations))
        self.assertTrue(any("PARAMETER_OUT_OF_BOUNDS" in v for v in report.violations))

    def test_stage5_response_synthesis_and_noc_interface(self):
        alarms = self.pipeline.data_loader.load_telemetry_alarms()
        bundle = self.pipeline.run_incident_triage(alarms[0])
        report_text = self.pipeline.noc_interface.render_diagnostic_report(bundle)
        self.assertIn("MULTI-AGENT CONSENSUS", report_text)
        self.assertIn("CHAIN-OF-THOUGHT REASONING TRACE", report_text)
        self.assertIn("3GPP EVIDENCE & CITATIONS", report_text)
        self.assertIn("ACTIONABLE REMEDIATION", report_text)
        self.assertIn("TELEMCP STANDARD EXPORT", report_text)
        self.assertIn("EXPLAINABLE NOC USER INTERFACE PANEL", report_text)

        metrics = self.pipeline.evaluator.evaluate_all_kpis()
        self.assertTrue(all(metrics["targets_met"].values()))


if __name__ == "__main__":
    unittest.main()
