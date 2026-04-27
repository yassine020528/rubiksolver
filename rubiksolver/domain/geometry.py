from rubiksolver.domain.config import FACE_NAMES
from rubiksolver.domain.types import Cubie, Vector


CUBIES = tuple(
    Cubie(x, y, z)
    for x in range(-1, 2)
    for y in range(-1, 2)
    for z in range(-1, 2)
)


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


def iter_facelet_positions():
    for face in FACE_NAMES:
        for row in range(3):
            for col in range(3):
                position, normal = position_from_facelet(face, row, col)
                yield face, row, col, position, normal


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
