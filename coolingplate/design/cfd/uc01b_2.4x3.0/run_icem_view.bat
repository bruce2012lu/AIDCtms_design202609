@echo off
REM One-click: open UC-01b hex mesh in ICEM GUI (File-Open equivalent).
REM Project: icem\uc01b.prj   Mesh: icem\uc01b.uns (from mesh\uc01b.msh)
setlocal
set AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261
set AWP_ROOT=%AWP_ROOT261%
set ICEM=%AWP_ROOT261%\icemcfd\win64_amd\bin\icemcfd.bat
cd /d "%~dp0"
if not exist logs mkdir logs
if not exist icem\views mkdir icem\views

if not exist "%ICEM%" (
  echo ICEM bat not found: %ICEM%
  echo ICEM bat not found: %ICEM% > logs\icem_view.log
  exit /b 2
)

if not exist "icem\uc01b.uns" (
  echo Importing Fluent msh into ICEM project...
  call "%ICEM%" -batch -script "%~dp0icem\import_uc01b_mesh.rpl" >> logs\icem_view.log 2>&1
)

if not exist "icem\uc01b.prj" (
  echo ERROR: icem\uc01b.prj was not created. See logs\icem_view.log
  exit /b 3
)

echo Opening ICEM GUI with icem\uc01b.prj
echo File ^> Open Project ^> icem\uc01b.prj
echo If blank: File ^> Mesh ^> Open Mesh ^> icem\uc01b.uns then Fit / F9
echo Replay views: File ^> Replay Scripts ^> Replay ^> icem\view_uc01b.rpl
echo Look at 3 slots (Y), jet (X=0), return slits (+/-X top). Units: meters.
REM Open the project file (one click). New window; ICEM stays up.
start "ICEM UC-01b mesh" /D "%~dp0icem" cmd /c call "%ICEM%" "%~dp0icem\uc01b.prj"
echo ICEM launch requested. Project: %~dp0icem\uc01b.prj
exit /b 0

