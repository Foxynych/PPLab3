from dataclasses import dataclass


@dataclass
class Cell:
    mine: bool = False
    revealed: bool = False
    flagged: bool = False

    @property
    def adjacent_mines(self) -> int:
        return self._adjacent

    _adjacent: int = 0      # вычисляется при генерации поля, наружу — только через property