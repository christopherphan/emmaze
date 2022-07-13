"""Functions to output mazes as pngs."""

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

from collections.abc import Collection
from io import BufferedWriter
from typing import Optional

import png  # type: ignore

import emmaze.maze as mz
import emmaze.solutions as solns


def _make_maze_png(
    str_version: str,
    f: BufferedWriter,
    wall_char: str = "#",
    step_char: str = "+",
    include_solution: bool = False,
    cell_color: tuple[int, int, int] = (0xFF, 0xFF, 0xFF),
    wall_color: tuple[int, int, int] = (0, 0, 0),
    soln_color: tuple[int, int, int] = (0xFF, 0x00, 0x00),
) -> None:
    """
    Write a PNG version of the maze to a file from the string provided by maze.str_version.

    :param str_version: The string version of the maze from maze.str_version
    :type str_version: str

    :param f: A file object in which to write the PNG.
    :type f: io.BufferedWriter

    :param wall_char: The character that represents the walls, default is "#"
    :type wall_char: str

    :param step_char: The character that represents the solution, default is "+"
    :type step_char: str

    :param include_solution: Set to ``True`` if the solution path is to be included
                             (assuming the string has the solution),
                             ``False`` otherwise.
    :type include_solution: bool

    :param cell_color: The color to make the walls in the PNG, as an RGB tuple, defaults
                       to ``(0xff, 0xff, 0xff)``.
    :type cell_color: tuple[int, int, int]

    :param wall_color: The color to make the walls in the PNG, as an RGB tuple, defaults
                       to ``(0, 0, 0)``.
    :type wall_color: tuple[int, int, int]

    :param soln_color: The color to make the solution path in the PNG, as an RGB tuple,
                       defaults to ``(0xff, 0, 0).
    :type soln_color: tuple[int, int, int]
    """
    palette = [
        cell_color,
        soln_color if include_solution else cell_color,
        wall_color,
        cell_color,
    ]
    bitmap = [
        [int(col) for col in row]
        for row in str_version.replace(wall_char, "2")
        .replace(" ", "0")
        .replace(step_char, "1")
        .split("\n")
    ]
    width = len(bitmap[0])
    height = len(bitmap)
    writer = png.Writer(width, height, palette=palette, bitdepth=2)
    writer.write(f, bitmap)


def maze_png(
    maze: mz.Maze,
    filename: str,
    cell_size: int = 1,
    wall_size: int = 1,
    border_size: int = 0,
    cell_color: tuple[int, int, int] = (0xFF, 0xFF, 0xFF),
    wall_color: tuple[int, int, int] = (0, 0, 0),
) -> str:
    """
    Write a PNG version of the maze to a file.

    The function returns a string version of the maze, for possible use in the
    `soln_png` function later.

    :param maze: The maze to draw in the PNG file.
    :type maze: emmaze.maze.Maze

    :param filename: The filename in which to write the PNG
    :type filename: str

    :param cell_size: Width and height of cells (not counting walls) in pixels,
                      defaults to 1.
    :type cell_size: int

    :param wall_size: Thickness of walls in pixels, defaults to 1.
    :type wall_size: int

    :param border_size: Thickness of the border, defaults to 0.
    :type border_size: int

    :param cell_color: The color to make the walls in the PNG, as an RGB tuple, defaults
                       to ``(0xff, 0xff, 0xff)``.
    :type cell_color: tuple[int, int, int]

    :param wall_color: The color to make the walls in the PNG, as an RGB tuple, defaults
                       to ``(0, 0, 0)``.
    :type wall_color: tuple[int, int, int]

    :returns: The text-art version of the maze
    :rtype: str
    """
    maze_str = maze.str_version(
        cell_size=cell_size, wall_size=wall_size, border_size=border_size
    )
    with open(filename, "wb") as outfile:
        _make_maze_png(
            maze_str,
            outfile,
            cell_color=cell_color,
            wall_color=wall_color,
        )
    return maze_str


def soln_png(
    filename: str,
    maze: Optional[mz.Maze] = None,
    maze_solns: Optional[Collection[solns.MazePath]] = None,
    maze_str: Optional[str] = None,
    wall_char: str = "#",
    cell_size: int = 1,
    wall_size: int = 1,
    border_size: int = 0,
    cell_color: tuple[int, int, int] = (0, 0, 0),
    wall_color: tuple[int, int, int] = (0xFF, 0xFF, 0xFF),
    soln_color: tuple[int, int, int] = (0xFF, 0, 0),
) -> None:
    """
    Write a PNG of the maze solution to a file.

    :param filename: The name of the file to which to write the PNG
    :type: str

    :param maze: The maze for which a solution is desired. This may be omitted if the
                 solution and string version of the maze are provided.
    :type Maze: Optional[emmaze.maze.Maze]

    :param maze_solns: The solutions for the maze. If ommitted and ``maze`` is provided,
                       then the solutions will be generated.
    :type maze_solns: Optional[Collection[emmaze.Solutions.MazePath]]

    :param maze_str: A pre-generated string for the maze. If omitted and ``maze`` is
                     provided, then the string will be generated.
    :type maze_str: str

    :param wall_char: The character that represents the walls, default is "#". (Only
                      used if ``maze_str`` is provided, to decode the string, otherwise
                      ignored.)
    :type wall_char: str

    :param cell_size: Width and height of cells (not counting walls) in pixels,
                      defaults to 1.
    :type cell_size: int

    :param wall_size: Thickness of walls in pixels, defaults to 1.
    :type wall_size: int

    :param border_size: Thickness of the border, defaults to 0.
    :type border_size: int

    :param cell_color: The color to make the walls in the PNG, as an RGB tuple, defaults
                       to ``(0xff, 0xff, 0xff)``.
    :type cell_color: tuple[int, int, int]

    :param wall_color: The color to make the walls in the PNG, as an RGB tuple, defaults
                       to ``(0, 0, 0)``.
    :type wall_color: tuple[int, int, int]

    :param soln_color: The color to make the solution path in the PNG, as an RGB tuple,
                       defaults to ``(0xff, 0, 0)``.
    :type soln_color: tuple[int, int, int]
    """
    if maze_str is None:
        if maze is None:
            raise ValueError("Must provide a maze string or maze.")
        else:
            maze_str = maze.str_version(
                cell_size=cell_size, wall_size=wall_size, border_size=border_size
            )
            wall_char = "#"
    if maze_solns is None:
        if maze is None:
            raise ValueError("Must provide a maze solution or maze.")
        else:
            if len(maze.exits) < 2:
                raise ValueError("Need at least two exits.")
            maze_solvers = [
                solns.MazeSolver(
                    maze, start.cell_position(maze), end.cell_position(maze)
                )
                for start, end in zip(maze.exits[:-1], maze.exits[1:])
            ]
            maze_solns = [solver.run() for solver in maze_solvers]
    for mp in maze_solns:
        maze_str = mp.append_text_solution(
            maze_str, cell_size=cell_size, wall_size=wall_size, border_size=border_size
        )
    with open(filename, "wb") as outfile:
        _make_maze_png(
            maze_str,
            outfile,
            wall_char,
            include_solution=True,
            cell_color=cell_color,
            wall_color=wall_color,
            soln_color=soln_color,
        )
