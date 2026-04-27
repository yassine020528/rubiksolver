from cube_types import Color


GRID_SIZE = 3

FACE_NAMES = {
    "top": "Up",
    "bottom": "Down",
    "left": "Left",
    "right": "Right",
    "front": "Front",
    "back": "Back",
}

FACE_LETTERS = {
    "front": "F",
    "back": "B",
    "right": "R",
    "left": "L",
    "top": "U",
    "bottom": "D",
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

SOLVED_FACE_COLORS = {
    "top": "yellow",
    "bottom": "white",
    "left": "blue",
    "right": "green",
    "front": "red",
    "back": "orange",
}

