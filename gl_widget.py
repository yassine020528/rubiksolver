from __future__ import annotations

from PyQt6.QtCore import QPoint, QTimer, Qt, pyqtSignal
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_LINES,
    GL_MODELVIEW,
    GL_PROJECTION,
    GL_QUADS,
    glBegin,
    glClear,
    glClearColor,
    glColor3f,
    glEnable,
    glEnd,
    glFrustum,
    glLineWidth,
    glLoadIdentity,
    glMatrixMode,
    glNormal3f,
    glScalef,
    glRotatef,
    glTranslatef,
    glVertex3f,
    glViewport,
)

from cube import MOVE_DEFINITIONS, RubiksCube


class RubiksGLWidget(QOpenGLWidget):
    move_finished = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.cube = RubiksCube()
        self.x_rotation = -28.0
        self.y_rotation = 35.0
        self.zoom = -10.0
        self.last_mouse_pos = QPoint()
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._advance_animation)
        self.active_move: str | None = None
        self.animation_angle = 0.0
        self.animation_target = 0.0
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def initializeGL(self) -> None:
        glClearColor(0.08, 0.09, 0.11, 1.0)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, width: int, height: int) -> None:
        side = max(1, height)
        aspect = width / side

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glFrustum(-aspect, aspect, -1.0, 1.0, 2.0, 40.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, self.zoom)
        glRotatef(self.x_rotation, 1.0, 0.0, 0.0)
        glRotatef(self.y_rotation, 0.0, 1.0, 0.0)

        for cubie in self.cube.cubies:
            self._draw_cubie(
                cubie.x,
                cubie.y,
                cubie.z,
                self.cube.stickers_for(cubie),
                self._animation_angle_for(cubie.x, cubie.y, cubie.z),
            )

    def animate_move(self, move: str) -> bool:
        if self.animation_timer.isActive():
            return False

        self.active_move = move
        definition = MOVE_DEFINITIONS[move[0]]
        clockwise = not move.endswith("'")
        self.animation_angle = 0.0
        self.animation_target = float(definition["angle"] if clockwise else -definition["angle"])
        if move.endswith("2"):
            self.animation_target *= 2.0
        self.animation_timer.start(16)
        return True

    def mousePressEvent(self, event) -> None:
        self.last_mouse_pos = event.position().toPoint()

    def mouseMoveEvent(self, event) -> None:
        pos = event.position().toPoint()
        dx = pos.x() - self.last_mouse_pos.x()
        dy = pos.y() - self.last_mouse_pos.y()

        if event.buttons() & Qt.MouseButton.LeftButton:
            self.x_rotation += dy * 0.5
            self.y_rotation += dx * 0.5
            self.update()

        self.last_mouse_pos = pos

    def wheelEvent(self, event) -> None:
        steps = event.angleDelta().y() / 120
        self.zoom = max(-18.0, min(-5.0, self.zoom + steps * 0.6))
        self.update()

    def keyPressEvent(self, event) -> None:
        key = event.key()

        if key == Qt.Key.Key_Left:
            self.y_rotation -= 5.0
        elif key == Qt.Key.Key_Right:
            self.y_rotation += 5.0
        elif key == Qt.Key.Key_Up:
            self.x_rotation -= 5.0
        elif key == Qt.Key.Key_Down:
            self.x_rotation += 5.0
        else:
            super().keyPressEvent(event)
            return

        self.update()

    def _draw_cubie(
        self,
        x: int,
        y: int,
        z: int,
        stickers: dict[str, tuple[float, float, float]],
        animation_angle: float | None,
    ) -> None:
        gap = 1.08
        size = 0.48

        glLoadIdentity()
        glTranslatef(0.0, 0.0, self.zoom)
        glRotatef(self.x_rotation, 1.0, 0.0, 0.0)
        glRotatef(self.y_rotation, 0.0, 1.0, 0.0)
        if animation_angle is not None and self.active_move is not None:
            axis = MOVE_DEFINITIONS[self.active_move[0]]["axis"]
            axis_vector = (1.0 if axis == 0 else 0.0, 1.0 if axis == 1 else 0.0, 1.0 if axis == 2 else 0.0)
            glRotatef(animation_angle, *axis_vector)
        glTranslatef(x * gap, y * gap, z * gap)
        glScalef(size, size, size)

        self._draw_black_body()
        self._draw_stickers(stickers)
        self._draw_orientation_labels(x, y, z, stickers)
        self._draw_edges()

    def _animation_angle_for(self, x: int, y: int, z: int) -> float | None:
        if self.active_move is None:
            return None
        definition = MOVE_DEFINITIONS[self.active_move[0]]
        coordinates = (x, y, z)
        if coordinates[definition["axis"]] != definition["layer"]:
            return None
        return self.animation_angle

    def _advance_animation(self) -> None:
        if self.active_move is None:
            self.animation_timer.stop()
            return

        step = 6.0 if self.animation_target > 0 else -6.0
        next_angle = self.animation_angle + step

        if abs(next_angle) >= abs(self.animation_target):
            move = self.active_move
            self.animation_angle = self.animation_target
            self.update()
            self.animation_timer.stop()
            self.cube.apply_move(move)
            self.active_move = None
            self.animation_angle = 0.0
            self.update()
            self.move_finished.emit(move)
            return

        self.animation_angle = next_angle
        self.update()

    def _draw_black_body(self) -> None:
        glColor3f(0.015, 0.015, 0.018)
        self._draw_cube_faces(1.0)

    def _draw_stickers(self, stickers: dict[str, tuple[float, float, float]]) -> None:
        inset = 0.82
        offset = 1.01

        faces = {
            "front": ((0.0, 0.0, 1.0), [(-inset, -inset, offset), (inset, -inset, offset), (inset, inset, offset), (-inset, inset, offset)]),
            "back": ((0.0, 0.0, -1.0), [(inset, -inset, -offset), (-inset, -inset, -offset), (-inset, inset, -offset), (inset, inset, -offset)]),
            "right": ((1.0, 0.0, 0.0), [(offset, -inset, inset), (offset, -inset, -inset), (offset, inset, -inset), (offset, inset, inset)]),
            "left": ((-1.0, 0.0, 0.0), [(-offset, -inset, -inset), (-offset, -inset, inset), (-offset, inset, inset), (-offset, inset, -inset)]),
            "top": ((0.0, 1.0, 0.0), [(-inset, offset, inset), (inset, offset, inset), (inset, offset, -inset), (-inset, offset, -inset)]),
            "bottom": ((0.0, -1.0, 0.0), [(-inset, -offset, -inset), (inset, -offset, -inset), (inset, -offset, inset), (-inset, -offset, inset)]),
        }

        glBegin(GL_QUADS)
        for name, color in stickers.items():
            normal, vertices = faces[name]
            glColor3f(*color)
            glNormal3f(*normal)
            for vertex in vertices:
                glVertex3f(*vertex)
        glEnd()

    def _draw_orientation_labels(
        self,
        x: int,
        y: int,
        z: int,
        stickers: dict[str, tuple[float, float, float]],
    ) -> None:
        center_faces = {
            "front": z == 1 and x == 0 and y == 0,
            "back": z == -1 and x == 0 and y == 0,
            "right": x == 1 and y == 0 and z == 0,
            "left": x == -1 and y == 0 and z == 0,
            "top": y == 1 and x == 0 and z == 0,
            "bottom": y == -1 and x == 0 and z == 0,
        }
        letters = {
            "front": "F",
            "back": "B",
            "right": "R",
            "left": "L",
            "top": "U",
            "bottom": "D",
        }

        for face, is_center in center_faces.items():
            if is_center and face in stickers:
                self._draw_label_on_face(face, letters[face], stickers[face])

    def _draw_label_on_face(
        self,
        face: str,
        letter: str,
        sticker_color: tuple[float, float, float],
    ) -> None:
        luminance = (
            0.2126 * sticker_color[0]
            + 0.7152 * sticker_color[1]
            + 0.0722 * sticker_color[2]
        )
        if luminance < 0.45:
            glColor3f(1.0, 1.0, 1.0)
        else:
            glColor3f(0.02, 0.02, 0.02)

        glLineWidth(5.0)
        glBegin(GL_LINES)
        for start, end in LETTER_SEGMENTS[letter]:
            glVertex3f(*self._face_label_point(face, *start))
            glVertex3f(*self._face_label_point(face, *end))
        glEnd()

    def _face_label_point(self, face: str, horizontal: float, vertical: float):
        offset = 1.045
        basis = FACE_LABEL_BASIS[face]
        normal = basis["normal"]
        right = basis["right"]
        up = basis["up"]
        scale = 0.44

        return (
            normal[0] * offset + right[0] * horizontal * scale + up[0] * vertical * scale,
            normal[1] * offset + right[1] * horizontal * scale + up[1] * vertical * scale,
            normal[2] * offset + right[2] * horizontal * scale + up[2] * vertical * scale,
        )

    def _draw_edges(self) -> None:
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        for start, end in (
            ((-1, -1, -1), (1, -1, -1)),
            ((1, -1, -1), (1, 1, -1)),
            ((1, 1, -1), (-1, 1, -1)),
            ((-1, 1, -1), (-1, -1, -1)),
            ((-1, -1, 1), (1, -1, 1)),
            ((1, -1, 1), (1, 1, 1)),
            ((1, 1, 1), (-1, 1, 1)),
            ((-1, 1, 1), (-1, -1, 1)),
            ((-1, -1, -1), (-1, -1, 1)),
            ((1, -1, -1), (1, -1, 1)),
            ((1, 1, -1), (1, 1, 1)),
            ((-1, 1, -1), (-1, 1, 1)),
        ):
            glVertex3f(*start)
            glVertex3f(*end)
        glEnd()

    def _draw_cube_faces(self, size: float) -> None:
        glBegin(GL_QUADS)

        glNormal3f(0.0, 0.0, 1.0)
        glVertex3f(-size, -size, size)
        glVertex3f(size, -size, size)
        glVertex3f(size, size, size)
        glVertex3f(-size, size, size)

        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(size, -size, -size)
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, size, -size)
        glVertex3f(size, size, -size)

        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f(size, -size, size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, size, size)

        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, -size, size)
        glVertex3f(-size, size, size)
        glVertex3f(-size, size, -size)

        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(-size, size, size)
        glVertex3f(size, size, size)
        glVertex3f(size, size, -size)
        glVertex3f(-size, size, -size)

        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(-size, -size, -size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size, size)
        glVertex3f(-size, -size, size)

        glEnd()


