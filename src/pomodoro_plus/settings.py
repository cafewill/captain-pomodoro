from __future__ import annotations

from dataclasses import asdict, dataclass
from json import JSONDecodeError
import json
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir


APP_NAME = "PomodoroPlus"
APP_AUTHOR = "CaptainPomodoro"

FOCUS_MIN_MINUTES = 10
FOCUS_MAX_MINUTES = 60
BREAK_MIN_MINUTES = 5
BREAK_MAX_MINUTES = 20


@dataclass(frozen=True)
class AppSettings:
    focus_label: str = "업무"
    focus_minutes: int = 25
    break_label: str = "휴식"
    break_minutes: int = 5
    always_on_top: bool = False
    auto_cycle: bool = False
    notification_sound: bool = True
    notification_sound_path: str = ""


def default_settings_path() -> Path:
    return Path(user_config_dir(APP_NAME, APP_AUTHOR)) / "settings.json"


def load_settings(path: Path | None = None) -> AppSettings:
    settings_path = path or default_settings_path()
    if not settings_path.exists():
        return AppSettings()

    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, JSONDecodeError):
        return AppSettings()

    if not isinstance(data, dict):
        return AppSettings()
    return validate_settings(data)


def save_settings(settings: AppSettings, path: Path | None = None) -> None:
    settings_path = path or default_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(asdict(settings), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def validate_settings(data: dict[str, Any]) -> AppSettings:
    defaults = AppSettings()
    focus_label = _clean_label(data.get("focus_label"), defaults.focus_label)
    break_label = _clean_label(data.get("break_label"), defaults.break_label)

    return AppSettings(
        focus_label=focus_label,
        focus_minutes=_bounded_int(
            data.get("focus_minutes"),
            defaults.focus_minutes,
            FOCUS_MIN_MINUTES,
            FOCUS_MAX_MINUTES,
        ),
        break_label=break_label,
        break_minutes=_bounded_int(
            data.get("break_minutes"),
            defaults.break_minutes,
            BREAK_MIN_MINUTES,
            BREAK_MAX_MINUTES,
        ),
        always_on_top=bool(data.get("always_on_top", defaults.always_on_top)),
        auto_cycle=bool(data.get("auto_cycle", defaults.auto_cycle)),
        notification_sound=bool(data.get("notification_sound", defaults.notification_sound)),
        notification_sound_path=_clean_path(data.get("notification_sound_path")),
    )


def _clean_label(value: object, fallback: str) -> str:
    if not isinstance(value, str):
        return fallback
    label = value.strip()
    if not label:
        return fallback
    return label[:20]


def _bounded_int(value: object, fallback: int, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(minimum, min(maximum, number))


def _clean_path(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()
