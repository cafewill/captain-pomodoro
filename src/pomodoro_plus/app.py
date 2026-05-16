from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from pomodoro_plus.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("포모도로+")
    app.setApplicationName("PomodoroPlus")
    window = MainWindow()
    window.show()
    return app.exec()
