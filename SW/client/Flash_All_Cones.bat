@ECHO off
FOR /L %%A IN (1,1,100) DO call :Flash %%A
goto End

:Flash
SET PADDED=0000000%1
SET PADDED=%PADDED:~-6%
ECHO Flash Cone %PADDED%
start python .\espota.py -p 13894 -a NC_update -f .\.pio\build\nodemcuv2_ota\firmware.bin -r -i  Night-cone-%PADDED%.local 
TIMEOUT /T 1
goto :eof

:End



