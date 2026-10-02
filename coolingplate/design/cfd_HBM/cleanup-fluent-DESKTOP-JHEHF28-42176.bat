echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 64220 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 55548) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 61812) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 37312) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 68060) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 42176) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 34060)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-42176.bat"
