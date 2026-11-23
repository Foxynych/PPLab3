import tkinter as tk
from pathlib import Path

from application.game_service import GameService
from infrastructure.json_repository import JsonGameRepository
from presentation.console import TkApp


def main() -> None:
    repository = JsonGameRepository(Path(__file__).parent / "saves.json")
    service = GameService(repository)

    root = tk.Tk()
    TkApp(service, root)
    root.mainloop()


if __name__ == "__main__":
    main()
    