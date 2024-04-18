clc;
clear;
%close all;

plot_t_min = -10;
plot_t_max = 100;
LW = 2;

t_0C = 273.15;
t = [plot_t_min:plot_t_max] + t_0C;
B = 3380; % Verify with datasheet
R_ref = 10e3;
t_ref = 25 + t_0C;
V_ref = 3.3;
ADC_NOF_BIT = 10;
ADC_REF = 1;

R = R_ref .* exp(B .* (1 ./ t - 1 ./ t_ref));

% Circuit 1
%
%   VCC
%    A
%    |
%   +++
%   | |  R (NTC 10K)
%   | |
%   +++
%    |
%    #---> ADC
%    |
%   +++
%   | |  R_meas
%   | |
%   +++
%    |
%    V
%   GND

R_meas = [1.2e3; 1.1e3; 1e3];
V_meas = V_ref .* R_meas ./ (R + R_meas);

l = {};
for i = 1:numel(R_meas); 
    l(i) = {['R_{meas}: ' num2str(R_meas(i)/1e3) ' kOhm']};
end;

figure(1);
plot(t-t_0C, V_meas, 'LineWidth', LW);
grid on; grid minor on;
xlim([plot_t_min plot_t_max]);
title(['Temperature measurement characteristics']);
xlabel(['Temperature [^\circC]']);
ylabel(['Voltage [V]']);
legend(l);
print('-dpng', 'Temp_Meas');

ADC = 0:(2.^ADC_NOF_BIT - 1);
V_ADC = ADC ./ max(max(ADC)) .* ADC_REF;
R_ADC = V_ref .* R_meas ./ V_ADC - R_meas; % Double-check formula!!!!!!!!!!!!!!!!!
t_adc = 1 ./ (log(R_ADC ./ R_ref) ./ B + 1 ./ t_ref);

figure(2);
plot(ADC, t_adc-t_0C, 'LineWidth', LW);
grid on; grid minor on;
xlim([min(ADC) max(ADC)]);
xticks([0 1023 2047 3071 4095])
ylim([plot_t_min plot_t_max]);
title(['Temperature measurement discretization']);
xlabel(['ADC count']);
ylabel(['Temperature [^\circ' 'C]']);
legend(l);
print('-dpng', 'Temp_Discretization');

figure(3);
plot(t_adc(:, 1:end-1)' - t_0C', abs(t_adc(:, 2:end)-t_adc(:, 1:end-1))'*1e3, 'LineWidth', LW);
grid on; grid minor on;
xlim([plot_t_min plot_t_max]);
ylim([0 200]);
title(['Temperature measurement resolution']);
xlabel(['Temperature [^\circC]']);
ylabel(['Resolution [mK]']);
legend(l);
print('-dpng', 'Temp_Res');

% Circuit 2
%
%   VCC
%    A
%    |
%   +++
%   | |  R1
%   | |
%   +++
%    |
%    #--------#---> ADC
%    |        |
%   +++      +++
%   | |  R2  | |  R (NTC 10K)
%   | |      | |
%   +++      +++
%    |        |
%    V        V
%   GND      GND

R_1= [10e3;  22e3; 33e3; 47e3; 68e3; 100e3];
R_2= [4.7e3; 12e3; 20e3; 36e3; 68e3; 470e3];
V_meas = V_ref .* (R.*R_2./(R+R_2)) ./ (R_1 + (R.*R_2./(R+R_2)));
l = {};
for i = 1:numel(R_1); 
    l(i) = {['R_{1}: ' num2str(R_1(i)/1e3) ' kOhm, R_{2}: ' num2str(R_2(i)/1e3) 'kOhm']};
end;

figure(4);
plot(t-t_0C, V_meas, 'LineWidth', LW);
grid on; grid minor on;
xlim([plot_t_min plot_t_max]);
title(['Temperature measurement characteristics']);
xlabel(['Temperature [^\circC]']);
ylabel(['Voltage [V]']);
legend(l);
print('-dpng', 'Temp_Meas');

ADC = 0:(2.^ADC_NOF_BIT - 1);
V_ADC = ADC ./ max(max(ADC)) .* ADC_REF;
R_ADC = (V_ADC .* R_1 .* R_2) ./ (V_ref .* R_2 - V_ADC .* (R_1 + R_2)); % Double-check formula!!!!!!!!!!!!!!!!!
t_adc = 1 ./ (log(R_ADC ./ R_ref) ./ B + 1 ./ t_ref);

figure(5);
plot(ADC, t_adc-t_0C, 'LineWidth', LW);
grid on; grid minor on;
xlim([min(ADC) max(ADC)]);
xticks([0 1023 2047 3071 4095])
ylim([plot_t_min plot_t_max]);
title(['Temperature measurement discretization']);
xlabel(['ADC count']);
ylabel(['Temperature [^\circ' 'C]']);
legend(l);
print('-dpng', 'Temp_Discretization');

figure(6);
plot(t_adc(:, 1:end-1)' - t_0C', abs(t_adc(:, 2:end)-t_adc(:, 1:end-1))'*1e3, 'LineWidth', LW);
grid on; grid minor on;
xlim([plot_t_min plot_t_max]);
ylim([0 200]);
title(['Temperature measurement resolution']);
xlabel(['Temperature [^\circC]']);
ylabel(['Resolution [mK]']);
legend(l);
print('-dpng', 'Temp_Res');

