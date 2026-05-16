from __future__ import annotations

import subprocess
import sys

from PySide6.QtCore import QSize, QTimer, Qt
from PySide6.QtGui import QFont, QIcon, QMovie, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from pomodoro_plus.assets import app_icon_path, random_animation_path, random_slot
from pomodoro_plus.settings import AppSettings, load_settings, save_settings
from pomodoro_plus.stats import record_completion, today_stats
from pomodoro_plus.timer import PomodoroTimer, TimerMode, TimerState, format_seconds
from pomodoro_plus.ui.settings_dialog import SettingsDialog


NORMAL_SIZE = (260, 340)
COMPACT_SIZE = (440, 56)


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.settings = load_settings()
        self.timer = PomodoroTimer(self.settings.focus_minutes, self.settings.break_minutes)
        self.animation_slot = random_slot(self.timer.mode)
        self.animation_path = random_animation_path(self.timer.mode)
        self.animation_movie: QMovie | None = None
        self._drag_offset = None
        self._compact_mode = False
        self._normal_geometry = None

        self.tick_timer = QTimer(self)
        self.tick_timer.setInterval(250)
        self.tick_timer.timeout.connect(self._on_tick)

        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(600)
        self.animation_timer.timeout.connect(self._animate_icon)
        self.animation_phase = 0

        self._build_ui()
        self._build_tray()
        self._apply_window_flags()
        self._render()
        self._move_to_bottom_right()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setWindowTitle("포모도로+")
        self.setObjectName("root")
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(*NORMAL_SIZE)

        self.title_label = QLabel("포모도로+")
        self.title_label.setObjectName("title")

        self.minimize_button = QPushButton("−")
        self.minimize_button.setObjectName("iconButton")
        self.minimize_button.setFixedSize(26, 26)
        self.minimize_button.clicked.connect(self._toggle_compact_mode)

        self.stats_button = QPushButton("📊")
        self.stats_button.setObjectName("iconButton")
        self.stats_button.setFixedSize(26, 26)
        self.stats_button.setToolTip("오늘 통계")
        self.stats_button.clicked.connect(self._show_stats)

        self.settings_button = QPushButton("⚙")
        self.settings_button.setObjectName("iconButton")
        self.settings_button.setFixedSize(26, 26)
        self.settings_button.clicked.connect(self._open_settings)

        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("iconButton")
        self.close_button.setFixedSize(26, 26)
        self.close_button.setToolTip("트레이로 최소화")
        self.close_button.clicked.connect(self._hide_to_tray)

        header = QHBoxLayout()
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.minimize_button)
        header.addWidget(self.stats_button)
        header.addWidget(self.settings_button)
        header.addWidget(self.close_button)

        self.icon_label = QLabel()
        self.icon_label.setObjectName("emoji")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setScaledContents(False)

        self.animation_label = QLabel()
        self.animation_label.setObjectName("animationLabel")
        self.animation_label.setAlignment(Qt.AlignCenter)

        self.mode_label = QLabel()
        self.mode_label.setObjectName("modeLabel")
        self.mode_label.setAlignment(Qt.AlignCenter)

        self.time_label = QLabel()
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Arial", 42, QFont.Bold))

        self.start_button = QPushButton("시작")
        self.start_button.clicked.connect(self._start)
        self.pause_button = QPushButton("중단")
        self.pause_button.clicked.connect(self._pause)
        self.reset_button = QPushButton("재시작")
        self.reset_button.clicked.connect(self._reset)

        controls = QHBoxLayout()
        controls.addWidget(self.start_button)
        controls.addWidget(self.pause_button)
        controls.addWidget(self.reset_button)

        self.switch_button = QPushButton("휴식으로 전환")
        self.switch_button.clicked.connect(self._switch_mode)

        self.stats_label = QLabel()
        self.stats_label.setObjectName("statsLabel")
        self.stats_label.setAlignment(Qt.AlignCenter)

        self.panel = QFrame()
        self.panel.setObjectName("panel")
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(14, 12, 14, 14)
        panel_layout.setSpacing(8)
        panel_layout.addLayout(header)
        panel_layout.addSpacing(4)
        panel_layout.addWidget(self.icon_label)
        panel_layout.addWidget(self.animation_label)
        panel_layout.addWidget(self.mode_label)
        panel_layout.addWidget(self.time_label)
        panel_layout.addSpacing(12)
        panel_layout.addLayout(controls)
        panel_layout.addWidget(self.switch_button)
        panel_layout.addWidget(self.stats_label)

        # Compact (1-line) panel
        self.compact_panel = QFrame()
        self.compact_panel.setObjectName("compactPanel")
        self.compact_panel.setVisible(False)

        self.compact_name_label = QLabel()
        self.compact_name_label.setObjectName("compactName")
        self.compact_name_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.compact_time_label = QLabel()
        self.compact_time_label.setObjectName("compactTime")
        self.compact_time_label.setAlignment(Qt.AlignCenter)

        self.restore_button = QPushButton("□")
        self.restore_button.setObjectName("compactIconButton")
        self.restore_button.setFixedSize(18, 18)
        self.restore_button.clicked.connect(self._exit_compact_mode)

        compact_layout = QHBoxLayout(self.compact_panel)
        compact_layout.setContentsMargins(18, 8, 18, 8)
        compact_layout.setSpacing(14)
        compact_layout.setAlignment(Qt.AlignVCenter)
        compact_layout.addWidget(self.compact_name_label, 1, Qt.AlignVCenter)
        compact_layout.addWidget(self.compact_time_label, 0, Qt.AlignVCenter)
        compact_layout.addWidget(self.restore_button, 0, Qt.AlignVCenter)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.addWidget(self.panel)
        root.addWidget(self.compact_panel)

        self._apply_style()

    def _build_tray(self) -> None:
        icon = QIcon(str(app_icon_path()))
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("포모도로+")

        menu = QMenu()
        self._tray_show_action = menu.addAction("창 보기")
        self._tray_show_action.triggered.connect(self._show_from_tray)
        menu.addSeparator()
        self._tray_start_action = menu.addAction("시작")
        self._tray_start_action.triggered.connect(self._start)
        self._tray_pause_action = menu.addAction("중단")
        self._tray_pause_action.triggered.connect(self._pause)
        menu.addAction("재시작").triggered.connect(self._reset)
        menu.addSeparator()
        menu.addAction("오늘 통계").triggered.connect(self._show_stats)
        menu.addSeparator()
        menu.addAction("종료").triggered.connect(self._quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    # ------------------------------------------------------------------
    # Stylesheet
    # ------------------------------------------------------------------

    def _apply_style(self) -> None:
        panel_bg     = "rgba(255, 250, 242, 0.92)" if not self._compact_mode else "rgba(39, 34, 29, 0.76)"
        panel_border = "#e1caa1"                   if not self._compact_mode else "rgba(255, 255, 255, 0.20)"
        title_color  = "#3d3428"
        text_color   = "#2e2822"
        sub_color    = "#6a5940"
        self.setStyleSheet(f"""
            QWidget#root {{
                background: transparent;
            }}
            QFrame#panel {{
                background: {panel_bg};
                border: 1px solid {panel_border};
                border-radius: 8px;
            }}
            QFrame#compactPanel {{
                background: rgba(39, 34, 29, 0.78);
                border: 1px solid rgba(255, 255, 255, 0.22);
                border-radius: 8px;
            }}
            QLabel#title {{
                color: {title_color};
                font-size: 15px;
                font-weight: 700;
                min-height: 28px;
            }}
            QLabel#emoji {{
                font-size: 58px;
                min-height: 72px;
            }}
            QLabel#animationLabel {{
                color: {sub_color};
                font-size: 14px;
                min-height: 20px;
            }}
            QLabel#modeLabel {{
                color: {sub_color};
                font-size: 17px;
                font-weight: 700;
            }}
            QLabel#timeLabel {{
                color: {text_color};
                min-height: 52px;
            }}
            QLabel#statsLabel {{
                color: {sub_color};
                font-size: 11px;
                min-height: 16px;
            }}
            QLabel#compactName {{
                color: #fff8ea;
                font-size: 16px;
                font-weight: 700;
                min-height: 34px;
            }}
            QLabel#compactTime {{
                color: #fff8ea;
                font-size: 28px;
                font-weight: 800;
                min-width: 112px;
                min-height: 34px;
            }}
            QPushButton {{
                background: #ffffff;
                color: #332b22;
                border: 1px solid #d7bd8d;
                border-radius: 6px;
                min-height: 30px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background: #f7ecd9;
            }}
            QPushButton#iconButton {{
                min-height: 24px;
                min-width: 24px;
                padding: 0;
                font-size: 13px;
            }}
            QPushButton#compactIconButton {{
                background: rgba(255,255,255,0.85);
                color: #43372d;
                border: 1px solid #d7bd8d;
                border-radius: 5px;
                padding: 0;
                font-size: 12px;
                min-width: 18px;
                min-height: 18px;
            }}
        """)

    # ------------------------------------------------------------------
    # Window flags & position
    # ------------------------------------------------------------------

    def _apply_window_flags(self) -> None:
        flags = Qt.Tool | Qt.FramelessWindowHint
        if self.settings.always_on_top or self._compact_mode:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

    def _move_to_bottom_right(self) -> None:
        screen = self.screen()
        if screen is None:
            return
        area = screen.availableGeometry()
        self.move(area.right() - self.width() - 18, area.bottom() - self.height() - 18)

    def _move_to_top_center(self) -> None:
        screen = self.screen()
        if screen is None:
            return
        area = screen.availableGeometry()
        x = area.left() + (area.width() - self.width()) // 2
        self.move(x, area.top() + 12)

    # ------------------------------------------------------------------
    # Compact mode
    # ------------------------------------------------------------------

    def _toggle_compact_mode(self) -> None:
        if self._compact_mode:
            self._exit_compact_mode()
        else:
            self._enter_compact_mode()

    def _enter_compact_mode(self) -> None:
        self._normal_geometry = self.geometry()
        self._compact_mode = True
        self._apply_window_flags()
        self._apply_compact_visibility()
        self.setFixedSize(*COMPACT_SIZE)
        self.setWindowOpacity(0.86)
        self._apply_style()
        self._render()
        self.show()
        self._move_to_top_center()

    def _exit_compact_mode(self) -> None:
        self._compact_mode = False
        self._apply_window_flags()
        self._apply_compact_visibility()
        self.setFixedSize(*NORMAL_SIZE)
        self.time_label.setFont(QFont("Arial", 42, QFont.Bold))
        self.setWindowOpacity(1.0)
        self._apply_style()
        self._render()
        self.show()
        if self._normal_geometry is not None:
            self.setGeometry(self._normal_geometry)
        else:
            self._move_to_bottom_right()

    def _apply_compact_visibility(self) -> None:
        self.panel.setVisible(not self._compact_mode)
        self.compact_panel.setVisible(self._compact_mode)

    # ------------------------------------------------------------------
    # Tray
    # ------------------------------------------------------------------

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_from_tray()

    def _show_from_tray(self) -> None:
        if self._compact_mode:
            self._exit_compact_mode()
        self.show()
        self.raise_()
        self.activateWindow()

    def _hide_to_tray(self) -> None:
        self.hide()
        if self.tray.isVisible():
            self.tray.showMessage(
                "포모도로+",
                "트레이에서 계속 실행됩니다. 아이콘을 더블클릭하면 창이 열려.",
                QSystemTrayIcon.Information,
                2000,
            )

    def _quit(self) -> None:
        self.tray.hide()
        QApplication.quit()

    # ------------------------------------------------------------------
    # Timer controls
    # ------------------------------------------------------------------

    def _start(self) -> None:
        if self.timer.state in {TimerState.IDLE, TimerState.FINISHED}:
            self._select_random_animation()
        self.timer.start()
        self.tick_timer.start()
        self.animation_timer.start()
        self._render()

    def _pause(self) -> None:
        self.timer.pause()
        self.tick_timer.stop()
        self.animation_timer.stop()
        self._render()

    def _reset(self) -> None:
        self.timer.reset()
        self.tick_timer.stop()
        self.animation_timer.stop()
        self.animation_phase = 0
        self._select_random_animation()
        self._render()

    def _switch_mode(self) -> None:
        self.timer.toggle_mode()
        self.tick_timer.stop()
        self.animation_timer.stop()
        self.animation_phase = 0
        self._select_random_animation()
        self._render()

    def _select_random_animation(self) -> None:
        self.animation_slot = random_slot(self.timer.mode)
        self.animation_path = random_animation_path(self.timer.mode)
        self._stop_animation_movie()

    def _stop_animation_movie(self) -> None:
        if self.animation_movie is not None:
            self.animation_movie.stop()
            self.animation_movie.deleteLater()
            self.animation_movie = None

    # ------------------------------------------------------------------
    # Timer completion
    # ------------------------------------------------------------------

    def _on_tick(self) -> None:
        before = self.timer.state
        snapshot = self.timer.tick()
        if before == TimerState.RUNNING and snapshot.state == TimerState.FINISHED:
            self.tick_timer.stop()
            self.animation_timer.stop()
            self._on_timer_complete(snapshot.mode)
        self._render()

    def _on_timer_complete(self, mode: TimerMode) -> None:
        minutes = self.settings.focus_minutes if mode == TimerMode.FOCUS else self.settings.break_minutes
        record_completion(mode.value, minutes)
        self._notify_done(mode)
        if self.settings.notification_sound:
            _play_sound()
        if self.settings.auto_cycle:
            self.timer.toggle_mode()
            self._select_random_animation()
            self.timer.start()
            self.tick_timer.start()
            self.animation_timer.start()
        else:
            from PySide6.QtWidgets import QMessageBox
            mode_name = self.settings.focus_label if mode == TimerMode.FOCUS else self.settings.break_label
            QMessageBox.information(self, "포모도로+", f"'{mode_name}' 타이머가 끝났어!")

    def _notify_done(self, mode: TimerMode) -> None:
        mode_name = self.settings.focus_label if mode == TimerMode.FOCUS else self.settings.break_label
        next_name = self.settings.break_label if mode == TimerMode.FOCUS else self.settings.focus_label
        if self.settings.auto_cycle:
            body = f"'{mode_name}' 완료! 이제 '{next_name}' 시간이야."
        else:
            body = f"'{mode_name}' 완료!"
        if self.tray.isVisible():
            self.tray.showMessage("포모도로+", body, QSystemTrayIcon.Information, 4000)

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() != SettingsDialog.Accepted:
            return
        self.settings = dialog.settings()
        save_settings(self.settings)
        self.timer.configure(self.settings.focus_minutes, self.settings.break_minutes)
        was_visible = self.isVisible()
        self._apply_window_flags()
        if was_visible:
            self.show()
        self._render()

    # ------------------------------------------------------------------
    # Stats dialog
    # ------------------------------------------------------------------

    def _show_stats(self) -> None:
        s = today_stats()
        dialog = QDialog(self)
        dialog.setWindowTitle("오늘 통계")
        dialog.setModal(True)
        dialog.setMinimumWidth(240)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<b>📊 오늘 집중 현황</b>"))
        for label, value in [
            ("집중 횟수", f"{s['focus_count']}회"),
            ("집중 시간", f"{s['focus_minutes']}분"),
            ("휴식 횟수", f"{s['break_count']}회"),
            ("휴식 시간", f"{s['break_minutes']}분"),
            ("총 기록 시간", f"{s['focus_minutes'] + s['break_minutes']}분"),
        ]:
            row = QLabel(f"<b>{label}</b>  {value}")
            row.setAlignment(Qt.AlignLeft)
            layout.addWidget(row)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def _animate_icon(self) -> None:
        self.animation_phase = (self.animation_phase + 1) % 3
        self._render()

    def _render(self) -> None:
        snapshot = self.timer.snapshot()
        mode_name = self.settings.focus_label if snapshot.mode == TimerMode.FOCUS else self.settings.break_label
        suffix = "." * self.animation_phase if snapshot.state == TimerState.RUNNING else ""

        compact_name = self.compact_name_label.fontMetrics().elidedText(
            mode_name, Qt.ElideRight, COMPACT_SIZE[0] - 210
        )
        self.compact_name_label.setText(compact_name)
        self.compact_name_label.setToolTip(mode_name)
        self.compact_time_label.setText(format_seconds(snapshot.remaining_seconds))

        self.title_label.setText("포모도로+")
        self._render_animation_media(snapshot.state)
        self.animation_label.setText(f"{self.animation_slot.label}{suffix}")
        self.mode_label.setText(mode_name)
        self.time_label.setText(format_seconds(snapshot.remaining_seconds))

        self.start_button.setEnabled(snapshot.state != TimerState.RUNNING)
        self.pause_button.setEnabled(snapshot.state == TimerState.RUNNING)
        self.reset_button.setEnabled(snapshot.state != TimerState.IDLE)
        self.switch_button.setText("휴식으로 전환" if snapshot.mode == TimerMode.FOCUS else "집중으로 전환")

        s = today_stats()
        self.stats_label.setText(
            f"오늘 집중 {s['focus_count']}회 · {s['focus_minutes']}분" if s["focus_count"] else ""
        )

        self._tray_start_action.setEnabled(snapshot.state != TimerState.RUNNING)
        self._tray_pause_action.setEnabled(snapshot.state == TimerState.RUNNING)
        state_text = {"idle": "대기", "running": "실행 중", "paused": "일시정지", "finished": "완료"}.get(
            snapshot.state.value, ""
        )
        self.tray.setToolTip(f"포모도로+ · {mode_name} {format_seconds(snapshot.remaining_seconds)} ({state_text})")

    def _render_animation_media(self, state: TimerState) -> None:
        if self._compact_mode:
            return
        if self.animation_path is None:
            self._stop_animation_movie()
            self.icon_label.setPixmap(QPixmap())
            self.icon_label.setText(self.animation_slot.icon)
            return

        self.icon_label.setText("")
        suffix = self.animation_path.suffix.lower()
        if suffix == ".gif":
            if self.animation_movie is None or self.animation_movie.fileName() != str(self.animation_path):
                self._stop_animation_movie()
                self.animation_movie = QMovie(str(self.animation_path))
                self.animation_movie.setScaledSize(QSize(72, 72))
                self.icon_label.setMovie(self.animation_movie)
            if state == TimerState.RUNNING:
                self.animation_movie.start()
            else:
                self.animation_movie.jumpToFrame(0)
                self.animation_movie.stop()
            return

        self._stop_animation_movie()
        pixmap = QPixmap(str(self.animation_path))
        if pixmap.isNull():
            self.icon_label.setText(self.animation_slot.icon)
            return
        self.icon_label.setPixmap(pixmap.scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    # ------------------------------------------------------------------
    # Drag
    # ------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self._drag_offset = None
        event.accept()

    def mouseDoubleClickEvent(self, event) -> None:
        if self._compact_mode and event.button() == Qt.LeftButton:
            self._exit_compact_mode()
            event.accept()

    # ------------------------------------------------------------------
    # Close → hide to tray
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        if self.tray.isVisible():
            event.ignore()
            self._hide_to_tray()
        else:
            event.accept()


# ------------------------------------------------------------------
# Platform sound helper
# ------------------------------------------------------------------

def _play_sound() -> None:
    try:
        if sys.platform == "darwin":
            subprocess.Popen(
                ["afplay", "-t", "1", "/System/Library/Sounds/Glass.aiff"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif sys.platform.startswith("linux"):
            subprocess.Popen(
                ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            import winsound  # type: ignore[import]
            winsound.MessageBeep(winsound.MB_OK)
    except Exception:
        QApplication.beep()
