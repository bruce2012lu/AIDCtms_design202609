@echo off
set AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261
set AWP_ROOT=%AWP_ROOT261%
cd /d "%~dp0"
"%AWP_ROOT261%\icemcfd\win64_amd\bin\icemcfd.bat" -batch -script "%~dp0build_lpddr_array.rpl"
echo exit %ERRORLEVEL%
