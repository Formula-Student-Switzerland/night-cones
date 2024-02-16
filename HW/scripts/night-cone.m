%%% nightcone dimensioning script

%% Cleanup workspace
clc;
clear;
close all;

%% System definition
nof_LED = 20;
% LED protocol
LED_buffer = 25;
% WS2813B
t_0_H = 400e-9;
t_0_L = 850e-9;
t_1_H = 800e-9;
t_1_L = 450e-9;
% WS2812C
t_0_H = 300e-9;
t_0_L = 1090e-9;
t_1_H = 1090e-9;
t_1_L = 320e-9;
t_reset = 50e-6;
failsafe_timeout = 1e-3;
failsafe_fps = 1000;
% TLC555
t_P_LH = 120e-9;
t_P_HL = 240e-9;
r_on = 150;

%% Predefinitions
C_Edge = 100e-9;
C_Missing_Pulse = 10e-9;
C_Pulse = 1e-9;

%% Edge Detector


%% Missing Pulse Detector


%% Pulse Generator
R_Pulse_B = t_1_L ./ 0.693 ./ C_Pulse;
R_Pulse_A = t_1_H ./ 0.693 ./ C_Pulse - R_Pulse_B;
disp('== Pulse Generator ==');
disp(['C =  ' num2str(C_Pulse .* 1e9) 'nF']);
disp(['RA = ' num2str(R_Pulse_A ./ 1e3) 'kOhm']);
disp(['RB = ' num2str(R_Pulse_B ./ 1e3) 'kOhm']);
disp(' ');

t_h = C_Pulse .* (R_Pulse_A + R_Pulse_B) .* log(3 - exp(-t_P_LH ./ (C_Pulse .* (R_Pulse_B + r_on)))) + t_P_HL;
t_l = C_Pulse .* (R_Pulse_B + r_on) .* log(3 - exp(-t_P_HL ./ (C_Pulse .* (R_Pulse_A + R_Pulse_B)))) + t_P_LH;
disp(['Exact duration of high pulse: ' num2str(t_h .* 1e9) 'ns']);
disp(['Exact duration of low pulse:  ' num2str(t_l .* 1e9) 'ns']);

%% Reset Generator Counter
Protocol_length = nof_LED .* LED_buffer;
Protocol_time = Protocol_length .* (t_1_H + t_1_L);
Counter_Protocol = 2 .* Protocol_length;
Counter_t_reset = 2 .* ceil(t_reset ./ (t_1_H + t_1_L));
Counter_fps = ceil(1./ failsafe_fps ./ (t_1_H + t_1_L));
Counter_min = max([Counter_Protocol, Counter_t_reset, Counter_fps]);
Counter_output = ceil(log(Counter_min)/log(2) - 1);

disp('== Reset Generator Counter ==');
disp(['Use counter output Q' num2str(Counter_output)]);

