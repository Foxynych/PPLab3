# Сапёр — пример слоистой архитектуры на Python

Минимальный консольный «Сапёр» на Python 3.10+, без сторонних зависимостей.

## Запуск в PyCharm

1. Распакуйте архив.
2. В PyCharm выберите **File → Open** и папку `layered_minesweeper`.
3. Укажите Python 3.10 или новее как интерпретатор проекта.
4. Откройте `main.py` и нажмите **Run**.
5. Партии сохраняются в `saves.json` рядом с `main.py`.

## Меню

1. Новая игра — ширина/высота/число мин (3..50, мины от 1 до `W*H-1`).
2. Продолжить игру — по ID партии.
3. Список партий — статус, размеры, число мин, ходов.
4. Удалить партию — по ID.
5. Очистить все партии — с подтверждением.
0. Выход.

## Команды в игре

- `r x y` — открыть клетку;
- `f x y` — поставить/снять флаг;
- `q` — выйти в меню (партия сохраняется).

Клетки: ` .` закрыта, ` ?` флаг, `  ` пусто, ` 1..8` число соседних мин,
` *` мина (показывается при поражении или после победы).

## GUI на Tkinter

Интерфейс вынесен в `presentation/tk_app.py`. Tkinter входит в стандартную
поставку Python (Windows/macOS — «из коробки»; Linux — пакет `python3-tk`).

- ЛКМ по клетке — открыть;
- ПКМ — поставить/снять флаг;
- Меню (кнопка «В меню» внутри игры) — вернуться к списку партий;
- Новые диалоги — «Новая игра» (размеры и мины), «Продолжить», «Удалить».

`application/`, `domain/`, `infrastructure/` от GUI не зависят; тесты
по-прежнему работают без Tkinter (`python -m unittest discover -s tests -v`).

## UML-диаграмма (draw.io)

Файл `minesweeper.drawio` открывается в https://app.diagrams.net через
**File → Open From → Device…** или перетаскиванием. Диаграмма содержит
слои (presentation / application / domain / infrastructure), сущности
`Cell`, `Board`, `Game`, интерфейс `GameRepository`, реализацию
`JsonGameRepository`, `GameService`, `TkApp`, `main` и иерархию
исключений с `MinesweeperError` в корне.

Экспорт для отчёта: **File → Export as → PNG** (поставьте галочку
«Transparent Background» выключенной, «Border» = 10).

## Слои

```text
main.py                       Сборка зависимостей (composition root)
presentation/console.py       UI: input/print, меню, отрисовка поля
application/game_service.py   Бизнес-правила: создание партии, ходы, удаление
domain/game.py                Сущность партии (статус, ходы, история)
domain/board.py               Поле: генерация, flood fill, проверка победы
domain/cell.py                Клетка: мина/открыта/флаг/число соседей
domain/errors.py              Своя иерархия исключений
domain/repository.py          Абстракция хранилища
infrastructure/json_repository.py  Сериализация партии в JSON и обратно
tests/test_service.py         Unit-тесты с InMemoryRepository