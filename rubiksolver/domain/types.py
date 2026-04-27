from dataclasses import dataclass


Color = tuple[float, float, float]
FaceGrid = list[list[str]]
Vector = tuple[int, int, int]


@dataclass(frozen=True)
class Cubie:
    x: int
    y: int
    z: int


@dataclass(frozen=True)
class MoveDefinition:
    axis: int
    layer: int
    angle: int

