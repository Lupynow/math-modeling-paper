% 粒子群优化 (PSO) MATLAB 模板

function [gbest_x, gbest_f, history] = pso_template()
    % ===== 参数设置 =====
    n_particles = 30;
    n_var = 2;
    bounds = [0, 10; 0, 10];
    max_iter = 200;
    w_start = 0.9; w_end = 0.4;
    c1 = 2.0; c2 = 2.0;
    patience = 50;
    tol = 1e-6;

    % ===== 初始化 =====
    pos = zeros(n_particles, n_var);
    vel = zeros(n_particles, n_var);
    for i = 1:n_var
        pos(:, i) = bounds(i,1) + (bounds(i,2)-bounds(i,1)) * rand(n_particles, 1);
        vel(:, i) = (bounds(i,2)-bounds(i,1)) * 0.1 * randn(n_particles, 1);
    end

    fitness = evaluate_pop(pos);

    pbest_pos = pos;
    pbest_fit = fitness;
    [gbest_f, idx] = max(fitness);
    gbest_x = pos(idx, :);
    no_improve = 0;

    history.best_fitness = zeros(max_iter, 1);
    history.avg_fitness = zeros(max_iter, 1);

    % ===== 主循环 =====
    for it = 1:max_iter
        w = w_start - (w_start - w_end) * it / max_iter;

        r1 = rand(n_particles, n_var);
        r2 = rand(n_particles, n_var);

        vel = w * vel + c1 * r1 .* (pbest_pos - pos) + c2 * r2 .* (gbest_x - pos);

        % 速度限制
        for i = 1:n_var
            v_max = abs(bounds(i,2) - bounds(i,1)) * 0.2;
            vel(:, i) = max(-v_max, min(v_max, vel(:, i)));
        end

        pos = pos + vel;

        % 边界处理
        for i = 1:n_var
            pos(:, i) = max(bounds(i,1), min(bounds(i,2), pos(:, i)));
        end

        fitness = evaluate_pop(pos);

        improved = fitness > pbest_fit;
        pbest_pos(improved, :) = pos(improved, :);
        pbest_fit(improved) = fitness(improved);

        [iter_best, idx] = max(fitness);
        if iter_best > gbest_f + tol
            gbest_f = iter_best;
            gbest_x = pos(idx, :);
            no_improve = 0;
        else
            no_improve = no_improve + 1;
        end

        history.best_fitness(it) = gbest_f;
        history.avg_fitness(it) = mean(fitness);

        if mod(it, 20) == 0
            fprintf('Iter %4d | Best: %.6f\n', it, gbest_f);
        end

        if no_improve >= patience
            fprintf('收敛于第 %d 次迭代\n', it);
            break;
        end
    end

    figure;
    plot(history.best_fitness(1:it), 'b-', 'LineWidth', 1.5); hold on;
    plot(history.avg_fitness(1:it), 'r-', 'LineWidth', 1);
    xlabel('Iteration'); ylabel('Fitness');
    legend('Best', 'Average');
    title('PSO Convergence');
end

function fit = evaluate_pop(pos)
    [n, ~] = size(pos);
    fit = zeros(n, 1);
    for i = 1:n
        fit(i) = obj_func(pos(i, :));
    end
end

function f = obj_func(x)
    % TODO: 替换为实际目标函数
    f = -sum(x.^2);
end
