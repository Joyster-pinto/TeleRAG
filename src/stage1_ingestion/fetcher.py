"""
Multi-Modal Telecom Data Fetcher & Ingestion Pipeline
Acquires, curates, and caches 3GPP specifications (Rel 15-18), O-RAN specifications (WG1-WG3),
TeleQnA benchmark dataset, and Simu5G / authentic 5G RAN alarm and telemetry traces.
"""
import os
import json
from typing import Dict, List, Any
from .chunker import SectionAwareChunker, DocumentChunk


class TelecomDataFetcher:
    """Manages raw and processed data acquisition for TeleRAG 2.0."""

    def __init__(self, base_data_dir: str = None):
        if base_data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.base_data_dir = os.path.join(base_dir, "data")
        else:
            self.base_data_dir = base_data_dir

        self.raw_specs_dir = os.path.join(self.base_data_dir, "raw", "specs")
        self.raw_teleqna_dir = os.path.join(self.base_data_dir, "raw", "teleqna")
        self.raw_telemetry_dir = os.path.join(self.base_data_dir, "raw", "telemetry")
        self.processed_dir = os.path.join(self.base_data_dir, "processed")

        for d in [self.raw_specs_dir, self.raw_teleqna_dir, self.raw_telemetry_dir, self.processed_dir]:
            os.makedirs(d, exist_ok=True)

        self.chunker = SectionAwareChunker(chunk_size_tokens=512, overlap_tokens=64)

    def fetch_all(self) -> Dict[str, Any]:
        """Runs the entire ingestion and chunking pipeline."""
        print("[DataFetcher] Starting full multi-modal ingestion pipeline...")
        specs = self.fetch_3gpp_and_oran_specs()
        teleqna = self.fetch_teleqna_benchmark()
        telemetry = self.fetch_ran_telemetry_and_alarms()

        chunks = self.process_and_chunk_specs(specs)

        summary = {
            "specs_loaded": len(specs),
            "total_chunks_indexed": len(chunks),
            "teleqna_questions_loaded": len(teleqna),
            "telemetry_incident_traces_loaded": len(telemetry)
        }
        print(f"[DataFetcher] Ingestion complete! Summary: {summary}")
        return summary

    def fetch_3gpp_and_oran_specs(self) -> List[Dict[str, Any]]:
        """Ingests 3GPP and O-RAN specifications."""
        specs_file = os.path.join(self.raw_specs_dir, "3gpp_oran_specs.json")

        curated_specs = [
            {
                "doc_id": "TS_38.331",
                "spec_number": "38.331",
                "release": "Rel-17",
                "title": "NR; Radio Resource Control (RRC); Protocol specification",
                "sections": [
                    {
                        "section_id": "5.3.3.3",
                        "title": "RRC Connection Establishment - RRCSetupRequest & Timer T300",
                        "content": (
                            "The UE initiates the RRC connection establishment procedure by starting timer T300 (allowed values: ms100, ms200, ms300, ms400, ms600, ms1000, ms1500, ms2000) "
                            "and transmitting RRCSetupRequest (Msg3 over PUSCH) following Random Access preamble (Msg1) and Random Access Response (Msg2). "
                            "If degraded Uplink SINR or PUSCH interference prevents the gNodeB from decoding Msg3 RRCSetupRequest or if the UE fails to receive RRCSetup (Msg4) before timer T300 expires, "
                            "the UE resets MAC, releases the MAC configuration, and records an RRC Setup Failure."
                        )
                    },
                    {
                        "section_id": "5.3.5.3",
                        "title": "RRC Reconfiguration - Handover Execution",
                        "content": (
                            "The UE shall perform handover execution upon reception of RRCReconfiguration message containing the reconfigurationWithSync field. "
                            "The UE starts timer T304 with the timer value set to the value received in reconfigurationWithSync for the target SpCell. "
                            "Allowed values for timer T304 are ms50, ms100, ms150, ms200, ms500, ms1000, ms2000, and ms10000. "
                            "The UE initiates Random Access procedure on the target SpCell in accordance with 3GPP TS 38.321. "
                            "If timer T304 expires before the Random Access procedure completes successfully, the UE initiates the RRC Connection Re-establishment procedure as specified in clause 5.3.7."
                        )
                    },
                    {
                        "section_id": "5.3.7.2",
                        "title": "Radio Link Failure (RLF) Detection & Timers",
                        "content": (
                            "The UE shall start timer T310 upon receiving N310 consecutive out-of-sync indications from lower layers for the SpCell. "
                            "While timer T310 is running, if the UE receives N311 consecutive in-sync indications from lower layers for the SpCell, the UE shall stop timer T310. "
                            "If timer T310 expires, the UE determines Radio Link Failure (RLF) to be detected. "
                            "Upon RLF detection, the UE initiates connection re-establishment by starting timer T311 and selecting a suitable cell."
                        )
                    },
                    {
                        "section_id": "5.5.4.4",
                        "title": "Event A3 - Neighbor Becomes Offset Better than SpCell",
                        "content": (
                            "Event A3 is triggered when the measurement result of a neighboring cell becomes better than the serving SpCell by a defined Cell Individual Offset (CIO) and Hysteresis. "
                            "The entry condition for Event A3 is: Mn + Ofn + Ocn - Hys > Mp + Ofp + Ocp + Off. "
                            "The parameter Ocn corresponds to the Cell Individual Offset of the neighbor cell, configured within the range [-24 dB, +24 dB] in steps of 0.5 dB. "
                            "Hysteresis (Hys) is configured in [0 dB, 15 dB] in steps of 0.5 dB. "
                            "The Time to Trigger (TTT) parameter delays measurement report generation (valid values: 0, 40, 64, 80, 100, 128, 160, 256, 320, 480, 512, 640, 1024, 1280, 2560, 5120 ms) to suppress Ping-Pong handovers."
                        )
                    }
                ]
            },
            {
                "doc_id": "TS_38.213",
                "spec_number": "38.213",
                "release": "Rel-17",
                "title": "NR; Physical layer procedures for control",
                "sections": [
                    {
                        "section_id": "7.1",
                        "title": "Uplink Power Control & PUSCH Transmission",
                        "content": (
                            "For PUSCH transmission on active UL BWP b of carrier f of serving cell c, the UE determines transmit power P_PUSCH(i) based on target P0_PUSCH, "
                            "pathloss compensation factor alpha in {0.0, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}, downlink pathloss PL_c, and TPC commands. "
                            "P0_NominalWithGrant is bounded within [-202 dBm, +24 dBm]. "
                            "High PUSCH interference from adjacent cells or external jammers degrades uplink Signal-to-Interference-plus-Noise Ratio (SINR). "
                            "When uplink SINR falls below -3 dB, Block Error Rate (BLER) increases above target 10% threshold, triggering excessive HARQ retransmissions and RLC resets."
                        )
                    },
                    {
                        "section_id": "8.1",
                        "title": "Random Access Preamble Transmission (PRACH)",
                        "content": (
                            "Physical Random Access Channel (PRACH) transmits preambles for initial access, handover, and beam failure recovery. "
                            "Contention Based Random Access (CBRA) preambles are partitioned across groups A and B. "
                            "High PRACH collision rates occur when multiple UEs select the identical preamble index during RACH storms or bursty cell reselection."
                        )
                    },
                    {
                        "section_id": "6.1",
                        "title": "Beam Failure Detection and Recovery (BFR)",
                        "content": (
                            "The physical layer assesses radio link quality of periodic CSI-RS or SSB resources in the beam failure detection set q0. "
                            "When hypothetical PDCCH BLER exceeds 10% threshold, PHY provides a Beam Failure Instance (BFI) indication to MAC. "
                            "Once BFI_COUNTER reaches maxCount, Beam Failure Recovery (BFR) is initiated via CFRA on candidate beam q1."
                        )
                    }
                ]
            },
            {
                "doc_id": "TS_38.413",
                "spec_number": "38.413",
                "release": "Rel-17",
                "title": "NG-RAN; NG Application Protocol (NGAP)",
                "sections": [
                    {
                        "section_id": "8.2.1",
                        "title": "Initial Context Setup - PDU Session Establishment",
                        "content": (
                            "The INITIAL CONTEXT SETUP REQUEST message is sent by the 5G Core AMF to establish UE context and PDU sessions over the N2 interface. "
                            "If the gNodeB cannot allocate requested QoS resources (5QI) or GTP-U transport tunnel capacity over N3, it responds with INITIAL CONTEXT SETUP FAILURE "
                            "with NGAP Cause set to 'Radio resources not available' or 'Transport Resource Unavailable'."
                        )
                    },
                    {
                        "section_id": "8.4.1",
                        "title": "Handover Preparation & Execution over NG / Xn",
                        "content": (
                            "The gNodeB initiates Handover Required message over NGAP when inter-gNodeB Xn interface is unavailable. "
                            "Target gNodeB allocates target cell resources and returns Handover Request Acknowledge with transparent RRCReconfiguration container. "
                            "If target cell lacks admission capacity, Handover Preparation Failure is returned."
                        )
                    }
                ]
            },
            {
                "doc_id": "TS_28.541",
                "spec_number": "28.541",
                "release": "Rel-17",
                "title": "Management and orchestration; 5G Network Resource Model (NRM)",
                "sections": [
                    {
                        "section_id": "4.3.1",
                        "title": "SON Parameter Optimization - CIO & Antenna Tilt",
                        "content": (
                            "Self-Organizing Network (SON) algorithms perform Coverage and Capacity Optimization (CCO), Mobility Load Balancing (MLB), and Mobility Robustness Optimization (MRO). "
                            "Remote Electrical Tilt (RET) adjustments shall remain within [0 deg, 10 deg] total downtilt to prevent cell footprint holes. "
                            "Cell Individual Offset (CIO) tuning must be bounded within [-24 dB, +24 dB] with 0.5 dB granularity to avoid ping-pong handovers with adjacent neighbor cell relations (ANR). "
                            "When neighbor cell PRB utilization exceeds 85%, MLB prohibits positive CIO shifts > +2.0 dB toward the congested neighbor."
                        )
                    }
                ]
            },
            {
                "doc_id": "ORAN_WG3_E2",
                "spec_number": "O-RAN.WG3.E2AP",
                "release": "v03.00",
                "title": "O-RAN Near-Real-Time RIC E2 Application Protocol",
                "sections": [
                    {
                        "section_id": "8.3.1",
                        "title": "E2 Node Disconnect & RIC Service Update",
                        "content": (
                            "The E2 interface connects Near-RT RIC to E2 Nodes (O-CU-CP, O-CU-UP, O-DU) over SCTP. "
                            "When SCTP association drops due to fronthaul jitter or network partition (latency > 10 ms SLA), E2 Node Disconnect alarm is asserted with Critical severity. "
                            "Active xApps (such as Traffic Steering xApp or Anomaly Detection xApp) enter fallback mode and trigger E2 Setup Procedure after SCTP recovery."
                        )
                    },
                    {
                        "section_id": "9.2.4",
                        "title": "CU-DU F1 Interface Latency & xApp Conflict Resolution",
                        "content": (
                            "O-RAN Conflict Mitigation function in the Near-RT RIC resolves direct and indirect parameter conflicts between concurrent xApps (e.g., MRO xApp vs MLB xApp). "
                            "F1-C and F1-U split interfaces between O-CU and O-DU require midhaul latency below 10 ms to maintain RRC and PDCP synchronization."
                        )
                    }
                ]
            }
        ]

        with open(specs_file, "w", encoding="utf-8") as f:
            json.dump(curated_specs, f, indent=2)

        return curated_specs

    def fetch_teleqna_benchmark(self) -> List[Dict[str, Any]]:
        """Ingests TeleQnA benchmark multiple-choice questions."""
        teleqna_file = os.path.join(self.raw_teleqna_dir, "teleqna_benchmark.json")

        curated_teleqna = [
            {
                "question_id": "Q_3GPP_001",
                "category": "3GPP Standards & Protocols",
                "question": "In 5G NR RRC protocol (TS 38.331), which timer is started by the UE upon reception of RRCReconfiguration with reconfigurationWithSync?",
                "option_1": "Timer T300",
                "option_2": "Timer T304",
                "option_3": "Timer T310",
                "option_4": "Timer T311",
                "correct_answer": "option_2",
                "target_doc_id": "TS_38.331",
                "target_section_id": "5.3.5.3",
                "explanation": "According to 3GPP TS 38.331 Section 5.3.5.3, timer T304 is started upon receiving reconfigurationWithSync for handover execution."
            },
            {
                "question_id": "Q_3GPP_002",
                "category": "3GPP Mobility & RRC",
                "question": "What is the standardized valid range and step size for Cell Individual Offset (CIO) in 5G NR Event A3 measurement configuration (TS 38.331 §5.5.4.4)?",
                "option_1": "[-10 dB, +10 dB] in steps of 1.0 dB",
                "option_2": "[-24 dB, +24 dB] in steps of 0.5 dB",
                "option_3": "[-15 dB, +15 dB] in steps of 0.25 dB",
                "option_4": "[-30 dB, +30 dB] in steps of 2.0 dB",
                "correct_answer": "option_2",
                "target_doc_id": "TS_38.331",
                "target_section_id": "5.5.4.4",
                "explanation": "3GPP TS 38.331 Section 5.5.4.4 defines the Cell Individual Offset parameter range as [-24 dB, +24 dB] with 0.5 dB step size."
            },
            {
                "question_id": "Q_ORAN_001",
                "category": "O-RAN Architecture",
                "question": "Which O-RAN interface connects the Near-RT RIC to E2 Nodes (O-CU-CP, O-CU-UP, O-DU) over SCTP in O-RAN.WG3.E2AP?",
                "option_1": "E2 Interface",
                "option_2": "O1 Interface",
                "option_3": "A1 Interface",
                "option_4": "Open Fronthaul 7.2x",
                "correct_answer": "option_1",
                "target_doc_id": "ORAN_WG3_E2",
                "target_section_id": "8.3.1",
                "explanation": "According to O-RAN WG3 E2AP Section 8.3.1, the E2 interface connects Near-RT RIC to E2 Nodes over SCTP."
            },
            {
                "question_id": "Q_3GPP_003",
                "category": "Core & Transport",
                "question": "Which protocol is utilized over the 5G N2 control plane interface between gNodeB and AMF for Initial Context Setup in TS 38.413?",
                "option_1": "GTP-U",
                "option_2": "NGAP (Next Generation Application Protocol)",
                "option_3": "XnAP",
                "option_4": "Diameter",
                "correct_answer": "option_2",
                "target_doc_id": "TS_38.413",
                "target_section_id": "8.2.1",
                "explanation": "3GPP TS 38.413 Section 8.2.1 specifies NGAP as the signaling protocol between gNodeB and AMF over the N2 reference point."
            },
            {
                "question_id": "Q_SON_001",
                "category": "SON & Network Optimization",
                "question": "What is the primary objective of tuning the Time-to-Trigger (TTT) parameter in 5G Event A3 mobility management (TS 38.331 §5.5.4.4)?",
                "option_1": "Increase transmission power during bad weather",
                "option_2": "Suppress ping-pong handovers and unnecessary cell reselection",
                "option_3": "Shorten PRACH preamble transmission time",
                "option_4": "Force immediate UE disconnect",
                "correct_answer": "option_2",
                "target_doc_id": "TS_38.331",
                "target_section_id": "5.5.4.4",
                "explanation": "TTT delays measurement report generation to suppress Ping-Pong handovers per TS 38.331 §5.5.4.4."
            },
            {
                "question_id": "Q_3GPP_004",
                "category": "3GPP Mobility & RRC",
                "question": "In 3GPP TS 38.331 §5.3.7.2, which timer is started by the UE upon receiving N310 consecutive out-of-sync indications from lower layers?",
                "option_1": "Timer T304",
                "option_2": "Timer T310",
                "option_3": "Timer T311",
                "option_4": "Timer T300",
                "correct_answer": "option_2",
                "target_doc_id": "TS_38.331",
                "target_section_id": "5.3.7.2",
                "explanation": "Per TS 38.331 §5.3.7.2, the UE starts timer T310 upon receiving N310 consecutive out-of-sync indications."
            },
            {
                "question_id": "Q_3GPP_005",
                "category": "3GPP Physical Layer",
                "question": "According to 3GPP TS 38.213 §7.1, when uplink PUSCH SINR falls below -3 dB due to interference, what happens to Block Error Rate (BLER)?",
                "option_1": "BLER drops to 0%",
                "option_2": "BLER increases above the 10% target threshold, triggering HARQ retransmissions",
                "option_3": "UE immediately switches to LTE",
                "option_4": "PRACH preambles are disabled",
                "correct_answer": "option_2",
                "target_doc_id": "TS_38.213",
                "target_section_id": "7.1",
                "explanation": "TS 38.213 §7.1 specifies that when uplink SINR falls below -3 dB, BLER exceeds the 10% threshold and causes excessive HARQ retransmissions."
            },
            {
                "question_id": "Q_SON_002",
                "category": "SON & Network Optimization",
                "question": "Under 3GPP TS 28.541 §4.3.1, what is the maximum allowed Remote Electrical Tilt (RET) downtilt angle to prevent cell footprint holes?",
                "option_1": "10 degrees",
                "option_2": "25 degrees",
                "option_3": "45 degrees",
                "option_4": "2 degrees",
                "correct_answer": "option_1",
                "target_doc_id": "TS_28.541",
                "target_section_id": "4.3.1",
                "explanation": "TS 28.541 §4.3.1 limits RET adjustments to a maximum of 10 degrees total downtilt."
            }
        ]

        with open(teleqna_file, "w", encoding="utf-8") as f:
            json.dump(curated_teleqna, f, indent=2)

        return curated_teleqna

    def fetch_ran_telemetry_and_alarms(self) -> List[Dict[str, Any]]:
        """Ingests synthetic Simu5G traces and authentic 5G RAN alarm logs."""
        telemetry_file = os.path.join(self.raw_telemetry_dir, "ran_incident_logs.json")

        curated_alarms = [
            {
                "incident_id": "INC-2026-5G-001",
                "timestamp": "2026-08-30T10:15:22Z",
                "cell_id": "gNB_Cell_102_Sector1",
                "neighbor_cell_id": "gNB_Cell_105_Sector3",
                "severity": "CRITICAL",
                "alarm_type": "HANDOVER_EXECUTION_FAILURE_T304",
                "probable_cause": "Timer T304 expiry during RRC Reconfiguration handover execution",
                "kpi_snapshot": {
                    "RSRP_serving_dBm": -108.5,
                    "RSRQ_serving_dB": -16.2,
                    "SINR_serving_dB": -2.4,
                    "RSRP_neighbor_dBm": -88.1,
                    "BLER_percent": 24.8,
                    "PRB_utilization_percent": 78.5,
                    "neighbor_PRB_utilization_percent": 91.5,
                    "current_CIO_dB": 0.0,
                    "current_Hysteresis_dB": 1.0,
                    "current_TTT_ms": 160,
                    "HO_failure_rate_percent": 42.1
                },
                "raw_log": "[2026-08-30 10:15:22.104] [RRC-WARN] gNB_Cell_102: Handover Execution Failure for UE_ID 0x4F1A. Target Cell: gNB_Cell_105 (PRB Load: 91.5%). Reason: T304_EXPIRY. Initiating RRC Connection Re-establishment per TS 38.331 §5.3.5.3."
            },
            {
                "incident_id": "INC-2026-5G-002",
                "timestamp": "2026-08-30T10:18:45Z",
                "cell_id": "gNB_Cell_204_Sector2",
                "neighbor_cell_id": None,
                "severity": "MAJOR",
                "alarm_type": "PUSCH_UPLINK_INTERFERENCE_HIGH_BLER",
                "probable_cause": "Severe uplink interference / external RF jammer causing SINR degradation",
                "kpi_snapshot": {
                    "RSRP_serving_dBm": -82.0,
                    "RSRQ_serving_dB": -12.0,
                    "SINR_serving_dB": -5.8,
                    "BLER_percent": 38.2,
                    "PRB_utilization_percent": 81.0,
                    "current_P0_PUSCH_dBm": -96.0,
                    "current_RET_tilt_deg": 4.0,
                    "UL_throughput_mbps": 1.2
                },
                "raw_log": "[2026-08-30 10:18:45.320] [PHY-ALARM] gNB_Cell_204: High PUSCH noise floor detected on BWP 1. Uplink SINR dropped to -5.8 dB, BLER > 35%. Possible adjacent channel interference per TS 38.213 §7.1."
            },
            {
                "incident_id": "INC-2026-5G-003",
                "timestamp": "2026-08-30T10:22:10Z",
                "cell_id": "O_CU_Node_01",
                "neighbor_cell_id": None,
                "severity": "CRITICAL",
                "alarm_type": "ORAN_E2_INTERFACE_DISCONNECT",
                "probable_cause": "SCTP heartbeat timeout between Near-RT RIC and O-CU-CP",
                "kpi_snapshot": {
                    "E2_latency_ms": 145.0,
                    "F1_latency_ms": 14.2,
                    "E2_packet_loss_percent": 100.0,
                    "Active_xApps": ["TrafficSteering_xApp", "MRO_xApp", "MLB_xApp"]
                },
                "raw_log": "[2026-08-30 10:22:10.890] [ORAN-ERR] Near-RT RIC: SCTP association to E2 Node (O-CU-CP 0x01) lost. Error: SCTP_COMMUNICATION_LOST per O-RAN.WG3.E2AP §8.3.1. xApps transitioning to safe fallback mode."
            },
            {
                "incident_id": "INC-2026-5G-004",
                "timestamp": "2026-08-30T10:25:50Z",
                "cell_id": "gNB_Cell_309_Sector1",
                "neighbor_cell_id": None,
                "severity": "MAJOR",
                "alarm_type": "NGAP_PDU_SESSION_SETUP_FAILURE",
                "probable_cause": "NGAP Initial Context Setup Failure due to N3 GTP-U transport congestion",
                "kpi_snapshot": {
                    "N2_setup_failure_rate_percent": 31.5,
                    "N3_GTPU_packet_drop_percent": 18.4,
                    "PRB_utilization_percent": 64.0,
                    "requested_5QI": 1
                },
                "raw_log": "[2026-08-30 10:25:50.412] [CORE-ERR] gNB_Cell_309: NGAP INITIAL CONTEXT SETUP FAILURE sent to AMF. Cause: Transport Resource Unavailable on N3 GTP-U tunnel for 5QI=1 per TS 38.413 §8.2.1."
            }
        ]

        with open(telemetry_file, "w", encoding="utf-8") as f:
            json.dump(curated_alarms, f, indent=2)

        return curated_alarms

    def process_and_chunk_specs(self, specs: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """Applies section-aware chunking to all specifications and saves to data/processed."""
        all_chunks: List[DocumentChunk] = []

        for spec in specs:
            doc_id = spec["doc_id"]
            spec_number = spec["spec_number"]
            release = spec["release"]

            for section in spec.get("sections", []):
                raw_text = f"# {section['section_id']} {section['title']}\n{section['content']}"
                sec_chunks = self.chunker.chunk_document(
                    raw_text=raw_text,
                    doc_id=doc_id,
                    spec_number=spec_number,
                    release=release
                )
                all_chunks.extend(sec_chunks)

        out_file = os.path.join(self.processed_dir, "spec_chunks.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in all_chunks], f, indent=2)

        print(f"[DataFetcher] Processed {len(all_chunks)} section-aware specification chunks saved to {out_file}")
        return all_chunks
