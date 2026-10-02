echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 60961 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 40324) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 31460) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 23532) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 23280) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 18748) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 30220) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 39728) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 2876) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 21884) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 12000)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-21884.bat"
