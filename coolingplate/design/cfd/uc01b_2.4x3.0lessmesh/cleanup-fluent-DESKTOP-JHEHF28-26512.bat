echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 61224 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 41864) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 14304) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 38932) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 42380) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 26512) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 39704)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh\cleanup-fluent-DESKTOP-JHEHF28-26512.bat"
