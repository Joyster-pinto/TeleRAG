%% =========================================================================
%% MATLAB Script: IEEE Publication Figures for 5G NR/O-RAN Multi-Agent Paper
%% Generates:
%%   1) fig_combined_half_page.png (Unified Half-Page Layout for IEEEtran)
%%   2) fig2_baseline_comparison.png (Standalone Benchmark Comparison)
%%   3) fig3_ablation_and_latency.png (Standalone Ablation & Latency)
%%
%% Instructions:
%%   Open MATLAB, run this script (F5).
%%   Figures will be saved at 300 DPI into the figures directory and current folder.
%% =========================================================================

clear; clc; close all;

% Set default font to Times New Roman for IEEE publications
set(0, 'DefaultAxesFontName', 'Times New Roman');
set(0, 'DefaultTextFontName', 'Times New Roman');
set(0, 'DefaultAxesFontSize', 10);
set(0, 'DefaultTextFontSize', 10);

output_dir = fullfile(fileparts(mfilename('fullpath')), '..', 'figures');
if ~exist(output_dir, 'dir')
    output_dir = pwd;
end
fprintf('Figures will be saved to: %s\n\n', output_dir);

%% =========================================================================
%% 1) UNIFIED HALF-PAGE FIGURE (for IEEE double-column top float)
%% =========================================================================
fig_half = figure('Color', 'w', 'Position', [100, 100, 1450, 750], 'Visible', 'off');

% ----------------- TOP: Benchmark Comparison (spans [1 2]) -----------------
subplot(2, 2, [1 2]);
metrics = {'MRR (%)', 'Top-5 Recall (%)', 'TeleQnA Acc. (%)', 'Citation Acc. (%)', 'SON Compliance (%)'};
data_f2 = [
    76.2,  81.5,  79.4,   94.2;
    84.5,  88.4,  86.0,  100.0;
    78.0,  82.1,  83.5,   87.5;
    85.2,  89.0,  88.5,  100.0;
     0.0,   0.0,  87.0,  100.0
];
colors = [
    0.30, 0.43, 0.54;   % Slate Blue: TelecomRAG
    0.00, 0.45, 0.74;   % MATLAB Blue: Telco-RAG
    0.85, 0.33, 0.10;   % MATLAB Orange: Tele-LLM-Hub
    0.18, 0.49, 0.20    % Forest Green: Proposed Multi-Agent Framework
];
b2 = bar(data_f2, 'grouped', 'LineWidth', 1.1);
for k = 1:4
    b2(k).FaceColor = colors(k, :);
    b2(k).EdgeColor = [0.15, 0.15, 0.15];
end
grid on;
set(gca, 'GridLineStyle', '--', 'GridAlpha', 0.4, 'LineWidth', 1.1, 'Box', 'on');
set(gca, 'XTick', 1:5, 'XTickLabel', metrics, 'FontWeight', 'bold');
set(gca, 'YTick', 0:20:100);
ylim([0, 138]);
ylabel('Performance Score (%)', 'FontWeight', 'bold', 'FontSize', 11);
title('(a) Quantitative Benchmark Comparison with State-of-the-Art Baselines', 'FontWeight', 'bold', 'FontSize', 12);
for i = 1:size(data_f2, 1)
    for j = 1:size(data_f2, 2)
        val = data_f2(i, j);
        if val > 0
            x_pos = b2(j).XEndPoints(i);
            y_pos = b2(j).YEndPoints(i);
            text(x_pos, y_pos + 2.5, sprintf('%.1f', val), ...
                'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', ...
                'FontWeight', 'bold', 'FontSize', 9, 'Color', [0.1, 0.1, 0.1]);
        end
    end
end
legend({'TelecomRAG (Yilma et al., 2024)', 'Telco-RAG (Bornea et al., 2024)', ...
        'Tele-LLM-Hub (Gajjar et al., 2025)', 'Proposed Multi-Agent Framework'}, ...
        'Location', 'north', 'NumColumns', 4, 'FontSize', 9.5, 'Box', 'on');

