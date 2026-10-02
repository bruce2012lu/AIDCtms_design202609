@echo off
setlocal
REM FLUENT_INC must be the fluent DIRECTORY, never fluent.exe.
set "AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261"
set "AWP_ROOT=%AWP_ROOT261%"
set "FLUENT_INC=%AWP_ROOT261%\fluent"
set "FLUENT_ARCH=win64"
set "FLUENT_EXE=%FLUENT_INC%\ntbin\win64\fluent.exe"
set "ROOT=%~dp0"
set "JOU=%ROOT%fluent\uc01b_cht_less_t4_gpu.jou"
set "LOG=%ROOT%logs\fluent_cht_less_launch.log"
if not "%~1"=="" set "JOU=%~1"
if not exist "%ROOT%logs" mkdir "%ROOT%logs"
cd /d "%ROOT%"
echo AWP_ROOT261=%AWP_ROOT261% > "%LOG%"
echo FLUENT_INC=%FLUENT_INC% >> "%LOG%"
echo CMD="%FLUENT_EXE%" 3ddp -r26.1.0 -t4 -gpu -i "%JOU%" >> "%LOG%"
if not exist "%FLUENT_EXE%" (
  echo fluent.exe not found >> "%LOG%"
  exit /b 2
)
if not exist "%FLUENT_INC%\fluent26.1.0\" (
  echo FLUENT_INC is not a directory: %FLUENT_INC% >> "%LOG%"
  exit /b 3
)
"%FLUENT_EXE%" 3ddp -r26.1.0 -t4 -gpu -i "%JOU%" >> "%LOG%" 2>&1
echo FLUENT_EXIT=%ERRORLEVEL% >> "%LOG%"
exit /b %ERRORLEVEL%
