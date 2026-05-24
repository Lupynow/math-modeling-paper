% 随机森林 MATLAB 模板 (需要 Statistics and Machine Learning Toolbox)

function [model, metrics] = rf_template()
    % 加载数据
    % TODO: data = readtable('data.csv');
    rng(42);
    n = 500;
    X = randn(n, 4);
    y = 3*X(:,1) + 2*X(:,2).^2 - 1.5*X(:,3) + 0.5*X(:,4).*X(:,1) + 0.5*randn(n,1);

    % 划分
    cv = cvpartition(n, 'HoldOut', 0.2);
    X_train = X(training(cv), :);
    y_train = y(training(cv));
    X_test = X(test(cv), :);
    y_test = y(test(cv));

    % 标准化
    [X_train, mu, sigma] = zscore(X_train);
    X_test = (X_test - mu) ./ sigma;

    % 训练随机森林
    model = TreeBagger(300, X_train, y_train, ...
        'Method', 'regression', ...
        'MinLeafSize', 5, ...
        'NumPredictorsToSample', 'all', ...
        'OOBPrediction', 'on');

    % 预测
    y_pred = str2double(predict(model, X_test));

    % 评估
    r2 = 1 - sum((y_test - y_pred).^2) / sum((y_test - mean(y_test)).^2);
    mae = mean(abs(y_test - y_pred));
    rmse = sqrt(mean((y_test - y_pred).^2));

    fprintf('\n===== 随机森林 评估结果 =====\n');
    fprintf('R²  = %.4f\n', r2);
    fprintf('MAE = %.4f\n', mae);
    fprintf('RMSE = %.4f\n', rmse);

    % 特征重要性
    imp = model.OOBPermutedPredictorDeltaError;
    figure;
    barh(imp);
    xlabel('Importance');
    title('Random Forest Feature Importance');
    set(gca, 'YTickLabel', {'x1','x2','x3','x4'});

    metrics = struct('r2', r2, 'mae', mae, 'rmse', rmse);
end
