$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent (Split-Path -Parent $here)
$py = Join-Path $root "cad\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
Write-Host "冷板设计台  http://127.0.0.1:8765/"
& $py (Join-Path $here "mcp\server.py") --http 8765
