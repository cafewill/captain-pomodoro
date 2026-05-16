#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python}"
if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
fi

export PYINSTALLER_CONFIG_DIR="${PYINSTALLER_CONFIG_DIR:-$PWD/.pyinstaller-cache}"

"${PYTHON_BIN}" -m PyInstaller \
  --name "PomodoroPlus" \
  --windowed \
  --noconfirm \
  --clean \
  --add-data "src/pomodoro_plus/assets:pomodoro_plus/assets" \
  src/pomodoro_plus/__main__.py
