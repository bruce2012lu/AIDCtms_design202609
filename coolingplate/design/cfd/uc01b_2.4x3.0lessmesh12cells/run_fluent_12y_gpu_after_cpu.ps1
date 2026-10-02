$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Log = Join-Path $Root "logs\fluent_cht_less_12y_cpu_gpu_launch.log"
$Cas = Join-Path $Root "fluent\uc01b_cht_less_12y_cpu_init.cas.h5"
$Jou = Join-Path $Root "fluent\uc01b_cht_less_12y_gpu_solve.jou"
$env:AWP_ROOT261 = "E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261"
$env:AWP_ROOT = $env:AWP_ROOT261
$env:FLUENT_INC = Join-Path $env:AWP_ROOT261 "fluent"
$env:FLUENT_ARCH = "win64"
$Exe = Join-Path $env:FLUENT_INC "ntbin\win64\fluent.exe"

Add-Content -Path $Log -Value "GPU_WAITER_STARTED"
while (Get-Process -Name fluent, fl_mpi2610 -ErrorAction SilentlyContinue) {
    Start-Sleep -Seconds 30
}
if (-not (Test-Path $Cas)) {
    Add-Content -Path $Log -Value "CPU init case was not written"
    exit 3
}
Add-Content -Path $Log -Value "CPU_INIT_DONE"
Start-Process -FilePath $Exe -ArgumentList @("3d", "-r26.1.0", "-t4", "-gpgpu=1", "-i", $Jou) -WorkingDirectory $Root
Add-Content -Path $Log -Value "CPU_SOLVE_STARTED"
