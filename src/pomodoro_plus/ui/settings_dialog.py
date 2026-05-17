from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
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
        self.notification_sound.toggled.connect(self._sync_sound_controls)

        self.notification_sound_path = QLineEdit(settings.notification_sound_path)
        self.notification_sound_path.setPlaceholderText("기본 알림음 사용")
        self.notification_sound_path.setReadOnly(True)

        self.sound_browse_button = QPushButton("선택")
        self.sound_browse_button.clicked.connect(self._choose_sound_file)
        self.sound_clear_button = QPushButton("기본값")
        self.sound_clear_button.clicked.connect(self.notification_sound_path.clear)

        sound_row = QWidget()
        sound_layout = QHBoxLayout(sound_row)
        sound_layout.setContentsMargins(0, 0, 0, 0)
        sound_layout.addWidget(self.notification_sound_path, 1)
        sound_layout.addWidget(self.sound_browse_button)
        sound_layout.addWidget(self.sound_clear_button)

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

        sound_group = QGroupBox("알림음")
        sound_form = QFormLayout(sound_group)
        sound_form.addRow(self.notification_sound)
        sound_form.addRow("파일", sound_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.always_on_top)
        layout.addWidget(self.auto_cycle)
        layout.addWidget(focus_group)
        layout.addWidget(break_group)
        layout.addWidget(sound_group)
        layout.addWidget(buttons)
        layout.setAlignment(Qt.AlignTop)
        self._sync_sound_controls(self.notification_sound.isChecked())

    def _choose_sound_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "알림음 선택",
            "",
            "Sound Files (*.wav *.mp3 *.m4a *.aiff *.aif *.ogg *.oga);;All Files (*)",
        )
        if path:
            self.notification_sound_path.setText(path)

    def _sync_sound_controls(self, enabled: bool) -> None:
        self.notification_sound_path.setEnabled(enabled)
        self.sound_browse_button.setEnabled(enabled)
        self.sound_clear_button.setEnabled(enabled)

    def settings(self) -> AppSettings:
        return AppSettings(
            focus_label=self.focus_label.text().strip() or "업무",
            focus_minutes=self.focus_minutes.value(),
            break_label=self.break_label.text().strip() or "휴식",
            break_minutes=self.break_minutes.value(),
            always_on_top=self.always_on_top.isChecked(),
            auto_cycle=self.auto_cycle.isChecked(),
            notification_sound=self.notification_sound.isChecked(),
            notification_sound_path=self.notification_sound_path.text().strip(),
        )
