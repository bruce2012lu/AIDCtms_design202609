echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\tell.exe" DESKTOP-JHEHF28 65394 CLEANUP_EXITING
timeout /t 1
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 53108) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 24504) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 51484) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 51352) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 45928) 
if /i "%LOCALHOST%"=="DESKTOP-JHEHF28" (%KILL_CMD% 22336)
del "D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\cleanup-fluent-DESKTOP-JHEHF28-45928.bat"
