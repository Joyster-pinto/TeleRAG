"""
Stage 4 -> Stage 2 Closed-Loop Feedback Controller & Stage 5 Response Synthesis Bridge
Implements the exact control flow from the TeleRAG 2.0 Architecture Diagram:
- Forward Data / Control Flow : Stage 1 -> Stage 2 -> Stage 3 -> Stage 4 -> Stage 5
- Feedback Loop               : Stage 4 (Verifier) --> Stage 2 (Supervisor / Dispatcher Agent) --> Stage 3 (Re-evaluation)
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from src.stage2_supervisor.supervisor import SupervisorAgent, DAGTaskPlan
from src.stage3_specialists.agents import Stage3SpecialistPool, AgentDiagnosisOutput
from .son_optimizer import SONOptimizationAgent, SONTopologyEvaluation
from .verifier_agent import GuardrailVerifierAgent, VerificationReport


@dataclass
class ConsensusSynthesisBundle:
    """
    Stage 5 Response Synthesis & Explainable User Interface Package:
    1. Multi-Agent Consensus
    2. Chain-of-Thought Reasoning Trace
    3. 3GPP Evidence & Citations
    4. Actionable Remediation
    5. TeleMCP Standard Export (JSON / YAML)
    6. Explainable NOC User Interface Payload
    """
    dag_plan: DAGTaskPlan
    agent_outputs: List[AgentDiagnosisOutput]
    son_evaluation: SONTopologyEvaluation
    verification_report: VerificationReport
    feedback_history: List[Dict[str, Any]]
    executive_rca_summary: str
    combined_cot_trace: List[str]
    total_iterations: int
    telemcp_export: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "multi_agent_consensus": self.executive_rca_summary,
            "chain_of_thought_reasoning_trace": self.combined_cot_trace,
            "evidence_and_citations_3gpp": self.verification_report.verified_clauses,
            "actionable_remediation": self.son_evaluation.son_remediation_plan,
            "telemcp_standard_export": self.telemcp_export,
            "verification": {
                "is_verified": self.verification_report.is_verified,
                "citation_faithfulness_score": self.verification_report.citation_faithfulness_score,
                "parameter_compliance_score": self.verification_report.parameter_compliance_score,
                "verified_package": (
                    {
                        "validated_citations": self.verification_report.verified_package.validated_citations,
                        "verified_parameters": self.verification_report.verified_package.verified_parameters,
                        "confidence_scores": self.verification_report.verified_package.confidence_scores
                    }
                    if self.verification_report.verified_package else None
                )
            },
            "total_iterations": self.total_iterations,
            "feedback_history": self.feedback_history
        }


class MultiTierReflectionEngine:
    """
    Coordinates:
    - Stage 2 -> Stage 3 task execution
    - Stage 4 (Citation Grounding Check + Parameter Bounds Enforcer)
    - Feedback Loop (Stage 4 -> Stage 2 Supervisor -> Stage 3 Domain Agents)
    - Stage 5 Response Synthesis & TeleMCP Export
    """

    def __init__(
        self,
        specialist_pool: Stage3SpecialistPool,
        son_optimizer: SONOptimizationAgent,
        verifier_agent: GuardrailVerifierAgent,
        supervisor: Optional[SupervisorAgent] = None,
        max_iterations: int = 3
    ):
        self.specialist_pool = specialist_pool
        self.son_optimizer = son_optimizer
        self.verifier_agent = verifier_agent
        self.supervisor = supervisor or SupervisorAgent()
        self.max_iterations = max_iterations

    def run_consensus_loop(
        self,
        dag_plan: DAGTaskPlan,
        incident_payload: Optional[Dict[str, Any]] = None,
        mcq_options: Optional[Dict[str, str]] = None
    ) -> ConsensusSynthesisBundle:
        feedback_history: List[Dict[str, Any]] = []
        current_plan = dag_plan

        combined_cot: List[str] = [
            f"[Stage 2: Supervisor / Dispatcher Agent] Acronym Normalizer -> Intent & Layer Classifier ({current_plan.intent_type}) -> Dynamic Task Delegator (DAG: {current_plan.active_layers}) -> Agent Router."
        ]

        # Initial Stage 3 execution (Iteration 0)
        agent_outputs = self.specialist_pool.execute_dag_plan(
            dag_plan=current_plan,
            incident_payload=incident_payload,
            mcq_options=mcq_options,
            iteration=0
        )
        for out in agent_outputs:
            combined_cot.extend(out.chain_of_thought)

        iteration = 0
        ver_report = self.verifier_agent.verify_outputs(agent_outputs, incident_payload=incident_payload)

        while iteration < self.max_iterations:
            ver_report = self.verifier_agent.verify_outputs(agent_outputs, incident_payload=incident_payload)
            combined_cot.extend(ver_report.verifier_trace)

            if not ver_report.is_verified:
                iteration += 1
                target_agent = ver_report.target_agent_type or "MOBILITY_RRC"

                # Feedback Loop: Stage 4 -> Stage 2 (Supervisor / Dispatcher Agent)
                feedback_history.append({
                    "iteration": iteration,
                    "loop_path": "Stage 4 (3GPP Verifier) --> Stage 2 (Supervisor / Dispatcher Agent) --> Stage 3 (Domain Agents)",
                    "tier": "STAGE_4_TO_STAGE_2_VERIFIER_FEEDBACK",
                    "from": "Stage 4: 3GPP Citation & Guardrail Verifier",
                    "via": "Stage 2: Supervisor / Dispatcher Agent (Agent Router)",
                    "to": target_agent,
                    "critique": ver_report.violation_critique
                })

                current_plan = self.supervisor.reroute_on_verifier_feedback(
                    previous_plan=current_plan,
                    verifier_critique=ver_report.violation_critique or "",
                    target_agent_types=[target_agent, "SON_OPTIMIZATION"]
                )
                combined_cot.append(
                    f"[Stage 2: Supervisor / Dispatcher Agent | Re-route Iter {iteration}] Received Stage 4 Verifier Feedback -> Re-routing DAG task to {target_agent} & SON_OPTIMIZATION for re-evaluation."
                )

                # Re-run Stage 3 Domain Agents via re-routed Stage 2 DAG Plan
                corrected_outputs = self.specialist_pool.execute_dag_plan(
                    dag_plan=current_plan,
                    incident_payload=incident_payload,
                    mcq_options=mcq_options,
                    feedback_critique=ver_report.violation_critique,
                    target_agent_type=target_agent,
                    iteration=iteration
                )
                for corr in corrected_outputs:
                    combined_cot.extend(corr.chain_of_thought)
                    agent_outputs = [
                        corr if existing.agent_type == corr.agent_type else existing
                        for existing in agent_outputs
                    ]
                continue

            # Verified & Trusted Response Package ready!
            break

        # Build Stage 5 Actionable Remediation & Multi-Agent Consensus
        son_eval = self.son_optimizer.evaluate_and_optimize(agent_outputs, incident_payload)
        rca_parts = [f"[{out.agent_name}] {out.root_cause_diagnosis}" for out in agent_outputs]
        executive_summary = " | ".join(rca_parts)

        telemcp_export = {
            "protocol_version": "TeleMCP-v2.0",
            "intent_type": current_plan.intent_type,
            "verified_3gpp_compliant": ver_report.is_verified,
            "feedback_loops_executed": iteration,
            "multi_agent_consensus": executive_summary,
            "verified_response_package": (
                {
                    "validated_citations": ver_report.verified_package.validated_citations,
                    "verified_parameters": ver_report.verified_package.verified_parameters,
                    "confidence_scores": ver_report.verified_package.confidence_scores
                }
                if ver_report.verified_package else {}
            ),
            "actionable_remediation": son_eval.son_remediation_plan
        }

        return ConsensusSynthesisBundle(
            dag_plan=current_plan,
            agent_outputs=agent_outputs,
            son_evaluation=son_eval,
            verification_report=ver_report,
            feedback_history=feedback_history,
            executive_rca_summary=executive_summary,
            combined_cot_trace=combined_cot,
            total_iterations=iteration,
            telemcp_export=telemcp_export
        )
