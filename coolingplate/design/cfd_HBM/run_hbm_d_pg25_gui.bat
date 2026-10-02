@echo off
setlocal
set "AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261"
set "AWP_ROOT=%AWP_ROOT261%"
set "FLUENT_INC=%AWP_ROOT261%\fluent"
set "FLUENT_ARCH=win64"
set "FLUENT_EXE=%FLUENT_INC%\ntbin\win64\fluent.exe"
set "ROOT=%~dp0"
set "JOU=%ROOT%fluent\hbm_d_pg25_gui_solve.jou"
set "LOG=%ROOT%logs\hbm_d_pg25_gui_solve_launch.log"
if not exist "%ROOT%logs" mkdir "%ROOT%logs"
cd /d "%ROOT%"
echo CMD="%FLUENT_EXE%" 3d -r26.1.0 -t8 -i "%JOU%" > "%LOG%"
"%FLUENT_EXE%" 3d -r26.1.0 -t8 -i "%JOU%" >> "%LOG%" 2>&1
echo FLUENT_EXIT=%ERRORLEVEL% >> "%LOG%"
exit /b %ERRORLEVEL%
