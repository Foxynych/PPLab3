import random

from domain.cell import Cell
from domain.errors import CellOutOfBoundsError, InvalidBoardSizeError


class Board:
    """Игровое поле. Не знает ни о UI, ни о хранении."""

    MIN_SIZE = 3
    MAX_SIZE = 50

    def __init__(self, width: int, height: int, mines: int, cells=None):
        if not (self.MIN_SIZE <= width <= self.MAX_SIZE):
            raise InvalidBoardSizeError(
                f"Ширина должна быть от {self.MIN_SIZE} до {self.MAX_SIZE}"
            )
        if not (self.MIN_SIZE <= height <= self.MAX_SIZE):
            raise InvalidBoardSizeError(
                f"Высота должна быть от {self.MIN_SIZE} до {self.MAX_SIZE}"
            )
        if not (1 <= mines <= width * height - 1):
            raise InvalidBoardSizeError(
                f"Число мин должно быть от 1 до {width * height - 1}"
            )
        
        self.width = width
        self.height = height
        self.mines = mines
        self.cells: list[list[Cell]] = (
            cells if cells is not None else self._generate_cells()
        )

    def _generate_cells(self) -> list[list[Cell]]:
        flat = [Cell() for _ in range(self.width * self.height)]
        for i in random.sample(range(len(flat)), self.mines):
            flat[i].mine = True

        grid = [flat[r * self.width:(r + 1) * self.width] for r in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                grid[y][x]._adjacent = sum(
                    1 for nx, ny in self.neighbors(x, y) if grid[ny][nx].mine
                )

        return grid

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def cell(self, x: int, y: int) -> Cell:
        if not self.in_bounds(x, y):
            raise CellOutOfBoundsError(f"Координаты ({x}, {y}) вне поля")
        
        return self.cells[y][x]

    def neighbors(self, x: int, y: int):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue

                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny):
                    yield nx, ny

    def reveal(self, x: int, y: int) -> None:
        cell = self.cell(x, y)
        if cell.revealed or cell.flagged:
            return
        
        cell.revealed = True
        if cell.mine or cell.adjacent_mines > 0:
            return
        
        for nx, ny in self.neighbors(x, y):
            self.reveal(nx, ny)

    def toggle_flag(self, x: int, y: int) -> None:
        cell = self.cell(x, y)
        if cell.revealed:
            return
        
        cell.flagged = not cell.flagged

    def all_safe_revealed(self) -> bool:
        return all(
            cell.revealed or cell.mine
            for row in self.cells
            for cell in row
        )

    def mines_revealed(self) -> bool:
        return any(cell.revealed and cell.mine for row in self.cells for cell in row)
