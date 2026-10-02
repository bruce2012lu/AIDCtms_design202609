$ErrorActionPreference = 'Continue'
$env:AWP_ROOT261 = 'E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261'
$env:AWP_ROOT = $env:AWP_ROOT261
$fluent = Join-Path $env:AWP_ROOT261 'fluent\ntbin\win64\fluent.exe'
$here = 'D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0'
Set-Location (Join-Path $here 'fluent')
$log = Join-Path $here 'logs\fluent_cht.log'
"START $(Get-Date -Format o)" | Set-Content -Encoding ascii $log
"FLUENT=$fluent exists=$([bool](Test-Path -LiteralPath $fluent))" | Add-Content -Encoding ascii $log
if (-not (Test-Path -LiteralPath $fluent)) { 'fluent.exe not found' | Add-Content $log; exit 2 }
& $fluent 3ddp -t4 -g -i uc01b_cht.jou *>> $log
"FLUENT_EXIT=$LASTEXITCODE" | Add-Content -Encoding ascii $log
exit $LASTEXITCODE
