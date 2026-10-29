%% =========================================================================
%% MATLAB Script: IEEE Publication Figures for 5G NR/O-RAN Multi-Agent Paper
%% Generates:
%%   1) fig2_baseline_comparison.png (Benchmark Comparison vs Baselines)
%%   2) fig3_ablation_and_latency.png (Ablation Study & Latency Profile)
%% =========================================================================

clear; clc; close all;

% Set default font to Times New Roman for IEEE publications
set(0, 'DefaultAxesFontName', 'Times New Roman');
set(0, 'DefaultTextFontName', 'Times New Roman');
set(0, 'DefaultAxesFontSize', 11);
set(0, 'DefaultTextFontSize', 11);

output_dir = fullfile(fileparts(mfilename('fullpath')), 'overleaf_ieee_paper', 'figures');
if ~exist(output_dir, 'dir')
    output_dir = pwd; % Fallback to current folder
end

%% =========================================================================
%% FIGURE 2: Quantitative Benchmark Comparison with State-of-the-Art Works
%% =========================================================================
figure('Color', 'w', 'Position', [100, 100, 950, 520]);

metrics = {'MRR (%)', 'Top-5 Recall (%)', 'TeleQnA Acc. (%)', 'Citation Acc. (%)', 'SON Compliance (%)'};
% Data matrix: 5 metrics x 4 models
data_f2 = [
    76.2,  81.5,  79.4,   94.2;   % MRR
    84.5,  88.4,  86.0,  100.0;   % Top-5 Recall
    78.0,  82.1,  83.5,   87.5;   % TeleQnA Acc
    85.2,  89.0,  88.5,  100.0;   % Citation Acc
     0.0,   0.0,  87.0,  100.0    % SON Compliance
];

% MATLAB Publication Color Palette
colors = [
    0.30, 0.43, 0.54;   % Slate Blue: TelecomRAG
    0.00, 0.45, 0.74;   % MATLAB Blue: Telco-RAG
    0.85, 0.33, 0.10;   % MATLAB Rust/Orange: Tele-LLM-Hub
    0.18, 0.49, 0.20    % Forest Green: Proposed Framework
];

b = bar(data_f2, 'grouped', 'LineWidth', 1.1);
for k = 1:size(data_f2, 2)
    b(k).FaceColor = colors(k, :);
    b(k).EdgeColor = [0.15, 0.15, 0.15];
end

grid on;
set(gca, 'GridLineStyle', '--', 'GridAlpha', 0.5, 'LineWidth', 1.2, 'Box', 'on');
set(gca, 'XTick', 1:5, 'XTickLabel', metrics, 'FontWeight', 'bold');
set(gca, 'YTick', 0:20:100);
ylim([0, 145]); % Generous headroom so labels never collide with top border

ylabel('Performance Score (%)', 'FontWeight', 'bold', 'FontSize', 12);
title('Quantitative Benchmark Comparison with State-of-the-Art Works', 'FontWeight', 'bold', 'FontSize', 13);

% Add data value labels on top of bars
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

legend({'TelecomRAG (Yilma et al., 2024)', ...
        'Telco-RAG (Bornea et al., 2024)', ...
        'Tele-LLM-Hub (Gajjar et al., 2025)', ...
        'Proposed Multi-Agent Framework'}, ...
        'Location', 'north', 'NumColumns', 2, 'FontSize', 10, 'Box', 'on');

fig2_save_path = fullfile(output_dir, 'fig2_baseline_comparison.png');
exportgraphics(gcf, fig2_save_path, 'Resolution', 300);
fprintf('Saved Figure 2 to: %s\n', fig2_save_path);

%% =========================================================================
%% FIGURE 3: Component Ablation and Stage-Wise Execution Latency
%% =========================================================================
figure('Color', 'w', 'Position', [150, 150, 1100, 480]);

% ------------------------- Subplot (a): Ablation -------------------------
subplot(1, 2, 1);
categories = {'Dense Only', 'Standard RRF', 'Proposed EWRRF', 'EWRRF + Verifier'};
ablation_data = [
    75.0,  62.5;   % Dense Only
    81.2,  75.0;   % Standard RRF
    87.5,  75.0;   % Proposed EWRRF
    87.5, 100.0    % EWRRF + Verifier
];

