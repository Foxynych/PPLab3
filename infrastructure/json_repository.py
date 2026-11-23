import json
from pathlib import Path

from domain.board import Board
from domain.cell import Cell
from domain.game import Game
from domain.repository import GameRepository


class JsonGameRepository(GameRepository):
    """Хранение партий в JSON-файле."""

    def __init__(self, path: Path):
        self.path = path

    def get_all(self) -> list[Game]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [self._game_from_dict(item) for item in data]

    def _game_from_dict(self, item: dict) -> Game:
        cells = [
            [
                Cell(
                    mine=c["mine"],
                    revealed=c["revealed"],
                    flagged=c["flagged"],
                    _adjacent=c["adjacent"],
                )
                for c in row
            ]
            for row in item["board"]["cells"]
        ]
        board = Board(
            width=item["board"]["width"],
            height=item["board"]["height"],
            mines=item["board"]["mines"],
            cells=cells,
        )
        return Game(
            id=item["id"],
            board=board,
            status=item["status"],
            moves=item["moves"],
            elapsed=item["elapsed"],
            history=list(item["history"]),
        )

    def save_all(self, games: list[Game]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = [self._game_to_dict(g) for g in games]
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _game_to_dict(game: Game) -> dict:
        return dict(
            id=game.id,
            status=game.status,
            moves=game.moves,
            elapsed=game.elapsed,
            history=list(game.history),
            board=dict(
                width=game.board.width,
                height=game.board.height,
                mines=game.board.mines,
                cells=[
                    [
                        dict(
                            mine=c.mine,
                            revealed=c.revealed,
                            flagged=c.flagged,
                            adjacent=c.adjacent_mines,
                        )
                        for c in row
                    ]
                    for row in game.board.cells
                ],
            ),
        )
