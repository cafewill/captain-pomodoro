from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from time import monotonic


class TimerMode(StrEnum):
    FOCUS = "focus"
    BREAK = "break"


class TimerState(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"


@dataclass(frozen=True)
class TimerSnapshot:
    mode: TimerMode
    state: TimerState
    duration_seconds: int
    remaining_seconds: int


class PomodoroTimer:
    def __init__(self, focus_minutes: int = 25, break_minutes: int = 5) -> None:
        self._durations = {
            TimerMode.FOCUS: focus_minutes * 60,
            TimerMode.BREAK: break_minutes * 60,
        }
        self._mode = TimerMode.FOCUS
        self._state = TimerState.IDLE
        self._remaining_seconds = self._durations[self._mode]
        self._started_at: float | None = None

    @property
    def mode(self) -> TimerMode:
        return self._mode

    @property
    def state(self) -> TimerState:
        return self._state

    def configure(self, focus_minutes: int, break_minutes: int) -> None:
        self._durations = {
            TimerMode.FOCUS: focus_minutes * 60,
            TimerMode.BREAK: break_minutes * 60,
        }
        if self._state in {TimerState.IDLE, TimerState.FINISHED}:
            self._remaining_seconds = self._durations[self._mode]

    def set_mode(self, mode: TimerMode) -> None:
        self._mode = mode
        self._state = TimerState.IDLE
        self._started_at = None
        self._remaining_seconds = self._durations[mode]

    def toggle_mode(self) -> None:
        self.set_mode(TimerMode.BREAK if self._mode == TimerMode.FOCUS else TimerMode.FOCUS)

    def start(self) -> None:
        if self._state == TimerState.RUNNING:
            return
        if self._state == TimerState.FINISHED:
            self.reset()
        self._started_at = monotonic()
        self._state = TimerState.RUNNING

    def pause(self) -> None:
        if self._state != TimerState.RUNNING:
            return
        self._remaining_seconds = self.remaining_seconds()
        self._started_at = None
        self._state = TimerState.PAUSED

    def reset(self) -> None:
        self._started_at = None
        self._remaining_seconds = self._durations[self._mode]
        self._state = TimerState.IDLE

    def remaining_seconds(self) -> int:
        if self._state != TimerState.RUNNING or self._started_at is None:
            return max(0, self._remaining_seconds)
        elapsed = int(monotonic() - self._started_at)
        return max(0, self._remaining_seconds - elapsed)

    def tick(self) -> TimerSnapshot:
        remaining = self.remaining_seconds()
        if self._state == TimerState.RUNNING and remaining <= 0:
            self._remaining_seconds = 0
            self._started_at = None
            self._state = TimerState.FINISHED
        return self.snapshot()

    def snapshot(self) -> TimerSnapshot:
        return TimerSnapshot(
            mode=self._mode,
            state=self._state,
            duration_seconds=self._durations[self._mode],
            remaining_seconds=self.remaining_seconds(),
        )


def format_seconds(seconds: int) -> str:
    minutes, rest = divmod(max(0, seconds), 60)
    return f"{minutes:02d}:{rest:02d}"
