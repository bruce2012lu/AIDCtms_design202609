@echo off
setlocal
set AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261
set AWP_ROOT=%AWP_ROOT261%
set FLUENT=%AWP_ROOT261%\fluent\ntbin\win64\fluent.exe
cd /d "%~dp0fluent"
if not exist ..\logs mkdir ..\logs
echo AWP_ROOT261=%AWP_ROOT261% > ..\logs\fluent_cht2.log
echo FLUENT=%FLUENT% >> ..\logs\fluent_cht2.log
echo CMD="%FLUENT%" -r26.1.0 -gu -wait 3ddp -t4 -i uc01b_cht.jou >> ..\logs\fluent_cht2.log
if not exist "%FLUENT%" (
  echo fluent.exe not found >> ..\logs\fluent_cht2.log
  exit /b 2
)
"%FLUENT%" -r26.1.0 -gu -wait 3ddp -t4 -i uc01b_cht.jou >> ..\logs\fluent_cht2.log 2>&1
echo FLUENT_EXIT=%ERRORLEVEL% >> ..\logs\fluent_cht2.log
exit /b %ERRORLEVEL%
