from abc import ABC, abstractmethod

from domain.game import Game


class GameRepository(ABC):
    """Контракт хранения партий. Бизнес-логика не знает о JSON."""

    @abstractmethod
    def get_all(self) -> list[Game]:
        pass

    @abstractmethod
    def save_all(self, games: list[Game]) -> None:
        pass
