from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

from pomodoro_plus.timer import TimerMode


@dataclass(frozen=True)
class AnimationSlot:
    icon: str
    label: str


FOCUS_SLOTS = [
    AnimationSlot("📚", "공부 중"),
    AnimationSlot("💻", "열일 중"),
    AnimationSlot("⛏️", "삽질 중"),
    AnimationSlot("✍️", "문서 작성"),
    AnimationSlot("🧠", "생각 정리"),
    AnimationSlot("🧑‍💻", "코딩 중"),
    AnimationSlot("📊", "분석 중"),
    AnimationSlot("🔍", "집중 탐색"),
    AnimationSlot("🛠️", "문제 해결"),
    AnimationSlot("📝", "메모 정리"),
    AnimationSlot("🎯", "목표 집중"),
    AnimationSlot("🚀", "몰입 가속"),
]

BREAK_SLOTS = [
    AnimationSlot("☕", "커피 한잔"),
    AnimationSlot("🫧", "멍때리기"),
    AnimationSlot("🎧", "노래 듣기"),
    AnimationSlot("🚶", "가벼운 산책"),
    AnimationSlot("🧘", "숨 고르기"),
    AnimationSlot("🥤", "물 마시기"),
    AnimationSlot("🌿", "눈 쉬기"),
    AnimationSlot("🤸", "스트레칭"),
    AnimationSlot("🍪", "간식 타임"),
    AnimationSlot("🛋️", "잠깐 쉬기"),
    AnimationSlot("🌤️", "창밖 보기"),
    AnimationSlot("😌", "기분 전환"),
]

IMAGE_SUFFIXES = {".gif", ".png", ".apng", ".jpg", ".jpeg", ".webp"}


def assets_dir() -> Path:
    return Path(__file__).resolve().parent / "assets"


def app_icon_path() -> Path:
    return assets_dir() / "app.png"


def random_animation_path(mode: TimerMode) -> Path | None:
    directory = assets_dir() / ("focus" if mode == TimerMode.FOCUS else "break")
    if not directory.exists():
        return None
    candidates = [path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES]
    if not candidates:
        return None
    return random.choice(candidates)


def random_slot(mode: TimerMode) -> AnimationSlot:
    return random.choice(FOCUS_SLOTS if mode == TimerMode.FOCUS else BREAK_SLOTS)
