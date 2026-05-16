from __future__ import annotations

from datetime import date
import json
from pathlib import Path

from platformdirs import user_config_dir

from pomodoro_plus.settings import APP_AUTHOR, APP_NAME


def _stats_path() -> Path:
    return Path(user_config_dir(APP_NAME, APP_AUTHOR)) / "stats.json"


def _load_all(path: Path | None = None) -> dict:
    target = path or _stats_path()
    if not target.exists():
        return {}
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        return {}


def record_completion(mode: str, minutes: int, path: Path | None = None) -> None:
    target = path or _stats_path()
    all_stats = _load_all(target)
    today = date.today().isoformat()
    day = all_stats.setdefault(today, _empty_day())
    if mode == "focus":
        day["focus_count"] += 1
        day["focus_minutes"] += minutes
    else:
        day["break_count"] += 1
        day["break_minutes"] += minutes
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(all_stats, ensure_ascii=False, indent=2), encoding="utf-8")


def today_stats(path: Path | None = None) -> dict:
    today = date.today().isoformat()
    return _load_all(path).get(today, _empty_day())


def _empty_day() -> dict:
    return {"focus_count": 0, "focus_minutes": 0, "break_count": 0, "break_minutes": 0}
