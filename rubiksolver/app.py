import sys

from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtWidgets import QApplication

from rubiksolver.ui.main_window import MainWindow


def main() -> int:
    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    fmt.setVersion(2, 1)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()

