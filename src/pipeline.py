"""
TeleRAG 2.0: End-to-End 5-Stage Multi-Agent Pipeline
Unifies:
- Stage 1: Multi-Modal Ingestion & DEW-RRF Hybrid Protocol Indexing
- Stage 2: Supervisor / Dispatcher Agent (Acronym Normalizer & DAG Task Decomposer)
- Stage 3: 5 Domain-Specialized Anomaly & Specification Agents + TeleMCP Tools
- Stage 4: Consensus, SON Optimization Agent & ★ 3GPP Citation/Guardrail Verifier (with Tier-1 & Tier-2 Loops)
- Stage 5: Explainable NOC Interface & Target KPI Benchmark Evaluator
"""
import os
import sys
import json
from typing import Dict, Any, Optional

try:
    from .data_loader import TeleRAGDataLoader, RANAlarmLog, TeleQnAItem
    from .stage1_ingestion.chunker import DocumentChunk
    from .stage2_supervisor.supervisor import SupervisorAgent
    from .stage3_specialists.tools import TeleMCPTools
    from .stage3_specialists.agents import Stage3SpecialistPool
    from .stage4_verification.son_optimizer import SONOptimizationAgent
    from .stage4_verification.verifier_agent import GuardrailVerifierAgent
    from .stage4_verification.consensus import MultiTierReflectionEngine, ConsensusSynthesisBundle
    from .stage5_interface.noc_dashboard import ExplainableNOCInterface
    from .stage5_interface.evaluator import TeleRAGBenchmarkEvaluator
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.data_loader import TeleRAGDataLoader, RANAlarmLog, TeleQnAItem
    from src.stage1_ingestion.chunker import DocumentChunk
    from src.stage2_supervisor.supervisor import SupervisorAgent
    from src.stage3_specialists.tools import TeleMCPTools
    from src.stage3_specialists.agents import Stage3SpecialistPool
    from src.stage4_verification.son_optimizer import SONOptimizationAgent
    from src.stage4_verification.verifier_agent import GuardrailVerifierAgent
    from src.stage4_verification.consensus import MultiTierReflectionEngine, ConsensusSynthesisBundle
    from src.stage5_interface.noc_dashboard import ExplainableNOCInterface
    from src.stage5_interface.evaluator import TeleRAGBenchmarkEvaluator


class TeleRAG2Pipeline:
    """Master orchestrator for the 5-stage TeleRAG 2.0 architecture."""

    def __init__(self, data_dir: Optional[str] = None):
        # Stage 1: Data Loader & Hybrid DEW-RRF Indexer
        self.data_loader = TeleRAGDataLoader(data_dir=data_dir)
        self.stage1_summary = self.data_loader.initialize_stage1_pipeline()
        self.indexer = self.data_loader.indexer

        # Stage 2: Supervisor / Dispatcher Agent
        self.supervisor = SupervisorAgent()

        # Stage 3: TeleMCP Tools & 5 Domain-Specialized Agents
        self.tools = TeleMCPTools(self.indexer)
        self.specialist_pool = Stage3SpecialistPool(self.tools)

        # Stage 4: SON Optimization Agent, 3GPP Guardrail Verifier & Multi-Tier Reflection Engine
        self.son_optimizer = SONOptimizationAgent()
        self.verifier_agent = GuardrailVerifierAgent(self.indexer.docs)
        self.reflection_engine = MultiTierReflectionEngine(
            specialist_pool=self.specialist_pool,
            son_optimizer=self.son_optimizer,
            verifier_agent=self.verifier_agent,
            supervisor=self.supervisor,
            max_iterations=3
        )

        # Stage 5: Explainable NOC Interface & Benchmark Evaluator
        self.noc_interface = ExplainableNOCInterface()
        self.evaluator = TeleRAGBenchmarkEvaluator(self)

    def run_query(
        self,
        query: str,
        incident_payload: Optional[Dict[str, Any]] = None,
        mcq_options: Optional[Dict[str, str]] = None
    ) -> ConsensusSynthesisBundle:
        """Executes Stages 2 -> 3 <-> 4 -> 5 for any natural language query or telemetry log."""
        dag_plan = self.supervisor.classify_and_decompose(
            query_or_log=query,
            incident_payload=incident_payload,
            is_mcq=(mcq_options is not None)
        )
        bundle = self.reflection_engine.run_consensus_loop(
            dag_plan=dag_plan,
            incident_payload=incident_payload,
            mcq_options=mcq_options
        )
        return bundle

    def run_incident_triage(self, alarm: RANAlarmLog) -> ConsensusSynthesisBundle:
        """Executes end-to-end multi-agent triage and closed-loop SON remediation on a RANAlarmLog."""
        payload = {
            "incident_id": alarm.incident_id,
            "cell_id": alarm.cell_id,
            "neighbor_cell_id": alarm.neighbor_cell_id,
            "severity": alarm.severity,
            "alarm_type": alarm.alarm_type,
            "probable_cause": alarm.probable_cause,
            "kpi_snapshot": alarm.kpi_snapshot,
            "raw_log": alarm.raw_log
        }
        return self.run_query(query=alarm.raw_log, incident_payload=payload)

    def run_teleqna_item(self, item: TeleQnAItem) -> ConsensusSynthesisBundle:
        """Executes the pipeline on a TeleQnA multiple-choice question."""
        return self.run_query(query=item.question, mcq_options=item.options)


if __name__ == "__main__":
    pipeline = TeleRAG2Pipeline()
    alarms = pipeline.data_loader.load_telemetry_alarms()

    print("\n" + "#" * 92)
    print("  RUNNING FULL 5-STAGE TELERAG 2.0 PIPELINE ON LIVE 5G RAN INCIDENT (INC-2026-5G-001)")
    print("#" * 92)
    bundle_01 = pipeline.run_incident_triage(alarms[0])
    print(pipeline.noc_interface.render_diagnostic_report(bundle_01))

    print("\n" + "#" * 92)
    print("  RUNNING STAGE 5 TARGET KPI & ABLATION BENCHMARK EVALUATION")
    print("#" * 92)
    metrics = pipeline.evaluator.evaluate_all_kpis()
    print(json.dumps(metrics, indent=2))
