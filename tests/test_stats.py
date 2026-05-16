from datetime import date, timedelta
import json
from pathlib import Path

import pytest

from pomodoro_plus.stats import period_stats, record_completion, today_stats


def test_record_and_read(tmp_path: Path) -> None:
    path = tmp_path / "stats.json"

    record_completion("focus", 25, path)
    record_completion("focus", 25, path)
    record_completion("break", 5, path)

    s = today_stats(path)
    assert s["focus_count"] == 2
    assert s["focus_minutes"] == 50
    assert s["break_count"] == 1
    assert s["break_minutes"] == 5


def test_empty_stats(tmp_path: Path) -> None:
    path = tmp_path / "stats.json"
    s = today_stats(path)
    assert s["focus_count"] == 0
    assert s["focus_minutes"] == 0


def test_period_stats_sums_requested_days(tmp_path: Path) -> None:
    path = tmp_path / "stats.json"
    end = date(2026, 5, 17)
    data = {
        end.isoformat(): {
            "focus_count": 2,
            "focus_minutes": 50,
            "break_count": 1,
            "break_minutes": 5,
        },
        (end - timedelta(days=6)).isoformat(): {
            "focus_count": 1,
            "focus_minutes": 25,
            "break_count": 1,
            "break_minutes": 5,
        },
        (end - timedelta(days=7)).isoformat(): {
            "focus_count": 9,
            "focus_minutes": 225,
            "break_count": 9,
            "break_minutes": 45,
        },
    }
    path.write_text(json.dumps(data), encoding="utf-8")

    s = period_stats(7, path, end)

    assert s["focus_count"] == 3
    assert s["focus_minutes"] == 75
    assert s["break_count"] == 2
    assert s["break_minutes"] == 10


def test_period_stats_rejects_non_positive_days(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        period_stats(0, tmp_path / "stats.json")
