rn1 = 28.2e3; % 0°C
%rn1 = 18.2e3; % 10°C
rn1 = 22.6e3; % 5°C

rn2 = 4.16e3; % 50°C
%rn2 = 3.04e3; % 60°C
rn = [rn1 rn2];

v1 = 0.8;
v2 = 0.45;

r2_exact = rn1*rn2/((v2-1)*rn2 + (v2/v1-v2)*rn1)
r2 = e_series(r2_exact)
r1_exact = r2*rn1*(1-v1)/(v1*(r2+rn1))
r1 = e_series(r1_exact)
v_calc = r2*rn./(r1*r2+r1*rn+r2*rn)
r2 = 100e3;
r1 = 4.7e3;
rn2 = 4.16e3; % 50°C
rn1 = 18.2e3; % 10°C
rn1 = 22.6e3; % 5°C
rn = [rn1 rn2];
v_calc = r2*rn./(r1*r2+r1*rn+r2*rn)

