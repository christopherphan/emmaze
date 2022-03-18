#!/usr/bin/env python3
"""Classes for generating and displaying random mazes."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from random import choice, random, sample
from typing import Final, Literal, NamedTuple, Optional, TypeAlias

DIRECTION_TYPE: TypeAlias = Literal["north", "south", "east", "west"]
NS_DIRECTIONS: Final[list[DIRECTION_TYPE]] = ["north", "south"]
EW_DIRECTIONS: Final[list[DIRECTION_TYPE]] = ["east", "west"]
DIRECTIONS: Final[list[DIRECTION_TYPE]] = ["north", "south", "east", "west"]
DIAG_DIRECTION_TYPE = tuple[DIRECTION_TYPE, DIRECTION_TYPE]
DIAG_DIRECTIONS: Final[list[DIAG_DIRECTION_TYPE]] = [
    (ns, ew) for ns in NS_DIRECTIONS for ew in EW_DIRECTIONS
]


class Position(NamedTuple):
    """
    Represent the location of a cell in the maze.

    :param row: The row of the cell
    :type row: int

    :param column: The column of the cell
    :type column: int
    """

    row: int
    column: int

    def __str__(self: Position) -> str:
        """Return ``str(self)``."""
        return f"({self.row}, {self.column})"

    def __add__(self: Position, other) -> Position:
        """Return ``self + other``."""
        if isinstance(other, Position):
            return self.__class__(self.row + other.row, self.column + other.column)
        return NotImplemented

    def __sub__(self: Position, other) -> Position:
        """Return ``self - other``."""
        if isinstance(other, Position):
            return self.__class__(self.row - other.row, self.column - other.column)
        return NotImplemented

    def get_cell(self: Position, maze: Maze) -> Optional[MazeCell]:
        """
        Get the cell with this position.

        :param maze: The maze from which to retrieve the cell.
        :type maze: Maze

        :returns: The cell at the desired position, if there is one. Otherwise,
            ``None`` is returned.
        :rtype: Optional[MazeCell]
        """
        return maze.cells[self.row][self.column]


@dataclass
class WallInfo:
    """
    Keep track of information about walls.

    This is a ``dataclass`` that provides a ``bool`` for each of the four cardinal
    directions.

    This is used by ``MazeCell`` objects to record the walls of each cell. It is also
    used in the ``wallfollower`` classes to keep track of which walls have been
    accounted for.

    :param north: The status of the north wall. Defaults to ``True``.
    :type north: bool

    :param south: The status of the south wall. Defaults to ``True``.
    :type south: bool

    :param east: The status of the east wall. Defaults to ``True``.
    :type east: bool

    :param west: The status of the west wall. Defaults to ``True``.
    :type west: bool

    In addition to, e.g., ``self.west``, the syntax ``self["west"]`` can be used
    to access and set a field.
    """

    north: bool = True
    south: bool = True
    east: bool = True
    west: bool = True

    def __getitem__(self: WallInfo, key: DIRECTION_TYPE) -> bool:
        """Return ``self[key]``, which is an alias for ``self.key``."""
        if key == "north":
            return self.north
        if key == "south":
            return self.south
        if key == "east":
            return self.east
        if key == "west":
            return self.west

    def __setitem__(self: WallInfo, key: DIRECTION_TYPE, value: bool) -> None:
        """Allow ``self[key]``to be an alias for ``self.key``."""
        if key == "north":
            self.north = value
        if key == "south":
            self.south = value
        if key == "east":
            self.east = value
        if key == "west":
            self.west = value

    def copy(self: WallInfo) -> WallInfo:
        """Return a copy of the object."""
        return self.__class__(self.north, self.south, self.east, self.west)

    def toggle(self: WallInfo, direction: DIRECTION_TYPE) -> None:
        """Toggle ``self.direction`` from ``False`` to ``True`` or vice-versa."""
        self[direction] = not self[direction]

    @property
    def any(self: WallInfo) -> bool:
        """Return ``True`` if any walls are True."""
        return any(self[direction] for direction in DIRECTIONS)

    @property
    def number(self: WallInfo) -> int:
        """Return the number of directions which are ``True``."""
        return sum(1 if self[direction] else 0 for direction in DIRECTIONS)


@dataclass
class AdjacencyInfo:
    """
    Record information about neighboring MazeCells.

    This is a ``dataclass`` that provides a ``MazeCell`` (or ``None``) for each of the
    four cardinal directions.

    These represent the cells that are adjacent in that direction (but does not
    necessarily indicate that there is a passage between the cells).

    :param north: The cell to the north
    :type north: Optional[MazeCell]

    :param south: The cell to the south
    :type south: Optional[MazeCell]

    :param east: The cell to the east
    :type east: Optional[MazeCell]

    :param west: The cell to the west
    :type west: Optional[MazeCell]

    In addition to, e.g., ``self.west``, the syntax ``self["west"]`` can be used
    to access and set a field.
    """

    north: Optional[MazeCell]
    south: Optional[MazeCell]
    east: Optional[MazeCell]
    west: Optional[MazeCell]

    def __getitem__(self: AdjacencyInfo, key: DIRECTION_TYPE) -> Optional[MazeCell]:
        """Return ``self[key]``, which is an alias for ``self.key``."""
        if key == "north":
            return self.north
        if key == "south":
            return self.south
        if key == "east":
            return self.east
        if key == "west":
            return self.west

    def __setitem__(
        self: AdjacencyInfo, key: DIRECTION_TYPE, value: Optional[MazeCell]
    ) -> None:
        """Allow ``self[key]``to be an alias for ``self.key``."""
        if key == "north":
            self.north = value
        if key == "south":
            self.south = value
        if key == "east":
            self.east = value
        if key == "west":
            self.west = value


class MazeCell:
    """
    Represent a single cell in the maze.

    :param maze: The maze to place the cell in. Defaults to ``None``.
    :type maze: Optional[Maze]

    :param position: The position within the maze to place the cell. Defaults to
        ``None``.
    :type position: Optional[Position]
    """

    def __init__(
        self: MazeCell, maze: Optional[Maze] = None, position: Optional[Position] = None
    ) -> None:
        """Initialize a new object."""
        self.maze = maze
        self.position = position
        self.adjacent = AdjacencyInfo(None, None, None, None)
        self.walls = WallInfo(True, True, True, True)
        if self.maze is not None and self.position is not None:
            self.maze.set_pos(self.position, self)
        self.update_neighbors()

    def __repr__(self: MazeCell) -> str:
        """Return ``repr(self)``."""
        return f"<{self.__class__.__name__} in {self.maze!r} at {self.position!r}>"

    def update_neighbors(
        self: MazeCell, direction: Optional[DIRECTION_TYPE] = None
    ) -> None:
        """
        Automatically update neighbor information based on the underlying maze.

        :param direction: The direction to update. If ``None``, update all directions.
            Defaults to ``None``. Otherwise, should be one of ``"north"``, ``"south"``,
            ``"east"``, or ``"west"``. (All other inputs are ignored.)
        :type direction: Optional[DIRECTION_TYPE]
        """
        if self.maze is not None and self.position is not None:
            row = self.position.row
            column = self.position.column
            if (
                direction in [None, "north"]
                and row > 0
                and (c := self.maze.cells[row - 1][column]) is not None
            ):
                self.adjacent.north = c
            if (
                direction in [None, "south"]
                and row < self.maze.rows - 1
                and (c := self.maze.cells[row + 1][column]) is not None
            ):
                self.adjacent.south = c
            if (
                direction in [None, "west"]
                and column > 0
                and (c := self.maze.cells[row][column - 1]) is not None
            ):
                self.adjacent.west = c
            if (
                direction in [None, "east"]
                and column < self.maze.cols - 1
                and (c := self.maze.cells[row][column + 1]) is not None
            ):
                self.adjacent.east = c

    def remove_wall(self: MazeCell, direction: DIRECTION_TYPE) -> None:
        """
        Remove the wall in a given direction.

        If there is a adjacent cell in the given direction, remove the wall in
        the cell and corresponding wall in the adjacent cell. If there is no
        adjacent cell in the given direction, do nothing.

        :param direction: The direction of the wall to removed. Should be one of
            ``"north"``, ``"south"``, ``"east"``, or ``"west"``. Any other input
            will be ignored.
        :type direction: DIRECTION_TYPE
        """
        if direction == "north" and (c := self.adjacent.north) is not None:
            self.walls.north = False
            c.walls.south = False
        if direction == "south" and (c := self.adjacent.south) is not None:
            self.walls.south = False
            c.walls.north = False
        if direction == "east" and (c := self.adjacent.east) is not None:
            self.walls.east = False
            c.walls.west = False
        if direction == "west" and (c := self.adjacent.west) is not None:
            self.walls.west = False
            c.walls.east = False


@dataclass
class MazeExit:
    """
    Represent an exit of the maze.

    :param wall: The side of the maze with contains the exit
    :type wall: DIRECTION_TYPE

    :param location: The row/column of the exit
    :type location: int
    """

    wall: DIRECTION_TYPE
    location: int

    def print_location(self: MazeExit, maze: Maze) -> tuple[int, int]:
        """
        Return the location in an ASCII maze for the exit.

        :param maze: The maze in which the exit is placed.
        :type maze: Maze

        :returns: The coordinates of the exit.
        :rtype: tuple[int, int]
        """
        if self.wall == "north":
            return (2 * self.location + 1, 0)
        if self.wall == "west":
            return (0, 2 * self.location + 1)
        if self.wall == "east":
            return (2 * maze.cols, 2 * self.location + 1)
        if self.wall == "south":
            return (2 * self.location + 1, 2 * maze.rows)
        raise ValueError("Invalid direction.")

    def cell_position(self: MazeExit, maze: Maze) -> Position:
        """
        Give the cell position (row and column) of the exit.

        :param maze: The maze in which the exit is placed.
        :type maze: Maze

        :returns: The position of the cell next to the exit.
        :rtype: Position
        """
        if self.wall == "north":
            return Position(0, self.location)
        if self.wall == "west":
            return Position(self.location, 0)
        if self.wall == "east":
            return Position(self.location, maze.cols - 1)
        if self.wall == "south":
            return Position(maze.rows - 1, self.location)
        raise ValueError("Invalid direction.")


class Maze:
    """
    Represent a whole maze.

    A maze comprises a rectangular array of cells.

    :param rows: The number of rows of cells in the maze.
    :type rows: int

    :param cols: The number of columns of cells in the maze.
    :type cols: int

    :param exits: Information about the exits of the maze.
    :type exits: Sequence[MazeExit]

    :ivar cells: The cells of the maze
    :vartype cells: list[list[Optional[MazeCell]]]

    """

    def __init__(self: Maze, rows: int, cols: int, exits: Sequence[MazeExit]) -> None:
        """Initialize a new object."""
        self.cells: list[list[Optional[MazeCell]]] = [
            [None for _2 in range(cols)] for _ in range(rows)
        ]
        self.rows = rows
        self.cols = cols
        self.exits = exits
        self.exit_loc = [a.print_location(self) for a in exits]

    def __repr__(self: Maze) -> str:
        """Return ``repr(self)``."""
        return (
            f"{self.__class__.__name__}({self.rows!r}, {self.cols!r}, {self.exits!r})"
        )

    def set_pos(self: Maze, position: Position, cell: MazeCell):
        """
        Place a MazeCell in a position.

        This method puts ``cell`` in ``self.cells[position.row][position.column]``
        and then updates all the appropriate ``AdjacencyInfo`` objects.

        :param position: The position in which to place the cell.
        :type position: Position

        :param cell: The cell to place.
        :type cell: MazeCell
        """
        row = position.row
        column = position.column
        if row < 0 or row >= self.rows:
            raise ValueError
        if column < 0 or column >= self.cols:
            raise ValueError
        self.cells[row][column] = cell
        if row > 0 and (c := self.cells[row - 1][column]) is not None:
            c.update_neighbors("south")
        if row < self.rows - 1 and (c := self.cells[row + 1][column]) is not None:
            c.update_neighbors("north")
        if column > 0 and (c := self.cells[row][column - 1]) is not None:
            c.update_neighbors("east")
        if column < self.cols - 1 and (c := self.cells[row][column + 1]) is not None:
            c.update_neighbors("west")

    def solid(self: Maze, x: int, y: int) -> bool:
        """
        Return ``True`` if location (``x``, ``y``) in an ASCII-art version of the maze is inside a wall.

        Note that the cell in position (0, 0) will take up locations (0, 0) to (3, 3),
        the cell in position (0, 1) will take up locations (3, 0) to (6, 3), etc.
        """
        if (x <= 0 or x >= 2 * self.cols) or (y <= 0 or y >= 2 * self.rows):
            return (x, y) not in self.exit_loc
        if x % 2 == 0 and y % 2 == 0:
            return True
        if x % 2 == 0:
            return (c := self.cells[y // 2][x // 2]) is None or c.walls.west
        if y % 2 == 0:
            return (c := self.cells[y // 2][x // 2]) is None or c.walls.north
        return (c := self.cells[y // 2][x // 2]) is None

    def ascii_version(self: Maze, wall_chr: str = "#") -> str:
        """
        Return ASCII art version of the maze.

        In this output, each cell is one character, and each wall is one character.

        :param wall_chr: The character that represents a wall.
        :type wall_chr: str

        :returns: An ASCII-art version of the maze.
        :rtype: str
        """
        return "\n".join(
            "".join(
                wall_chr if self.solid(x, y) else " " for x in range(2 * self.cols + 1)
            )
            for y in range(2 * self.rows + 1)
        )

    def __str__(self: Maze) -> str:
        """Return ``str(self)``."""
        return self.ascii_version()


class MazeConstructor:
    """A class that makes a maze."""

    def __init__(self: MazeConstructor, workers: list[MazeWorker]):
        """Initialize object."""
        self.workers = workers
        self.visited: set[MazeCell] = {w.current_cell for w in self.workers}
        for w in self.workers:
            w.set_MazeConstructor(self)

    def add_worker(self: MazeConstructor, worker: MazeWorker):
        """Add a worker to the constuctor."""
        self.workers.append(worker)
        self.visited |= {worker.current_cell}
        worker.set_MazeConstructor(self)

    def step(self: MazeConstructor) -> None:
        """Run all the MazeWorkers."""
        for w in self.workers:
            if w.alive:
                w.step()

    def run_all(self: MazeConstructor) -> None:
        """Keep running all the MazeWorkers until all finished."""
        while any(w.alive for w in self.workers):
            self.step()


class MazeWorker:
    """Knocks down walls to make a maze, and occasionally spawns."""

    def __init__(
        self: MazeWorker,
        initial_cell: MazeCell,
        spawn_frequency: float = 0,
    ) -> None:
        """Initialize object."""
        self.current_cell: MazeCell = initial_cell
        self.spawn_frequency = spawn_frequency
        self.maze_constructor: Optional[MazeConstructor] = None
        self.path: list[MazeCell] = [initial_cell]
        self.alive = True

    def set_MazeConstructor(
        self: MazeWorker, maze_constructor: MazeConstructor
    ) -> None:
        """Set the current MazeConstructor (so we know where to spawn)."""
        self.maze_constructor = maze_constructor

    @property
    def unvisited_neighbors(self: MazeWorker) -> dict[DIRECTION_TYPE, MazeCell]:
        """Return a dictionary containing the unvisited neighbors."""
        if self.maze_constructor is None:
            raise ValueError("Maze constructor is not set.")
        return {
            k: n
            for k in DIRECTIONS
            if (
                (n := self.current_cell.adjacent[k]) is not None
                and n not in self.maze_constructor.visited
            )
        }

    def move(self: MazeWorker, direction: DIRECTION_TYPE) -> None:
        """Knock down a wall and move."""
        if self.maze_constructor is None:
            raise ValueError("Maze constructor is not set.")
        if (
            n := self.current_cell.adjacent[direction]
        ) is None or n in self.maze_constructor.visited:
            raise ValueError("Cannot move that direction.")
        self.current_cell.remove_wall(direction)
        self.current_cell = n
        self.path.append(n)
        self.maze_constructor.visited |= {n}

    def spawn(self: MazeWorker, direction: DIRECTION_TYPE) -> None:
        """Knock down a wall and spawn."""
        if self.maze_constructor is None:
            raise ValueError("Maze constructor is not set.")
        if (
            n := self.current_cell.adjacent[direction]
        ) is None or n in self.maze_constructor.visited:
            raise ValueError("Cannot move that direction.")
        self.current_cell.remove_wall(direction)
        spawned = MazeWorker(n, self.spawn_frequency)
        self.maze_constructor.add_worker(spawned)

    def step(self: MazeWorker) -> None:
        """Knock down a wall and possibly spawn."""
        if self.maze_constructor is None:
            raise ValueError("Maze constructor is not set.")
        if not self.alive:
            return None
        while self.alive and not (un := self.unvisited_neighbors):
            self.backtrack()
        if self.alive:
            if random() < self.spawn_frequency and len(un.keys()) >= 2:
                places = sample(sorted(un.keys()), 2)
                self.spawn(places[0])
                self.move(places[1])
            else:
                place = choice(list(un.keys()))
                self.move(place)

    def backtrack(self: MazeWorker):
        """Go back to a cell with unvisited neighbors."""
        if self.path:
            self.path.pop()
        if self.path:
            self.current_cell = self.path[-1]
        else:
            self.alive = False

    @property
    def worker_number(self: MazeWorker) -> Optional[int]:
        """Return the worker's index in ``self.maze_constructor.workers``."""
        if self.maze_constructor is not None:
            return self.maze_constructor.workers.index(self)
        else:
            return None


def make_maze(
    rows: int = 10,
    cols: int = 10,
    exits: Optional[Sequence[MazeExit]] = None,
    mazeworker_start: Optional[Position] = None,
    spawn_probability: float = 0,
) -> Maze:
    """Make a maze."""
    if exits is None:
        exits = [MazeExit("north", 0)]
    maze = Maze(rows, cols, exits)
    for row in range(rows):
        for col in range(cols):
            MazeCell(maze, Position(row, col))
    if mazeworker_start is None:
        mazeworker_start = Position(0, 0)
    if isinstance(
        mz := maze.cells[mazeworker_start.row][mazeworker_start.column], MazeCell
    ):
        mw = MazeWorker(mz, 0.05)
    else:
        raise ValueError
    mc = MazeConstructor([mw])
    mc.run_all()
    return maze


if __name__ == "__main__":
    # main program
    maze = make_maze(
        20, 30, (MazeExit("north", 10), MazeExit("east", 18)), Position(10, 15), 0.05
    )
    print(maze.ascii_version("\u2588"))
