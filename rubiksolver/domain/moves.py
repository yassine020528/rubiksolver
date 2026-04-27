from rubiksolver.domain.types import MoveDefinition


MOVE_DEFINITIONS = {
    "U": MoveDefinition(axis=1, layer=1, angle=-90),
    "D": MoveDefinition(axis=1, layer=-1, angle=90),
    "R": MoveDefinition(axis=0, layer=1, angle=-90),
    "L": MoveDefinition(axis=0, layer=-1, angle=90),
    "F": MoveDefinition(axis=2, layer=1, angle=-90),
    "B": MoveDefinition(axis=2, layer=-1, angle=90),
}


def move_definition(move: str) -> MoveDefinition:
    try:
        return MOVE_DEFINITIONS[move[0]]
    except (IndexError, KeyError) as error:
        raise ValueError(f"Unknown move: {move}") from error


def move_turn_count(move: str) -> int:
    return 2 if move.endswith("2") else 1


def is_clockwise(move: str) -> bool:
    return not move.endswith("'")


def signed_move_angle(move: str) -> float:
    definition = move_definition(move)
    angle = definition.angle if is_clockwise(move) else -definition.angle
    return float(angle * move_turn_count(move))
