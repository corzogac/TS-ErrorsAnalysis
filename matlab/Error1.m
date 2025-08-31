function Error = Error1(P, T, Comment)
% -------------------------------------------------------------------------
% File    : Error1.m
% Purpose : Compute standard error/skill metrics for hydrological series and plot.
% Author  : Gerald Augusto Corzo Pérez
% Affil.  : IHE Delft — Hydroinformatics
% Version : 2.1 (2025-08-31)  % cleaned NaN handling and plotting
% License : MIT
% SPDX-License-Identifier: MIT
%
% Usage
%   Error = Error1(P, T, Comment)
% Inputs
%   P : Predicted values (vector)
%   T : Target/Observed values (vector)
%   Comment (optional) : figure tag/title suffix
%
% Outputs (fields)
%   RMSE, NSC, Cor, NRMSE (%), MAE, StdT, StdP, MuT, MuP,
%   PERS, SSE, SSEN, RMSEN, NRMSEN (%), MARE, Er, Po, Pu, h
%
% Notes
%   - NRMSE = 100 * RMSE / Std(T)     % your convention
%   - To use range-based NRMSE instead, set rngT = max(T)-min(T) and use:
%       NRMSE = 100 * RMSE / rngT;
%   - Coefficient of persistence PERS = 1 - SSE / SSEN (persistence baseline)
% -------------------------------------------------------------------------

if nargin < 3 || isempty(Comment)
    Comment = 'Target and Predicted';
end

% Ensure column vectors and pairwise finite values only
P = P(:); T = T(:);
mask = isfinite(P) & isfinite(T);
P = P(mask); T = T(mask);

n = numel(P);
if n < 2
    error('Error1:NotEnoughData', 'Need at least 2 paired values.');
end

% Basic stats (MATLAB-style population std uses w=1; omit NaNs already)
MuT  = mean(T, 'omitnan');   MuP  = mean(P, 'omitnan');
StdT = std(T, 1, 'omitnan'); StdP = std(P, 1, 'omitnan');

% Errors
resid = P - T;
SSE  = sum(resid.^2, 'omitnan');
RMSE = sqrt(SSE / n);
MAE  = mean(abs(resid), 'omitnan');

% NRMSE (% of Std(T)) -- change here if you prefer range-based
NRMSE = 100 * RMSE / StdT;    % if StdT==0 -> Inf; keep as-is to signal degenerate series

% Nash–Sutcliffe (NSC/NSE)
den = sum((T - MuT).^2, 'omitnan');
NSC = 1 - SSE / den;

% Pearson correlation (guard zero variance)
if StdT > 0 && StdP > 0
    Cor = corr(P, T);
else
    Cor = NaN;
end

% MARE (exclude zeros in T to avoid division by zero)
nz = (T ~= 0);
if any(nz)
    MARE = mean(abs((T(nz) - P(nz)) ./ T(nz)), 'omitnan');
else
    MARE = NaN;
end

% Persistence baseline: T_hat(i) = T(i-1)
T1 = T(1:end-1);
T2 = T(2:end);
m2 = isfinite(T1) & isfinite(T2);
dT = T2(m2) - T1(m2);

SSEN  = sum(dT.^2, 'omitnan');
RMSEN = sqrt(SSEN / max(1, numel(dT)));
% Range- or std-based normalization; here keep % of Std(T)
NRMSEN = 100 * RMSEN / StdT;

% Pack struct
Error.RMSE  = RMSE;
Error.NSC   = NSC;
Error.Cor   = Cor;
Error.NRMSE = NRMSE;
Error.MAE   = MAE;
Error.StdT  = StdT;
Error.StdP  = StdP;
Error.MuT   = MuT;
Error.MuP   = MuP;
Error.PERS  = 1 - SSE / SSEN;   % coefficient of persistence
Error.SSE   = SSE;
Error.SSEN  = SSEN;             % SSE of naive (persistence)
Error.RMSEN = RMSEN;
Error.NRMSEN= NRMSEN;
Error.MARE  = MARE;

% Error sign stats
Error.Er    = T - P;
Error.Po    = sum(Error.Er <= 0) / numel(Error.Er);  % proportion <= 0
Error.Pu    = sum(Error.Er >  0) / numel(Error.Er);  % proportion >  0

% Plot
figure1 = figure('Color',[1 1 1], 'Tag', Comment, 'HandleVisibility','on','Visible','on');
tiledlayout(2,1, 'Padding','compact', 'TileSpacing','compact');

% Upper: series
nexttile;
H1 = plot(P,'r--','LineWidth',1.8); hold on;
H2 = plot(T,'b-','LineWidth',1.2);
legend([H1 H2], {'Predicted','Target'}, 'Location','southoutside');
title({ 'Time series of target and predicted', ...
        sprintf('(RMSE = %.4g)  %s', RMSE, Comment) });
xlabel('Time'); ylabel('Discharge (m^3/s)'); grid on;

% Lower: error (T - P)
nexttile;
stem(T - P, 'filled'); grid on;
title(sprintf('Error between target and predicted (NRMSE = %.2f%%)', NRMSE));
xlabel('Time'); ylabel('Error (T - P)');

Error.h = figure1;
end
