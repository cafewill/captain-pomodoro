#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python}"
if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
fi

export PYINSTALLER_CONFIG_DIR="${PYINSTALLER_CONFIG_DIR:-$PWD/.pyinstaller-cache}"

ICON_PNG="src/pomodoro_plus/assets/app.png"
ICONSET="build/PomodoroPlus.iconset"
ICON_ICNS="src/pomodoro_plus/assets/app_icon.icns"

if [[ -f "$ICON_PNG" ]] && command -v sips >/dev/null 2>&1 && command -v iconutil >/dev/null 2>&1; then
  mkdir -p "$ICONSET"
  for size in 16 32 128 256 512; do
    sips -z "$size" "$size" "$ICON_PNG" --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
    sips -z "$((size * 2))" "$((size * 2))" "$ICON_PNG" --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
  done
  if ! iconutil -c icns "$ICONSET" -o "$ICON_ICNS"; then
    echo "warning: failed to create $ICON_ICNS; building with the default bundle icon" >&2
    rm -f "$ICON_ICNS"
  fi
fi

"${PYTHON_BIN}" -m PyInstaller --noconfirm --clean PomodoroPlus.spec
