from __future__ import annotations

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cube import RubiksCube
from solver import CubeValidationError, describe_move, inverse_move, solve_cube


READY_MESSAGE = "Enter cube colors, then solve."


class SolvePanel(QWidget):
    move_requested = pyqtSignal(str)

    def __init__(self, cube: RubiksCube, parent=None) -> None:
        super().__init__(parent)
        self.cube = cube
        self.solution: list[str] = []
        self.current_index = 0
        self.is_animating = False
        self.auto_playing = False
        self.pending_direction = "forward"
        self.auto_timer = QTimer(self)
        self.auto_timer.setInterval(250)
        self.auto_timer.timeout.connect(self.play_next_move)

        self._build_ui()
        self._sync_buttons()

    def clear_solution(self) -> None:
        self._reset_solution_state(READY_MESSAGE)

    def solve(self) -> None:
        if self.is_animating:
            return

        try:
            self.solution = solve_cube(self.cube)
        except CubeValidationError as error:
            self._reset_solution_state(str(error))
            return
        except Exception as error:
            self._reset_solution_state(f"Solver rejected this cube: {error}")
            return

        self.current_index = 0
        self._render_solution()

        if self.solution:
            self.status_label.setText(f"Solution found: {len(self.solution)} moves.")
            self._show_current_guide()
        else:
            self.status_label.setText("This cube is already solved.")
            self.guide_label.setText("")

        self._sync_buttons()

    def play_next_move(self) -> None:
        if self.is_animating or self.current_index >= len(self.solution):
            self._finish_auto_play_if_needed()
            return

        move = self.solution[self.current_index]
        self.is_animating = True
        self.pending_direction = "forward"
        self._sync_buttons()
        self.move_requested.emit(move)

    def play_previous_move(self) -> None:
        if self.is_animating or self.current_index <= 0:
            return

        self.auto_playing = False
        self.auto_timer.stop()
        self.current_index -= 1
        move = inverse_move(self.solution[self.current_index])
        self.is_animating = True
        self.pending_direction = "back"
        self._show_current_guide()
        self._sync_buttons()
        self.move_requested.emit(move)

    def toggle_auto_play(self) -> None:
        if self.auto_playing:
            self.auto_playing = False
            self.auto_timer.stop()
        else:
            self.auto_playing = True
            self.play_next_move()
            self.auto_timer.start()
        self._sync_buttons()

    def on_move_finished(self, move: str) -> None:
        if (
            self.pending_direction == "forward"
            and self.current_index < len(self.solution)
            and self.solution[self.current_index] == move
        ):
            self.current_index += 1

        self.is_animating = False
        self._show_current_guide()
        self._sync_buttons()
        self._finish_auto_play_if_needed()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        title = QLabel("Solver")
        title.setObjectName("panelTitle")
        root.addWidget(title)

        self.status_label = QLabel(READY_MESSAGE)
        self.status_label.setWordWrap(True)
        root.addWidget(self.status_label)

        self.guide_label = QLabel("")
        self.guide_label.setWordWrap(True)
        self.guide_label.setMinimumHeight(44)
        root.addWidget(self.guide_label)

        buttons = QHBoxLayout()
        self.solve_button = QPushButton("Solve")
        self.back_button = QPushButton("Back")
        self.next_button = QPushButton("Next Move")
        self.auto_button = QPushButton("Auto Play")
        self.solve_button.clicked.connect(self.solve)
        self.back_button.clicked.connect(self.play_previous_move)
        self.next_button.clicked.connect(self.play_next_move)
        self.auto_button.clicked.connect(self.toggle_auto_play)
        buttons.addWidget(self.solve_button)
        buttons.addWidget(self.back_button)
        buttons.addWidget(self.next_button)
        buttons.addWidget(self.auto_button)
        root.addLayout(buttons)

        self.solution_list = QListWidget()
        root.addWidget(self.solution_list, stretch=1)

        self.setStyleSheet(
            """
            #panelTitle {
                font-size: 20px;
                font-weight: 700;
            }
            QPushButton {
                min-height: 30px;
            }
            """
        )

    def _reset_solution_state(self, status: str) -> None:
        self.solution = []
        self.current_index = 0
        self.auto_playing = False
        self.auto_timer.stop()
        self.solution_list.clear()
        self.status_label.setText(status)
        self.guide_label.setText("")
        self._sync_buttons()

    def _render_solution(self) -> None:
        self.solution_list.clear()
        for index, move in enumerate(self.solution, start=1):
            item = QListWidgetItem(f"{index}. {move} - {describe_move(move)}")
            self.solution_list.addItem(item)

    def _show_current_guide(self) -> None:
        for row in range(self.solution_list.count()):
            item = self.solution_list.item(row)
            item.setSelected(row == self.current_index)

        if self.current_index < len(self.solution):
            move = self.solution[self.current_index]
            self.solution_list.setCurrentRow(self.current_index)
            self.guide_label.setText(
                f"Step {self.current_index + 1}: {move}. {describe_move(move)}"
            )
        elif self.solution:
            self.status_label.setText("Solved. All listed moves have been applied.")
            self.guide_label.setText("")

    def _finish_auto_play_if_needed(self) -> None:
        if self.current_index >= len(self.solution):
            self.auto_playing = False
            self.auto_timer.stop()
            self._sync_buttons()

    def _sync_buttons(self) -> None:
        has_pending_moves = self.current_index < len(self.solution)
        has_previous_moves = self.current_index > 0
        self.solve_button.setEnabled(not self.is_animating)
        self.back_button.setEnabled(has_previous_moves and not self.is_animating)
        self.next_button.setEnabled(has_pending_moves and not self.is_animating)
        self.auto_button.setEnabled(has_pending_moves or self.auto_playing)
        self.auto_button.setText("Pause" if self.auto_playing else "Auto Play")
