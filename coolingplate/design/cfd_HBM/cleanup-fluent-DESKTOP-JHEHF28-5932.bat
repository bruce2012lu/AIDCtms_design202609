echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 62729 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 36580) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 5932) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 35940)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-5932.bat"
