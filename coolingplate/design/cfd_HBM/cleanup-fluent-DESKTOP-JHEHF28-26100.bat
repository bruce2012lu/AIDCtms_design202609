echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 56251 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 23612) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 21256) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 27904) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 22056) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 20000) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 7084) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 10388) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 32728) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 26100) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 31812)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-26100.bat"
