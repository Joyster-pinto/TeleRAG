import os
import matplotlib.pyplot as plt
import numpy as np

# Configure publication-grade IEEE aesthetic
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Times']
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['axes.edgecolor'] = '#262626'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.color'] = '#e0e0e0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.linewidth'] = 0.7

out_dir = os.path.join(r"D:\Vit\SEM 5\F2-NLP\NLP Project\overleaf_ieee_paper\figures")
os.makedirs(out_dir, exist_ok=True)

# -------------------------------------------------------------
# FIGURE 2: Baseline Comparison (Clean Solid Colors, NO Lines/Hatches)
# -------------------------------------------------------------
metrics = ['MRR\n(%)', 'Top-5 Recall\n(%)', 'TeleQnA Acc.\n(%)', 'Citation Acc.\n(%)', 'SON Compliance\n(%)']
telecom_rag = [76.2, 84.5, 78.0, 85.2, 0]
telco_rag   = [81.5, 88.4, 82.1, 89.0, 0]
tele_llm    = [79.4, 86.0, 83.5, 88.5, 87.0]
proposed    = [94.2, 100.0, 87.5, 100.0, 100.0]

x = np.arange(len(metrics))
w = 0.18

fig, ax = plt.subplots(figsize=(9.2, 5.0), dpi=300)

# Professional solid color palette (no hatches/lines)
c1 = '#5B84B1'  # Soft Slate Blue
c2 = '#0072BD'  # Classic MATLAB Deep Blue
c3 = '#E66101'  # Vibrant Professional Amber/Orange
c4 = '#2CA02C'  # Solid Forest Green

b1 = ax.bar(x - 1.5*w, telecom_rag, w, label='TelecomRAG (Yilma et al., 2024)', color=c1, edgecolor='#2b415a', linewidth=0.8)
b2 = ax.bar(x - 0.5*w, telco_rag,   w, label='Telco-RAG (Bornea et al., 2024)', color=c2, edgecolor='#003b63', linewidth=0.8)
b3 = ax.bar(x + 0.5*w, tele_llm,    w, label='Tele-LLM-Hub (Gajjar et al., 2025)', color=c3, edgecolor='#803600', linewidth=0.8)
b4 = ax.bar(x + 1.5*w, proposed,    w, label='Proposed Multi-Agent Framework', color=c4, edgecolor='#134d13', linewidth=1.0)

# Ample headroom to prevent text colliding with top ceiling or legend
ax.set_ylim(0, 142)
ax.set_yticks([0, 20, 40, 60, 80, 100])

for bars in [b1, b2, b3, b4]:
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.annotate(f'{h:.1f}',
                        xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(0, 4), textcoords='offset points',
                        ha='center', va='bottom', fontsize=9.2, fontweight='bold', color='#111111')

ax.set_ylabel('Performance Score (%)', fontweight='bold', fontsize=12, labelpad=8)
ax.set_title('Quantitative Benchmark Comparison with State-of-the-Art Works', fontweight='bold', fontsize=13, pad=12)
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontweight='bold', fontsize=11)
ax.tick_params(axis='both', which='major', labelsize=10.5, direction='in', length=5)
ax.grid(axis='y', alpha=0.7)
ax.set_axisbelow(True)

ax.legend(loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=2, frameon=True,
          framealpha=0.98, fontsize=9.8, edgecolor='#b0b0b0')

plt.tight_layout()
f2_path = os.path.join(out_dir, "fig2_baseline_comparison.png")
plt.savefig(f2_path, dpi=300)
plt.close()
print("Saved clean solid-color fig2 to:", f2_path)

# -------------------------------------------------------------
# FIGURE 3: Ablation & Latency (Clean Solid Colors, NO Hatches)
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.6), dpi=300)

categories = ['Dense\nOnly', 'Standard\nRRF', 'Proposed\nEWRRF', 'EWRRF +\nVerifier']
qna_acc = [75.0, 81.2, 87.5, 87.5]
son_safe = [62.5, 75.0, 75.0, 100.0]

x_abl = np.arange(len(categories))
w_abl = 0.33

# Solid colors without any hatch patterns
bar_q = ax1.bar(x_abl - w_abl/2, qna_acc, w_abl, label='TeleQnA Accuracy (%)', color='#0072BD', edgecolor='#003b63', linewidth=0.8)
bar_s = ax1.bar(x_abl + w_abl/2, son_safe, w_abl, label='SON Parameter Compliance (%)', color='#E66101', edgecolor='#803600', linewidth=0.8)

# Headroom for annotations
ax1.set_ylim(45, 128)
ax1.set_yticks([50, 60, 70, 80, 90, 100])

for b in bar_q:
    ax1.annotate(f'{b.get_height():.1f}%', xy=(b.get_x() + b.get_width()/2, b.get_height()),
                 xytext=(0, 4), textcoords='offset points', ha='center', va='bottom', fontsize=9.0, fontweight='bold')
for b in bar_s:
    ax1.annotate(f'{b.get_height():.1f}%', xy=(b.get_x() + b.get_width()/2, b.get_height()),
                 xytext=(0, 4), textcoords='offset points', ha='center', va='bottom', fontsize=9.0, fontweight='bold')

ax1.set_ylabel('Score (%)', fontweight='bold', fontsize=11.5)
ax1.set_title('(a) Architectural Component Ablation', fontweight='bold', fontsize=12, pad=10)
ax1.set_xticks(x_abl)
ax1.set_xticklabels(categories, fontweight='bold', fontsize=10)
ax1.tick_params(axis='both', which='major', labelsize=10, direction='in', length=5)
ax1.grid(axis='y', alpha=0.7)
ax1.set_axisbelow(True)
ax1.legend(loc='upper left', frameon=True, framealpha=0.95, fontsize=9.2, edgecolor='#b0b0b0')

stages = ['Stage 1\n(EWRRF)', 'Stage 2\n(DAG Plan)', 'Stage 3\n(6 Agents)', 'Stage 4\n(Verifier)', 'Stage 5\n(Qwen GPU)']
latencies = [48, 18, 42, 32, 1450]
colors_lat = ['#4DBEEE', '#77AC30', '#EDB120', '#D95319', '#0072BD']

y_pos = np.arange(len(stages))
bars_lat = ax2.barh(y_pos, latencies, color=colors_lat, edgecolor='#1a1a1a', linewidth=0.8, height=0.55)

ax2.set_xscale('log')
ax2.set_xlim(5, 30000)

for bar in bars_lat:
    w_val = bar.get_width()
    txt = f' {w_val} ms' if w_val < 1000 else f' {w_val/1000:.2f} s ({w_val} ms)'
    ax2.annotate(txt, xy=(w_val, bar.get_y() + bar.get_height()/2),
                 xytext=(4, 0), textcoords='offset points', ha='left', va='center',
                 fontsize=9.2, fontweight='bold', color='#111111')

ax2.set_xlabel('Execution Latency (milliseconds, log scale)', fontweight='bold', fontsize=11.5)
ax2.set_title('(b) Stage-Wise Execution Latency', fontweight='bold', fontsize=12, pad=10)
ax2.set_yticks(y_pos)
ax2.set_yticklabels(stages, fontweight='bold', fontsize=10)
ax2.tick_params(axis='both', which='major', labelsize=10, direction='in', length=5)
ax2.grid(axis='x', alpha=0.7)
ax2.set_axisbelow(True)

plt.tight_layout()
f3_path = os.path.join(out_dir, "fig3_ablation_and_latency.png")
plt.savefig(f3_path, dpi=300)
plt.close()
print("Saved clean solid-color fig3 to:", f3_path)