% ----------------- BOTTOM LEFT: Ablation Study -----------------
subplot(2, 2, 3);
categories = {'Dense Only', 'Standard RRF', 'Proposed EWRRF', 'EWRRF + Verifier'};
ablation_data = [
    75.0,  62.5;
    81.2,  75.0;
    87.5,  75.0;
    87.5, 100.0
];
b_abl = bar(ablation_data, 'grouped', 'LineWidth', 1.0);
b_abl(1).FaceColor = [0.00, 0.45, 0.74];
b_abl(1).EdgeColor = [0.00, 0.22, 0.40];
b_abl(2).FaceColor = [0.85, 0.33, 0.10];
b_abl(2).EdgeColor = [0.44, 0.14, 0.00];
grid on;
set(gca, 'GridLineStyle', '--', 'GridAlpha', 0.4, 'LineWidth', 1.1, 'Box', 'on');
set(gca, 'XTick', 1:4, 'XTickLabel', categories, 'FontWeight', 'bold');
set(gca, 'YTick', 50:10:100);
ylim([45, 125]);
ylabel('Score (%)', 'FontWeight', 'bold', 'FontSize', 10.5);
title('(b) Architectural Component Ablation', 'FontWeight', 'bold', 'FontSize', 11);
for i = 1:size(ablation_data, 1)
    for j = 1:size(ablation_data, 2)
        val = ablation_data(i, j);
        x_pos = b_abl(j).XEndPoints(i);
        y_pos = b_abl(j).YEndPoints(i);
        text(x_pos, y_pos + 2.0, sprintf('%.1f%%', val), ...
            'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', ...
            'FontWeight', 'bold', 'FontSize', 8.5);
    end
end
legend({'TeleQnA Accuracy (%)', 'SON Compliance (%)'}, 'Location', 'northwest', 'FontSize', 9, 'Box', 'on');

% ----------------- BOTTOM RIGHT: Stage Latency -----------------
subplot(2, 2, 4);
stages = {'Stage 1 (EWRRF)', 'Stage 2 (DAG Plan)', 'Stage 3 (6 Agents)', 'Stage 4 (Verifier)', 'Stage 5 (Qwen GPU)'};
latencies = [48, 18, 42, 32, 1450];
bar_colors = [
    0.30, 0.75, 0.93;
    0.47, 0.67, 0.19;
    0.93, 0.69, 0.13;
    0.64, 0.08, 0.18;
    0.00, 0.45, 0.74
];
b_lat = barh(1:5, latencies, 0.55, 'LineWidth', 1.0, 'EdgeColor', [0.1, 0.1, 0.1]);
b_lat.FaceColor = 'flat';
for k = 1:5
    b_lat.CData(k, :) = bar_colors(k, :);
end
set(gca, 'XScale', 'log');
xlim([5, 30000]);
grid on;
set(gca, 'GridLineStyle', '--', 'GridAlpha', 0.4, 'LineWidth', 1.1, 'Box', 'on');
set(gca, 'YTick', 1:5, 'YTickLabel', stages, 'FontWeight', 'bold');
xlabel('Execution Latency (ms, log scale)', 'FontWeight', 'bold', 'FontSize', 10.5);
title('(c) Stage-Wise Execution Latency', 'FontWeight', 'bold', 'FontSize', 11);
for k = 1:5
    val = latencies(k);
    if val < 1000
        lbl = sprintf(' %d ms', val);
    else
        lbl = sprintf(' %.2f s (%d ms)', val/1000, val);
    end
    text(val * 1.18, k, lbl, 'VerticalAlignment', 'middle', 'FontWeight', 'bold', 'FontSize', 8.8, 'Color', [0.1, 0.1, 0.1]);
end

save_half = fullfile(output_dir, 'fig_combined_half_page.png');
exportgraphics(fig_half, save_half, 'Resolution', 300);
fprintf('Saved Half-Page Figure to: %s\n', save_half);

%% =========================================================================
%% 2) STANDALONE FIGURE 2
%% =========================================================================
fig2 = figure('Color', 'w', 'Position', [100, 100, 950, 520], 'Visible', 'off');
b = bar(data_f2, 'grouped', 'LineWidth', 1.1);
for k = 1:size(data_f2, 2)
    b(k).FaceColor = colors(k, :);
    b(k).EdgeColor = [0.15, 0.15, 0.15];
end
grid on;
set(gca, 'GridLineStyle', '--', 'GridAlpha', 0.5, 'LineWidth', 1.2, 'Box', 'on');
set(gca, 'XTick', 1:5, 'XTickLabel', metrics, 'FontWeight', 'bold');
set(gca, 'YTick', 0:20:100);
ylim([0, 140]);
ylabel('Performance Score (%)', 'FontWeight', 'bold', 'FontSize', 12);
title('Quantitative Benchmark Comparison with State-of-the-Art Works', 'FontWeight', 'bold', 'FontSize', 13);
for i = 1:size(data_f2, 1)
    for j = 1:size(data_f2, 2)
        val = data_f2(i, j);
        if val > 0
            x_pos = b(j).XEndPoints(i);
            y_pos = b(j).YEndPoints(i);
            text(x_pos, y_pos + 3.0, sprintf('%.1f', val), ...
                'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', ...
                'FontWeight', 'bold', 'FontSize', 9.5, 'Color', [0.1, 0.1, 0.1]);
        end
    end
