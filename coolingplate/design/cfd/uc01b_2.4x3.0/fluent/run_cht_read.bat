@echo off
setlocal
set AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261
set AWP_ROOT=%AWP_ROOT261%
set FLUENT=%AWP_ROOT261%\fluent\ntbin\win64\fluent.exe
cd /d "%~dp0"
if not exist ..\logs mkdir ..\logs
echo START_READ >> ..\logs\fluent_cht_read.log
"%FLUENT%" 3ddp -t2 -g -i uc01b_cht_read.jou >> ..\logs\fluent_cht_read.log 2>&1
echo FLUENT_EXIT=%ERRORLEVEL% >> ..\logs\fluent_cht_read.log
exit /b %ERRORLEVEL%
