# Capture the ICEM CFD main window to PNG (fallback when ICEM write_ppm fails).
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class NativeWin {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [StructLayout(LayoutKind.Sequential)]
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@

$outDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$proc = Get-Process med -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne [IntPtr]::Zero } | Select-Object -First 1
if (-not $proc) {
    Write-Host "NO_ICEM_WINDOW"
    exit 2
}
$hwnd = $proc.MainWindowHandle
[void][NativeWin]::ShowWindow($hwnd, 9)
[void][NativeWin]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 800
$r = New-Object NativeWin+RECT
[void][NativeWin]::GetWindowRect($hwnd, [ref]$r)
$w = $r.Right - $r.Left
$h = $r.Bottom - $r.Top
Write-Host "HWND=$hwnd title='$($proc.MainWindowTitle)' ${w}x${h}"
if ($w -lt 200 -or $h -lt 200) {
    Write-Host "WINDOW_TOO_SMALL"
    exit 3
}
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size $w, $h))
$png = Join-Path $outDir "icem_gui.png"
$bmp.Save($png, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
Write-Host "WROTE $png"
exit 0
