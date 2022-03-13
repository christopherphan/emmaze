#!/usr/bin/env python3
"""Generate a random maze."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from random import choice, random, sample
from typing import Final, NamedTuple, Optional

DIRECTIONS: Final[list[str]] = ["north", "south", "east", "west"]

logging.basicConfig(filename="maze.log", encoding="utf-8", level=logging.DEBUG)


class Position(NamedTuple):
    """Represent coordinates in the maze."""

    row: int
    column: int


@dataclass
class WallInfo:
    """Record info about the walls."""

    north: bool = True
    south: bool = True
    east: bool = True
    west: bool = True

    def __getitem__(self: WallInfo, key: str) -> bool:
        """Return ``self[key]``."""
        if key == "north":
            return self.north
        if key == "south":
            return self.south
        if key == "east":
            return self.east
        if key == "west":
            return self.west
        return False


@dataclass
class AdjacencyInfo:
    """Record information about neighboring MazeCells."""

    north: Optional[MazeCell]
    south: Optional[MazeCell]
    east: Optional[MazeCell]
    west: Optional[MazeCell]

    def __getitem__(self: AdjacencyInfo, key: str) -> Optional[MazeCell]:
        """Return ``self[key]``."""
        if key == "north":
            return self.north
        if key == "south":
            return self.south
        if key == "east":
            return self.east
        if key == "west":
            return self.west
        return None


class MazeCell:
    """Represent a single cell in the maze."""

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

    def _update_neighbors_log(self: MazeCell, direction: str, other_cell: MazeCell):
        """Make a log entry for updating neighbor info."""
        logging.info(
            f"Updating cell at {self.position} to have a"
            + f" neighbor to the {direction} at {other_cell.position}"
        )

    def update_neighbors(self: MazeCell, direction: Optional[str] = None) -> None:
        """Update neighbor information."""
        if self.maze is not None and self.position is not None:
            row = self.position.row
            column = self.position.column
            if (
                direction in [None, "north"]
                and row > 0
                and (c := self.maze.cells[row - 1][column]) is not None
            ):
                self._update_neighbors_log("north", c)
                self.adjacent.north = c
            if (
                direction in [None, "south"]
                and row < self.maze.rows - 1
                and (c := self.maze.cells[row + 1][column]) is not None
            ):
                self._update_neighbors_log("south", c)
                self.adjacent.south = c
            if (
                direction in [None, "west"]
                and column > 0
                and (c := self.maze.cells[row][column - 1]) is not None
            ):
                self._update_neighbors_log("west", c)
                self.adjacent.west = c
            if (
                direction in [None, "east"]
                and column < self.maze.cols - 1
                and (c := self.maze.cells[row][column + 1]) is not None
            ):
                self._update_neighbors_log("east", c)
                self.adjacent.east = c

    def remove_wall(self: MazeCell, direction: str) -> None:
        """Remove the wall in a given direction."""
        logging.info(f"Removing {direction} wall from cell at {self.position}.")
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
    """Represent an exit of the maze."""

    wall: str
    location: int

    def print_location(self: MazeExit, maze: Maze) -> tuple[int, int]:
        """Give the location coordinates."""
        if self.wall == "north":
            return (2 * self.location + 1, 0)
        if self.wall == "west":
            return (0, 2 * self.location + 1)
        if self.wall == "east":
            return (2 * maze.cols, 2 * self.location + 1)
        if self.wall == "south":
            return (2 * self.location + 1, 2 * maze.rows)
        return (-1, -1)


class Maze:
    """Represent a whole maze."""

    def __init__(self: Maze, rows: int, cols: int, exits: Sequence[MazeExit]) -> None:
        """Initialize a new object."""
        self.cells: list[list[Optional[MazeCell]]] = [
            [None for _2 in range(cols)] for _ in range(rows)
        ]
        self.rows = rows
        self.cols = cols
        self.exits = [a.print_location(self) for a in exits]

    def set_pos(self: Maze, position: Position, cell: MazeCell):
        """Place a MazeCell in a position."""
        row = position.row
        column = position.column
        if row < 0 or row >= self.rows:
            raise ValueError
        if column < 0 or column >= self.cols:
            raise ValueError
        self.cells[row][column] = cell
        logging.info(f"Placed cell at row {row}, column {column}. Cell info: {cell}")
        if row > 0 and (c := self.cells[row - 1][column]) is not None:
            c.update_neighbors("south")
        if row < self.rows - 1 and (c := self.cells[row + 1][column]) is not None:
            c.update_neighbors("north")
        if column > 0 and (c := self.cells[row][column - 1]) is not None:
            c.update_neighbors("east")
        if column < self.cols - 1 and (c := self.cells[row][column + 1]) is not None:
            c.update_neighbors("west")

    def _solid_log(
        self: Maze, x: int, y: int, answer: bool, cell: Optional[MazeCell] = None
    ):
        if cell:
            cell_text = f", which represents the cell at {cell.position}."
        else:
            cell_text = "."
        logging.info(
            f"Determining character at position ({x}, {y})"
            + cell_text
            + f" Answer: {answer}"
        )

    def solid(self: Maze, x: int, y: int) -> bool:
        """
        Return True if location (x, y) is inside a wall.

        Note that the cell in position (0, 0) will take up locations (0, 0) to (3, 3),
        the cell in position (0, 1) will take up locations (3, 0) to (6, 3), etc.
        """
        logging.info(f" Running ``solid({x}, {y})``. Note {x // 2 =} and {y // 2=}.")
        # Edges
        if (x <= 0 or x >= 2 * self.cols) or (y <= 0 or y >= 2 * self.rows):
            self._solid_log(x, y, res := (x, y) not in self.exits)
        elif x % 2 == 0 and y % 2 == 0:
            self._solid_log(x, y, res := True)
        elif x % 2 == 0:
            self._solid_log(
                x,
                y,
                res := (c := self.cells[y // 2][x // 2]) is None or c.walls.east,
                c,
            )
        elif y % 2 == 0:
            self._solid_log(
                x,
                y,
                res := (c := self.cells[y // 2][x // 2]) is None or c.walls.north,
                c,
            )
        else:
            self._solid_log(x, y, res := (c := self.cells[y // 2][x // 2]) is None, c)
        return res

    def __str__(self: Maze) -> str:
        """Return ASCII art version of the maze."""
        return "\n".join(
            "".join("#" if self.solid(x, y) else " " for x in range(2 * self.cols + 1))
            for y in range(2 * self.rows + 1)
        )


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
    def unvisited_neighbors(self: MazeWorker) -> dict[str, MazeCell]:
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

    def move(self: MazeWorker, direction: str) -> None:
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
        logging.info(
            f"MazeWorker {self.maze_constructor.workers.index(self)}"
            + f" moved to {n.position}"
        )

    def spawn(self: MazeWorker, direction: str) -> None:
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
        logging.info(
            f"MazeWorker {self.maze_constructor.workers.index(self)}"
            + f" spawned in {n.position} ({direction})."
        )

    def step(self: MazeWorker) -> None:
        """Knock down a wall and possibly spawn."""
        if self.maze_constructor is None:
            raise ValueError("Maze constructor is not set.")
        if not self.alive:
            return None
        while self.alive and not (un := self.unvisited_neighbors):
            self.backtrack()
        if self.alive:
            logging.info(
                "Unvisted neighbors are: "
                + "".join(
                    str((key, item.position))
                    for key, item in self.unvisited_neighbors.items()
                )
            )
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
            assert self.maze_constructor is not None
            logging.info(
                f"MazeWorker {self.maze_constructor.workers.index(self)}"
                + f" backtracks to {self.current_cell.position}."
            )
        else:
            self.alive = False


def make_maze(
    rows: int,
    cols: int,
    exits: Sequence[MazeExit],
    mazeworker_start: Optional[Position] = None,
    spawn_probability: float = 0,
) -> Maze:
    """Make a maze."""
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
    logging.info("-------------------------- NEW EXECUTION -----------------------")
    maze = make_maze(
        20, 30, (MazeExit("north", 10), MazeExit("east", 18)), Position(10, 15), 0.01
    )
    print(maze)
