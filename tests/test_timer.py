from pomodoro_plus.timer import PomodoroTimer, TimerMode, TimerState, format_seconds


def test_timer_starts_pauses_and_resets() -> None:
    timer = PomodoroTimer(focus_minutes=25, break_minutes=5)

    assert timer.snapshot().remaining_seconds == 25 * 60
    assert timer.state == TimerState.IDLE

    timer.start()
    assert timer.state == TimerState.RUNNING

    timer.pause()
    assert timer.state == TimerState.PAUSED

    timer.reset()
    snapshot = timer.snapshot()
    assert snapshot.state == TimerState.IDLE
    assert snapshot.remaining_seconds == 25 * 60


def test_timer_switches_mode() -> None:
    timer = PomodoroTimer(focus_minutes=25, break_minutes=5)

    timer.toggle_mode()

    snapshot = timer.snapshot()
    assert snapshot.mode == TimerMode.BREAK
    assert snapshot.remaining_seconds == 5 * 60


def test_format_seconds() -> None:
    assert format_seconds(0) == "00:00"
    assert format_seconds(65) == "01:05"
    assert format_seconds(25 * 60) == "25:00"
