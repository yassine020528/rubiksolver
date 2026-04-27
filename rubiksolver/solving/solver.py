from __future__ import annotations

from collections import Counter

import kociemba

from rubiksolver.domain.config import CUBE_COLORS, GRID_SIZE
from rubiksolver.domain.cube import RubiksCube
from rubiksolver.domain.geometry import facelet_from_position
from rubiksolver.domain.types import Vector


SOLVER_FACE_ORDER = [
    ("top", "U"),
    ("right", "R"),
    ("front", "F"),
    ("bottom", "D"),
    ("left", "L"),
    ("back", "B"),
]

KOCIEMBA_FACELETS: list[tuple[Vector, Vector]] = (
    [((x, 1, z), (0, 1, 0)) for z in (-1, 0, 1) for x in (-1, 0, 1)]
    + [((1, y, z), (1, 0, 0)) for y in (1, 0, -1) for z in (1, 0, -1)]
    + [((x, y, 1), (0, 0, 1)) for y in (1, 0, -1) for x in (-1, 0, 1)]
    + [((x, -1, z), (0, -1, 0)) for z in (1, 0, -1) for x in (-1, 0, 1)]
    + [((-1, y, z), (-1, 0, 0)) for y in (1, 0, -1) for z in (-1, 0, 1)]
    + [((x, y, -1), (0, 0, -1)) for y in (1, 0, -1) for x in (1, 0, -1)]
)

MOVE_DESCRIPTIONS = {
    "U": "Turn the top face clockwise.",
    "U'": "Turn the top face counter-clockwise.",
    "U2": "Turn the top face halfway around.",
    "D": "Turn the bottom face clockwise.",
    "D'": "Turn the bottom face counter-clockwise.",
    "D2": "Turn the bottom face halfway around.",
    "L": "Turn the left face clockwise.",
    "L'": "Turn the left face counter-clockwise.",
    "L2": "Turn the left face halfway around.",
    "R": "Turn the right face clockwise.",
    "R'": "Turn the right face counter-clockwise.",
    "R2": "Turn the right face halfway around.",
    "F": "Turn the front face clockwise.",
    "F'": "Turn the front face counter-clockwise.",
    "F2": "Turn the front face halfway around.",
    "B": "Turn the back face clockwise.",
    "B'": "Turn the back face counter-clockwise.",
    "B2": "Turn the back face halfway around.",
}


class CubeValidationError(ValueError):
    pass


def solve_cube(cube: RubiksCube) -> list[str]:
    state = cube_to_kociemba_state(cube)
    if state == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB":
        return []
    solution = kociemba.solve(state)
    if solution.strip() == "":
        return []
    return solution.split()


def cube_to_kociemba_state(cube: RubiksCube) -> str:
    validate_cube(cube)
    color_to_facelet = {
        cube.get_sticker(face, 1, 1): facelet
        for face, facelet in SOLVER_FACE_ORDER
    }

    state = []
    for position, normal in KOCIEMBA_FACELETS:
        face, row, col = facelet_from_position(position, normal)
        state.append(color_to_facelet[cube.get_sticker(face, row, col)])
    return "".join(state)


def validate_cube(cube: RubiksCube) -> None:
    counts = Counter()
    for face, _facelet in SOLVER_FACE_ORDER:
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                counts[cube.get_sticker(face, row, col)] += 1

    missing_counts = [
        f"{color}: {counts[color]}/9"
        for color in CUBE_COLORS
        if counts[color] != 9
    ]
    if missing_counts:
        raise CubeValidationError(
            "Each color must appear exactly 9 times. "
            + ", ".join(missing_counts)
        )

    centers = [cube.get_sticker(face, 1, 1) for face, _facelet in SOLVER_FACE_ORDER]
    if len(set(centers)) != 6:
        raise CubeValidationError(
            "The six center stickers must all use different colors."
        )


def describe_move(move: str) -> str:
    return MOVE_DESCRIPTIONS.get(move, f"Apply move {move}.")


def inverse_move(move: str) -> str:
    if move.endswith("2"):
        return move
    if move.endswith("'"):
        return move[0]
    return f"{move}'"
