from cube_config import CUBE_COLORS, GRID_SIZE, SOLVED_FACE_COLORS
from cube_geometry import (
    CUBIES,
    facelet_from_position,
    iter_facelet_positions,
    rotate_vector,
)
from cube_moves import is_clockwise, move_definition, move_turn_count
from cube_types import Cubie, FaceGrid, Vector


class RubiksCube:
    """Editable 3x3 cube state with quarter-turn move support."""

    def __init__(self) -> None:
        self.cubies = CUBIES
        self.reset()

    def reset(self) -> None:
        self.faces = {
            face: self._filled_face(color)
            for face, color in SOLVED_FACE_COLORS.items()
        }

    def set_sticker(self, face: str, row: int, col: int, color_name: str) -> None:
        self._validate_sticker(face, row, col, color_name)
        self.faces[face][row][col] = color_name

    def get_sticker(self, face: str, row: int, col: int) -> str:
        return self.faces[face][row][col]

    def apply_move(self, move: str) -> None:
        for _ in range(move_turn_count(move)):
            self._apply_quarter_turn(move)

    def stickers_for(self, cubie: Cubie) -> dict[str, tuple[float, float, float]]:
        stickers = {}

        if cubie.y == 1:
            stickers["top"] = self._sticker_color("top", cubie.z + 1, cubie.x + 1)
        if cubie.y == -1:
            stickers["bottom"] = self._sticker_color("bottom", cubie.z + 1, 1 - cubie.x)
        if cubie.x == -1:
            stickers["left"] = self._sticker_color("left", 1 - cubie.y, cubie.z + 1)
        if cubie.x == 1:
            stickers["right"] = self._sticker_color("right", 1 - cubie.y, 1 - cubie.z)
        if cubie.z == 1:
            stickers["front"] = self._sticker_color("front", 1 - cubie.y, cubie.x + 1)
        if cubie.z == -1:
            stickers["back"] = self._sticker_color("back", 1 - cubie.y, 1 - cubie.x)

        return stickers

    def _apply_quarter_turn(self, move: str) -> None:
        definition = move_definition(move)
        angle = definition.angle if is_clockwise(move) else -definition.angle
        rotated: dict[tuple[Vector, Vector], str] = {}

        for face, row, col, position, normal in iter_facelet_positions():
            if position[definition.axis] == definition.layer:
                position = rotate_vector(position, definition.axis, angle)
                normal = rotate_vector(normal, definition.axis, angle)
            rotated[(position, normal)] = self.faces[face][row][col]

        self.faces = self._empty_faces()
        for (position, normal), color_name in rotated.items():
            face, row, col = facelet_from_position(position, normal)
            self.faces[face][row][col] = color_name

    def _sticker_color(self, face: str, row: int, col: int) -> tuple[float, float, float]:
        return CUBE_COLORS[self.faces[face][row][col]]

    def _filled_face(self, color_name: str) -> FaceGrid:
        return [[color_name for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def _empty_faces(self) -> dict[str, FaceGrid]:
        return {
            face: self._filled_face("white")
            for face in self.faces
        }

    def _validate_sticker(self, face: str, row: int, col: int, color_name: str) -> None:
        if face not in self.faces:
            raise ValueError(f"Unknown face: {face}")
        if color_name not in CUBE_COLORS:
            raise ValueError(f"Unknown color: {color_name}")
        if row not in range(GRID_SIZE) or col not in range(GRID_SIZE):
            raise ValueError(
                f"Sticker coordinates must be between 0 and {GRID_SIZE - 1}"
            )
