import tkinter as tk
from tkinter import messagebox, simpledialog

from application.game_service import GameService
from domain.errors import MinesweeperError


CELL_SIZE = 32
FONT_CELL = ("TkDefaultFont", 14, "bold")

NUM_COLORS = {
    1: "#1976d2", 2: "#388e3c", 3: "#d32f2f", 4: "#7b1fa2",
    5: "#ff8f00", 6: "#0097a7", 7: "#212121", 8: "#616161",
}

COLOR_CLOSED   = "#bdbdbd"
COLOR_CLOSED_H = "#a8a8a8"
COLOR_OPENED   = "#eeeeee"
COLOR_FLAG     = "#fbc02d"
COLOR_MINE     = "#c62828"


class TkApp:
    """GUI на Tkinter. Никаких бизнес-правил и работы с JSON."""

    def __init__(self, service: GameService, root: tk.Tk):
        self.service = service
        self.root = root
        self.current_game = None

        self.root.title("Сапёр")
        self.root.resizable(False, False)

        self.menu_frame = tk.Frame(root, padx=20, pady=20)
        self.game_frame = tk.Frame(root)
        self._build_menu()
        self.menu_frame.pack()

    # ───────────────────────────── МЕНЮ ─────────────────────────────

    def _build_menu(self) -> None:
        f = self.menu_frame
        tk.Label(f, text="САПЁР", font=("TkDefaultFont", 22, "bold")).pack(pady=(0, 16))
        for text, cmd in (
            ("Новая игра",           self._new_game),
            ("Продолжить игру",      self._continue_game),
            ("Список партий",        self._list_games),
            ("Удалить партию",       self._delete_game),
            ("Очистить все партии",  self._clear_all),
        ):
            tk.Button(f, text=text, width=24, command=cmd).pack(pady=3)
        tk.Button(f, text="Выход", width=24, command=self.root.destroy).pack(pady=(16, 0))

    def _show_menu(self) -> None:
        for child in self.game_frame.winfo_children():
            child.destroy()
        self.game_frame.pack_forget()
        self.menu_frame.pack()

    # ──────────────────────── ПУНКТЫ МЕНЮ ───────────────────────────

    def _new_game(self) -> None:
        w = simpledialog.askinteger("Новая игра", "Ширина (3..50):",
                                    minvalue=3, maxvalue=50, initialvalue=9)
        if w is None:
            return
        h = simpledialog.askinteger("Новая игра", "Высота (3..50):",
                                    minvalue=3, maxvalue=50, initialvalue=9)
        if h is None:
            return
        m = simpledialog.askinteger("Новая игра", f"Число мин (1..{w * h - 1}):",
                                    minvalue=1, maxvalue=w * h - 1,
                                    initialvalue=max(1, w * h // 6))
        if m is None:
            return
        try:
            game = self.service.new_game(w, h, m)
        except MinesweeperError as error:
            messagebox.showerror("Ошибка", str(error))
            return
        self._open_game(game)

    def _continue_game(self) -> None:
        game_id = self._pick_game_id("Продолжить игру")
        if game_id is None:
            return
        try:
            self._open_game(self.service.get_game(game_id))
        except MinesweeperError as error:
            messagebox.showerror("Ошибка", str(error))

    def _list_games(self) -> None:
        games = self.service.list_games()
        if not games:
            messagebox.showinfo("Партии", "Сохранённых партий нет.")
            return
        text = "\n".join(
            f"#{g.id}  [{g.status:7}]  {g.board.width}x{g.board.height}  "
            f"мин: {g.board.mines}  ходов: {g.moves}"
            for g in games
        )
        messagebox.showinfo("Партии", text)

    def _delete_game(self) -> None:
        game_id = self._pick_game_id("Удалить партию")
        if game_id is None:
            return
        try:
            self.service.delete_game(game_id)
            messagebox.showinfo("Готово", f"Партия #{game_id} удалена.")
        except MinesweeperError as error:
            messagebox.showerror("Ошибка", str(error))

    def _clear_all(self) -> None:
        if messagebox.askyesno("Очистить", "Удалить все сохранённые партии?"):
            self.service.clear_history()
            messagebox.showinfo("Готово", "История очищена.")

    # ────────────────────────── ЭКРАН ИГРЫ ──────────────────────────

    def _open_game(self, game) -> None:
        self.current_game = game
        self.menu_frame.pack_forget()
        for child in self.game_frame.winfo_children():
            child.destroy()

        self.status_label = tk.Label(self.game_frame, anchor="w",
                                     font=("TkDefaultFont", 11))
        self.status_label.pack(fill="x", padx=8, pady=(8, 4))

        b = game.board
        self.canvas = tk.Canvas(
            self.game_frame,
            width=b.width * CELL_SIZE,
            height=b.height * CELL_SIZE,
            highlightthickness=1,
            highlightbackground="#616161",
        )
        self.canvas.pack(padx=8)
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)

        tk.Button(self.game_frame, text="В меню", command=self._show_menu
                  ).pack(pady=8)

        self.game_frame.pack()
        self._render()

    def _render(self) -> None:
        game = self.current_game
        board = game.board
        self.canvas.delete("all")

        for y in range(board.height):
            for x in range(board.width):
                self._draw_cell(x, y)

        self.status_label.config(
            text=f"Партия #{game.id}   |   ходов: {game.moves}   |   "
                 f"статус: {self._status_ru(game.status)}"
        )

    def _draw_cell(self, x: int, y: int) -> None:
        game = self.current_game
        board = game.board
        cell = board.cells[y][x]

        x1, y1 = x * CELL_SIZE, y * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE

        if not cell.revealed:
            if game.is_over and cell.mine:
                fill, text, color = COLOR_MINE, "*", "white"
            elif cell.flagged:
                fill, text, color = COLOR_FLAG, "F", "#000000"
            else:
                fill, text, color = COLOR_CLOSED, "", "#000000"
        elif cell.mine:
            fill, text, color = COLOR_MINE, "*", "white"
        elif cell.adjacent_mines == 0:
            fill, text, color = COLOR_OPENED, "", "#000000"
        else:
            fill = COLOR_OPENED
            text = str(cell.adjacent_mines)
            color = NUM_COLORS[cell.adjacent_mines]

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#9e9e9e")
        if text:
            self.canvas.create_text(x1 + CELL_SIZE / 2, y1 + CELL_SIZE / 2,
                                    text=text, fill=color, font=FONT_CELL)

    # ────────────────────────── ОБРАБОТКА ───────────────────────────

    def _on_left_click(self, event) -> None:
        self._do_move(self._reveal, event)

    def _on_right_click(self, event) -> None:
        self._do_move(self._flag, event)

    def _do_move(self, action, event) -> None:
        game = self.current_game
        if game is None or game.is_over:
            return
        x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
        try:
            self.current_game = action(game.id, x, y)
            self._render()
            self._check_end()
        except MinesweeperError as error:
            self._flash_error(str(error))

    def _reveal(self, game_id, x, y):
        return self.service.reveal(game_id, x, y)

    def _flag(self, game_id, x, y):
        return self.service.flag(game_id, x, y)

    def _check_end(self) -> None:
        game = self.current_game
        if game.status == "won":
            messagebox.showinfo("Победа!",
                                f"Все безопасные клетки открыты за {game.moves} ходов.")
            self._show_menu()
        elif game.status == "lost":
            messagebox.showerror("Поражение", "Вы открыли мину.")
            self._show_menu()

    def _flash_error(self, message: str) -> None:
        # Неверный ход (уже открыто/вне поля) — не диалог, чтобы не мешать игре.
        self.status_label.config(text=f"⚠ {message}")
        self.root.after(1500, self._render)

    # ────────────────────────── ДИАЛОГИ ─────────────────────────────

    def _pick_game_id(self, title: str) -> int | None:
        games = self.service.list_games()
        if not games:
            messagebox.showinfo("Партии", "Сохранённых партий нет.")
            return None

        top = tk.Toplevel(self.root)
        top.title(title)
        top.resizable(False, False)
        listbox = tk.Listbox(top, width=52, height=min(15, max(3, len(games))))
        for g in games:
            listbox.insert(
                "end",
                f"#{g.id}  [{g.status:7}]  {g.board.width}x{g.board.height}  "
                f"мин: {g.board.mines}  ходов: {g.moves}",
            )
        listbox.pack(padx=10, pady=10)

        result = {"id": None}

        def on_ok() -> None:
            sel = listbox.curselection()
            if sel:
                result["id"] = games[sel[0]].id
            top.destroy()

        tk.Button(top, text="Выбрать", width=12, command=on_ok).pack(pady=(0, 10))
        top.grab_set()
        self.root.wait_window(top)
        return result["id"]

    @staticmethod
    def _status_ru(status: str) -> str:
        return {"playing": "идёт", "won": "победа", "lost": "поражение"}.get(status, status)