FACE_LABEL_BASIS = {
    "front": {
        "normal": (0.0, 0.0, 1.0),
        "right": (1.0, 0.0, 0.0),
        "up": (0.0, 1.0, 0.0),
    },
    "back": {
        "normal": (0.0, 0.0, -1.0),
        "right": (-1.0, 0.0, 0.0),
        "up": (0.0, 1.0, 0.0),
    },
    "right": {
        "normal": (1.0, 0.0, 0.0),
        "right": (0.0, 0.0, -1.0),
        "up": (0.0, 1.0, 0.0),
    },
    "left": {
        "normal": (-1.0, 0.0, 0.0),
        "right": (0.0, 0.0, 1.0),
        "up": (0.0, 1.0, 0.0),
    },
    "top": {
        "normal": (0.0, 1.0, 0.0),
        "right": (1.0, 0.0, 0.0),
        "up": (0.0, 0.0, -1.0),
    },
    "bottom": {
        "normal": (0.0, -1.0, 0.0),
        "right": (-1.0, 0.0, 0.0),
        "up": (0.0, 0.0, -1.0),
    },
}

LETTER_SEGMENTS = {
    "F": [
        ((-0.55, -0.65), (-0.55, 0.65)),
        ((-0.55, 0.65), (0.5, 0.65)),
        ((-0.55, 0.05), (0.35, 0.05)),
    ],
    "B": [
        ((-0.5, -0.65), (-0.5, 0.65)),
        ((-0.5, 0.65), (0.32, 0.65)),
        ((0.32, 0.65), (0.5, 0.42)),
        ((0.5, 0.42), (0.5, 0.12)),
        ((0.5, 0.12), (0.32, 0.0)),
        ((-0.5, 0.0), (0.32, 0.0)),
        ((0.32, 0.0), (0.5, -0.18)),
        ((0.5, -0.18), (0.5, -0.48)),
        ((0.5, -0.48), (0.32, -0.65)),
        ((-0.5, -0.65), (0.32, -0.65)),
    ],
    "R": [
        ((-0.5, -0.65), (-0.5, 0.65)),
        ((-0.5, 0.65), (0.35, 0.65)),
        ((0.35, 0.65), (0.5, 0.42)),
        ((0.5, 0.42), (0.5, 0.12)),
        ((0.5, 0.12), (0.32, 0.0)),
        ((-0.5, 0.0), (0.32, 0.0)),
        ((-0.05, 0.0), (0.55, -0.65)),
    ],
    "L": [
        ((-0.45, 0.65), (-0.45, -0.65)),
        ((-0.45, -0.65), (0.5, -0.65)),
    ],
    "U": [
        ((-0.5, 0.65), (-0.5, -0.4)),
        ((0.5, 0.65), (0.5, -0.4)),
        ((-0.5, -0.4), (-0.25, -0.65)),
        ((0.5, -0.4), (0.25, -0.65)),
        ((-0.25, -0.65), (0.25, -0.65)),
    ],
    "D": [
        ((-0.5, -0.65), (-0.5, 0.65)),
        ((-0.5, 0.65), (0.2, 0.65)),
        ((0.2, 0.65), (0.5, 0.35)),
        ((0.5, 0.35), (0.5, -0.35)),
        ((0.5, -0.35), (0.2, -0.65)),
        ((-0.5, -0.65), (0.2, -0.65)),
    ],
}
