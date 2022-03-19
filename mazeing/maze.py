#!/usr/bin/env python3
"""Classes for generating and displaying random mazes."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from random import choice, random, sample
from typing import Final, Generic, Literal, Optional, TypeAlias, TypeVar

T = TypeVar("T")

DIRECTION_TYPE: TypeAlias = Literal["north", "south", "east", "west"]
NS_DIRECTIONS: Final[list[DIRECTION_TYPE]] = ["north", "south"]
EW_DIRECTIONS: Final[list[DIRECTION_TYPE]] = ["east", "west"]
DIRECTIONS: Final[list[DIRECTION_TYPE]] = ["north", "west", "south", "east"]
DIAG_DIRECTION_TYPE = tuple[DIRECTION_TYPE, DIRECTION_TYPE]
DIAG_DIRECTIONS: Final[list[DIAG_DIRECTION_TYPE]] = [
    (ns, ew) for ns in NS_DIRECTIONS for ew in EW_DIRECTIONS
]


@dataclass(frozen=True)
class Position:
    """
    Represent the location of a cell in the maze.

    :param row: The row of the cell
    :type row: int

    :param column: The column of the cell
    :type column: int

    Each paramater is an instance variable.
    """

    row: int
    column: int

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

    @property
    def neighbor(self: Position) -> DirectionInfo[Position]:
        """Give the positions of neighboring cells."""
        return DirectionInfo(
            north=self + Position(-1, 0),
            south=self + Position(1, 0),
            east=self + Position(0, 1),
            west=self + Position(0, -1),
        )

    def convert_wall_coordinates(
        self: Position, direction: DIRECTION_TYPE
    ) -> tuple[Literal["NS", "EW"], int, int]:
        """Determine the orientation, row, and column of a wall given the cell position and direction."""
        if direction == "north":
            return "EW", self.row, self.column
        if direction == "south":
            return "EW", self.row + 1, self.column
        if direction == "east":
            return "NS", self.row, self.column + 1
        if direction == "west":
            return "NS", self.row, self.column


@dataclass
class DirectionInfo(Generic[T]):
    """
    Keep track of information about directions.

    This is a ``dataclass`` that provides data for each of the four cardinal
    directions.

    :param north: The status of the north wall.
    :type north: T

    :param south: The status of the south wall.
    :type south: T

    :param east: The status of the east wall.
    :type east: T

    :param west: The status of the west wall.
    :type west: T

    Each parameter is an instance variable.

    In addition to, e.g., ``self.west``, the syntax ``self["west"]`` can be used
    to access and set an instance variable.
    """

    north: T
    south: T
    east: T
    west: T

    def __getitem__(self: DirectionInfo, key: DIRECTION_TYPE) -> T:
        """Return ``self[key]``, which is an alias for ``self.key``."""
        if key == "north":
            return self.north
        if key == "south":
            return self.south
        if key == "east":
            return self.east
        if key == "west":
            return self.west

    def __setitem__(self: DirectionInfo, key: DIRECTION_TYPE, value: T) -> None:
        """Allow ``self[key]``to be an alias for ``self.key``."""
        if key == "north":
            self.north = value
        if key == "south":
            self.south = value
        if key == "east":
            self.east = value
        if key == "west":
            self.west = value

    def copy(self: DirectionInfo) -> DirectionInfo:
        """Return a copy of the object."""
        return self.__class__(self.north, self.south, self.east, self.west)

    @property
    def any(self: DirectionInfo) -> bool:
        """Return ``True`` if any directions are truthy."""
        return any(self[direction] for direction in DIRECTIONS)

    @property
    def number(self: DirectionInfo) -> int:
        """Return the number of directions which are truthy."""
        return sum(1 if self[direction] else 0 for direction in DIRECTIONS)

    @classmethod
    def from_mapping(
        cls: type[DirectionInfo], mapping: Mapping[DIRECTION_TYPE, T], default: T
    ) -> DirectionInfo[T]:
        """Construct an object from a mapping."""
        return DirectionInfo(
            north=mapping["north"] if "north" in mapping else default,
            south=mapping["south"] if "south" in mapping else default,
            east=mapping["east"] if "east" in mapping else default,
            west=mapping["west"] if "west" in mapping else default,
        )

    def with_value(self: DirectionInfo, value: T) -> set[DIRECTION_TYPE]:
        """Return all the directions set to ``value``."""
        return {direction for direction in DIRECTIONS if self[direction] == value}


@dataclass
class MazeExit:
    """
    Represent an exit of the maze.

    :param wall: The side of the maze with contains the exit
    :type wall: DIRECTION_TYPE

    :param location: The row/column of the exit
    :type location: int

    Each parameter is also an instance variable.
    """

    wall: DIRECTION_TYPE
    location: int

    def string_output_location(self: MazeExit, maze: Maze) -> tuple[int, int]:
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


class WallLine(Generic[T]):
    """
    Represent a row or column of walls.

    The cell at ``Position(row, col)`` will have north-south walls in columns ``col``
    and ``col + 1`` and east-west walls in rows ``row`` and ``row + 1``.

    :param orientation: The orientation of the walls: ``NS`` for north-south, and ``EW``
        for east-west.
    :type orientation: Literal["NS", "EW"]

    :param position: The row (if ``orientation=="EW"``) or column
        (if ``orientation=="NS"``) of walls represented
    :type position: int

    :param wallstatus: The status of each wall
    :type wallstatus: Mapping[int, T]

    Each paramater is also an instance variable, except that ``wallstatus`` is changed:

    :ivar wallstatus: The status of each wall
    :vartype wallstatus: dict[int, T]
    """

    def __init__(
        self: WallLine[T],
        orientation: Literal["NS", "EW"],
        position: int,
        wallstatus: Mapping[int, T],
    ) -> None:
        """Initialize an object."""
        self.orientation = orientation
        self.position = position
        self.wallstatus = dict(wallstatus)

    @classmethod
    def from_callable(
        cls: type[WallLine],
        orientation: Literal["NS", "EW"],
        position: int,
        line_length: int,
        wallstatus: Callable[[int], T],
    ) -> WallLine[T]:
        """
        Create a ``WallLine`` object from a callable.

        The parameter ``wallstatus`` will be evaluated for each integer between ``0``
        and ``line_length`` (inclusive).

        :param orientation: The orientation of the walls: ``NS`` for north-south, and ``EW``
            for east-west.
        :type orientation: Literal["NS", "EW"]

        :param position: The row (if ``orientation=="EW"``) or column
            (if ``orientation=="NS"``) of walls represented
        :type position: int

        :param wallstatus: A callable returning status of each wall
        :type wallstatus: Callable[[int], T]

        :returns: A ``WallLine`` object created from the callable
        :rtype: WallLine[T]
        """
        return cls(
            orientation, position, {k: wallstatus(k) for k in range(line_length)}
        )

    def num_walls(self: WallLine[T], value: T) -> int:
        """
        Return the number of walls with a certain value stored.

        :param value: The value for which to test
        :type value: T

        :returns: The number of walls having the value
        :rtype: int
        """
        return list(self.wallstatus.values()).count(value)


class Maze:
    """
    Represent a whole maze.

    A maze comprises a rectangular array of cells.

    :param rows: The number of rows of cells in the maze.
    :type rows: int

    :param cols: The number of columns of cells in the maze.
    :type cols: int

    :param exits: The exits of the maze.
    :type exits: Sequence[MazeExit]

    Each of these parameters is an instance variable, except that ``exits`` is modified.

    :ivar exits: The exists of the maze.
    :vartype exits: list[MazeExit]
    """

    def __init__(self: Maze, rows: int, cols: int, exits: Sequence[MazeExit]) -> None:
        """Initialize a new object."""
        self.rows = rows
        self.cols = cols
        self.exits: list[MazeExit] = list(exits)
        self._ns_walls: list[WallLine[bool]] = [
            WallLine("NS", col, {row: True for row in range(rows + 1)})
            for col in range(cols + 1)
        ]
        self._ew_walls: list[WallLine[bool]] = [
            WallLine("EW", row, {col: True for col in range(cols + 1)})
            for row in range(rows + 1)
        ]
        for exit in self.exits:
            cell_pos = exit.cell_position(self)
            if exit.wall in NS_DIRECTIONS:
                row_offset = 0 if exit.wall == "north" else 1
                self._ew_walls[cell_pos.row + row_offset].wallstatus[
                    cell_pos.column
                ] = False
            else:
                col_offset = 0 if exit.wall == "west" else 1
                self._ns_walls[cell_pos.column + col_offset].wallstatus[
                    cell_pos.row
                ] = False

    def valid_cell(self: Maze, position: Position) -> bool:
        """Return ``True`` if ``position`` is the location of a cell."""
        return (
            position.row >= 0
            and position.row < self.rows
            and position.column >= 0
            and position.column < self.cols
        )

    def remove_wall(
        self: Maze, orientation: Literal["NS", "EW"], row: int, col: int
    ) -> None:
        """Remove a wall."""
        if orientation == "NS":
            self._ns_walls[col].wallstatus[row] = False
        if orientation == "EW":
            self._ew_walls[row].wallstatus[col] = False

    def remove_wall_cell_direction(
        self: Maze, cell_position: Position, direction: DIRECTION_TYPE
    ) -> None:
        """Remove a wall given by cell and direction."""
        self.remove_wall(*cell_position.convert_wall_coordinates(direction))

    @property
    def num_walls(self: Maze) -> int:
        """Return the number of wall segments in the maze."""
        return sum(
            wall_line.num_walls(True) for wall_line in self._ns_walls + self._ew_walls
        )

    def retrieve_wall(
        self: Maze, orientation: Literal["NS", "EW"], row: int, col: int
    ) -> bool:
        """Return ``True`` if the wall exists."""
        if orientation == "NS":
            return self._ns_walls[col].wallstatus[row]
        if orientation == "EW":
            return self._ew_walls[row].wallstatus[col]

    def cell_walls(self: Maze, position: Position) -> DirectionInfo[bool]:
        """Return information about the walls of the cell at position."""
        return DirectionInfo.from_mapping(
            {
                direction: self.retrieve_wall(*info)
                for direction in DIRECTIONS
                if (  # Check that wall has valid coordinates
                    (info := position.convert_wall_coordinates(direction))[1] >= 0
                    and (
                        info[1] < self.rows
                        or (info[1] == self.rows and info[0] == "EW")
                    )
                    and (
                        info[2] >= 0
                        and (
                            info[2] < self.cols
                            or (info[2] == self.cols and info[0] == "NS")
                        )
                    )
                )
            },
            False,
        )

    def __repr__(self: Maze) -> str:
        """Return ``repr(self)``."""
        return (
            f"<{self.rows} x {self.cols} maze with {len(self.exits)} exits and "
            + f"{self.num_walls} wall segments>"
        )

    def solid(self: Maze, x: int, y: int) -> bool:
        """
        Return ``True`` if location (``x``, ``y``) in an ASCII-art version of the maze is inside a wall.

        Note that the cell in position (0, 0) will take up locations (0, 0) to (3, 3),
        the cell in position (0, 1) will take up locations (3, 0) to (6, 3), etc.
        """
        if (x < 0 or x > 2 * self.cols) or (y < 0 or y > 2 * self.rows):
            return False
        if x % 2 == 0 and y % 2 == 0:
            return True
        if x % 2 == 0:  # NS wall
            return self.retrieve_wall("NS", y // 2, x // 2)
        if y % 2 == 0:
            return self.retrieve_wall("EW", y // 2, x // 2)
        return False

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
    """
    A class that makes a maze.

    An object in this class can be comprise a list of `MazeWorker`` objects (which
    go around the maze and knock down walls) and a set of ``Position`` objects that
    are used to keep track of which cells have been visited by some ``MazeWorker``
    already.

    :param workers: the ``MazeWorker`` object that the constructor will have at the
        first execution. Must be nonempty.
    :type workers: Sequence[MazeWorker]

    :ivar workers: the current list of ``MazeWorker`` objects
    :vartype workers: list[MazeWorker]

    :ivar visited: The current list of cell positions that have been visited by a
        ``MazeWorker``.
    :vartype visited: set[Position]
    """

    def __init__(self: MazeConstructor, workers: Sequence[MazeWorker]):
        """Initialize object."""
        if not workers:
            raise ValueError("Worker sequence must be nonempty.")
        self.maze = workers[0].maze
        if any(w.maze != self.maze for w in workers[1:]):
            raise ValueError("All workers must be in the same maze.")
        self.workers = list(workers)
        self.visited: set[Position] = {w.current_cell for w in self.workers}
        for w in self.workers:
            w.set_MazeConstructor(self)

    def add_worker(self: MazeConstructor, worker: MazeWorker):
        """Add a worker to the constuctor."""
        if worker.maze != self.maze:
            raise ValueError("All workers must be in the same maze.")
        self.workers.append(worker)
        self.visited |= {worker.current_cell}
        worker.set_MazeConstructor(self)

    def step(self: MazeConstructor) -> None:
        """Run all the (unretired) MazeWorkers for one step."""
        for w in self.workers:
            if w.alive:
                w.step()

    def run_all(self: MazeConstructor) -> None:
        """Keep running all the MazeWorkers until all retired."""
        while any(w.alive for w in self.workers):
            self.step()


class MazeWorker:
    """
    Objects that build the maze by knocking down walls.

    Each turn, each ``MazeWorker`` will possibly spawn, knock down a wall, and move
    into that adjacent cell. If there are no unvisted adjacent cells, then the
    ``MazeWorker`` backtracks. (The current path of the object is given by the
    ``path`` instance variable.) Once no unvisited cells are reachable by the
    ``MazeWorker``, the object "retires" and becomes inactive.

    :param maze: The maze that the ``MazeWorker`` will work on.
    :type maze: Maze

    :param initial_cell: the initial position of the ``MazeWorker``.
    :type initial_cell: Position

    :param spawn_probability: the probability each step that the  ``MazeWorker`` spawns,
         if spawning is possible. Defaults to 0.
    :type spawn_probability: float

    The parameters ``maze`` and ``spawn_probability`` are instance variables as well as:

    :ivar current_cell: The object's position (in terms of cell) in the maze.
    :vartype current_cell: Position

    :ivar maze_constructor: The ``MazeConstructor`` object to which this object is
        assigned. Initially set to ``None``, the ``set_MazeConstructor`` method is used
        to change this variable.
    :vartype maze_constructor:  Optional[MazeConstructor]

    :ivar path: A stack representing the previous and current position of the object.
        If the object backtracks, then the path will be shortened.
    :vartype path: list[Position]

    :ivar alive: Set to ``True`` if the object is still alive. Once there are no more
        possible cells to visit, the object will "retire" and ``alive`` will be set to
        false.
    """

    def __init__(
        self: MazeWorker,
        maze: Maze,
        initial_cell: Position,
        spawn_probability: float = 0,
    ) -> None:
        """Initialize object."""
        self.maze = maze
        self.current_cell = initial_cell
        self.spawn_probability = spawn_probability
        self.maze_constructor: Optional[MazeConstructor] = None
        self.path: list[Position] = [initial_cell]
        self.alive = True

    def set_MazeConstructor(
        self: MazeWorker, maze_constructor: MazeConstructor
    ) -> None:
        """
        Set the ``maze_constructor`` attribute.

        A ``MazeWorker`` object must be assigned to a ``MazeConstructor`` to run.
        """
        self.maze_constructor = maze_constructor

    @property
    def unvisited_neighbors(self: MazeWorker) -> DirectionInfo[bool]:
        """Return information about which neighbors have not be visisted."""
        if self.maze_constructor is None:
            raise ValueError("Maze constructor is not set.")
        else:
            return DirectionInfo.from_mapping(
                {
                    direction: self.maze.valid_cell(
                        nb := self.current_cell.neighbor[direction]
                    )
                    and nb not in self.maze_constructor.visited
                    for direction in DIRECTIONS
                },
                False,
            )

    def remove_wall(self: MazeWorker, direction: DIRECTION_TYPE) -> None:
        """Knock down a wall."""
        self.maze.remove_wall_cell_direction(self.current_cell, direction)

    def move(self: MazeWorker, direction: DIRECTION_TYPE) -> None:
        """Knock down a wall and move."""
        if self.maze_constructor is None:
            raise ValueError("Maze constructor is not set.")
        if not self.unvisited_neighbors[direction]:
            raise ValueError("Cannot move that direction.")
        self.remove_wall(direction)
        self.current_cell = self.current_cell.neighbor[direction]
        self.path.append(self.current_cell)
        self.maze_constructor.visited |= {self.current_cell}

    def spawn(self: MazeWorker, direction: DIRECTION_TYPE) -> None:
        """Knock down a wall and spawn."""
        if self.maze_constructor is None:
            raise ValueError("Maze constructor is not set.")
        if not self.unvisited_neighbors[direction]:
            raise ValueError("Cannot move that direction.")
        self.remove_wall(direction)
        spawned = MazeWorker(
            self.maze, self.current_cell.neighbor[direction], self.spawn_probability
        )
        self.maze_constructor.add_worker(spawned)

    def step(self: MazeWorker) -> None:
        """Knock down a wall and possibly spawn."""
        if self.maze_constructor is None:
            raise ValueError("Maze constructor is not set.")
        if not self.alive:
            return None
        while self.alive and not (un := self.unvisited_neighbors).any:
            self.backtrack()
        if self.alive:
            if random() < self.spawn_probability and un.number >= 2:
                places = sample(list(un.with_value(True)), 2)
                self.spawn(places[0])
                self.move(places[1])
            else:
                place = choice(list(un.with_value(True)))
                self.move(place)

    def backtrack(self: MazeWorker) -> None:
        """
        Go back to a cell with unvisited neighbors.

        If this is not possible, then retire.
        """
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
    """
    Make a random maze.

    Create a maze with one initial ``MazeWorker``.

    :param rows: The number of rows of cells
    :type rows: int

    :param cols: The number of columns of cells
    :type cols: int

    :param exits: The exits of the maze. Defaults to ``[MazeExit("north", 0)]``.
    :type exits: Sequence[MazeExit]

    :param mazeworker_start: The position of the first ``MazeWorker``. Defaults to
        ``Position(0, 0)``.
    :type mazeworker_start: Position

    :param spawn_probability: The probability that a ``MazeWorker`` will spawn when
        it is possible. Defaults to ``0``.
    :type spawn_probability: float

    :returns: A random maze.
    :type: Maze
    """
    if exits is None:
        exits = [MazeExit("north", 0)]
    maze = Maze(rows, cols, exits)
    if mazeworker_start is None:
        mazeworker_start = Position(0, 0)
    mw = MazeWorker(maze, mazeworker_start, spawn_probability)
    mc = MazeConstructor([mw])
    mc.run_all()
    return maze
