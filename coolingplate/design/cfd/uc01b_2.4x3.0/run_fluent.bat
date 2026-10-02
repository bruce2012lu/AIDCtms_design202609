@echo off
setlocal
set AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261
set AWP_ROOT=%AWP_ROOT261%
set FLUENT=%AWP_ROOT261%\fluent\ntbin\win64\fluent.exe
cd /d "%~dp0fluent"
if not exist ..\logs mkdir ..\logs
echo AWP_ROOT261=%AWP_ROOT261% > ..\logs\fluent_batch.log
echo FLUENT=%FLUENT% >> ..\logs\fluent_batch.log
if not exist "%FLUENT%" (
  echo fluent.exe not found >> ..\logs\fluent_batch.log
  exit /b 2
)
"%FLUENT%" 3ddp -t4 -g -i uc01b_laminar.jou >> ..\logs\fluent_batch.log 2>&1
echo FLUENT_EXIT=%ERRORLEVEL% >> ..\logs\fluent_batch.log
exit /b %ERRORLEVEL%
