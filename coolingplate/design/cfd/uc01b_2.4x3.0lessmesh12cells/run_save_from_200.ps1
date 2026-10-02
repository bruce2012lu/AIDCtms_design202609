$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Log = Join-Path $Root "logs\fluent_cht_less_12y_sp_gpgpu.log"
$Jou = Join-Path $Root "fluent\uc01b_cht_less_12y_gpu_solve.jou"
$Watch = Join-Path $Root "logs\save_from_200_watch.log"
$Marker = "/solve/iterate 300`n"
$Out = "D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd/uc01b_2.4x3.0lessmesh12cells/fluent/uc01b_cht_less_12y"
$utf8 = New-Object System.Text.UTF8Encoding $false

function Write-Watch([string]$msg) {
    Add-Content -Path $Watch -Value ("{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg)
}

function Get-Residual {
    if (-not (Test-Path $Log)) { return $null }
    $hit = $null
    foreach ($line in (Get-Content -Path $Log -Tail 80)) {
        if ($line -match '^\s+(\d+)\s+([0-9.]+e[+-]\d+)\s+([0-9.]+e[+-]\d+)\s+([0-9.]+e[+-]\d+)\s+([0-9.]+e[+-]\d+)\s+([0-9.]+e[+-]\d+)\s+([0-9.]+e[+-]\d+)\s+([0-9.]+e[+-]\d+)') {
            $hit = $Matches
        }
    }
    if (-not $hit) { return $null }
    return [pscustomobject]@{
        Iter = [int]$hit[1]
        Cont = [double]$hit[2]
        X = [double]$hit[3]
        Y = [double]$hit[4]
        Z = [double]$hit[5]
        Energy = [double]$hit[6]
        K = [double]$hit[7]
        Omega = [double]$hit[8]
    }
}

function Get-Iter {
    $r = Get-Residual
    if ($r) { return $r.Iter }
    return $null
}

function Test-Converged($r) {
    if (-not $r) { return $false }
    return ($r.Cont -le 1e-4 -and $r.X -le 1e-4 -and $r.Y -le 1e-4 -and $r.Z -le 1e-4 -and $r.Energy -le 1e-6 -and $r.K -le 1e-3 -and $r.Omega -le 1e-3)
}

function Set-JournalTail([string]$tail) {
    $text = [System.IO.File]::ReadAllText($Jou)
    $i = $text.IndexOf($Marker)
    if ($i -lt 0) { throw "iterate 300 marker not found" }
    $head = $text.Substring(0, $i + $Marker.Length)
    [System.IO.File]::WriteAllText($Jou, $head + $tail, $utf8)
}

function Tail-Lines([int[]]$steps) {
    $lines = New-Object System.Collections.Generic.List[string]
    foreach ($s in $steps) {
        $lines.Add("/file/write-case-data `"$Out`_i$s`"")
        if ($s -lt 1000) { $lines.Add("/solve/iterate 200") }
    }
    $lines.Add("/file/stop-transcript")
    return ($lines -join "`n") + "`n"
}

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class FluentKeys {
  public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@

function Send-Interrupt {
    $script:found = [IntPtr]::Zero
    $cb = [FluentKeys+EnumProc]{
        param($h, $l)
        if (-not [FluentKeys]::IsWindowVisible($h)) { return $true }
        $sb = New-Object System.Text.StringBuilder 500
        [void][FluentKeys]::GetWindowText($h, $sb, $sb.Capacity)
        if ($sb.ToString() -match 'Parallel Fluent') { $script:found = $h; return $false }
        return $true
    }
    [void][FluentKeys]::EnumWindows($cb, [IntPtr]::Zero)
    if ($script:found -eq [IntPtr]::Zero) { throw "Fluent window not found" }
    [void][FluentKeys]::ShowWindow($script:found, 9)
    [void][FluentKeys]::SetForegroundWindow($script:found)
    Start-Sleep -Milliseconds 400
    $rect = New-Object FluentKeys+RECT
    [void][FluentKeys]::GetWindowRect($script:found, [ref]$rect)
    $x = $rect.Left + 180
    $y = $rect.Bottom - 80
    [void][FluentKeys]::SetCursorPos($x, $y)
    [FluentKeys]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    [FluentKeys]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 300
    [FluentKeys]::keybd_event(0x11, 0, 0, [UIntPtr]::Zero)
    [FluentKeys]::keybd_event(0x43, 0, 0, [UIntPtr]::Zero)
    [FluentKeys]::keybd_event(0x43, 0, 2, [UIntPtr]::Zero)
    [FluentKeys]::keybd_event(0x11, 0, 2, [UIntPtr]::Zero)
}

$originalTail = @"
/file/write-case-data "$Out`_i300"
/solve/iterate 100
/file/write-case-data "$Out`_i400"
/solve/iterate 200
/file/write-case-data "$Out`_i600"
/solve/iterate 200
/file/write-case-data "$Out`_i800"
/solve/iterate 200
/file/write-case-data "$Out`_i1000"
/file/stop-transcript
"@.Replace("`r`n", "`n")
if (-not $originalTail.EndsWith("`n")) { $originalTail += "`n" }
$from200 = (Tail-Lines @(200, 400, 600, 800, 1000))

Write-Watch "watcher started"
$reason = "iteration 200"
while ($true) {
    if (-not (Get-Process -Name cx2610 -ErrorAction SilentlyContinue)) {
        Write-Watch "fluent cortex exited before iteration 200"
        exit 2
    }
    $r = Get-Residual
    $n = if ($r) { $r.Iter } else { $null }
    Write-Watch "iter=$n"
    if ($n -ge 200) { break }
    if (Test-Converged $r) { $reason = "converged at iteration $n"; break }
    Start-Sleep -Seconds 20
}

if ($reason -like "converged*" -and $n -lt 200) {
    $remain = 200 - $n
    $early = @(
        "/file/write-case-data `"$Out`_i$n`"",
        "/solve/iterate $remain",
        "/file/write-case-data `"$Out`_i200`""
    )
    foreach ($s in 400, 600, 800, 1000) {
        $early += "/solve/iterate 200"
        $early += "/file/write-case-data `"$Out`_i$s`""
    }
    $early += "/file/stop-transcript"
    Set-JournalTail (($early -join "`n") + "`n")
    Write-Watch "journal tail set to save converged i$n, then i200 and every 200 steps"
} else {
    Set-JournalTail $from200
    Write-Watch "journal tail set to save i200 then every 200 steps"
}
Send-Interrupt
Write-Watch "interrupt sent"

$stopped = $false
for ($k = 0; $k -lt 12; $k++) {
    Start-Sleep -Seconds 15
    $n2 = Get-Iter
    $tail = (Get-Content -Path $Log -Tail 25) -join "`n"
    Write-Watch "after interrupt iter=$n2"
    if ($tail -match 'i200|write-case-data|Interrupt') { $stopped = $true; break }
    if ($n2 -ge 203) { break }
}
if (-not $stopped -and (Get-Iter) -ge 203) {
    Set-JournalTail $originalTail
    Write-Watch "interrupt did not stop the block; restored save at i300 then every 200 steps"
    exit 3
}
Write-Watch "stop at iteration 200 accepted"
exit 0
