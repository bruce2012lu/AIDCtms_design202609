echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 62599 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 50744) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 59840) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 41500) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 34156) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 34392) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 45524)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-34392.bat"
