echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 60639 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 59656) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 58812) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 50784) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 55020) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 53892) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 53792)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-53892.bat"
