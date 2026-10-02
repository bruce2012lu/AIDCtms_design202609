@echo off
setlocal
set "AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261"
set "AWP_ROOT=%AWP_ROOT261%"
set "FLUENT_INC=%AWP_ROOT261%\fluent"
set "FLUENT_ARCH=win64"
set "FLUENT_EXE=%FLUENT_INC%\ntbin\win64\fluent.exe"
set "ROOT=%~dp0"
set "JOU_CPU=%ROOT%fluent\uc01b_cht_less_12y_cpu_init.jou"
set "JOU_GPU=%ROOT%fluent\uc01b_cht_less_12y_gpu_solve.jou"
set "LOG=%ROOT%logs\fluent_cht_less_12y_cpu_gpu_launch.log"
if not exist "%ROOT%logs" mkdir "%ROOT%logs"
cd /d "%ROOT%"
echo AWP_ROOT261=%AWP_ROOT261% > "%LOG%"
echo FLUENT_INC=%FLUENT_INC% >> "%LOG%"
echo CPU="%FLUENT_EXE%" 3d -r26.1.0 -t4 -g -i "%JOU_CPU%" >> "%LOG%"
echo CPU_SOLVE="%FLUENT_EXE%" 3d -r26.1.0 -t4 -gpgpu=1 -i "%JOU_GPU%" >> "%LOG%"
if not exist "%FLUENT_EXE%" (
  echo fluent.exe not found >> "%LOG%"
  exit /b 2
)
start "fluent-cpu-init" /b "%FLUENT_EXE%" 3d -r26.1.0 -t4 -g -i "%JOU_CPU%"
echo CPU_STARTED>> "%LOG%"
call :wait_for_solver
if errorlevel 1 exit /b %ERRORLEVEL%
if not exist "%ROOT%fluent\uc01b_cht_less_12y_cpu_init.cas.h5" (
  echo CPU init case was not written>> "%LOG%"
  exit /b 3
)
echo CPU_INIT_DONE>> "%LOG%"
start "fluent-cpu-solve" /b "%FLUENT_EXE%" 3d -r26.1.0 -t4 -gpgpu=1 -i "%JOU_GPU%"
echo CPU_SOLVE_STARTED>> "%LOG%"
exit /b 0

:wait_for_solver
set /a N=0
:wait_up
set /a N+=1
if %N% GTR 24 exit /b 4
tasklist /FI "IMAGENAME eq fl_mpi2610.exe" | find /I "fl_mpi2610.exe" >nul
if not errorlevel 1 goto wait_down
ping -n 6 127.0.0.1 >nul
goto wait_up
:wait_down
ping -n 31 127.0.0.1 >nul
tasklist /FI "IMAGENAME eq fl_mpi2610.exe" | find /I "fl_mpi2610.exe" >nul
if not errorlevel 1 goto wait_down
tasklist /FI "IMAGENAME eq fluent.exe" | find /I "fluent.exe" >nul
if not errorlevel 1 goto wait_down
exit /b 0
