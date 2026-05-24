% 遗传算法 (GA) MATLAB 模板
% 问题适配：修改 obj_func.m 和约束条件

function [best_x, best_f, history] = ga_template()
    % ===== 参数设置 =====
    pop_size = 50;
    n_var = 2;              % 变量数
    bounds = [0, 10; 0, 10]; % 变量范围 [min, max]
    pc = 0.8;               % 交叉概率
    pm = 0.05;              % 变异概率
    max_gen = 200;
    elite_size = max(1, round(pop_size * 0.05));
    patience = 50;
    tol = 1e-6;

    % ===== 初始化种群 =====
    pop = zeros(pop_size, n_var);
    for i = 1:n_var
        pop(:, i) = bounds(i,1) + (bounds(i,2)-bounds(i,1)) * rand(pop_size, 1);
    end
    fitness = evaluate_pop(pop);

    % 记录
    history.best_fitness = zeros(max_gen, 1);
    history.avg_fitness = zeros(max_gen, 1);

    [best_f, idx] = max(fitness);
    best_x = pop(idx, :);
    no_improve = 0;

    % ===== 主循环 =====
    for gen = 1:max_gen
        % 精英保留
        [~, sort_idx] = sort(fitness, 'descend');
        elites = pop(sort_idx(1:elite_size), :);

        % 锦标赛选择
        selected = tournament_select(pop, fitness, 3);

        % SBX 交叉
        offspring = sbx_crossover(selected, pc, bounds);

        % 多项式变异
        offspring = polynomial_mutation(offspring, pm, bounds);

        % 精英替换
        offspring(1:elite_size, :) = elites;

        pop = offspring;
        fitness = evaluate_pop(pop);

        [gen_best, idx] = max(fitness);
        history.best_fitness(gen) = gen_best;
        history.avg_fitness(gen) = mean(fitness);

        if gen_best > best_f + tol
            best_f = gen_best;
            best_x = pop(idx, :);
            no_improve = 0;
        else
            no_improve = no_improve + 1;
        end

        if mod(gen, 20) == 0
            fprintf('Gen %4d | Best: %.6f | Avg: %.6f\n', gen, best_f, history.avg_fitness(gen));
        end

        if no_improve >= patience
            fprintf('收敛于第 %d 代\n', gen);
            break;
        end
    end

    % 收敛曲线图
    figure;
    plot(history.best_fitness(1:gen), 'b-', 'LineWidth', 1.5); hold on;
    plot(history.avg_fitness(1:gen), 'r-', 'LineWidth', 1);
    xlabel('Generation'); ylabel('Fitness');
    legend('Best', 'Average');
    title('GA Convergence');
end

function fit = evaluate_pop(pop)
    [n, ~] = size(pop);
    fit = zeros(n, 1);
    for i = 1:n
        fit(i) = obj_func(pop(i, :));
    end
end

function f = obj_func(x)
    % TODO: 替换为实际目标函数（GA 最大化）
    f = -sum(x.^2);
    % 约束惩罚示例：
    % penalty = 0;
    % if x(1) + x(2) > 15
    %     penalty = 1e6 * (x(1) + x(2) - 15)^2;
    % end
    % f = f - penalty;
end

function selected = tournament_select(pop, fitness, k)
    [pop_size, n_var] = size(pop);
    selected = zeros(pop_size, n_var);
    for i = 1:pop_size
        candidates = randperm(pop_size, k);
        [~, winner] = max(fitness(candidates));
        selected(i, :) = pop(candidates(winner), :);
    end
end

function offspring = sbx_crossover(parents, pc, bounds)
    [n, n_var] = size(parents);
    offspring = parents;
    eta = 20;
    for i = 1:2:n-1
        if rand < pc
            for j = 1:n_var
                if abs(parents(i,j) - parents(i+1,j)) > 1e-10
                    u = rand;
                    if u <= 0.5
                        beta = (2*u)^(1/(eta+1));
                    else
                        beta = (1/(2*(1-u)))^(1/(eta+1));
                    end
                    offspring(i,j) = 0.5*((1+beta)*parents(i,j) + (1-beta)*parents(i+1,j));
                    offspring(i+1,j) = 0.5*((1-beta)*parents(i,j) + (1+beta)*parents(i+1,j));
                end
            end
        end
    end
    % 边界修正
    for i = 1:n_var
        offspring(:, i) = max(bounds(i,1), min(bounds(i,2), offspring(:, i)));
    end
end

function offspring = polynomial_mutation(parents, pm, bounds)
    [n, n_var] = size(parents);
    offspring = parents;
    eta = 20;
    for i = 1:n
        for j = 1:n_var
            if rand < pm
                u = rand;
                low = bounds(j,1); high = bounds(j,2);
                delta = min(offspring(i,j)-low, high-offspring(i,j)) / (high-low+1e-10);
                if u <= 0.5
                    delta_q = (2*u + (1-2*u)*(1-delta)^(eta+1))^(1/(eta+1)) - 1;
                else
                    delta_q = 1 - (2*(1-u) + 2*(u-0.5)*(1-delta)^(eta+1))^(1/(eta+1));
                end
                offspring(i,j) = offspring(i,j) + delta_q * (high - low);
            end
        end
    end
    for i = 1:n_var
        offspring(:, i) = max(bounds(i,1), min(bounds(i,2), offspring(:, i)));
    end
end
