from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)

from pomodoro_plus.settings import (
    BREAK_MAX_MINUTES,
    BREAK_MIN_MINUTES,
    FOCUS_MAX_MINUTES,
    FOCUS_MIN_MINUTES,
    AppSettings,
)


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("설정")
        self.setModal(True)
        self.setMinimumWidth(320)

        self.always_on_top = QCheckBox("항상 화면 위에 표시")
        self.always_on_top.setChecked(settings.always_on_top)

        self.auto_cycle = QCheckBox("집중/휴식 자동 전환 (사이클)")
        self.auto_cycle.setChecked(settings.auto_cycle)
        self.auto_cycle.setToolTip("타이머가 끝나면 자동으로 다음 모드를 시작합니다.")

        self.notification_sound = QCheckBox("타이머 종료 알림음")
        self.notification_sound.setChecked(settings.notification_sound)

        self.focus_label = QLineEdit(settings.focus_label)
        self.focus_label.setMaxLength(20)
        self.focus_minutes = QSpinBox()
        self.focus_minutes.setRange(FOCUS_MIN_MINUTES, FOCUS_MAX_MINUTES)
        self.focus_minutes.setSuffix(" 분")
        self.focus_minutes.setValue(settings.focus_minutes)

        self.break_label = QLineEdit(settings.break_label)
        self.break_label.setMaxLength(20)
        self.break_minutes = QSpinBox()
        self.break_minutes.setRange(BREAK_MIN_MINUTES, BREAK_MAX_MINUTES)
        self.break_minutes.setSuffix(" 분")
        self.break_minutes.setValue(settings.break_minutes)

        focus_group = QGroupBox("집중 시간")
        focus_form = QFormLayout(focus_group)
        focus_form.addRow("명칭", self.focus_label)
        focus_form.addRow("시간", self.focus_minutes)

        break_group = QGroupBox("유휴 시간")
        break_form = QFormLayout(break_group)
        break_form.addRow("명칭", self.break_label)
        break_form.addRow("시간", self.break_minutes)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.always_on_top)
        layout.addWidget(self.auto_cycle)
        layout.addWidget(self.notification_sound)
        layout.addWidget(focus_group)
        layout.addWidget(break_group)
        layout.addWidget(buttons)
        layout.setAlignment(Qt.AlignTop)

    def settings(self) -> AppSettings:
        return AppSettings(
            focus_label=self.focus_label.text().strip() or "업무",
            focus_minutes=self.focus_minutes.value(),
            break_label=self.break_label.text().strip() or "휴식",
            break_minutes=self.break_minutes.value(),
            always_on_top=self.always_on_top.isChecked(),
            auto_cycle=self.auto_cycle.isChecked(),
            notification_sound=self.notification_sound.isChecked(),
        )
