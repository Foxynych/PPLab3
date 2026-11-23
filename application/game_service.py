from domain.board import Board
from domain.errors import (
    AlreadyRevealedError,
    GameOverError,
    InvalidBoardSizeError,
)
from domain.game import Game
from domain.repository import GameRepository


class GameService:
    """Бизнес-правила: новая партия, ходы, завершение, история."""

    def __init__(self, repository: GameRepository):
        self.repository = repository

    def list_games(self) -> list[Game]:
        return self.repository.get_all()

    def new_game(self, width: int, height: int, mines: int) -> Game:
        games = self.repository.get_all()
        next_id = max((g.id for g in games), default=0) + 1
        game = Game(id=next_id, board=Board(width, height, mines))
        games.append(game)
        self.repository.save_all(games)
        return game

    def get_game(self, game_id: int) -> Game:
        for game in self.repository.get_all():
            if game.id == game_id:
                return game
        raise InvalidBoardSizeError(f"Партия с ID {game_id} не найдена")

    def reveal(self, game_id: int, x: int, y: int) -> Game:
        game = self.get_game(game_id)
        game.reveal(x, y)
        self._save(game)
        return game

    def flag(self, game_id: int, x: int, y: int) -> Game:
        game = self.get_game(game_id)
        game.flag(x, y)
        self._save(game)
        return game

    def delete_game(self, game_id: int) -> None:
        games = self.repository.get_all()
        remaining = [g for g in games if g.id != game_id]
        if len(remaining) == len(games):
            raise InvalidBoardSizeError(f"Партия с ID {game_id} не найдена")
        self.repository.save_all(remaining)

    def clear_history(self) -> None:
        self.repository.save_all([])

    # --- внутренние ------------------------------------------------------

    def _save(self, updated: Game) -> None:
        games = self.repository.get_all()
        self.repository.save_all(
            [updated if g.id == updated.id else g for g in games]
        )