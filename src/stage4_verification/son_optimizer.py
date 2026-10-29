"""
Stage 4: SON Optimization Agent & Tier-1 Topology Conflict Loop (3GPP TS 28.541)
Evaluates proposed parameters against multi-cell ANR topology, neighbor PRB utilization,
and Event A3 Ping-Pong handover stability criteria.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from src.stage3_specialists.agents import AgentDiagnosisOutput


@dataclass
class SONTopologyEvaluation:
    """Result of the SON Optimization Agent's Tier-1 topology & stability check."""
    has_conflict: bool
    target_agent_type: Optional[str]
    conflict_critique: Optional[str]
    son_remediation_plan: Dict[str, Any] = field(default_factory=dict)
    son_reasoning_trace: List[str] = field(default_factory=list)


class SONOptimizationAgent:
    """
    SON Optimization & Healing Agent (3GPP TS 28.541 §4.3.1 & TS 38.331 §5.5.4.4).
    Performs closed-loop parameter tuning and Tier-1 Inter-Agent Topology Conflict Detection.
    """

    def evaluate_and_optimize(
        self,
        agent_outputs: List[AgentDiagnosisOutput],
        incident_payload: Optional[Dict[str, Any]] = None
    ) -> SONTopologyEvaluation:
        kpi = (incident_payload or {}).get("kpi_snapshot", {})
        cell_id = (incident_payload or {}).get("cell_id", "gNB_Serving_01")
        neighbor_id = (incident_payload or {}).get("neighbor_cell_id", "gNB_Neighbor_02")
        neigh_prb = float(kpi.get("neighbor_PRB_utilization_percent", 50.0))

        merged_params: Dict[str, Any] = {}
        trace: List[str] = []

        for out in agent_outputs:
            merged_params.update(out.proposed_parameters)

        # Check Tier-1 Topology & Ping-Pong Conflicts on Mobility & RRC Agent proposals
        if "CIO_dB" in merged_params:
            cio = float(merged_params["CIO_dB"])
            hys = float(merged_params.get("Hysteresis_dB", 2.0))
            ttt = int(merged_params.get("TTT_ms", 160))

            # Conflict Condition 1: Neighbor cell PRB overload (>85%) with large positive CIO (> +2.0 dB)
            # Conflict Condition 2: Ping-Pong risk when CIO - Hys > 3.0 dB and TTT < 256 ms
            overload_conflict = (neigh_prb > 85.0 and cio > 2.0)
            ping_pong_conflict = ((cio - hys) > 3.0 and ttt < 256)

            if overload_conflict or ping_pong_conflict:
                reasons = []
                if overload_conflict:
                    reasons.append(
                        f"Target neighbor cell {neighbor_id} PRB utilization is {neigh_prb}% (> 85% MLB threshold in 3GPP TS 28.541 §4.3.1), so CIO={cio:+.1f} dB will cause neighbor congestion collapse"
                    )
                if ping_pong_conflict:
                    reasons.append(
                        f"CIO={cio:+.1f} dB with Hysteresis={hys:.1f} dB and TTT={ttt} ms violates Event A3 stability margin (TS 38.331 §5.5.4.4), inducing severe Ping-Pong handovers"
                    )

                critique_msg = (
                    f"[TIER-1 SON TOPOLOGY CONFLICT -> Mobility & RRC Agent] {' AND '.join(reasons)}. "
                    "Re-evaluate mobility parameters using bounded CIO <= +2.0 dB (0.5 dB step), Hysteresis >= 2.0 dB, and TTT >= 256 ms."
                )
                trace.append(critique_msg)
                return SONTopologyEvaluation(
                    has_conflict=True,
                    target_agent_type="MOBILITY_RRC",
                    conflict_critique=critique_msg,
                    son_remediation_plan={},
                    son_reasoning_trace=trace
                )

        # If no conflict, synthesize the actionable O1/NETCONF SON parameter configuration plan
        trace.append(
            f"[SON Optimization Agent] Verified multi-cell ANR stability on {cell_id} (Neighbor {neighbor_id} PRB={neigh_prb}%). Formulated O1/NETCONF closed-loop parameter patch per TS 28.541 §4.3.1."
        )
        remediation_plan = {
            "target_cell_id": cell_id,
            "neighbor_cell_id": neighbor_id,
            "interface": "O-RAN O1 / 3GPP TS 28.541 NRM",
            "validated_parameters": merged_params,
            "execution_mode": "CLOSED_LOOP_AUTONOMOUS"
        }

        return SONTopologyEvaluation(
            has_conflict=False,
            target_agent_type=None,
            conflict_critique=None,
            son_remediation_plan=remediation_plan,
            son_reasoning_trace=trace
        )
