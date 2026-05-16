from pathlib import Path

from pomodoro_plus.stats import record_completion, today_stats


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
