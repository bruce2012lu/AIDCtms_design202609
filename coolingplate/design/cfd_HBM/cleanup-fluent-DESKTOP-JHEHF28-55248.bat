echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 56268 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 60320) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 63496) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 53252) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 55920) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 55248) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 64356)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\cleanup-fluent-DESKTOP-JHEHF28-55248.bat"
