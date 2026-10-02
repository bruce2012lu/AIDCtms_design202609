@echo off
setlocal
REM Visible ICEM GUI. No -batch. Mesh already written; this does not remesh.
set "AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261"
set "AWP_ROOT=%AWP_ROOT261%"
set "ICEM=%AWP_ROOT261%\icemcfd\win64_amd\bin\icemcfd.bat"
set "ROOT=%~dp0"
cd /d "%ROOT%"
if not exist "%ROOT%logs" mkdir "%ROOT%logs"
echo ICEM=%ICEM% > "%ROOT%logs\icem_gui_launch.log"
echo CMD=call "%ICEM%" >> "%ROOT%logs\icem_gui_launch.log"
if not exist "%ICEM%" (
  echo ICEM bat not found >> "%ROOT%logs\icem_gui_launch.log"
  exit /b 2
)
call "%ICEM%"
echo ICEM_EXIT=%ERRORLEVEL% >> "%ROOT%logs\icem_gui_launch.log"
exit /b %ERRORLEVEL%
