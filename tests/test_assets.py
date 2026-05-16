from pomodoro_plus.assets import app_icon_path, random_animation_path
from pomodoro_plus.timer import TimerMode


def test_app_icon_exists() -> None:
    assert app_icon_path().exists()


def test_default_animation_assets_exist() -> None:
    assert random_animation_path(TimerMode.FOCUS) is not None
    assert random_animation_path(TimerMode.BREAK) is not None
