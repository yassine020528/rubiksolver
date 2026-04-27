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

from rubiksolver.domain.cube import RubiksCube
from rubiksolver.domain.moves import move_definition, signed_move_angle
from rubiksolver.rendering.data import (
    CUBE_EDGES,
    CUBE_FACE_NORMALS_AND_VERTICES,
    FACE_LABEL_BASIS,
    LETTER_SEGMENTS,
    STICKER_FACE_VERTICES,
    center_face_for_cubie,
    label_for_face,
)


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
        self.animation_angle = 0.0
        self.animation_target = signed_move_angle(move)
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
            axis = move_definition(self.active_move).axis
            axis_vector = (
                1.0 if axis == 0 else 0.0,
                1.0 if axis == 1 else 0.0,
                1.0 if axis == 2 else 0.0,
            )
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
        definition = move_definition(self.active_move)
        coordinates = (x, y, z)
        if coordinates[definition.axis] != definition.layer:
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
        glBegin(GL_QUADS)
        for name, color in stickers.items():
            normal, vertices = STICKER_FACE_VERTICES[name]
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
        face = center_face_for_cubie(x, y, z)
        if face is not None and face in stickers:
            self._draw_label_on_face(face, label_for_face(face), stickers[face])

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
        for start, end in CUBE_EDGES:
            glVertex3f(*start)
            glVertex3f(*end)
        glEnd()

    def _draw_cube_faces(self, size: float) -> None:
        glBegin(GL_QUADS)

        for normal, vertices in CUBE_FACE_NORMALS_AND_VERTICES:
            glNormal3f(*normal)
            for x, y, z in vertices:
                glVertex3f(x * size, y * size, z * size)

        glEnd()
