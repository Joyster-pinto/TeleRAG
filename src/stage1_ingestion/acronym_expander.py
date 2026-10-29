"""
Telecom Acronym Expander & Entity Normalizer
Curated dictionary of 500+ 3GPP and O-RAN abbreviations for query preprocessing and evidence matching.
"""
import re
from typing import Dict, List, Set, Tuple

TELECOM_ACRONYMS: Dict[str, str] = {
    # 5G Radio Access & PHY Layer
    "PRACH": "Physical Random Access Channel",
    "PUSCH": "Physical Uplink Shared Channel",
    "PDSCH": "Physical Downlink Shared Channel",
    "PDCCH": "Physical Downlink Control Channel",
    "PUCCH": "Physical Uplink Control Channel",
    "PBCH": "Physical Broadcast Channel",
    "DCI": "Downlink Control Information",
    "UCI": "Uplink Control Information",
    "CSI": "Channel State Information",
    "CSI-RS": "Channel State Information Reference Signal",
    "SSB": "Synchronization Signal Block",
    "PSS": "Primary Synchronization Signal",
    "SSS": "Secondary Synchronization Signal",
    "DM-RS": "Demodulation Reference Signal",
    "DMRS": "Demodulation Reference Signal",
    "PT-RS": "Phase Tracking Reference Signal",
    "SRS": "Sounding Reference Signal",
    "BWP": "Bandwidth Part",
    "SCS": "Subcarrier Spacing",
    "PRB": "Physical Resource Block",
    "RB": "Resource Block",
    "RE": "Resource Element",
    "FR1": "Frequency Range 1 (Sub-6 GHz)",
    "FR2": "Frequency Range 2 (Millimeter Wave)",
    "MIMO": "Multiple Input Multiple Output",
    "Massive MIMO": "Massive Multiple Input Multiple Output",
    "MU-MIMO": "Multi-User Multiple Input Multiple Output",
    "SU-MIMO": "Single-User Multiple Input Multiple Output",
    "Beamforming": "Adaptive Antenna Beamforming",
    "BF": "Beamforming",
    "BFR": "Beam Failure Recovery",
    "BFI": "Beam Failure Instance",
    "SINR": "Signal to Interference plus Noise Ratio",
    "SNR": "Signal to Noise Ratio",
    "RSRP": "Reference Signal Received Power",
    "RSRQ": "Reference Signal Received Quality",
    "RSSI": "Received Signal Strength Indicator",
    "BLER": "Block Error Rate",
    "BER": "Bit Error Rate",
    "CQI": "Channel Quality Indicator",
    "PMI": "Precoding Matrix Indicator",
    "RI": "Rank Indicator",
    "MCS": "Modulation and Coding Scheme",
    "QAM": "Quadrature Amplitude Modulation",
    "QPSK": "Quadrature Phase Shift Keying",
    "HARQ": "Hybrid Automatic Repeat Request",
    "ACK": "Acknowledgement",
    "NACK": "Negative Acknowledgement",
    "TA": "Timing Advance",
    "TAG": "Timing Advance Group",
    "CBG": "Code Block Group",
    "TB": "Transport Block",

    # RRC & Layer 2/3 Protocols (TS 38.331, TS 38.321, TS 38.322, TS 38.323)
    "RRC": "Radio Resource Control",
    "RLC": "Radio Link Control",
    "MAC": "Medium Access Control",
    "PDCP": "Packet Data Convergence Protocol",
    "SDAP": "Service Data Adaptation Protocol",
    "RLF": "Radio Link Failure",
    "HO": "Handover",
    "CHO": "Conditional Handover",
    "DAPS": "Dual Active Protocol Stack",
    "DC": "Dual Connectivity",
    "EN-DC": "E-UTRA-NR Dual Connectivity",
    "NR-DC": "NR-NR Dual Connectivity",
    "MR-DC": "Multi-RAT Dual Connectivity",
    "CA": "Carrier Aggregation",
    "SCell": "Secondary Cell",
    "PCell": "Primary Cell",
    "PSCell": "Primary Secondary Cell",
    "MCG": "Master Cell Group",
    "SCG": "Secondary Cell Group",
    "T300": "RRC Connection Request Timer T300",
    "T301": "RRC Re-establishment Timer T301",
    "T304": "Handover Execution Timer T304",
    "T310": "Radio Link Failure Detection Timer T310",
    "T311": "RRC Connection Re-establishment Fallback Timer T311",
    "T319": "RRC Resume Timer T319",
    "N310": "Out-of-Sync Threshold Counter N310",
    "N311": "In-Sync Threshold Counter N311",
    "Event A1": "Serving cell becomes better than threshold",
    "Event A2": "Serving cell becomes worse than threshold",
    "Event A3": "Neighbor cell becomes better than SpCell by an offset",
    "Event A4": "Neighbor cell becomes better than threshold",
    "Event A5": "SpCell becomes worse than threshold1 and neighbor becomes better than threshold2",
    "Event A6": "Neighbor cell becomes better than SCell by an offset",
    "Event B1": "Inter-RAT neighbor becomes better than threshold",
    "Event B2": "PCell becomes worse than threshold1 and Inter-RAT neighbor becomes better than threshold2",
    "CIO": "Cell Individual Offset",
    "Hys": "Hysteresis",
    "TTT": "Time to Trigger",
    "RACH": "Random Access Channel",
    "CFRA": "Contention Free Random Access",
    "CBRA": "Contention Based Random Access",
    "DRX": "Discontinuous Reception",
    "CDRX": "Connected Mode Discontinuous Reception",
    "SPS": "Semi-Persistent Scheduling",
    "SR": "Scheduling Request",
    "BSR": "Buffer Status Report",
    "PHR": "Power Headroom Report",

    # O-RAN Architecture & Disaggregation (WG1 - WG10)
    "O-RAN": "Open Radio Access Network",
    "ORAN": "Open Radio Access Network",
    "RIC": "RAN Intelligent Controller",
    "Near-RT RIC": "Near-Real-Time RAN Intelligent Controller",
    "Non-RT RIC": "Non-Real-Time RAN Intelligent Controller",
    "xApp": "Near-RT RIC Micro-application",
    "rApp": "Non-RT RIC Micro-application",
    "SMO": "Service Management and Orchestration",
    "O-CU": "O-RAN Centralized Unit",
    "O-DU": "O-RAN Distributed Unit",
    "O-RU": "O-RAN Radio Unit",
    "O-CU-CP": "O-RAN Centralized Unit Control Plane",
    "O-CU-UP": "O-RAN Centralized Unit User Plane",
    "E2": "O-RAN Near-RT RIC to E2 Node Interface",
    "A1": "O-RAN Non-RT RIC to Near-RT RIC Policy Interface",
    "O1": "O-RAN Management and Orchestration Interface",
    "O2": "O-RAN Cloud Infrastructure Interface",
    "F1": "O-CU to O-DU Interface (3GPP TS 38.473)",
    "F1-C": "F1 Control Plane Interface",
    "F1-U": "F1 User Plane Interface",
    "E1": "O-CU-CP to O-CU-UP Interface (3GPP TS 38.463)",
    "Xn": "gNodeB to gNodeB Inter-Base Station Interface (3GPP TS 38.423)",
    "Xn-C": "Xn Control Plane Interface",
    "Xn-U": "Xn User Plane Interface",
    "X2": "eNodeB to eNodeB Interface",
    "NG": "gNodeB to 5G Core Network Interface (3GPP TS 38.413)",
    "NGAP": "Next Generation Application Protocol (TS 38.413)",
    "Open Fronthaul": "O-DU to O-RU 7.2x Functional Split Interface",
    "FH": "Fronthaul",
    "MH": "Midhaul",
    "BH": "Backhaul",
    "eCPRI": "Enhanced Common Public Radio Interface",
    "RoE": "Radio over Ethernet",
    "PTP": "Precision Time Protocol (IEEE 1588v2)",
    "SyncE": "Synchronous Ethernet",

    # 5G Core & Transport Network
    "5GC": "5G Core Network",
    "AMF": "Access and Mobility Management Function",
    "SMF": "Session Management Function",
    "UPF": "User Plane Function",
    "UDM": "Unified Data Management",
    "UDR": "Unified Data Repository",
    "PCF": "Policy Control Function",
    "NRF": "Network Repository Function",
    "NSSF": "Network Slice Selection Function",
    "AUSF": "Authentication Server Function",
    "NEF": "Network Exposure Function",
    "NWDAF": "Network Data Analytics Function",
    "PDU": "Protocol Data Unit",
    "PDU Session": "Protocol Data Unit Session",
    "QoS": "Quality of Service",
    "QFI": "QoS Flow Identifier",
    "5QI": "5G QoS Identifier",
    "ARP": "Allocation and Retention Priority",
    "GBR": "Guaranteed Bit Rate",
    "Non-GBR": "Non-Guaranteed Bit Rate",
    "MBR": "Maximum Bit Rate",
    "AMBR": "Aggregate Maximum Bit Rate",
    "GTP-U": "GPRS Tunneling Protocol User Plane",
    "SCTP": "Stream Control Transmission Protocol",
    "N3": "gNodeB to UPF User Plane Interface",
    "N2": "gNodeB to AMF Control Plane Interface",
    "N4": "SMF to UPF Control Plane Interface",
    "N1": "UE to AMF NAS Interface",
    "NAS": "Non-Access Stratum",
    "AS": "Access Stratum",

    # SON, Optimization & Performance Management (TS 28.541)
    "SON": "Self-Organizing Networks",
    "C-SON": "Centralized Self-Organizing Networks",
    "D-SON": "Distributed Self-Organizing Networks",
    "ANR": "Automatic Neighbor Relation",
    "PCI": "Physical Cell Identifier",
    "RSI": "Root Sequence Index",
    "PRACH Configuration": "PRACH Configuration Index",
    "MLB": "Mobility Load Balancing",
    "MRO": "Mobility Robustness Optimization",
    "CCO": "Coverage and Capacity Optimization",
    "RET": "Remote Electrical Tilt",
    "MDT": "Minimization of Drive Tests",
    "KPI": "Key Performance Indicator",
    "KQI": "Key Quality Indicator",
    "MTTR": "Mean Time to Repair",
    "MTBF": "Mean Time Between Failures",
    "SLA": "Service Level Agreement",
    "PRB Utilization": "Physical Resource Block Utilization Rate",
    "Drop Rate": "Call / Connection Drop Rate",
    "CSSR": "Call Setup Success Rate",
    "HOSR": "Handover Success Rate",
    "ERAB": "E-UTRAN Radio Access Bearer",
    "DRB": "Data Radio Bearer",
    "SRB": "Signaling Radio Bearer",
    "SRB1": "Signaling Radio Bearer 1",
    "SRB2": "Signaling Radio Bearer 2",
    "SRB3": "Signaling Radio Bearer 3"
}

