"""Solve mazes."""

# MIT License
#
# Copyright (c) 2022 Christopher L. Phan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from collections.abc import Sequence

import emmaze.maze as mz
import emmaze.svgfunctions as svgfunctions
import emmaze.svgmazes as svgmazes


def _make_text_step_range(start: int, end: int, include_end: bool) -> range:
    """Make a range for the integers between ``start`` and ``end``."""
    if start < end:
        return range(start, end + int(include_end))
    elif start > end:
        return range(end + int(not include_end), start + 1)
    else:
        raise ValueError("Positions are the same")


def _text_step(
    start: mz.Position, end: mz.Position, include_end: bool = False
) -> list[tuple[int, int]]:
    """
    Return the characters that represent the steps between two positions.

    The positions must be in the same row or column.
    """
    initial = start.text_location
    final = end.text_location
    if all(a != b for a, b in zip(initial, final)):
        raise ValueError("Not in the same row or same column.")
    if initial[0] == final[0]:  # same column
        rg = _make_text_step_range(initial[1], final[1], include_end)
        return [(initial[0], y) for y in rg]
    else:  # same row
        rg = _make_text_step_range(initial[0], final[0], include_end)
        return [(x, initial[1]) for x in rg]


class MazePath:
    """Represent a path through the maze."""

    def __init__(self: MazePath, path: Sequence[mz.Position]) -> None:
        """Initialize object."""
        if not all(
            pos1.neighbor.with_value(pos2) for pos1, pos2 in zip(path[:-1], path[1:])
        ):
            raise ValueError("Not a valid path.")
        self.path = list(path)

    def svg_path(
        self: MazePath,
        maze: mz.Maze,
        width: float,
        height: float,
        offset: svgmazes.GraphicalCoordinates = svgmazes.COORD_ZERO,
    ) -> svgfunctions.Element:
        """Convert to an SVG path."""
        svg_info = svgmazes.SVGInfo(width, height, maze.rows, maze.cols, offset)
        graphical_path = svgmazes.GraphicalPath(
            [svg_info.cell_position(k) for k in self.path]
        )
        return graphical_path.svg_polyline("red")

    def add_path_to_svg(
        self: MazePath,
        maze: mz.Maze,
        width: float,
        height: float,
        svg: svgfunctions.Element,
        offset: svgmazes.GraphicalCoordinates = svgmazes.COORD_ZERO,
    ) -> None:
        """Add the path to the interior of the element (in-place)."""
        svg.interior.append(self.svg_path(maze, width, height, offset))

    def append_text_solution(
        self: MazePath, maze_str: str, step_char: str = "+"
    ) -> str:
        """Append path to a text version of the maze."""
        text_path: list[tuple[int, int]] = sum(
            (
                _text_step(start, end)
                for start, end in zip(self.path[:-1], self.path[1:])
            ),
            start=[],
        ) + [  # type: ignore
            self.path[-1].text_location
        ]
        text_version = maze_str.split("\n")
        for a, b in text_path:
            text_version[b] = text_version[b][:a] + step_char + text_version[b][a + 1 :]
        return "\n".join(text_version)


class MazeSolver:
    """A worker that solves mazes."""

    def __init__(
        self: MazeSolver,
        maze: mz.Maze,
        start: mz.Position,
        goal: mz.Position,
        initial_orientation: mz.DIRECTION_TYPE = "north",
    ) -> None:
        """Initialize object."""
        self.maze = maze
        self.start = start
        self.goal = goal
        self.visited = [start]
        self.path = [start]
        self.current_position = start
        self.completed: bool = False
        self.active: bool = True
        self.orientation: mz.DIRECTION_TYPE = initial_orientation

    @property
    def unvisited_neighbors(self: MazeSolver) -> mz.DirectionInfo[bool]:
        """Find the unvisited neighbors."""
        cell_walls = self.maze.cell_walls(self.current_position)
        neighbors = self.current_position.neighbor
        return mz.DirectionInfo.from_mapping(
            {
                direction: (
                    not cell_walls[direction]
                    and self.maze.valid_cell(nbr := neighbors[direction])
                    and nbr not in self.visited
                )
                for direction in mz.DIRECTIONS
            },
            False,
        )

    @property
    def direction_order(self: MazeSolver) -> list[mz.DIRECTION_TYPE]:
        """List the directions to try in clockwise order, starting with the current orientation."""
        start_idx = mz.DIRECTIONS.index(self.orientation)
        return [mz.DIRECTIONS[(start_idx - k) % 4] for k in range(4)]

    def step(self: MazeSolver) -> None:
        """Make the next move."""
        self.completed = self.at_destination
        if self.active and not self.completed:
            un = self.unvisited_neighbors
            possible_directions = [
                direction for direction in self.direction_order if un[direction]
            ]
            if not possible_directions:
                self.backtrack()
            else:
                self.move(possible_directions[0])

    def backtrack(self: MazeSolver) -> None:
        """Go back to previously-visited cell."""
        self.path.pop()
        if self.path:
            self.orientation = self.direction_order[2]  # Turn around
            self.current_position = self.path[-1]
        else:
            self.active = False

    @property
    def at_destination(self: MazeSolver) -> bool:
        """Check if the solver is at the destination."""
        return self.current_position == self.goal

    def move(self: MazeSolver, direction: mz.DIRECTION_TYPE) -> None:
        """Move in a direction."""
        if not self.unvisited_neighbors[direction]:
            raise ValueError("Cannot move in that direction.")
        self.orientation = direction
        self.current_position = self.current_position.neighbor[direction]
        self.visited.append(self.current_position)
        self.path.append(self.current_position)

    def run(self: MazeSolver) -> MazePath:
        """Return a path from the start to goal."""
        while self.active and not self.completed:
            self.step()
        if self.completed:
            return MazePath(self.path)
        else:
            raise ValueError("No solution")

    def svg_path(
        self: MazeSolver,
        width: float,
        height: float,
        offset: svgmazes.GraphicalCoordinates = svgmazes.COORD_ZERO,
    ) -> svgfunctions.Element:
        """Return an SVG path of the solution."""
        path: MazePath = self.run()
        return path.svg_path(self.maze, width, height, offset)

    def add_path_to_svg(
        self: MazeSolver,
        width: float,
        height: float,
        svg: svgfunctions.Element,
        offset: svgmazes.GraphicalCoordinates = svgmazes.COORD_ZERO,
    ) -> None:
        """Add the path to the interior of the element (in-place)."""
        path: MazePath = self.run()
        path.add_path_to_svg(self.maze, width, height, svg, offset)

    def append_text_solution(
        self: MazeSolver, maze_str: str, step_char: str = "+"
    ) -> str:
        """Append solution to a text version of the maze."""
        path: MazePath = self.run()
        return path.append_text_solution(maze_str, step_char)
