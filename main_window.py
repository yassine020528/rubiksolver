from PyQt6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from face_editor import FaceEditor
from gl_widget import RubiksGLWidget
from solve_panel import SolvePanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Rubik Solver")
        self.resize(1120, 720)

        self.gl_widget = RubiksGLWidget(self)
        self.face_editor = FaceEditor(self.gl_widget.cube, self)
        self.solve_panel = SolvePanel(self.gl_widget.cube, self)
        self.face_editor.cube_changed.connect(self.solve_panel.clear_solution)
        self.face_editor.cube_changed.connect(self.gl_widget.update)
        self.solve_panel.move_requested.connect(self.gl_widget.animate_move)
        self.gl_widget.move_finished.connect(self.solve_panel.on_move_finished)
        self.gl_widget.move_finished.connect(lambda _move: self.face_editor.refresh())

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        side_panel = QWidget()
        side_panel.setFixedWidth(360)
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(0)
        side_layout.addWidget(self.face_editor)
        side_layout.addWidget(self.solve_panel, stretch=1)

        layout.addWidget(self.gl_widget, stretch=1)
        layout.addWidget(side_panel)

        self.setCentralWidget(central)
