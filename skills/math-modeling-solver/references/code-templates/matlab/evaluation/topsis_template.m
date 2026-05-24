% topsis_template.m — 简化版
function [C, ranking] = topsis_template()
    % 决策矩阵 (n_alt × n_crit)
    X = [100, 85, 0.95, 80;
         120, 92, 0.88, 75;
          95, 78, 0.92, 90;
         110, 88, 0.90, 85];
    [n_alt, n_crit] = size(X);

    % 权重
    w = [0.25, 0.30, 0.25, 0.20];

    % 正向化：指标2-4 极大型，指标1 极小型
    X(:,1) = max(X(:,1)) - X(:,1);

    % 向量归一化
    Z = X ./ sqrt(sum(X.^2, 1));

    % 加权
    V = Z .* w;

    % 理想解
    V_plus = max(V, [], 1);
    V_minus = min(V, [], 1);

    % 距离
    D_plus = sqrt(sum((V - V_plus).^2, 2));
    D_minus = sqrt(sum((V - V_minus).^2, 2));

    % 相对贴近度
    C = D_minus ./ (D_plus + D_minus + 1e-10);

    % 排名
    [~, idx] = sort(C, 'descend');
    ranking = zeros(n_alt, 1);
    ranking(idx) = 1:n_alt;

    fprintf('===== TOPSIS 结果 =====\n');
    for i = 1:n_alt
        fprintf('方案 %d: C = %.4f, 排名 = %d\n', i, C(i), ranking(i));
    end

    figure; barh(C);
    yticklabels({'A','B','C','D'});
    xlabel('Relative Closeness');
    title('TOPSIS Results');
end
