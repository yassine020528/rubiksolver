from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from rubiksolver.domain.config import COLOR_HEX, CUBE_COLORS, FACE_NAMES, GRID_SIZE
from rubiksolver.domain.cube import RubiksCube


class FaceEditor(QWidget):
    cube_changed = pyqtSignal()

    def __init__(self, cube: RubiksCube, parent=None) -> None:
        super().__init__(parent)
        self.cube = cube
        self.current_face = "front"
        self.current_color = "red"
        self.sticker_buttons: list[list[QPushButton]] = []
        self.color_buttons: dict[str, QPushButton] = {}

        self._build_ui()
        self._refresh_grid()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)

        title = QLabel("Cube Colors")
        title.setObjectName("panelTitle")
        root.addWidget(title)

        self.face_select = QComboBox()
        for face, label in FACE_NAMES.items():
            self.face_select.addItem(label, face)
        self.face_select.setCurrentIndex(self.face_select.findData(self.current_face))
        self.face_select.currentIndexChanged.connect(self._change_face)
        root.addWidget(self.face_select)

        grid_frame = QFrame()
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setSpacing(6)

        for row in range(GRID_SIZE):
            button_row: list[QPushButton] = []
            for col in range(GRID_SIZE):
                button = QPushButton()
                button.setFixedSize(64, 64)
                button.clicked.connect(
                    lambda checked=False, r=row, c=col: self._paint_sticker(r, c)
                )
                grid_layout.addWidget(button, row, col)
                button_row.append(button)
            self.sticker_buttons.append(button_row)

        root.addWidget(grid_frame)

        palette_label = QLabel("Palette")
        root.addWidget(palette_label)

        palette = QHBoxLayout()
        palette.setSpacing(8)
        group = QButtonGroup(self)
        group.setExclusive(True)

        for color_name in CUBE_COLORS:
            button = QPushButton()
            button.setCheckable(True)
            button.setFixedSize(34, 34)
            button.setToolTip(color_name.title())
            button.clicked.connect(
                lambda checked=False, name=color_name: self._select_color(name)
            )
            group.addButton(button)
            palette.addWidget(button)
            self.color_buttons[color_name] = button

        self.color_buttons[self.current_color].setChecked(True)
        self._refresh_palette_styles()
        root.addLayout(palette)

        reset_button = QPushButton("Reset Solved")
        reset_button.clicked.connect(self._reset_cube)
        root.addWidget(reset_button)
        root.addStretch()

        self.setStyleSheet(
            """
            #panelTitle {
                font-size: 20px;
                font-weight: 700;
            }
            QComboBox, QPushButton {
                min-height: 30px;
            }
            """
        )

    def _change_face(self) -> None:
        self.current_face = self.face_select.currentData()
        center_color = self.cube.get_sticker(self.current_face, 1, 1)
        self._select_color(center_color)
        self._refresh_grid()

    def _paint_sticker(self, row: int, col: int) -> None:
        self.cube.set_sticker(self.current_face, row, col, self.current_color)
        self._refresh_grid()
        self.cube_changed.emit()

    def _select_color(self, color_name: str) -> None:
        self.current_color = color_name
        self.color_buttons[color_name].setChecked(True)
        self._refresh_palette_styles()

    def _reset_cube(self) -> None:
        self.cube.reset()
        self.refresh()
        self.cube_changed.emit()

    def refresh(self) -> None:
        self._refresh_grid()

    def _refresh_grid(self) -> None:
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                color_name = self.cube.get_sticker(self.current_face, row, col)
                self.sticker_buttons[row][col].setStyleSheet(
                    self._button_style(COLOR_HEX[color_name], border="#20242a")
                )

    def _refresh_palette_styles(self) -> None:
        for color_name, button in self.color_buttons.items():
            border = "#111827" if color_name == self.current_color else "#7a8491"
            width = 3 if color_name == self.current_color else 1
            button.setStyleSheet(
                self._button_style(COLOR_HEX[color_name], border=border, width=width)
            )

    def _button_style(self, color: str, border: str, width: int = 2) -> str:
        return (
            f"background-color: {color};"
            f"border: {width}px solid {border};"
            "border-radius: 4px;"
        )
