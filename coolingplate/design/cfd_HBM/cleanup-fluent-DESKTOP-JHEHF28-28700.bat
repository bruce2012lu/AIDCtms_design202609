echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 53366 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 17120) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 30120) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 11020) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 5840) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 28700) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 9344)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-28700.bat"
