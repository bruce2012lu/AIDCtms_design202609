echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 58410 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 11096) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 20060) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 20812) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 18204) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 11084) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 16728) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 13104) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 38768) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 27076) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 37552)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-27076.bat"
