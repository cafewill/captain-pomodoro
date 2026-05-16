from pathlib import Path

from pomodoro_plus.settings import AppSettings, load_settings, save_settings, validate_settings


def test_validate_settings_clamps_ranges() -> None:
    settings = validate_settings(
        {
            "focus_label": "  창의적인 활동  ",
            "focus_minutes": 100,
            "break_label": "  커피 타임  ",
            "break_minutes": 1,
            "always_on_top": True,
        }
    )

    assert settings.focus_label == "창의적인 활동"
    assert settings.focus_minutes == 60
    assert settings.break_label == "커피 타임"
    assert settings.break_minutes == 5
    assert settings.always_on_top is True


def test_save_and_load_settings(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    original = AppSettings(
        focus_label="업무 및 생산",
        focus_minutes=30,
        break_label="산책",
        break_minutes=10,
        always_on_top=True,
    )

    save_settings(original, path)

    assert load_settings(path) == original
