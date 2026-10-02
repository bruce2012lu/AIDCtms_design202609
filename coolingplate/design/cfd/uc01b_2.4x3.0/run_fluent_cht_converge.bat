@echo off
setlocal
set AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261
set AWP_ROOT=%AWP_ROOT261%
set FLUENT=%AWP_ROOT261%\fluent\ntbin\win64\fluent.exe
set JOU=%~dp0fluent\uc01b_cht_converge.jou
set LOG=%~dp0logs\fluent_cht_converge.log
cd /d "%~dp0fluent"
if not exist "%~dp0logs" mkdir "%~dp0logs"
echo AWP_ROOT261=%AWP_ROOT261% > "%LOG%"
echo FLUENT=%FLUENT% >> "%LOG%"
echo CMD="%FLUENT%" -r26.1.0 -gu -wait 3ddp -t4 -i "%JOU%" >> "%LOG%"
echo START=%DATE% %TIME% >> "%LOG%"
if not exist "%FLUENT%" (
  echo fluent.exe not found >> "%LOG%"
  exit /b 2
)
"%FLUENT%" -r26.1.0 -gu -wait 3ddp -t4 -i "%JOU%" >> "%LOG%" 2>&1
echo FLUENT_EXIT=%ERRORLEVEL% >> "%LOG%"
echo END=%DATE% %TIME% >> "%LOG%"
exit /b %ERRORLEVEL%
