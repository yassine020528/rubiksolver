from dataclasses import dataclass


Color = tuple[float, float, float]
FaceGrid = list[list[str]]
Vector = tuple[int, int, int]

FACE_NAMES = {
    "top": "Up",
    "bottom": "Down",
    "left": "Left",
    "right": "Right",
    "front": "Front",
    "back": "Back",
}

CUBE_COLORS: dict[str, Color] = {
    "white": (1.0, 1.0, 1.0),
    "yellow": (1.0, 0.86, 0.05),
    "blue": (0.05, 0.28, 0.95),
    "green": (0.0, 0.62, 0.2),
    "red": (0.88, 0.05, 0.05),
    "orange": (1.0, 0.45, 0.05),
}

COLOR_HEX = {
    "white": "#ffffff",
    "yellow": "#ffd80d",
    "blue": "#0d47f2",
    "green": "#009e33",
    "red": "#e00d0d",
    "orange": "#ff730d",
}


@dataclass(frozen=True)
class Cubie:
    x: int
    y: int
    z: int


class RubiksCube:
    """Simple 3x3x3 cube model for rendering and sticker editing."""

    def __init__(self) -> None:
        self.cubies = [
            Cubie(x, y, z)
            for x in range(-1, 2)
            for y in range(-1, 2)
            for z in range(-1, 2)
        ]
        self.reset()

    def reset(self) -> None:
        self.faces: dict[str, FaceGrid] = {
            "top": self._filled_face("white"),
            "bottom": self._filled_face("yellow"),
            "left": self._filled_face("blue"),
            "right": self._filled_face("green"),
            "front": self._filled_face("red"),
            "back": self._filled_face("orange"),
        }

    def set_sticker(self, face: str, row: int, col: int, color_name: str) -> None:
        if face not in self.faces:
            raise ValueError(f"Unknown face: {face}")
        if color_name not in CUBE_COLORS:
            raise ValueError(f"Unknown color: {color_name}")
        if row not in range(3) or col not in range(3):
            raise ValueError("Sticker coordinates must be between 0 and 2")

        self.faces[face][row][col] = color_name

    def get_sticker(self, face: str, row: int, col: int) -> str:
        return self.faces[face][row][col]

    def color_counts(self) -> dict[str, int]:
        counts = {color_name: 0 for color_name in CUBE_COLORS}
        for grid in self.faces.values():
            for row in grid:
                for color_name in row:
                    counts[color_name] += 1
        return counts

    def copy_faces(self) -> dict[str, FaceGrid]:
        return {
            face: [row.copy() for row in grid]
            for face, grid in self.faces.items()
        }

    def apply_move(self, move: str) -> None:
        face_letter = move[0]
        turns = 2 if move.endswith("2") else 1
        clockwise = not move.endswith("'")

        for _ in range(turns):
            self._apply_quarter_turn(face_letter, clockwise)

    def stickers_for(self, cubie: Cubie) -> dict[str, tuple[float, float, float]]:
        stickers: dict[str, tuple[float, float, float]] = {}

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

    def _sticker_color(self, face: str, row: int, col: int) -> Color:
        return CUBE_COLORS[self.faces[face][row][col]]

    def _filled_face(self, color_name: str) -> FaceGrid:
        return [[color_name for _ in range(3)] for _ in range(3)]

    def _apply_quarter_turn(self, face_letter: str, clockwise: bool) -> None:
        move = MOVE_DEFINITIONS[face_letter]
        angle = move["angle"] if clockwise else -move["angle"]
        rotated: dict[tuple[Vector, Vector], str] = {}

        for face, row, col, position, normal in self._iter_facelets():
            if position[move["axis"]] == move["layer"]:
                position = rotate_vector(position, move["axis"], angle)
                normal = rotate_vector(normal, move["axis"], angle)
            rotated[(position, normal)] = self.faces[face][row][col]

        new_faces = self._empty_faces()
        for (position, normal), color_name in rotated.items():
            face, row, col = facelet_from_position(position, normal)
            new_faces[face][row][col] = color_name

        self.faces = new_faces

    def _iter_facelets(self):
        for face in self.faces:
            for row in range(3):
                for col in range(3):
                    position, normal = position_from_facelet(face, row, col)
                    yield face, row, col, position, normal

    def _empty_faces(self) -> dict[str, FaceGrid]:
        return {
            face: [["white" for _ in range(3)] for _ in range(3)]
            for face in self.faces
        }


MOVE_DEFINITIONS = {
    "U": {"axis": 1, "layer": 1, "angle": -90},
    "D": {"axis": 1, "layer": -1, "angle": 90},
    "R": {"axis": 0, "layer": 1, "angle": -90},
    "L": {"axis": 0, "layer": -1, "angle": 90},
    "F": {"axis": 2, "layer": 1, "angle": -90},
    "B": {"axis": 2, "layer": -1, "angle": 90},
}


def position_from_facelet(face: str, row: int, col: int) -> tuple[Vector, Vector]:
    if face == "top":
        return (col - 1, 1, row - 1), (0, 1, 0)
    if face == "bottom":
        return (1 - col, -1, row - 1), (0, -1, 0)
    if face == "left":
        return (-1, 1 - row, col - 1), (-1, 0, 0)
    if face == "right":
        return (1, 1 - row, 1 - col), (1, 0, 0)
    if face == "front":
        return (col - 1, 1 - row, 1), (0, 0, 1)
    if face == "back":
        return (1 - col, 1 - row, -1), (0, 0, -1)

    raise ValueError(f"Unknown face: {face}")


def facelet_from_position(position: Vector, normal: Vector) -> tuple[str, int, int]:
    x, y, z = position

    if normal == (0, 1, 0):
        return "top", z + 1, x + 1
    if normal == (0, -1, 0):
        return "bottom", z + 1, 1 - x
    if normal == (-1, 0, 0):
        return "left", 1 - y, z + 1
    if normal == (1, 0, 0):
        return "right", 1 - y, 1 - z
    if normal == (0, 0, 1):
        return "front", 1 - y, x + 1
    if normal == (0, 0, -1):
        return "back", 1 - y, 1 - x

    raise ValueError(f"Unknown facelet normal: {normal}")


def rotate_vector(vector: Vector, axis: int, angle: int) -> Vector:
    x, y, z = vector

    if axis == 0 and angle == 90:
        return x, -z, y
    if axis == 0 and angle == -90:
        return x, z, -y
    if axis == 1 and angle == 90:
        return z, y, -x
    if axis == 1 and angle == -90:
        return -z, y, x
    if axis == 2 and angle == 90:
        return -y, x, z
    if axis == 2 and angle == -90:
        return y, -x, z

    raise ValueError(f"Unsupported rotation: axis={axis}, angle={angle}")
