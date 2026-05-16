$ErrorActionPreference = "Stop"

$PythonBin = "python"
if (Test-Path ".venv\Scripts\python.exe") {
  $PythonBin = ".venv\Scripts\python.exe"
}

if (-not $env:PYINSTALLER_CONFIG_DIR) {
  $env:PYINSTALLER_CONFIG_DIR = Join-Path (Get-Location) ".pyinstaller-cache"
}

& $PythonBin -m PyInstaller `
  --name "PomodoroPlus" `
  --windowed `
  --noconfirm `
  --clean `
  --add-data "src/pomodoro_plus/assets;pomodoro_plus/assets" `
  src/pomodoro_plus/__main__.py
