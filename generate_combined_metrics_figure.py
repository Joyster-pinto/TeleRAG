import os
import matplotlib.pyplot as plt
import numpy as np

# Publication aesthetic settings
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Times']
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['axes.edgecolor'] = '#262626'
plt.rcParams['axes.linewidth'] = 1.1
plt.rcParams['grid.color'] = '#e0e0e0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.linewidth'] = 0.65

out_dir = r"D:\Vit\SEM 5\F2-NLP\NLP Project\overleaf_ieee_paper\figures"
os.makedirs(out_dir, exist_ok=True)

# Create 1 row with 3 subplots: [Left: Fig 2] [Middle: Fig 3a] [Right: Fig 3b]
fig = plt.figure(figsize=(15.5, 4.4), dpi=300)
gs = fig.add_gridspec(1, 3, width_ratios=[1.35, 1.0, 1.05], wspace=0.32)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])

# -----------------------------------------------------------------------------
# PANEL 1: Benchmark Comparison
# -----------------------------------------------------------------------------
metrics = ['MRR\n(%)', 'Top-5 Recall\n(%)', 'TeleQnA Acc.\n(%)', 'Citation Acc.\n(%)', 'SON Compl.\n(%)']
telecom_rag = [76.2, 84.5, 78.0, 85.2, 0]
telco_rag   = [81.5, 88.4, 82.1, 89.0, 0]
tele_llm    = [79.4, 86.0, 83.5, 88.5, 87.0]
proposed    = [94.2, 100.0, 87.5, 100.0, 100.0]

x = np.arange(len(metrics))
w = 0.18

c1 = '#5B84B1'  # Slate Blue
c2 = '#0072BD'  # Classic Deep Blue
c3 = '#E66101'  # Amber-Orange
c4 = '#2CA02C'  # Forest Green

b1 = ax1.bar(x - 1.5*w, telecom_rag, w, label='TelecomRAG (2024)', color=c1, edgecolor='#2b415a', linewidth=0.7)
b2 = ax1.bar(x - 0.5*w, telco_rag,   w, label='Telco-RAG (2024)', color=c2, edgecolor='#003b63', linewidth=0.7)
b3 = ax1.bar(x + 0.5*w, tele_llm,    w, label='Tele-LLM-Hub (2025)', color=c3, edgecolor='#803600', linewidth=0.7)
b4 = ax1.bar(x + 1.5*w, proposed,    w, label='Proposed Framework', color=c4, edgecolor='#134d13', linewidth=0.9)

ax1.set_ylim(0, 142)
ax1.set_yticks([0, 20, 40, 60, 80, 100])

for bars in [b1, b2, b3, b4]:
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax1.annotate(f'{h:.1f}',
                         xy=(bar.get_x() + bar.get_width()/2, h),
                         xytext=(0, 3.5), textcoords='offset points',
                         ha='center', va='bottom', fontsize=8.2, fontweight='bold', color='#111111')

ax1.set_ylabel('Score (%)', fontweight='bold', fontsize=11, labelpad=6)
ax1.set_title('(a) SOTA Benchmark Comparison', fontweight='bold', fontsize=11.5, pad=9)
ax1.set_xticks(x)
ax1.set_xticklabels(metrics, fontweight='bold', fontsize=9.2)
ax1.tick_params(axis='both', which='major', labelsize=9.5, direction='in', length=4)
ax1.grid(axis='y', alpha=0.7)
ax1.set_axisbelow(True)
ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=2, frameon=True,
           framealpha=0.96, fontsize=8.2, edgecolor='#b0b0b0')

# -----------------------------------------------------------------------------
# PANEL 2: Architectural Component Ablation
# -----------------------------------------------------------------------------
categories = ['Dense\nOnly', 'Standard\nRRF', 'Proposed\nEWRRF', 'EWRRF +\nVerifier']
qna_acc = [75.0, 81.2, 87.5, 87.5]
son_safe = [62.5, 75.0, 75.0, 100.0]

x_abl = np.arange(len(categories))
w_abl = 0.33

bar_q = ax2.bar(x_abl - w_abl/2, qna_acc, w_abl, label='TeleQnA Acc. (%)', color='#0072BD', edgecolor='#003b63', linewidth=0.7)
bar_s = ax2.bar(x_abl + w_abl/2, son_safe, w_abl, label='SON Compliance (%)', color='#E66101', edgecolor='#803600', linewidth=0.7)

ax2.set_ylim(45, 126)
ax2.set_yticks([50, 60, 70, 80, 90, 100])

for b in bar_q:
    ax2.annotate(f'{b.get_height():.1f}%', xy=(b.get_x() + b.get_width()/2, b.get_height()),
                 xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=8.0, fontweight='bold')
for b in bar_s:
    ax2.annotate(f'{b.get_height():.1f}%', xy=(b.get_x() + b.get_width()/2, b.get_height()),
                 xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=8.0, fontweight='bold')

ax2.set_ylabel('Score (%)', fontweight='bold', fontsize=11)
ax2.set_title('(b) Component Ablation', fontweight='bold', fontsize=11.5, pad=9)
ax2.set_xticks(x_abl)
ax2.set_xticklabels(categories, fontweight='bold', fontsize=9.0)
ax2.tick_params(axis='both', which='major', labelsize=9.0, direction='in', length=4)
ax2.grid(axis='y', alpha=0.7)
ax2.set_axisbelow(True)
ax2.legend(loc='upper left', frameon=True, framealpha=0.96, fontsize=8.2, edgecolor='#b0b0b0')

# -----------------------------------------------------------------------------
# PANEL 3: Stage-Wise Execution Latency
# -----------------------------------------------------------------------------
stages = ['Stage 1\n(EWRRF)', 'Stage 2\n(DAG Plan)', 'Stage 3\n(6 Agents)', 'Stage 4\n(Verifier)', 'Stage 5\n(Qwen GPU)']
latencies = [48, 18, 42, 32, 1450]
colors_lat = ['#4DBEEE', '#77AC30', '#EDB120', '#D95319', '#0072BD']

y_pos = np.arange(len(stages))
bars_lat = ax3.barh(y_pos, latencies, color=colors_lat, edgecolor='#1a1a1a', linewidth=0.7, height=0.55)

ax3.set_xscale('log')
ax3.set_xlim(5, 30000)

for bar in bars_lat:
    w_val = bar.get_width()
    txt = f' {w_val} ms' if w_val < 1000 else f' {w_val/1000:.2f} s ({w_val} ms)'
    ax3.annotate(txt, xy=(w_val, bar.get_y() + bar.get_height()/2),
                 xytext=(3, 0), textcoords='offset points', ha='left', va='center',
                 fontsize=8.0, fontweight='bold', color='#111111')

ax3.set_xlabel('Latency (ms, log scale)', fontweight='bold', fontsize=10.5)
ax3.set_title('(c) Stage-Wise Latency', fontweight='bold', fontsize=11.5, pad=9)
ax3.set_yticks(y_pos)
ax3.set_yticklabels(stages, fontweight='bold', fontsize=8.5)
ax3.tick_params(axis='both', which='major', labelsize=8.8, direction='in', length=4)
ax3.grid(axis='x', alpha=0.7)
ax3.set_axisbelow(True)

plt.tight_layout()
comb_path = os.path.join(out_dir, "fig_combined_metrics.png")
plt.savefig(comb_path, dpi=300, bbox_inches='tight')
plt.close()
print("Saved combined metrics figure to:", comb_path)