b_abl = bar(ablation_data, 'grouped', 'LineWidth', 1.0);
b_abl(1).FaceColor = [0.00, 0.45, 0.74]; % Blue
b_abl(1).EdgeColor = [0.00, 0.22, 0.40];
b_abl(2).FaceColor = [0.85, 0.33, 0.10]; % Rust/Orange
b_abl(2).EdgeColor = [0.44, 0.14, 0.00];

grid on;
set(gca, 'GridLineStyle', '--', 'GridAlpha', 0.5, 'LineWidth', 1.2, 'Box', 'on');
set(gca, 'XTick', 1:4, 'XTickLabel', categories, 'FontWeight', 'bold');
set(gca, 'YTick', 50:10:100);
ylim([45, 130]); % Ample headroom for annotations

ylabel('Score (%)', 'FontWeight', 'bold', 'FontSize', 11.5);
title('(a) Architectural Component Ablation', 'FontWeight', 'bold', 'FontSize', 12);

% Add percentage annotations
for i = 1:size(ablation_data, 1)
    for j = 1:size(ablation_data, 2)
        val = ablation_data(i, j);
        x_pos = b_abl(j).XEndPoints(i);
        y_pos = b_abl(j).YEndPoints(i);
        text(x_pos, y_pos + 2.5, sprintf('%.1f%%', val), ...
            'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', ...
            'FontWeight', 'bold', 'FontSize', 9.0);
    end
end

legend({'TeleQnA Accuracy (%)', 'SON Parameter Compliance (%)'}, ...
       'Location', 'northwest', 'FontSize', 9.5, 'Box', 'on');

% ------------------------- Subplot (b): Latency -------------------------
subplot(1, 2, 2);
stages = {'Stage 1 (EWRRF)', 'Stage 2 (DAG Plan)', 'Stage 3 (6 Agents)', 'Stage 4 (Verifier)', 'Stage 5 (Qwen GPU)'};
latencies = [48, 18, 42, 32, 1450]; % in milliseconds

bar_colors = [
    0.30, 0.75, 0.93;   % Stage 1: Cyan/Light Blue
    0.47, 0.67, 0.19;   % Stage 2: Olive/Green
    0.93, 0.69, 0.13;   % Stage 3: Yellow/Amber
    0.64, 0.08, 0.18;   % Stage 4: Crimson/Red
    0.00, 0.45, 0.74    % Stage 5: Classic Blue
];

b_lat = barh(1:5, latencies, 0.55, 'LineWidth', 1.0, 'EdgeColor', [0.1, 0.1, 0.1]);
b_lat.FaceColor = 'flat';
for k = 1:5
    b_lat.CData(k, :) = bar_colors(k, :);
end

set(gca, 'XScale', 'log');
xlim([5, 30000]); % Extensive headroom to ensure text never collides with right axis border
grid on;
set(gca, 'GridLineStyle', '--', 'GridAlpha', 0.5, 'LineWidth', 1.2, 'Box', 'on');
set(gca, 'YTick', 1:5, 'YTickLabel', stages, 'FontWeight', 'bold');

xlabel('Execution Latency (milliseconds, log scale)', 'FontWeight', 'bold', 'FontSize', 11.5);
title('(b) Stage-Wise Execution Latency', 'FontWeight', 'bold', 'FontSize', 12);

% Annotate horizontal bars
for k = 1:5
    val = latencies(k);
    if val < 1000
        lbl = sprintf(' %d ms', val);
    else
        lbl = sprintf(' %.2f s (%d ms)', val/1000, val);
    end
    text(val * 1.15, k, lbl, 'VerticalAlignment', 'middle', ...
        'FontWeight', 'bold', 'FontSize', 9.2, 'Color', [0.1, 0.1, 0.1]);
end

fig3_save_path = fullfile(output_dir, 'fig3_ablation_and_latency.png');
exportgraphics(gcf, fig3_save_path, 'Resolution', 300);
fprintf('Saved Figure 3 to: %s\n', fig3_save_path);

fprintf('\nDone! Both figures generated successfully in IEEE standard format.\n');
