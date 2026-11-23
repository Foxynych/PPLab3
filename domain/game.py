from dataclasses import dataclass, field

from domain.board import Board
from domain.errors import AlreadyRevealedError, GameOverError


@dataclass
class Game:
    id: int
    board: Board
    status: str = "playing"
    moves: int = 0
    elapsed: int = 0
    history: list[str] = field(default_factory=list)

    @property
    def is_over(self) -> bool:
        return self.status != "playing"

    def reveal(self, x: int, y: int) -> None:
        if self.is_over:
            raise GameOverError("Игра завершена")
        
        cell = self.board.cell(x, y)
        if cell.revealed:
            raise AlreadyRevealedError(f"Клетка ({x}, {y}) уже открыта")
        
        self.board.reveal(x, y)
        self.moves += 1
        self.history.append(f"reveal {x},{y}")
        self._update_status()

    def flag(self, x: int, y: int) -> None:
        if self.is_over:
            raise GameOverError("Игра завершена")
        
        self.board.toggle_flag(x, y)
        self.moves += 1
        self.history.append(f"flag {x},{y}")

    def _update_status(self) -> None:
        if self.board.mines_revealed():
            self.status = "lost"
        elif self.board.all_safe_revealed():
            self.status = "won"
