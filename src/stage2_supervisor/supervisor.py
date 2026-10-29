"""
Stage 2: Supervisor / Dispatcher Agent
Implements the 4 sequential blocks of Stage 2 in the TeleRAG 2.0 Architecture:
1. Acronym Normalizer (Expands abbreviations: PRACH, BWP, DCI, SSB, etc.)
2. Intent & Layer Classifier (Identifies intent: root cause, optimization, spec QA & telecom layer)
3. Dynamic Task Delegator (DAG) (Decomposes complex query into subtasks: DAG execution plan)
4. Agent Router (Routes tasks to appropriate Stage 3 specialized agents & handles Stage 4 -> Stage 2 Feedback Loop)
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re
from src.stage1_ingestion.acronym_expander import TelecomAcronymExpander


@dataclass
class SubTaskNode:
    """Represents a single node in the Supervisor's DAG execution plan."""
    task_id: str
    agent_type: str                 # MOBILITY_RRC, PHY_QUALITY, ORAN_INTERFACE, CORE_TRANSPORT, SPEC_QNA, SON_OPTIMIZATION
    agent_name: str                 # Human-readable agent name
    sub_query: str                  # Focused query for this specialist
    assigned_tools: List[str]       # TeleMCP tools to invoke
    depends_on: List[str] = field(default_factory=list)
    priority: int = 1
    feedback_critique: Optional[str] = None


@dataclass
class DAGTaskPlan:
    """Directed Acyclic Graph (DAG) decomposition produced by the Supervisor Agent."""
    original_input: str
    normalized_input: str
    expanded_input: str
    extracted_entities: List[str]
    intent_type: str                # SPEC_QNA, ALARM_TRIAGE, MULTI_LAYER_INCIDENT
    active_layers: List[str]
    tasks: List[SubTaskNode]
    requires_son_optimization: bool
    rerouted_from_verifier: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_input": self.original_input,
            "normalized_input": self.normalized_input,
            "expanded_input": self.expanded_input,
            "extracted_entities": self.extracted_entities,
            "intent_type": self.intent_type,
            "active_layers": self.active_layers,
            "requires_son_optimization": self.requires_son_optimization,
            "rerouted_from_verifier": self.rerouted_from_verifier,
            "tasks": [
                {
                    "task_id": t.task_id,
                    "agent_type": t.agent_type,
                    "agent_name": t.agent_name,
                    "sub_query": t.sub_query,
                    "assigned_tools": t.assigned_tools,
                    "depends_on": t.depends_on,
                    "priority": t.priority,
                    "feedback_critique": t.feedback_critique
                }
                for t in self.tasks
            ]
        }


