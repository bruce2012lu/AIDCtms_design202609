@echo off
setlocal
set "AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261"
set "AWP_ROOT=%AWP_ROOT261%"
set "FLUENT_INC=%AWP_ROOT261%\fluent"
set "FLUENT_ARCH=win64"
set "FLUENT_EXE=%FLUENT_INC%\ntbin\win64\fluent.exe"
set "ROOT=%~dp0"
set "JOU=%ROOT%fluent\hbm_w08h35.jou"
set "LOG=%ROOT%logs\hbm_w08h35_launch.log"
if not exist "%ROOT%logs" mkdir "%ROOT%logs"
if not exist "%ROOT%fluent" mkdir "%ROOT%fluent"
cd /d "%ROOT%"
echo AWP_ROOT261=%AWP_ROOT261% > "%LOG%"
echo CMD="%FLUENT_EXE%" 3d -r26.1.0 -t4 -g -i "%JOU%" >> "%LOG%"
if not exist "%FLUENT_EXE%" (
  echo fluent.exe not found >> "%LOG%"
  exit /b 2
)
"%FLUENT_EXE%" 3d -r26.1.0 -t4 -g -i "%JOU%" >> "%LOG%" 2>&1
echo FLUENT_EXIT=%ERRORLEVEL% >> "%LOG%"
exit /b %ERRORLEVEL%
