echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 60800 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 3692) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 16512) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 6640) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 24788) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 27580) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 25020)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0\cleanup-fluent-DESKTOP-JHEHF28-27580.bat"
