"""
Generates high-resolution IEEE publication figures for the Overleaf LaTeX package.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

out_dir = r"D:\Vit\SEM 5\F2-NLP\NLP Project\overleaf_ieee_paper\figures"
os.makedirs(out_dir, exist_ok=True)

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.size"] = 10

# ==============================================================================
# FIGURE 1: 5-Stage System Architecture Diagram (Clean Vector-Style Diagram)
# ==============================================================================
fig, ax = plt.subplots(figsize=(12, 6.2), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 56)
ax.axis("off")

def draw_box(x, y, w, h, title, subtitle="", facecolor="#f0f4f8", edgecolor="#1e3a8a", title_color="#0f172a", fontsize=9):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.4,rounding_size=1.2",
        linewidth=1.5, edgecolor=edgecolor, facecolor=facecolor
    )
    ax.add_patch(rect)
    if subtitle:
        ax.text(x + w/2, y + h*0.66, title, ha="center", va="center", fontweight="bold", fontsize=fontsize, color=title_color)
        ax.text(x + w/2, y + h*0.30, subtitle, ha="center", va="center", fontsize=fontsize-1.3, color="#334155")
    else:
        ax.text(x + w/2, y + h/2, title, ha="center", va="center", fontweight="bold", fontsize=fontsize, color=title_color)

# Stage Headers
stages = [
    (2, 40, 17, 13, "STAGE 1: INGESTION\n& EWRRF RETRIEVAL", "512-Token Section Chunker\nBM25 + Dense Vector Store\nCross-Encoder & Evidence E(q,d)", "#e0f2fe", "#0369a1"),
    (22, 40, 17, 13, "STAGE 2: SUPERVISOR\n& DAG ROUTER", "Acronym Normalizer\nIntent & Layer Classifier\nDynamic DAG Task Delegator", "#ede9fe", "#5b21b6"),
    (42, 40, 18, 13, "STAGE 3: SPECIALIST\nDOMAIN AGENTS (6)", "1. Mobility & RRC  2. PHY Quality\n3. O-RAN & E2/F1  4. Core & NGAP\n5. Spec QnA       6. SON Healing", "#fef3c7", "#b45309"),
    (63, 40, 17, 13, "STAGE 4: GUARDRAIL\nVERIFIER AGENT", "1. Citation Grounding Check\n2. 3GPP Parameter Bounds\n3. Neighbor PRB <= 85% Check", "#fee2e2", "#b91c1c"),
    (83, 40, 15, 13, "STAGE 5: SYNTHESIS\n& NOC INTERFACE", "Multi-Agent Consensus\n4-Bit Quantized Local LLM\nInteractive Spec Drawer", "#dcfce7", "#15803d"),
]

for x, y, w, h, t, sub, fc, ec in stages:
    draw_box(x, y, w, h, t, sub, facecolor=fc, edgecolor=ec, fontsize=8.5)

# Forward Arrows between Stages
arrow_style = dict(arrowstyle="->,head_width=0.35,head_length=0.45", lw=1.8, color="#1e293b")
ax.annotate("", xy=(22, 46.5), xytext=(19, 46.5), arrowprops=arrow_style)
ax.annotate("", xy=(42, 46.5), xytext=(39, 46.5), arrowprops=arrow_style)
ax.annotate("", xy=(63, 46.5), xytext=(60, 46.5), arrowprops=arrow_style)
ax.annotate("", xy=(83, 46.5), xytext=(80, 46.5), arrowprops=arrow_style)

# Detailed Sub-blocks in lower half
draw_box(2, 16, 17, 19, "Normative Corpus\n& Telemetry Inputs",
         "• 3GPP TS 38.331 (RRC)\n• 3GPP TS 38.213 (PHY)\n• 3GPP TS 38.413 (NGAP)\n• 3GPP TS 28.541 (SON)\n• O-RAN.WG3.E2AP\n• Live RAN KPIs & Alarms",
         "#f8fafc", "#475569", fontsize=8.2)

draw_box(22, 16, 17, 19, "EWRRF Scoring\nFormulation",
         "α [ w_D C_D/(k+r_D) +\n    w_B C_B/(k+r_B) ]\n+ β C_CE(q,d)\n+ γ E(q,d)\n\nα+β+γ = 1, w_D+w_B = 1",
         "#f8fafc", "#475569", fontsize=8.2)

draw_box(42, 16, 18, 19, "Domain Analytical\nTool Execution",
         "• rrc_spec_retriever (T300/T304)\n• kpi_anomaly_detect (SINR/BLER)\n• oran_alarm_parser (E2/F1 SLA)\n• ngap_cause_analyzer (N2/N3)\n• son_param_optimizer (CIO/RET)",
         "#f8fafc", "#475569", fontsize=8.0)

draw_box(63, 16, 17, 19, "Normative Safety\nConstraints",
         "• CIO in [-24, +24] dB (0.5 step)\n• RET in [0, 10] deg\n• Hysteresis in [0, 15] dB\n• If Neighbor PRB > 85%:\n   Cap ΔCIO <= +2.0 dB",
         "#fff1f2", "#be123c", fontsize=8.0)

draw_box(83, 16, 15, 19, "Explainable NOC\nOperator Output",
         "• Ranked Root Causes\n• Step-by-Step Workflow\n• Verified SON Parameters\n• Clickable Clause Pills\n• Full 5-Stage CoT Trace",
         "#f0fdf4", "#166534", fontsize=8.0)

# Vertical connectors
for x_c in [10.5, 30.5, 51.0, 71.5, 90.5]:
    ax.annotate("", xy=(x_c, 40), xytext=(x_c, 35), arrowprops=dict(arrowstyle="<->", lw=1.3, color="#64748b"))

# Closed-Loop Feedback Path (Stage 4 -> Stage 2 -> Stage 3)
feedback_rect = patches.FancyBboxPatch(
    (22, 3), 58, 8.5,
    boxstyle="round,pad=0.3,rounding_size=1.0",
    linewidth=1.8, edgecolor="#dc2626", facecolor="#fef2f2", linestyle="--"
)
ax.add_patch(feedback_rect)
ax.text(51, 7.25,
        "CLOSED-LOOP VERIFIER FEEDBACK & SELF-CORRECTION PATH (Stage 4 -> Stage 2 Supervisor -> Stage 3 Agents)\n"
        "Intercepts Out-of-Bounds SON Parameters (e.g., CIO = +6.0 dB on 91.5% Congested Neighbor) & Re-Routes DAG Critique for Re-Evaluation",
        ha="center", va="center", fontweight="bold", fontsize=8.2, color="#991b1b")

ax.annotate("", xy=(71.5, 11.5), xytext=(71.5, 16), arrowprops=dict(arrowstyle="->", lw=2.0, color="#dc2626"))
ax.annotate("", xy=(30.5, 16), xytext=(30.5, 11.5), arrowprops=dict(arrowstyle="->", lw=2.0, color="#dc2626"))

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "fig1_architecture.png"), dpi=300, bbox_inches="tight")
plt.close()

# ==============================================================================
# FIGURE 2: Quantitative Comparison with 3 Baseline Papers
# ==============================================================================
fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=300)

metrics = ["MRR (%)", "Top-5 Recall (%)", "TeleQnA Acc (%)", "Citation Faith. (%)", "SON Compliance (%)"]
telecom_rag = [76.2, 84.5, 78.0, 85.2, 0.0]
telco_rag   = [81.5, 88.4, 82.1, 89.0, 0.0]
tele_llm    = [79.4, 86.0, 83.5, 88.5, 87.0]
ours        = [94.2, 100.0, 87.5, 100.0, 100.0]

x = np.arange(len(metrics))
width = 0.19

b1 = ax.bar(x - 1.5*width, telecom_rag, width, label="TelecomRAG (Yilma et al., 2024)", color="#94a3b8", edgecolor="#1e293b", linewidth=0.7)
b2 = ax.bar(x - 0.5*width, telco_rag, width, label="Telco-RAG (Bornea et al., 2024)", color="#60a5fa", edgecolor="#1e293b", linewidth=0.7)
b3 = ax.bar(x + 0.5*width, tele_llm, width, label="Tele-LLM-Hub (Gajjar et al., 2025)", color="#fbbf24", edgecolor="#1e293b", linewidth=0.7)
b4 = ax.bar(x + 1.5*width, ours, width, label="Proposed Multi-Agent EWRRF (Ours)", color="#16a34a", edgecolor="#1e293b", linewidth=0.7)

ax.set_ylabel("Performance Score (%)", fontweight="bold")
ax.set_title("Quantitative Performance Comparison Against State-of-the-Art Baselines", fontweight="bold", fontsize=10.5)
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontweight="bold", fontsize=8.5)
ax.set_ylim(0, 115)
ax.grid(axis="y", linestyle="--", alpha=0.5)
ax.legend(loc="upper left", fontsize=8, frameon=True)

for bars in [b1, b2, b3, b4]:
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.annotate(f"{h:.1f}",
                        xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(0, 2), textcoords="offset points",
                        ha="center", va="bottom", fontsize=6.8, fontweight="bold")

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "fig2_baseline_comparison.png"), dpi=300, bbox_inches="tight")
plt.close()

# ==============================================================================
# FIGURE 3: Ablation Study & End-to-End Stage Latency Breakdown
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 3.3), dpi=300)

# Subplot 1: Ablation Study
variants = ["Dense\nOnly", "Standard\nRRF", "Proposed\nEWRRF", "EWRRF +\nStage 4 Loop"]
qna_acc = [75.0, 81.2, 87.5, 87.5]
son_comp = [62.5, 75.0, 75.0, 100.0]

x_a = np.arange(len(variants))
w_a = 0.32
ax1.bar(x_a - w_a/2, qna_acc, w_a, label="TeleQnA Accuracy (%)", color="#2563eb", edgecolor="#0f172a")
ax1.bar(x_a + w_a/2, son_comp, w_a, label="SON Safety Compliance (%)", color="#dc2626", edgecolor="#0f172a")
ax1.set_title("(a) Architectural Ablation Study", fontweight="bold", fontsize=9.5)
ax1.set_xticks(x_a)
ax1.set_xticklabels(variants, fontsize=8)
ax1.set_ylim(50, 110)
ax1.set_ylabel("Score (%)", fontweight="bold", fontsize=8.5)
ax1.grid(axis="y", linestyle="--", alpha=0.5)
ax1.legend(loc="lower right", fontsize=7.5)

# Subplot 2: Latency Breakdown
stages_lat = ["Stage 1\nEWRRF", "Stage 2\nDAG Plan", "Stage 3\n6 Agents", "Stage 4\nVerifier", "Stage 5\nQwen 3B GPU"]
lat_ms = [48, 18, 42, 32, 1450]
colors_lat = ["#38bdf8", "#818cf8", "#fbbf24", "#f87171", "#22c55e"]

bars_l = ax2.barh(stages_lat, lat_ms, color=colors_lat, edgecolor="#0f172a", height=0.55)
ax2.set_title("(b) Stage-Wise Execution Latency (ms)", fontweight="bold", fontsize=9.5)
ax2.set_xlabel("Latency (milliseconds, log scale)", fontweight="bold", fontsize=8.5)
ax2.set_xscale("log")
ax2.set_xlim(10, 4000)
ax2.grid(axis="x", linestyle="--", alpha=0.5)

for bar in bars_l:
    w_val = bar.get_width()
    ax2.annotate(f"{w_val} ms",
                 xy=(w_val, bar.get_y() + bar.get_height()/2),
                 xytext=(4, 0), textcoords="offset points",
                 ha="left", va="center", fontsize=8, fontweight="bold")

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "fig3_ablation_and_latency.png"), dpi=300, bbox_inches="tight")
plt.close()

print("All 3 high-resolution IEEE figures generated successfully!")
