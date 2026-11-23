class MinesweeperError(Exception):
    """Базовое исключение игры."""


class InvalidBoardSizeError(MinesweeperError, ValueError):
    """Некорректные размеры поля или число мин."""


class CellOutOfBoundsError(MinesweeperError, ValueError):
    """Координаты за пределами поля."""


class AlreadyRevealedError(MinesweeperError):
    """Клетка уже открыта."""


class GameOverError(MinesweeperError):
    """Игра завершена — ходы запрещены."""
