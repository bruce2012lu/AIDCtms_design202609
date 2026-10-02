echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 65014 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 21328) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 2700) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 31132) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 22512) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 17836) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 30296) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 26064) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 33116) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 39896) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 24428)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-39896.bat"
