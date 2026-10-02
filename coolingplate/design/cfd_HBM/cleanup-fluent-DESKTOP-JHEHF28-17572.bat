echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 63561 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 24164) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 10664) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 20144) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 14776) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 5820) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 22216) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 10380) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 31728) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 17572) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 17700)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-17572.bat"
