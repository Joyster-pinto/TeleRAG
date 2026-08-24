"""
TeleRAG: Domain-Specific Multi-Agent RAG Assistant for Telecom RAN Operations
Dataset Loading and Preprocessing Module for DA1 Submission

Datasets Handled:
1. TeleQnA: Multiple-choice benchmark across 3GPP and O-RAN standards.
2. 3GPP Technical Specifications: Section-aware hierarchical chunking for TS 38.331 (RRC), TS 38.213 (PHY), TS 38.413 (NGAP).
3. Telecom Telemetry & Alarm Stream: Simu5G / O-RAN KPI time-series and multi-layer cascade alarm logs.
"""

import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class TeleQnAItem:
    question_id: str
    question: str
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    correct_answer: str
    category: str
    explanation: Optional[str] = None

@dataclass
class SpecChunk:
    doc_id: str
    spec_number: str
    release: str
    section_id: str
    section_title: str
    content: str
    token_count: int

@dataclass
class RANAlarmLog:
    timestamp: str
    cell_id: str
    severity: str
    alarm_type: str
    probable_cause: str
    kpi_snapshot: Dict[str, float]
    raw_log: str


class TelecomDataLoader:
    """
    Unified DataLoader for TeleRAG Multi-Agent System.
    Loads and standardizes Telecom standards, TeleQnA benchmarks, and RAN operational logs.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def load_teleqna(self, filepath: Optional[str] = None) -> List[TeleQnAItem]:
        """Loads TeleQnA dataset for benchmark evaluation."""
        path = filepath or os.path.join(self.data_dir, "teleqna_sample.json")
        if not os.path.exists(path):
            self._create_default_teleqna(path)
            
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        items = []
        for q_id, q_data in raw_data.items():
            items.append(TeleQnAItem(
                question_id=q_id,
                question=q_data.get("question", ""),
                option_1=q_data.get("option 1", ""),
                option_2=q_data.get("option 2", ""),
                option_3=q_data.get("option 3", ""),
                option_4=q_data.get("option 4", ""),
                correct_answer=q_data.get("answer", ""),
                category=q_data.get("category", "3GPP Standard"),
                explanation=q_data.get("explanation", "")
            ))
        print(f"[DataLoader] Successfully loaded {len(items)} TeleQnA benchmark items from {path}")
        return items

    def load_specs(self, filepath: Optional[str] = None) -> List[SpecChunk]:
        """Loads and parses 3GPP and O-RAN specifications with section-level chunking."""
        path = filepath or os.path.join(self.data_dir, "specs_sample.json")
        if not os.path.exists(path):
            self._create_default_specs(path)
            
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        chunks = []
        for item in raw_data:
            chunks.append(SpecChunk(
                doc_id=item["doc_id"],
                spec_number=item["spec_number"],
                release=item["release"],
                section_id=item["section_id"],
                section_title=item["section_title"],
                content=item["content"],
                token_count=len(item["content"].split())
            ))
        print(f"[DataLoader] Successfully loaded {len(chunks)} 3GPP/O-RAN specification chunks from {path}")
        return chunks

    def load_telemetry_logs(self, filepath: Optional[str] = None) -> List[RANAlarmLog]:
        """Loads synthetic 5G RAN incident alarms and KPI snapshots (Simu5G / O-RAN format)."""
        path = filepath or os.path.join(self.data_dir, "telemetry_sample.json")
        if not os.path.exists(path):
            self._create_default_telemetry(path)
            
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        logs = []
        for item in raw_data:
            logs.append(RANAlarmLog(
                timestamp=item["timestamp"],
                cell_id=item["cell_id"],
                severity=item["severity"],
                alarm_type=item["alarm_type"],
                probable_cause=item["probable_cause"],
                kpi_snapshot=item["kpi_snapshot"],
                raw_log=item["raw_log"]
            ))
        print(f"[DataLoader] Successfully loaded {len(logs)} RAN alarm and telemetry traces from {path}")
        return logs

    def _create_default_teleqna(self, path: str):
        """Generates representative TeleQnA sample items spanning 3GPP RRC, PHY, and O-RAN."""
        samples = {
            "Q_38331_001": {
                "question": "In 3GPP TS 38.331 (NR RRC), which timer is started by the UE upon transmission of RRCReconfigurationComplete including mobilityControlInfo?",
                "option 1": "Timer T300",
                "option 2": "Timer T304 (Handover timer)",
                "option 3": "Timer T310 (Radio link failure timer)",
                "option 4": "Timer T311 (RRC re-establishment timer)",
                "answer": "option 2",
                "category": "3GPP TS 38.331 RRC Protocol",
                "explanation": "According to TS 38.331 Section 5.3.5.3, timer T304 is started upon reception of RRCReconfiguration containing reconfigurationWithSync (Handover) and stopped upon successful random access to the target cell."
            },
            "Q_38213_002": {
                "question": "What is the primary cause of sudden Uplink PUSCH SINR degradation when RSRP from the serving gNB remains high (-75 dBm)?",
                "option 1": "Propagation path loss attenuation",
                "option 2": "Co-channel uplink inter-cell interference (high neighboring PRB load) or external jammer",
                "option 3": "Downlink SSB beam failure",
                "option 4": "AMF signaling overload",
                "answer": "option 2",
                "category": "3GPP TS 38.213 PHY Layer",
                "explanation": "High serving RSRP combined with severely degraded SINR indicates a high interference-plus-noise denominator, typically caused by uncoordinated co-channel PUSCH transmissions or pilot pollution."
            },
            "Q_ORAN_003": {
                "question": "In O-RAN architecture, which interface is responsible for connecting the Near-RT RIC to the E2 Nodes (O-CU-CP, O-CU-UP, O-DU) for fine-grained control loops (10ms-1s)?",
                "option 1": "O1 Interface",
                "option 2": "A1 Interface",
                "option 3": "E2 Interface",
                "option 4": "Open Fronthaul 7.2x Interface",
                "answer": "option 3",
                "category": "O-RAN Alliance Architecture",
                "explanation": "The E2 interface connects the Near-RT RIC to E2 nodes (CU/DU) allowing xApps to subscribe to metrics and execute RAN control actions."
            },
            "Q_38413_004": {
                "question": "When an NG-RAN node rejects a PDU Session Resource Setup Request due to transport network congestion, which NGAP Cause group is signaled?",
                "option 1": "CauseRadioNetwork",
                "option 2": "CauseTransport (Transport Resource Unavailable)",
                "option 3": "CauseNas",
                "option 4": "CauseProtocol",
                "answer": "option 2",
                "category": "3GPP TS 38.413 NGAP",
                "explanation": "TS 38.413 Clause 9.3.1.2 defines CauseTransport for signaling failures stemming from GTP-U transport and IP backbone congestion."
            }
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(samples, f, indent=2)

    def _create_default_specs(self, path: str):
        """Generates representative 3GPP specification chunks with clause metadata."""
        specs = [
            {
                "doc_id": "TS_38331_SEC_5_3_5",
                "spec_number": "TS 38.331",
                "release": "Rel 17",
                "section_id": "5.3.5.3",
                "section_title": "RRC Reconfiguration with Sync (Handover Execution)",
                "content": "Upon receiving an RRCReconfiguration message including reconfigurationWithSync, the UE shall start timer T304 for the target SpCell. The UE shall apply the target SpCell configuration, configure lower layers to perform Random Access on the target SpCell, and transmit the RRCReconfigurationComplete message. If timer T304 expires before successful completion of random access on the target SpCell, the UE shall initiate the RRC connection re-establishment procedure as specified in clause 5.3.7."
            },
            {
                "doc_id": "TS_38213_SEC_7_1",
                "spec_number": "TS 38.213",
                "release": "Rel 16",
                "section_id": "7.1.1",
                "section_title": "Physical Uplink Shared Channel (PUSCH) Power Control and Interference",
                "content": "For PUSCH transmission on serving cell c, carrier f, and active UL BWP b, the UE sets the transmit power according to the target power P0_PUSCH, alpha path loss compensation, and closed-loop TPC commands. When severe uplink interference is detected on target Physical Resource Blocks (PRBs), the network may adjust the target nominal power or invoke fractional power control. High PUSCH RSSI with low SINR signifies excessive co-channel interference or pilot contamination from adjacent unsynchronized cells."
            },
            {
                "doc_id": "TS_38413_SEC_8_2",
                "spec_number": "TS 38.413",
                "release": "Rel 17",
                "section_id": "8.2.1",
                "section_title": "Initial Context Setup and NGAP Cause Codes",
                "content": "The INITIAL CONTEXT SETUP procedure is used to establish the required UE context, including PDU session resources and security capabilities. If the NG-RAN node is unable to establish any PDU session resource, it sends an INITIAL CONTEXT SETUP FAILURE message with appropriate cause value (e.g., CauseRadioNetwork: cell-not-available, or CauseTransport: transport-resource-unavailable). Upon receiving CauseTransport, the AMF logs transport route exhaustion."
            },
            {
                "doc_id": "ORAN_WG3_E2_SEC_4",
                "spec_number": "O-RAN.WG3.E2GAP",
                "release": "v03.00",
                "section_id": "4.2.1",
                "section_title": "E2 Setup and Node Configuration Update Procedures",
                "content": "The purpose of the E2 Setup procedure is to establish the E2 interface connection between an E2 Node (O-CU/O-DU) and the Near-RT RIC. If the Near-RT RIC rejects the setup due to unsupported E2 Service Model (E2SM) or schema mismatch, it returns an E2 SETUP FAILURE message containing CauseProtocol: AbstractSyntaxError_Reject. The E2 Node shall back off according to the TimeToWait timer before attempting re-transmission."
            },
            {
                "doc_id": "TS_28541_SEC_6_2",
                "spec_number": "TS 28.541",
                "release": "Rel 17",
                "section_id": "6.2.3",
                "section_title": "Self-Organizing Networks (SON): Mobility Robustness and Handover Optimization",
                "content": "Handover parameter optimization (MRO) adjusts the Cell Individual Offset (CIO) and time-to-trigger (TTT) parameters to prevent Handover Failure: Too Early Handover, Too Late Handover, and Handover to Wrong Cell. If the failure type is Too Late Handover (RLF occurs in source cell before handover completes), the CIO towards the target cell shall be increased (e.g. +1 dB to +3 dB) to trigger earlier measurement reports (Event A3). Valid CIO range is [-24 dB, +24 dB] in steps of 0.5 dB."
            }
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(specs, f, indent=2)

    def _create_default_telemetry(self, path: str):
        """Generates representative 5G RAN telemetry incident traces."""
        logs = [
            {
                "timestamp": "2026-08-24T14:22:10Z",
                "cell_id": "gNB_102_Sec3",
                "severity": "CRITICAL",
                "alarm_type": "HANDOVER_EXECUTION_FAILURE_T304_EXPIRY",
                "probable_cause": "Target cell gNB_105 RACH failure or severe pilot pollution at cell boundary",
                "kpi_snapshot": {
                    "RSRP_dBm": -82.4,
                    "RSRQ_dB": -14.1,
                    "SINR_dB": -2.8,
                    "HO_Success_Rate_pct": 54.2,
                    "T304_Expiry_Count": 42
                },
                "raw_log": "Aug 24 14:22:10 gNB-102 RRC_MRO: [ALARM-4102] T304 timer expired for UE-ID=88412 during HO towards target gNB-105. RRC connection re-establishment initiated."
            },
            {
                "timestamp": "2026-08-24T14:25:30Z",
                "cell_id": "gNB_204_Sec1",
                "severity": "MAJOR",
                "alarm_type": "HIGH_PUSCH_UPLINK_INTERFERENCE",
                "probable_cause": "Uncoordinated adjacent cell PRB allocation or external industrial RF jammer",
                "kpi_snapshot": {
                    "RSRP_dBm": -74.1,
                    "PUSCH_RSSI_dBm": -86.3,
                    "Uplink_BLER_pct": 28.6,
                    "Uplink_Throughput_Mbps": 3.4
                },
                "raw_log": "Aug 24 14:25:30 gNB-204 PHY_MON: [ALARM-2091] Uplink interference threshold exceeded on PRBs 12-48. Average PUSCH RSSI=-86.3dBm, SINR=-4.1dB."
            },
            {
                "timestamp": "2026-08-24T14:30:15Z",
                "cell_id": "NearRT_RIC_Instance_01",
                "severity": "CRITICAL",
                "alarm_type": "E2_NODE_SETUP_FAILURE",
                "probable_cause": "AbstractSyntaxError_Reject in E2SM-KPM schema negotiation with O-DU-301",
                "kpi_snapshot": {
                    "Active_E2_Nodes": 14,
                    "Disconnected_Nodes": 1,
                    "xApp_Traffic_Steering_Status": 0.0
                },
                "raw_log": "Aug 24 14:30:15 RIC-E2TERM: [ALARM-7014] E2 Setup Request rejected from node O-DU-301. Cause=AbstractSyntaxError_Reject. TimeToWait=5s."
            }
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)

if __name__ == "__main__":
    loader = TelecomDataLoader()
    teleqna = loader.load_teleqna()
    specs = loader.load_specs()
    telemetry = loader.load_telemetry_logs()
    print("\n[Summary] TelecomDataLoader initialized and verified all datasets successfully!")