class SupervisorAgent:
    """
    Stage 2 Supervisor / Dispatcher Agent.
    Executes:
    1. Acronym Normalizer
    2. Intent & Layer Classifier
    3. Dynamic Task Delegator (DAG)
    4. Agent Router (including Stage 4 -> Stage 2 Verifier Feedback Re-routing)
    """

    LAYER_KEYWORDS: Dict[str, List[str]] = {
        "MOBILITY_RRC": [
            "handover", "ho", "rrc", "t304", "t310", "t311", "t300", "n310", "n311",
            "rlf", "radio link failure", "event a3", "event a1", "event a2", "event a5",
            "cio", "cell individual offset", "hysteresis", "ttt", "time to trigger",
            "reconfiguration", "re-establishment", "38.331", "ping-pong", "mobility", "spcell",
            "call drop", "calls dropping", "dropping calls", "moving", "driving", "highway",
            "switch tower", "switching towers", "cannot connect", "can't connect", "unable to connect"
        ],
        "PHY_QUALITY": [
            "sinr", "bler", "pusch", "pdsch", "prach", "pdcch", "pucch", "interference",
            "pilot pollution", "rsrp", "rsrq", "bwp", "beam failure", "bfr", "bfi",
            "uplink noise", "jammer", "power control", "p0_pusch", "harq", "38.213", "38.211", "ret", "tilt",
            "bad signal", "weak signal", "poor signal", "static", "noise", "antenna"
        ],
        "ORAN_INTERFACE": [
            "o-ran", "oran", "ric", "near-rt ric", "non-rt ric", "e2", "e2ap", "a1", "o1",
            "xapp", "rapp", "f1", "f1-c", "f1-u", "e1", "o-cu", "o-du", "o-ru", "fronthaul",
            "sctp_communication_lost", "wg3", "smo", "controller", "radio unit"
        ],
        "CORE_TRANSPORT": [
            "ngap", "s1-ap", "pdu", "pdu session", "gtp-u", "gtpu", "amf", "smf", "upf",
            "5qi", "qos", "n2", "n3", "initial context setup", "transport resource", "38.413", "23.501",
            "no internet", "slow internet", "data session", "packet loss", "core network"
        ]
    }

    AGENT_METADATA: Dict[str, Dict[str, Any]] = {
        "MOBILITY_RRC": {
            "name": "Mobility & RRC Agent",
            "tools": ["rc_spec_retriever", "rrc_spec_retriever", "ho_matrix_parser"]
        },
        "PHY_QUALITY": {
            "name": "PHY & Quality Agent",
            "tools": ["kpi_anomaly_detect", "rf_spec_retriever"]
        },
        "ORAN_INTERFACE": {
            "name": "O-RAN & Interface Agent",
            "tools": ["o_ran_alarm_parser", "oran_alarm_parser", "f1_latency_checker"]
        },
        "CORE_TRANSPORT": {
            "name": "Core & Transport Agent",
            "tools": ["pdu_session_parser", "pdu_session_tracer", "ngap_cause_analyzer"]
        },
        "SPEC_QNA": {
            "name": "3GPP Spec QnA Agent",
            "tools": ["hybrid_rrf_search", "dew_rrf_retriever", "bge_reranker_large"]
        },
        "SON_OPTIMIZATION": {
            "name": "SON Optimization & Healing Agent",
            "tools": ["son_param_optimizer"]
        }
    }

    def __init__(self):
        self.acronym_expander = TelecomAcronymExpander()

    # ------------------------------------------------------------------
    # Step 1: Acronym Normalizer
    # ------------------------------------------------------------------
    def normalize_and_expand(self, raw_text: str) -> Dict[str, Any]:
        normalized = self.acronym_expander.normalize_acronyms(raw_text)
        expanded = self.acronym_expander.expand_query(normalized)
        entities = self.acronym_expander.extract_telecom_entities(raw_text)
        return {
            "normalized_input": normalized,
            "expanded_input": expanded,
            "extracted_entities": entities
        }

    # ------------------------------------------------------------------
    # Step 2: Intent & Layer Classifier
    # ------------------------------------------------------------------
    def classify_intent_and_layers(
        self,
        combined_text: str,
        query_or_log: str,
        incident_payload: Optional[Dict[str, Any]] = None,
        is_mcq: bool = False
    ) -> Dict[str, Any]:
        lower_text = combined_text.lower()
        layer_scores: Dict[str, int] = {}

        for layer, kw_list in self.LAYER_KEYWORDS.items():
            score = sum(
                1 for kw in kw_list
                if re.search(r'(?<!\w)' + re.escape(kw) + r'(?!\w)', lower_text)
            )
            if score > 0:
                layer_scores[layer] = score

        # Prevent generic "3GPP/O-RAN" phrasing from falsely triggering ORAN_INTERFACE when no specific O-RAN entity is present
        if "ORAN_INTERFACE" in layer_scores and len(layer_scores) > 1:
            specific_oran = ["ric", "e2", "e2ap", "a1", "o1", "xapp", "rapp", "f1", "f1-c", "f1-u", "e1", "o-cu", "o-du", "o-ru", "fronthaul", "sctp_communication_lost", "wg3", "smo"]
            if not any(re.search(r'(?<!\w)' + re.escape(k) + r'(?!\w)', lower_text) for k in specific_oran):
                del layer_scores["ORAN_INTERFACE"]

        sorted_layers = [k for k, _ in sorted(layer_scores.items(), key=lambda item: item[1], reverse=True)]

        has_alarm_indicators = (
            incident_payload is not None
            or any(
                tok in lower_text
                for tok in [
                    "[rrc-warn]", "[phy-alarm]", "[oran-err]", "[core-err]",
                    "alarm", "incident", "failure for ue_id", "dropped to",
                    "how do i fix", "how to fix", "help me", "help fix",
                    "my cell", "our cell", "gnb_", "o-du", "is failing",
                    "is dropping", "dropping handovers", "handover failure",
                    "t304 expiry", "t304 expired", "t304 is expiring",
                    "high bler", "low sinr", "sctp_communication_lost",
                    "connection lost", "packet drop", "troubleshoot",
                    "remediate", "what parameters should", "what should i do"
                ]
            )
        )

        if is_mcq or (not has_alarm_indicators and ("?" in query_or_log or "which " in lower_text or "what " in lower_text or "explain " in lower_text)):
            intent_type = "SPEC_QNA"
            if "SPEC_QNA" not in sorted_layers:
                sorted_layers = ["SPEC_QNA"] + sorted_layers[:1]
            requires_son = False
        else:
            if len(sorted_layers) > 1:
                intent_type = "MULTI_LAYER_INCIDENT"
            else:
                intent_type = "ALARM_TRIAGE"
                if not sorted_layers:
                    sorted_layers = ["MOBILITY_RRC"]
            requires_son = True
            if "SON_OPTIMIZATION" not in sorted_layers:
                sorted_layers.append("SON_OPTIMIZATION")

        return {
            "intent_type": intent_type,
            "active_layers": sorted_layers,
            "requires_son_optimization": requires_son
        }

    # ------------------------------------------------------------------
    # Step 3 & 4: Dynamic Task Delegator (DAG) & Agent Router
    # ------------------------------------------------------------------
    def classify_and_decompose(
        self,
        query_or_log: str,
        incident_payload: Optional[Dict[str, Any]] = None,
        is_mcq: bool = False
    ) -> DAGTaskPlan:
        combined_text = query_or_log
        if incident_payload:
            combined_text += " " + str(incident_payload.get("alarm_type", ""))
            combined_text += " " + str(incident_payload.get("probable_cause", ""))
            combined_text += " " + str(incident_payload.get("raw_log", ""))

        norm_info = self.normalize_and_expand(combined_text)
        cls_info = self.classify_intent_and_layers(
            combined_text=combined_text,
            query_or_log=query_or_log,
            incident_payload=incident_payload,
            is_mcq=is_mcq
        )

        tasks: List[SubTaskNode] = []
        prev_task_id: Optional[str] = None

        for idx, layer in enumerate(cls_info["active_layers"], start=1):
            task_id = f"TASK_{idx}_{layer}"
            meta = self.AGENT_METADATA[layer]
            depends = [prev_task_id] if (prev_task_id and layer != "SPEC_QNA") else []

            sub_query = (
                f"[{meta['name']}] Analyze {', '.join(norm_info['extracted_entities'][:6]) if norm_info['extracted_entities'] else 'protocol state'}: {norm_info['normalized_input']}"
            )
            tasks.append(SubTaskNode(
                task_id=task_id,
                agent_type=layer,
                agent_name=meta["name"],
                sub_query=sub_query,
                assigned_tools=list(meta["tools"]),
                depends_on=depends,
                priority=idx
            ))
            prev_task_id = task_id

        return DAGTaskPlan(
            original_input=query_or_log,
            normalized_input=norm_info["normalized_input"],
            expanded_input=norm_info["expanded_input"],
            extracted_entities=norm_info["extracted_entities"],
            intent_type=cls_info["intent_type"],
            active_layers=cls_info["active_layers"],
            tasks=tasks,
            requires_son_optimization=cls_info["requires_son_optimization"],
            rerouted_from_verifier=False
        )

    def reroute_on_verifier_feedback(
        self,
        previous_plan: DAGTaskPlan,
        verifier_critique: str,
        target_agent_types: Optional[List[str]] = None
    ) -> DAGTaskPlan:
        """
        Handles the Stage 4 -> Stage 2 Feedback Loop (Verifier Feedback / Re-routing for Re-evaluation).
        Updates the DAG execution plan with the Verifier critique and re-routes to Stage 3 agents.
        """
        updated_tasks: List[SubTaskNode] = []
        for t in previous_plan.tasks:
            if target_agent_types is None or t.agent_type in target_agent_types or t.agent_type == "SON_OPTIMIZATION":
                updated_tasks.append(SubTaskNode(
                    task_id=t.task_id,
                    agent_type=t.agent_type,
                    agent_name=t.agent_name,
                    sub_query=f"{t.sub_query} | [STAGE 4 VERIFIER FEEDBACK]: {verifier_critique}",
                    assigned_tools=t.assigned_tools,
                    depends_on=t.depends_on,
                    priority=t.priority,
                    feedback_critique=verifier_critique
                ))
            else:
                updated_tasks.append(t)

        return DAGTaskPlan(
            original_input=previous_plan.original_input,
            normalized_input=previous_plan.normalized_input,
            expanded_input=previous_plan.expanded_input,
            extracted_entities=previous_plan.extracted_entities,
            intent_type=previous_plan.intent_type,
            active_layers=previous_plan.active_layers,
            tasks=updated_tasks,
            requires_son_optimization=previous_plan.requires_son_optimization,
            rerouted_from_verifier=True
        )
