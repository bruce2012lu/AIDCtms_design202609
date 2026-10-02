echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 62167 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 68036) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 52444) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 68012) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 42204) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 66324) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 56960)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-66324.bat"
