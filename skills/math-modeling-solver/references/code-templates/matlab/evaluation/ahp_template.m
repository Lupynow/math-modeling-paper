% ahp_template.m — 简化版
function [w, CR, ok] = ahp_template(A)
    if nargin < 1
        A = [1, 1/3, 1/5; 3, 1, 1/2; 5, 2, 1];
    end

    [n, ~] = size(A);
    [V, D] = eig(A);
    eigenvalues = diag(D);
    [lambda_max, idx] = max(real(eigenvalues));
    w = abs(real(V(:, idx)));
    w = w / sum(w);

    CI = (lambda_max - n) / (n - 1);
    RI_list = [0, 0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45];
    RI = RI_list(min(n, length(RI_list)));
    CR = CI / max(RI, 1e-10);
    ok = CR < 0.1;

    fprintf('===== AHP 结果 =====\n');
    fprintf('λ_max = %.4f\n', lambda_max);
    fprintf('CR = %.4f ', CR);
    if ok, fprintf('✓ 通过\n'); else, fprintf('✗ 不通过！\n'); end
    for i = 1:n
        fprintf('w%d = %.4f\n', i, w(i));
    end
end
