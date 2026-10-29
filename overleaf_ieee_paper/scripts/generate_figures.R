# =========================================================================
# R Script: IEEE Publication Figures for 5G NR/O-RAN Multi-Agent Paper
# Generates:
#   1) fig2_baseline_comparison.png (Benchmark Comparison vs Baselines)
#   2) fig3_ablation_and_latency.png (Ablation Study & Latency Profile)
# =========================================================================

# Ensure target output directory exists
out_dir <- file.path("D:", "Vit", "SEM 5", "F2-NLP", "NLP Project", "overleaf_ieee_paper", "figures")
if (!dir.exists(out_dir)) {
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
}

# -------------------------------------------------------------------------
# FIGURE 2: Quantitative Benchmark Comparison
# -------------------------------------------------------------------------
png(filename = file.path(out_dir, "fig2_baseline_comparison_R.png"),
    width = 9.2, height = 5.2, units = "in", res = 300)

par(family = "serif", mar = c(4.5, 4.5, 3.5, 1.5))

metrics <- c("MRR (%)", "Top-5 Recall (%)", "TeleQnA Acc. (%)", "Citation Acc. (%)", "SON Compl. (%)")

# 4 models x 5 metrics
data_matrix <- matrix(c(
  76.2, 84.5, 78.0, 85.2, 0.0,    # TelecomRAG
  81.5, 88.4, 82.1, 89.0, 0.0,    # Telco-RAG
  79.4, 86.0, 83.5, 88.5, 87.0,   # Tele-LLM-Hub
  94.2, 100.0, 87.5, 100.0, 100.0 # Proposed Framework
), nrow = 4, byrow = TRUE)

colors <- c("#4D6D8A", "#0072BD", "#D95319", "#2E7D32")

# Barplot with wide y-limits (0 to 145) to prevent any text-border overlap
bp <- barplot(data_matrix, beside = TRUE, names.arg = metrics,
              col = colors, border = "#1a1a1a",
              ylim = c(0, 145), yaxt = "n",
              ylab = "Performance Score (%)", font.lab = 2, cex.lab = 1.15,
              main = "Quantitative Benchmark Comparison with State-of-the-Art Works",
              font.main = 2, cex.main = 1.25)

axis(2, at = seq(0, 100, by = 20), labels = seq(0, 100, by = 20), font = 2)
grid(nx = NA, ny = NULL, col = "#e0e0e0", lty = 2)
box(lwd = 1.2)

# Value annotations on top of each bar
for (i in 1:nrow(data_matrix)) {
  for (j in 1:ncol(data_matrix)) {
    val <- data_matrix[i, j]
    if (val > 0) {
      text(bp[i, j], val + 3.5, sprintf("%.1f", val),
           cex = 0.82, font = 2, col = "#111111")
    }
  }
}

# 2-column Legend centered at top
legend("top", legend = c("TelecomRAG (Yilma et al., 2024)",
                         "Telco-RAG (Bornea et al., 2024)",
                         "Tele-LLM-Hub (Gajjar et al., 2025)",
                         "Proposed Multi-Agent Framework"),
       fill = colors, ncol = 2, cex = 0.88, bg = "white", box.col = "#b0b0b0")

dev.off()
cat("Saved Figure 2 to:", file.path(out_dir, "fig2_baseline_comparison_R.png"), "\n")

# -------------------------------------------------------------------------
# FIGURE 3: Component Ablation & Stage-Wise Latency
# -------------------------------------------------------------------------
png(filename = file.path(out_dir, "fig3_ablation_and_latency_R.png"),
    width = 10.8, height = 4.8, units = "in", res = 300)

par(family = "serif", mfrow = c(1, 2), mar = c(4.5, 4.5, 3.5, 2.0))

# Subplot (a): Ablation
categories <- c("Dense Only", "Standard RRF", "Proposed EWRRF", "EWRRF + Verifier")
abl_matrix <- matrix(c(
  75.0, 81.2, 87.5, 87.5,   # TeleQnA Acc
  62.5, 75.0, 75.0, 100.0   # SON Compliance
), nrow = 2, byrow = TRUE)

bp_abl <- barplot(abl_matrix, beside = TRUE, names.arg = categories,
                  col = c("#0072BD", "#D95319"), border = "#1a1a1a",
                  ylim = c(45, 130), yaxt = "n",
                  ylab = "Score (%)", font.lab = 2, cex.lab = 1.1,
                  main = "(a) Architectural Component Ablation",
                  font.main = 2, cex.main = 1.2)

axis(2, at = seq(50, 100, by = 10), labels = seq(50, 100, by = 10), font = 2)
grid(nx = NA, ny = NULL, col = "#e0e0e0", lty = 2)
box(lwd = 1.2)

for (i in 1:nrow(abl_matrix)) {
  for (j in 1:ncol(abl_matrix)) {
    val <- abl_matrix[i, j]
    text(bp_abl[i, j], val + 3.0, sprintf("%.1f%%", val),
         cex = 0.80, font = 2)
  }
}

legend("topleft", legend = c("TeleQnA Accuracy (%)", "SON Parameter Compliance (%)"),
       fill = c("#0072BD", "#D95319"), cex = 0.82, bg = "white", box.col = "#b0b0b0")

# Subplot (b): Latency (Horizontal Barplot on Log Scale)
stages <- c("Stage 1\n(EWRRF)", "Stage 2\n(DAG Plan)", "Stage 3\n(6 Agents)",
            "Stage 4\n(Verifier)", "Stage 5\n(Qwen GPU)")
latencies <- c(48, 18, 42, 32, 1450)
stage_colors <- c("#4DBEEE", "#77AC30", "#EDB120", "#A2142F", "#0072BD")

bp_lat <- barplot(latencies, horiz = TRUE, names.arg = stages,
                  col = stage_colors, border = "#1a1a1a",
                  log = "x", xlim = c(5, 30000),
                  xlab = "Execution Latency (milliseconds, log scale)",
                  font.lab = 2, cex.lab = 1.1,
                  main = "(b) Stage-Wise Execution Latency",
                  font.main = 2, cex.main = 1.2, las = 1)

grid(nx = NULL, ny = NA, col = "#e0e0e0", lty = 2)
box(lwd = 1.2)

for (k in 1:length(latencies)) {
  val <- latencies[k]
  txt <- if (val < 1000) sprintf(" %d ms", val) else sprintf(" %.2f s (%d ms)", val / 1000, val)
  text(val * 1.2, bp_lat[k], txt, pos = 4, font = 2, cex = 0.82, col = "#111111")
}

dev.off()
cat("Saved Figure 3 to:", file.path(out_dir, "fig3_ablation_and_latency_R.png"), "\n")
