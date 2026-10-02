echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 62013 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 10876) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 24004) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 28840) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 22588) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 17748) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 35096) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 19956) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 10948) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 28308) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 33064)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-28308.bat"
