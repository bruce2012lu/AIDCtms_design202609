@echo off
setlocal
set "AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261"
set "AWP_ROOT=%AWP_ROOT261%"
set "FLUENT_INC=%AWP_ROOT261%\fluent"
set "FLUENT_ARCH=win64"
set "FLUENT_EXE=%FLUENT_INC%\ntbin\win64\fluent.exe"
set "ROOT=%~dp0"
set "JOU=%ROOT%fluent\probe_exit.jou"
set "LOG=%ROOT%logs\fluent_gpu_probe_cmd.log"
cd /d "%ROOT%"
echo FLUENT_INC=%FLUENT_INC% > "%LOG%"
echo CMD="%FLUENT_EXE%" 3ddp -r26.1.0 -g -t4 -gpu -i "%JOU%" >> "%LOG%"
"%FLUENT_EXE%" 3ddp -r26.1.0 -g -t4 -gpu -i "%JOU%" >> "%LOG%" 2>&1
echo FLUENT_EXIT=%ERRORLEVEL% >> "%LOG%"
exit /b %ERRORLEVEL%
