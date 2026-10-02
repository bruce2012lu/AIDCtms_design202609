@echo off
setlocal
set AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261
set AWP_ROOT=%AWP_ROOT261%
set ICEM=%AWP_ROOT261%\icemcfd\win64_amd\bin\icemcfd.bat
cd /d "%~dp0"
if not exist logs mkdir logs
echo AWP_ROOT261=%AWP_ROOT261% > logs\icem_batch.log
echo ICEM=%ICEM% >> logs\icem_batch.log
if not exist "%ICEM%" (
  echo ICEM bat not found >> logs\icem_batch.log
  exit /b 2
)
call "%ICEM%" -batch -script "%~dp0icem\build_uc01b.rpl" >> logs\icem_batch.log 2>&1
echo ICEM_EXIT=%ERRORLEVEL% >> logs\icem_batch.log
exit /b %ERRORLEVEL%