end
legend({'TelecomRAG (Yilma et al., 2024)', 'Telco-RAG (Bornea et al., 2024)', ...
        'Tele-LLM-Hub (Gajjar et al., 2025)', 'Proposed Multi-Agent Framework'}, ...
        'Location', 'north', 'NumColumns', 2, 'FontSize', 10, 'Box', 'on');
save_fig2 = fullfile(output_dir, 'fig2_baseline_comparison.png');
exportgraphics(fig2, save_fig2, 'Resolution', 300);
fprintf('Saved Figure 2 to: %s\n', save_fig2);

%% =========================================================================
%% 3) STANDALONE FIGURE 3
%% =========================================================================
fig3 = figure('Color', 'w', 'Position', [150, 150, 1100, 480], 'Visible', 'off');
subplot(1, 2, 1);
b_abl2 = bar(ablation_data, 'grouped', 'LineWidth', 1.0);
b_abl2(1).FaceColor = [0.00, 0.45, 0.74];
b_abl2(1).EdgeColor = [0.00, 0.22, 0.40];
b_abl2(2).FaceColor = [0.85, 0.33, 0.10];
b_abl2(2).EdgeColor = [0.44, 0.14, 0.00];
grid on;
set(gca, 'GridLineStyle', '--', 'GridAlpha', 0.5, 'LineWidth', 1.2, 'Box', 'on');
set(gca, 'XTick', 1:4, 'XTickLabel', categories, 'FontWeight', 'bold');
set(gca, 'YTick', 50:10:100);
ylim([45, 130]);
ylabel('Score (%)', 'FontWeight', 'bold', 'FontSize', 11.5);
title('(a) Architectural Component Ablation', 'FontWeight', 'bold', 'FontSize', 12);
for i = 1:size(ablation_data, 1)
    for j = 1:size(ablation_data, 2)
        val = ablation_data(i, j);
        x_pos = b_abl2(j).XEndPoints(i);
        y_pos = b_abl2(j).YEndPoints(i);
        text(x_pos, y_pos + 2.5, sprintf('%.1f%%', val), ...
            'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', ...
            'FontWeight', 'bold', 'FontSize', 9.0);
    end
end
legend({'TeleQnA Accuracy (%)', 'SON Parameter Compliance (%)'}, 'Location', 'northwest', 'FontSize', 9.5, 'Box', 'on');

subplot(1, 2, 2);
b_lat2 = barh(1:5, latencies, 0.55, 'LineWidth', 1.0, 'EdgeColor', [0.1, 0.1, 0.1]);
b_lat2.FaceColor = 'flat';
for k = 1:5
    b_lat2.CData(k, :) = bar_colors(k, :);
end
set(gca, 'XScale', 'log');
xlim([5, 30000]);
grid on;
set(gca, 'GridLineStyle', '--', 'GridAlpha', 0.5, 'LineWidth', 1.2, 'Box', 'on');
set(gca, 'YTick', 1:5, 'YTickLabel', stages, 'FontWeight', 'bold');
xlabel('Execution Latency (milliseconds, log scale)', 'FontWeight', 'bold', 'FontSize', 11.5);
title('(b) Stage-Wise Execution Latency', 'FontWeight', 'bold', 'FontSize', 12);
for k = 1:5
    val = latencies(k);
    if val < 1000
        lbl = sprintf(' %d ms', val);
    else
        lbl = sprintf(' %.2f s (%d ms)', val/1000, val);
    end
    text(val * 1.18, k, lbl, 'VerticalAlignment', 'middle', 'FontWeight', 'bold', 'FontSize', 9.2, 'Color', [0.1, 0.1, 0.1]);
end
save_fig3 = fullfile(output_dir, 'fig3_ablation_and_latency.png');
exportgraphics(fig3, save_fig3, 'Resolution', 300);
fprintf('Saved Figure 3 to: %s\n\n', save_fig3);

fprintf('Done! All figures generated successfully in IEEE standard format.\n');
