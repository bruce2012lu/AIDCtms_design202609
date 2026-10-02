echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 56684 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 28228) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 44196) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 12132) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 41136) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 43920) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 40104)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0\fluent\cleanup-fluent-DESKTOP-JHEHF28-43920.bat"
