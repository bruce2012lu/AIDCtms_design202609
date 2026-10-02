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
function Get-Iter {
    $n = $null
    foreach ($line in (Get-Content -Path $Log -Tail 40)) {
        if ($line -match '^\s+(\d+)\s+[0-9.]+e[+-]\d+') { $n = [int]$Matches[1] }
    }
    return $n
}
function Set-JournalTail([string]$tail) {
    $text = [System.IO.File]::ReadAllText($Jou)
    $i = $text.IndexOf($Marker)
    if ($i -lt 0) { throw "iterate 300 marker not found" }
    $head = $text.Substring(0, $i + $Marker.Length)
    [System.IO.File]::WriteAllText($Jou, $head + $tail, $utf8)
}

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class FluentFg {
  public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@

$n = Get-Iter
if (-not $n -or $n -ge 200) { Write-Watch "skip interrupt, iter=$n"; exit 0 }
$remain = 200 - $n
$lines = @(
    "/file/write-case-data `"$Out`_i$n`"",
    "/solve/iterate $remain",
    "/file/write-case-data `"$Out`_i200`""
)
foreach ($s in 400, 600, 800, 1000) {
    $lines += "/solve/iterate 200"
    $lines += "/file/write-case-data `"$Out`_i$s`""
}
$lines += "/file/stop-transcript"
Set-JournalTail (($lines -join "`n") + "`n")
Write-Watch "foreground interrupt at iter=$n"

$script:hwnd = [IntPtr]::Zero
$cb = [FluentFg+EnumProc]{
    param($h, $l)
    if (-not [FluentFg]::IsWindowVisible($h)) { return $true }
    $sb = New-Object System.Text.StringBuilder 500
    [void][FluentFg]::GetWindowText($h, $sb, $sb.Capacity)
    if ($sb.ToString() -match 'Parallel Fluent') { $script:hwnd = $h; return $false }
    return $true
}
[void][FluentFg]::EnumWindows($cb, [IntPtr]::Zero)
if ($script:hwnd -eq [IntPtr]::Zero) { throw "Fluent window not found" }
$fg = [FluentFg]::GetForegroundWindow()
$fgThread = [uint32]0
$myThread = [FluentFg]::GetCurrentThreadId()
$targetThread = [FluentFg]::GetWindowThreadProcessId($script:hwnd, [ref]$fgThread)
$foreThread = [FluentFg]::GetWindowThreadProcessId($fg, [ref]$fgThread)
[void][FluentFg]::AttachThreadInput($myThread, $targetThread, $true)
[void][FluentFg]::AttachThreadInput($myThread, $foreThread, $true)
[FluentFg]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
[FluentFg]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
[void][FluentFg]::ShowWindow($script:hwnd, 9)
[void][FluentFg]::BringWindowToTop($script:hwnd)
[void][FluentFg]::SetForegroundWindow($script:hwnd)
Start-Sleep -Milliseconds 500
$rect = New-Object FluentFg+RECT
[void][FluentFg]::GetWindowRect($script:hwnd, [ref]$rect)
$x = [int](($rect.Left + $rect.Right) / 2)
$y = $rect.Bottom - 60
[void][FluentFg]::SetCursorPos($x, $y)
[FluentFg]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
[FluentFg]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 200
[FluentFg]::keybd_event(0x11, 0, 0, [UIntPtr]::Zero)
[FluentFg]::keybd_event(0x43, 0, 0, [UIntPtr]::Zero)
[FluentFg]::keybd_event(0x43, 0, 2, [UIntPtr]::Zero)
[FluentFg]::keybd_event(0x11, 0, 2, [UIntPtr]::Zero)
[void][FluentFg]::AttachThreadInput($myThread, $targetThread, $false)
[void][FluentFg]::AttachThreadInput($myThread, $foreThread, $false)
Write-Watch "foreground ctrl+c sent at iter=$n"

$start = $n
$saved = $false
for ($k = 0; $k -lt 16; $k++) {
    Start-Sleep -Seconds 15
    $now = Get-Iter
    $tail = (Get-Content -Path $Log -Tail 30) -join "`n"
    Write-Watch "check iter=$now"
    if ($tail -match 'Interrupt|write-case-data|Writing to') { $saved = $true; break }
    if ($now -ge ($start + 2)) { break }
}
if ($saved) {
    Write-Watch "converged field save started"
    exit 0
}
$restore = @"
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
if (-not $restore.EndsWith("`n")) { $restore += "`n" }
Set-JournalTail $restore
Write-Watch "interrupt failed at iter=$(Get-Iter); restored i300 then every 200 steps"
exit 3
