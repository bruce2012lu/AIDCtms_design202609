echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 59894 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 29104) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 29232) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 17692) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 20092) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 27868) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 12964)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-27868.bat"
