@echo off
setlocal
set AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261
set AWP_ROOT=%AWP_ROOT261%
set FLUENT=%AWP_ROOT261%\fluent\ntbin\win64\fluent.exe
cd /d "%~dp0"
echo AWP=%AWP_ROOT261% > ..\logs\probe_launch.log
echo EXE=%FLUENT% >> ..\logs\probe_launch.log
if not exist "%FLUENT%" (
  echo MISSING >> ..\logs\probe_launch.log
  exit /b 2
)
echo ===A 3ddp -g === >> ..\logs\probe_launch.log
"%FLUENT%" 3ddp -t1 -g -i exit_only.jou >> ..\logs\probe_launch.log 2>&1
echo A_EXIT=%ERRORLEVEL% >> ..\logs\probe_launch.log
echo ===B -r26.1.0 -gu -wait 3ddp === >> ..\logs\probe_launch.log
"%FLUENT%" -r26.1.0 -gu -wait 3ddp -t1 -i exit_only.jou >> ..\logs\probe_launch.log 2>&1
echo B_EXIT=%ERRORLEVEL% >> ..\logs\probe_launch.log
echo ===C 3ddp -r26.1.0 -gu -wait === >> ..\logs\probe_launch.log
"%FLUENT%" 3ddp -r26.1.0 -gu -wait -t1 -i exit_only.jou >> ..\logs\probe_launch.log 2>&1
echo C_EXIT=%ERRORLEVEL% >> ..\logs\probe_launch.log
exit /b 0
