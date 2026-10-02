param([Parameter(Mandatory = $true)][string]$Journal)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class RJ {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool f);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(int f, int dx, int dy, int data, int extra);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, int flags, int extra);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
}
"@
$main = (Get-Process cx2610).MainWindowHandle
$fgPid = 0
$targetThread = [RJ]::GetWindowThreadProcessId($main, [ref]$fgPid)
$me = [RJ]::GetCurrentThreadId()
[RJ]::AttachThreadInput($me, $targetThread, $true) | Out-Null
[RJ]::ShowWindow($main, 3) | Out-Null
[RJ]::BringWindowToTop($main) | Out-Null
[RJ]::SetForegroundWindow($main) | Out-Null
[RJ]::AttachThreadInput($me, $targetThread, $false) | Out-Null
Start-Sleep -Milliseconds 600
[RJ]::keybd_event(0x1B, 0, 0, 0); Start-Sleep -Milliseconds 15; [RJ]::keybd_event(0x1B, 0, 2, 0)
Start-Sleep -Milliseconds 60
function Click([int]$x, [int]$y) {
  [RJ]::SetCursorPos($x, $y) | Out-Null
  Start-Sleep -Milliseconds 30
  [RJ]::mouse_event(0x0002, 0, 0, 0, 0)
  Start-Sleep -Milliseconds 15
  [RJ]::mouse_event(0x0004, 0, 0, 0, 0)
  Start-Sleep -Milliseconds 280
}
$rect = New-Object RJ+RECT
[RJ]::GetWindowRect($main, [ref]$rect) | Out-Null
Click ($rect.L + 45) ($rect.T + 48)
Click ($rect.L + 128) ($rect.T + 86)
Start-Sleep -Milliseconds 400
$invoke = {
  param($MainHandle)
  Add-Type -AssemblyName UIAutomationClient
  Add-Type -AssemblyName UIAutomationTypes
  $root = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$MainHandle)
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, "Journal...")
  $item = $null
  foreach ($n in 1..20) {
    $item = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
    if ($item) { break }
    Start-Sleep -Milliseconds 100
  }
  if (-not $item) { throw "Journal menu item not found" }
  $item.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
}
$thread = New-Object System.Threading.Thread([System.Threading.ParameterizedThreadStart]$invoke)
$thread.IsBackground = $true
$thread.Start($main)
$script:hwnd = [IntPtr]::Zero
$cb = [RJ+EnumProc]{ param($h, $l)
  if (-not [RJ]::IsWindowVisible($h)) { return $true }
  $sb = New-Object System.Text.StringBuilder 80
  [RJ]::GetWindowText($h, $sb, 80) | Out-Null
  if ($sb.ToString() -eq "Select File") { $script:hwnd = $h; return $false }
  return $true
}
foreach ($n in 1..30) {
  $script:hwnd = [IntPtr]::Zero
  [RJ]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null
  if ($script:hwnd -ne [IntPtr]::Zero) { break }
  Start-Sleep -Milliseconds 100
}
if ($script:hwnd -eq [IntPtr]::Zero) { throw "Select File dialog did not open" }
$dlg = [System.Windows.Automation.AutomationElement]::FromHandle($script:hwnd)
$edits = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, "Journal File")))
$wrote = $false
foreach ($e in $edits) {
  if ($e.Current.ControlType.ProgrammaticName -eq "ControlType.Edit") {
    $e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($Journal)
    $wrote = $true
  }
}
if (-not $wrote) { throw "Journal File edit not found" }
$btns = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, "OK")))
foreach ($b in $btns) {
  if ($b.Current.ControlType.ProgrammaticName -eq "ControlType.Button") {
    $b.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
  }
}
Write-Output "reading $Journal"
