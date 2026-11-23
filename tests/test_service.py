import unittest

from application.game_service import GameService
from domain.board import Board
from domain.errors import (
    AlreadyRevealedError,
    CellOutOfBoundsError,
    GameOverError,
    InvalidBoardSizeError,
)
from domain.game import Game
from domain.repository import GameRepository


class InMemoryRepository(GameRepository):
    def __init__(self):
        self.games: list[Game] = []

    def get_all(self) -> list[Game]:
        return self.games

    def save_all(self, games: list[Game]) -> None:
        self.games = games


def make_game(width=3, height=3, mines=1, mine_at=(0, 0)) -> Game:
    """Партия с предсказуемой миной — без random."""
    board = Board(width, height, mines)
    for row in board.cells:
        for c in row:
            c.mine = False
            c._adjacent = 0
    mx, my = mine_at
    board.cells[my][mx].mine = True
    for y in range(height):
        for x in range(width):
            board.cells[y][x]._adjacent = sum(
                1 for nx, ny in board.neighbors(x, y) if board.cells[ny][nx].mine
            )
    return Game(id=1, board=board)


class GameServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = GameService(InMemoryRepository())

    def test_new_game_valid(self):
        game = self.service.new_game(5, 5, 3)
        self.assertEqual(game.board.width, 5)
        self.assertEqual(game.board.height, 5)
        self.assertEqual(game.board.mines, 3)
        self.assertEqual(game.status, "playing")
        self.assertEqual(len(self.service.list_games()), 1)

    def test_new_game_bad_size(self):
        for args in ((2, 5, 1), (5, 2, 1), (5, 5, 0), (5, 5, 25)):
            with self.subTest(args=args):
                with self.assertRaises(InvalidBoardSizeError):
                    self.service.new_game(*args)

    def test_ids_increase(self):
        a = self.service.new_game(5, 5, 1)
        b = self.service.new_game(5, 5, 1)
        self.assertEqual((a.id, b.id), (1, 2))

    def test_reveal_mine_loses(self):
        repo = InMemoryRepository()
        repo.games.append(make_game(3, 3, 1, mine_at=(1, 1)))
        service = GameService(repo)
        service.reveal(1, 1, 1)
        self.assertEqual(repo.games[0].status, "lost")

    def test_reveal_after_game_over(self):
        repo = InMemoryRepository()
        repo.games.append(make_game(3, 3, 1, mine_at=(1, 1)))
        service = GameService(repo)
        service.reveal(1, 1, 1)
        with self.assertRaises(GameOverError):
            service.reveal(1, 2, 2)

    def test_reveal_out_of_bounds(self):
        repo = InMemoryRepository()
        repo.games.append(make_game(3, 3, 1, mine_at=(0, 0)))
        service = GameService(repo)
        with self.assertRaises(CellOutOfBoundsError):
            service.reveal(1, 99, 0)

    def test_flag_toggle(self):
        repo = InMemoryRepository()
        repo.games.append(make_game(3, 3, 1, mine_at=(0, 0)))
        service = GameService(repo)
        service.flag(1, 1, 1)
        self.assertTrue(repo.games[0].board.cells[1][1].flagged)
        service.flag(1, 1, 1)
        self.assertFalse(repo.games[0].board.cells[1][1].flagged)

    def test_delete_game(self):
        game = self.service.new_game(5, 5, 1)
        self.service.delete_game(game.id)
        self.assertEqual(self.service.list_games(), [])

    def test_delete_missing_game(self):
        with self.assertRaises(InvalidBoardSizeError):
            self.service.delete_game(42)

    def test_clear_history(self):
        self.service.new_game(5, 5, 1)
        self.service.clear_history()
        self.assertEqual(self.service.list_games(), [])


if __name__ == "__main__":
    unittest.main()
