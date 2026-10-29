"""
Generates an ultra-crisp, publication-grade 5-stage architecture diagram for the IEEE paper.
Saves directly as pipeline.jpeg and fig1_architecture.png with exact spellings, correct Qwen 2.5 3B details,
and precise Stage 4 -> Stage 2 closed-loop feedback loop.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set IEEE-standard typography
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

fig, ax = plt.subplots(figsize=(15, 17.5), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 116)
ax.axis('off')

# Helpers for drawing boxes and cards
def draw_rounded_card(x, y, w, h, bg_color='#ffffff', border_color='#cbd5e1', border_width=1.2, radius=1.0, linestyle='-'):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.2,rounding_size={radius}",
        linewidth=border_width, edgecolor=border_color, facecolor=bg_color, linestyle=linestyle
    )
    ax.add_patch(rect)

def draw_header_pill(x, y, w, h, text, bg_color='#1e293b', text_color='#ffffff', fontsize=10):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.2,rounding_size=0.8",
        linewidth=0, facecolor=bg_color
    )
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontweight='bold', fontsize=fontsize, color=text_color)

# -----------------------------------------------------------------------------
# STAGE 1: KNOWLEDGE INGESTION & HYBRID RETRIEVAL (Y: 92 to 114)
# -----------------------------------------------------------------------------
draw_rounded_card(2, 92, 96, 22, bg_color='#f8fafc', border_color='#0284c7', border_width=1.6)
draw_header_pill(4, 110.5, 92, 2.8, "STAGE 1: KNOWLEDGE INGESTION & DYNAMIC EVIDENCE-WEIGHTED HYBRID RETRIEVAL", bg_color='#0284c7')

# 1.1 Inputs Box
draw_rounded_card(4, 93.5, 23, 15.5, bg_color='#ffffff', border_color='#94a3b8', border_width=1.0)
ax.text(15.5, 107.2, "Multi-Modal Telecom Inputs", ha='center', va='center', fontweight='bold', fontsize=9.2, color='#0f172a')
inputs_text = (
    "• 3GPP Technical Specs\n"
    "   (TS 38.331, 38.213, 28.541)\n"
    "• O-RAN Alliance Standards\n"
    "   (O-RAN.WG3.E2AP v03.00)\n"
    "• TeleQnA Benchmark (10k MCQs)\n"
    "• Simu5G & OMNeT++ Traces\n"
    "• Live RAN Alarms & Telemetry\n"
    "   (SINR, BLER, RSRP, PRB)"
)
ax.text(5.5, 100.0, inputs_text, ha='left', va='center', fontsize=8.2, color='#334155', linespacing=1.35)

# Forward arrow 1.1 -> 1.2
ax.annotate("", xy=(30.5, 101.2), xytext=(27, 101.2),
            arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.45", lw=1.8, color="#0284c7"))

# 1.2 Preprocessing Pipeline Box
draw_rounded_card(31, 93.5, 26, 15.5, bg_color='#ffffff', border_color='#94a3b8', border_width=1.0)
ax.text(44, 107.2, "Standards Preprocessing Pipeline", ha='center', va='center', fontweight='bold', fontsize=9.2, color='#0f172a')
prep_text = (
    "• Hierarchical Section Parser\n"
    "   (L = 512 tokens, o = 64 overlap)\n"
    "• 500+ Telecom Acronym Expander\n"
    "   (RRC, SINR, PUSCH, CIO, RET)\n"
    "• Structured Metadata Enrichment\n"
    "   (Spec ID, Version, Section,\n"
    "    Clause Title, Protocol Layer)\n"
    "• Persistent ChromaDB Indexing"
)
ax.text(32.5, 100.0, prep_text, ha='left', va='center', fontsize=8.2, color='#334155', linespacing=1.35)

# Forward arrow 1.2 -> 1.3
ax.annotate("", xy=(60.5, 101.2), xytext=(57, 101.2),
            arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.45", lw=1.8, color="#0284c7"))

# 1.3 Hybrid Retrieval & EWRRF Engine Box
draw_rounded_card(61, 93.5, 35, 15.5, bg_color='#f0f9ff', border_color='#0284c7', border_width=1.2)
ax.text(78.5, 107.2, "Dynamic EWRRF Retrieval Engine", ha='center', va='center', fontweight='bold', fontsize=9.5, color='#0369a1')
ewrrf_text = (
    "1. Sparse BM25 Lexical Search (Rank r_B, Weight w_B = 0.45)\n"
    "2. Dense Semantic Cosine Search (Rank r_D, Weight w_D = 0.55)\n"
    "3. BGE Cross-Encoder Semantic Re-Ranker: C_CE(q, d)\n"
    "4. Normative Protocol Evidence Match: E(q, d) for\n"
    "    Timers (T300, T304, T310) & Exact Clause Headings\n"
    "-------------------------------------------------------------------\n"
    "EWRRF(q, d) = α·RRF_weighted + β·C_CE(q, d) + γ·E(q, d)\n"
    "==> Top-5 Clause Candidate Set Output"
)
ax.text(62.5, 100.0, ewrrf_text, ha='left', va='center', fontsize=8.0, color='#0c4a6e', linespacing=1.3)

# Downward Arrow: Stage 1 -> Stage 2
ax.annotate("", xy=(50, 89.5), xytext=(50, 92),
            arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.5", lw=2.2, color="#0f172a"))

# -----------------------------------------------------------------------------
# STAGE 2: SUPERVISOR & DYNAMIC TASK DELEGATOR (Y: 71 to 89)
# -----------------------------------------------------------------------------
draw_rounded_card(2, 71, 96, 18, bg_color='#fdf4ff', border_color='#7c3aed', border_width=1.6)
draw_header_pill(4, 85.5, 92, 2.6, "STAGE 2: SUPERVISOR AGENT & DYNAMIC TASK DELEGATION (DAG)", bg_color='#7c3aed')

# 4 Sequential Steps in Stage 2
s2_steps = [
    (4, 72.5, 21, 11.5, "1. Acronym & Entity\nNormalizer",
     "• Expands Telecom Acronyms\n• Canonical Entity Extraction\n• Standard Timer Identification\n  (e.g., T300, T304, T310)"),
    (28, 72.5, 21, 11.5, "2. Intent & Layer\nClassifier",
     "• Spec Q&A Inquiry\n• Single-Layer Anomaly\n• Correlated Multi-Layer\n  Incident (PHY + RRC + SON)"),
    (52, 72.5, 21, 11.5, "3. Dynamic Task\nDelegator (DAG)",
     "• Instantiates Graph G = (V, E)\n• Prerequisite Edge Mapping\n• Parallel Task Scheduling\n• Dependent Task Chaining"),
    (76, 72.5, 20, 11.5, "4. Agent Router\n& Dispatcher",
     "• Schedules Target Specialists\n• Attaches 3GPP Context\n• Injects Live Telemetry Slice\n• Manages Agent Execution")
]

for x_b, y_b, w_b, h_b, t_b, c_b in s2_steps:
    draw_rounded_card(x_b, y_b, w_b, h_b, bg_color='#ffffff', border_color='#c084fc', border_width=1.0)
    ax.text(x_b + w_b/2, y_b + h_b*0.77, t_b, ha='center', va='center', fontweight='bold', fontsize=8.8, color='#581c87')
    ax.text(x_b + 1.0, y_b + h_b*0.35, c_b, ha='left', va='center', fontsize=7.8, color='#334155', linespacing=1.3)

# Horizontal connectors inside Stage 2
ax.annotate("", xy=(27.5, 78.2), xytext=(25, 78.2), arrowprops=dict(arrowstyle="->", lw=1.5, color="#7c3aed"))
ax.annotate("", xy=(51.5, 78.2), xytext=(49, 78.2), arrowprops=dict(arrowstyle="->", lw=1.5, color="#7c3aed"))
ax.annotate("", xy=(75.5, 78.2), xytext=(73, 78.2), arrowprops=dict(arrowstyle="->", lw=1.5, color="#7c3aed"))

# Downward Arrow: Stage 2 -> Stage 3
ax.annotate("", xy=(50, 68.5), xytext=(50, 71),
            arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.5", lw=2.2, color="#0f172a"))

# -----------------------------------------------------------------------------
# STAGE 3: PROTOCOL-SPECIALIZED DOMAIN AGENTS (6) (Y: 48 to 68)
# -----------------------------------------------------------------------------
draw_rounded_card(2, 48, 96, 20, bg_color='#fffbeb', border_color='#d97706', border_width=1.6)
draw_header_pill(4, 64.5, 92, 2.6, "STAGE 3: PROTOCOL-SPECIALIZED DOMAIN AGENTS (6 SPECIALISTS)", bg_color='#d97706')

agents = [
    (4, 56.5, 30, 6.8, "1. Mobility & RRC Agent (TS 38.331)",
     "• Handover Failure & Event A3 Analysis\n• Timers T300 (Setup), T304 (HO), T310 (RLF)\n• Radio Link Failure & Re-establishment"),
    (35, 56.5, 30, 6.8, "2. Physical & Quality Agent (TS 38.213)",
     "• Uplink PUSCH / PUCCH SINR Tracking\n• Block Error Rate (BLER > 10% threshold)\n• Open-loop Power Control (P0) & Alpha"),
    (66, 56.5, 30, 6.8, "3. O-RAN & Interface Agent (O-RAN.WG3)",
     "• Near-RT RIC E2AP SCTP Connection\n• F1-C / F1-U Latency SLA (<= 10 ms)\n• xApp Conflict Detection (Mobility vs MLB)"),
    (4, 49.0, 30, 6.8, "4. Core & Transport Agent (TS 38.413)",
     "• NGAP Signaling Cause Codes & Drops\n• PDU Session Establishment Failures\n• User-Plane GTP-U Transport Packet Loss"),
    (35, 49.0, 30, 6.8, "5. Specification Q&A Agent (3GPP/O-RAN)",
     "• Normative Clause & Architecture Search\n• Deep Cross-Encoder Ranking of Clauses\n• Standardized Procedural Definitions"),
    (66, 49.0, 30, 6.8, "6. SON Optimization & Healing Agent (TS 28.541)",
     "• Synthesizes Self-Healing Parameter Actions\n• Cell Individual Offset (CIO) Calculation\n• Hysteresis, Time-To-Trigger (TTT), & Tilt")
]

for x_a, y_a, w_a, h_a, t_a, c_a in agents:
    draw_rounded_card(x_a, y_a, w_a, h_a, bg_color='#ffffff', border_color='#f59e0b', border_width=1.0)
    ax.text(x_a + w_a/2, y_a + h_a*0.77, t_a, ha='center', va='center', fontweight='bold', fontsize=8.4, color='#78350f')
    ax.text(x_a + 1.0, y_a + h_a*0.35, c_a, ha='left', va='center', fontsize=7.5, color='#334155', linespacing=1.25)

# Downward Arrow: Stage 3 -> Stage 4
ax.annotate("", xy=(50, 45.5), xytext=(50, 48),
            arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.5", lw=2.2, color="#0f172a"))

# -----------------------------------------------------------------------------
# STAGE 4: CITATION & GUARDRAIL VERIFIER (PROPOSED NOVELTY) (Y: 28 to 45)
# -----------------------------------------------------------------------------
draw_rounded_card(2, 28, 96, 17, bg_color='#fef2f2', border_color='#dc2626', border_width=1.8)
draw_header_pill(4, 41.5, 92, 2.6, "STAGE 4: 3GPP CITATION & GUARDRAIL VERIFIER (CLOSED-LOOP NOVELTY)", bg_color='#dc2626')

s4_blocks = [
    (4, 29.5, 29, 10.8, "1. Citation Grounding Check",
     "• Verifies Specification ID & Version\n• Validates Section / Clause Exists\n• Checks Token & Acronym Evidence Overlap\n• Rejects Unsubstantiated Claims"),
    (35, 29.5, 30, 10.8, "2. Normative Parameter Bounds",
     "• CIO Bounds: [-24, +24] dB (Step: 0.5 dB)\n• Antenna Tilt: RET in [0 deg, 10 deg]\n• Hysteresis: Hys in [0, 15] dB\n• Enforces 3GPP TS 38.331 & TS 28.541"),
    (67, 29.5, 29, 10.8, "3. Neighbor Congestion Guardrail",
     "• Mobility Load Balancing (TS 28.541):\n  If Target Cell PRB > 85%:\n  Hard Cap Delta_CIO <= +2.0 dB\n• Prevents Target Sector Overload")
]

for x_s, y_s, w_s, h_s, t_s, c_s in s4_blocks:
    draw_rounded_card(x_s, y_s, w_s, h_s, bg_color='#ffffff', border_color='#f87171', border_width=1.1)
    ax.text(x_s + w_s/2, y_s + h_s*0.77, t_s, ha='center', va='center', fontweight='bold', fontsize=8.8, color='#991b1b')
    ax.text(x_s + 1.0, y_s + h_s*0.35, c_s, ha='left', va='center', fontsize=7.8, color='#334155', linespacing=1.3)

# Connectors inside Stage 4
ax.annotate("", xy=(34.5, 35.0), xytext=(33.0, 35.0), arrowprops=dict(arrowstyle="->", lw=1.5, color="#dc2626"))
ax.annotate("", xy=(66.5, 35.0), xytext=(65.0, 35.0), arrowprops=dict(arrowstyle="->", lw=1.5, color="#dc2626"))

# =============================================================================
# CLOSED-LOOP FEEDBACK PATH: Stage 4 -> Stage 2 (RED DASHED LINE & CALLOUT)
# =============================================================================
# Draw dashed arrow going right from Stage 4, up, and back into Stage 2
ax.annotate("", xy=(98.5, 78.5), xytext=(98.5, 35.0),
            arrowprops=dict(arrowstyle="->,head_width=0.45,head_length=0.55", lw=2.2, color="#dc2626", linestyle="--"))
ax.plot([96.0, 98.5], [35.0, 35.0], color='#dc2626', lw=2.2, linestyle='--')
ax.plot([98.5, 96.0], [78.5, 78.5], color='#dc2626', lw=2.2, linestyle='--')

# Feedback loop descriptive badge (centered on the right margin)
draw_rounded_card(73, 21.0, 25, 5.8, bg_color='#fff1f2', border_color='#dc2626', border_width=1.2, linestyle='--')
ax.text(85.5, 24.8, "REFLECTIVE FEEDBACK LOOP", ha='center', va='center', fontweight='bold', fontsize=7.8, color='#991b1b')
ax.text(85.5, 22.5, "Re-routes violated parameters (e.g. +6 dB)\nwith 3GPP clause critique for autonomous fix", ha='center', va='center', fontsize=7.0, color='#7f1d1d', linespacing=1.2)

# Downward Arrow: Stage 4 -> Stage 5
ax.annotate("", xy=(50, 24.5), xytext=(50, 27.5),
            arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.5", lw=2.2, color="#0f172a"))
ax.text(50.8, 26.0, "Verified & Compliant Triage", ha='left', va='center', fontsize=8.0, fontweight='bold', color='#15803d')

# -----------------------------------------------------------------------------
# STAGE 5: CONSENSUS SYNTHESIS & NOC INTERFACE (Y: 2 to 24)
# -----------------------------------------------------------------------------
draw_rounded_card(2, 2, 96, 22, bg_color='#f0fdf4', border_color='#16a34a', border_width=1.8)
draw_header_pill(4, 20.5, 92, 2.6, "STAGE 5: NEURAL CONSENSUS & EXPLAINABLE NOC OPERATOR INTERFACE", bg_color='#16a34a')

# 5.1 Consensus & Local Neural Engine (QWEN 2.5 3B INSTRUCT)
draw_rounded_card(4, 3.5, 45, 15.5, bg_color='#ffffff', border_color='#22c55e', border_width=1.3)
ax.text(26.5, 16.8, "Local Neural Synthesis & Consensus Engine", ha='center', va='center', fontweight='bold', fontsize=9.2, color='#14532d')

# Special Highlight Box for Qwen 2.5 3B Instruct
draw_rounded_card(6, 11.2, 41, 4.2, bg_color='#dcfce7', border_color='#16a34a', border_width=1.2)
ax.text(26.5, 13.8, "MODEL: Qwen 2.5 3B Instruct (4-Bit GGUF, q4_k_m)", ha='center', va='center', fontweight='bold', fontsize=8.6, color='#14532d')
ax.text(26.5, 12.2, "Local Edge GPU Offload (RTX 4050 6GB) • 100% Offline / Zero Cloud", ha='center', va='center', fontsize=7.2, color='#166534')

s5_details = (
    "• Multi-Agent Consensus Aggregation across 6 domains\n"
    "• Chain-of-Thought (CoT) Diagnostic Reasoning Trace\n"
    "• Normative 3GPP Evidence & Clause Grounding Binding\n"
    "• Prescriptive Step-by-Step Remediation Action Plan\n"
    "• TeleMCP Standardized Diagnostic Schema Serialization"
)
ax.text(5.5, 7.2, s5_details, ha='left', va='center', fontsize=7.8, color='#1f2937', linespacing=1.3)

# Forward connector 5.1 -> 5.2
ax.annotate("", xy=(52.5, 11.2), xytext=(49.5, 11.2),
            arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.45", lw=1.8, color="#16a34a"))

# 5.2 Explainable NOC Operator Interface Dashboard
draw_rounded_card(53, 3.5, 43, 15.5, bg_color='#ffffff', border_color='#22c55e', border_width=1.3)
ax.text(74.5, 16.8, "Explainable NOC Operator Interface (Flask Console)", ha='center', va='center', fontweight='bold', fontsize=9.2, color='#14532d')

noc_text = (
    "1. Ranked Root-Cause Cards (e.g. Uplink PUSCH SINR Degradation)\n"
    "2. Standardized 3GPP & O-RAN Normative Evidence Badges\n"
    "3. Step-by-Step Prescriptive Engineering Actions for Field Ops\n"
    "4. Verified SON Parameter Matrix (CIO = +2.0 dB, Hys = 2.5 dB)\n"
    "5. Interactive Specification Drawer (Slide-out Clause Viewer)\n"
    "6. Real-time Verification Status & Confidence Fidelity Score"
)
ax.text(54.5, 9.8, noc_text, ha='left', va='center', fontsize=7.8, color='#1f2937', linespacing=1.35)

plt.tight_layout()

# Save as both pipeline.jpeg and fig1_architecture.png in overleaf figures
out_dir = r"D:\Vit\SEM 5\F2-NLP\NLP Project\overleaf_ieee_paper\figures"
jpeg_path = os.path.join(out_dir, "pipeline.jpeg")
png_path = os.path.join(out_dir, "fig1_architecture.png")
root_jpeg = r"D:\Vit\SEM 5\F2-NLP\NLP Project\pipeline.jpeg"

plt.savefig(jpeg_path, dpi=300, format='jpeg', bbox_inches='tight')
plt.savefig(png_path, dpi=300, format='png', bbox_inches='tight')
plt.savefig(root_jpeg, dpi=300, format='jpeg', bbox_inches='tight')
plt.close()

print(f"Successfully generated perfect architecture diagrams at:\n1) {jpeg_path}\n2) {png_path}\n3) {root_jpeg}")