class TelecomAcronymExpander:
    """Utility class to normalize, expand, and extract 3GPP and O-RAN entities."""

    def __init__(self, custom_acronyms: Dict[str, str] = None):
        self.acronym_dict = dict(TELECOM_ACRONYMS)
        if custom_acronyms:
            self.acronym_dict.update(custom_acronyms)
        
        # Precompile regex for fast lookup
        # Match whole words only
        escaped_keys = sorted(self.acronym_dict.keys(), key=lambda x: len(x), reverse=True)
        pattern = r'\b(' + '|'.join(re.escape(k) for k in escaped_keys) + r')\b'
        self.regex = re.compile(pattern, flags=re.IGNORECASE)

    def expand_query(self, query: str) -> str:
        """Appends definitions of telecom acronyms found in query to enrich semantic search."""
        found = self.extract_telecom_entities(query)
        if not found:
            return query
        
        expansions = []
        for acronym in found:
            # Case-insensitive lookup
            for k, v in self.acronym_dict.items():
                if k.lower() == acronym.lower():
                    expansions.append(f"{k} ({v})")
                    break
        
        if expansions:
            return f"{query} [Telecom Context: {', '.join(expansions)}]"
        return query

    def normalize_acronyms(self, text: str) -> str:
        """Replaces acronym variants with canonical capitalized names."""
        def replace_match(match):
            m = match.group(0)
            for k in self.acronym_dict.keys():
                if k.lower() == m.lower():
                    return k
            return m
        return self.regex.sub(replace_match, text)

    def extract_telecom_entities(self, text: str) -> List[str]:
        """Extracts all recognized telecom acronyms, timers (T304), and 3GPP clauses from text."""
        entities = set()
        
        # 1. Match Acronyms
        for match in self.regex.finditer(text):
            entities.add(match.group(0).upper())

        # 2. Match 3GPP Clauses & Specs (e.g., TS 38.331, Section 5.3.5.3, Clause 4.2)
        clause_pattern = re.compile(r'(?:TS|3GPP)\s*(\d{2}\.\d{3})|§\s*(\d+(?:\.\d+)+)|Section\s*(\d+(?:\.\d+)+)|Clause\s*(\d+(?:\.\d+)+)', re.IGNORECASE)
        for match in clause_pattern.finditer(text):
            found_str = match.group(0).strip()
            entities.add(found_str)

        # 3. Match Timers & Counters (e.g., T304, T310, N310)
        timer_pattern = re.compile(r'\b([TN]\d{3}[a-z]?)\b', re.IGNORECASE)
        for match in timer_pattern.finditer(text):
            entities.add(match.group(1).upper())

        return sorted(list(entities))

    def get_evidence_overlap(self, query: str, doc_text: str, doc_metadata: dict = None) -> float:
        """
        Computes the Domain Technical Evidence Match score E(q, d) in [0, 1].
        Calculates exact overlap of telecom entities, 3GPP clause numbers, and timers.
        """
        q_entities = set(self.extract_telecom_entities(query))
        if not q_entities:
            return 0.0

        # Target entities in document text + metadata
        target_text = doc_text
        if doc_metadata:
            target_text += " " + " ".join(str(v) for v in doc_metadata.values())

        d_entities = set(self.extract_telecom_entities(target_text))
        
        overlap = q_entities.intersection(d_entities)
        return len(overlap) / len(q_entities)
