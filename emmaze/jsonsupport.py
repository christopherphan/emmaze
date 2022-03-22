"""JSON import/export support."""

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

from collections.abc import Sequence
from json import dumps, loads
from typing import Optional

import emmaze.maze as mz
from emmaze.solutions import MazePath


def _WallLine_to_int(wall_line: mz.WallLine[bool]) -> int:
    """
    Convert a ``maze.WallLine[bool]`` object to an integer.

    The integer will be a binary position of the status of each wall location.
    For example, ``maze.WallLine("EW", 3, {0: True, 1: True, 2: False, 3: True})``
    will be represented by ``0b1101``, which is ``13``.


    >>> wl = maze.WallLine("EW", 3, {0: True, 1: True, 2: False, 3: True})
    >>> _WallLine_to_int(wl)
    13
    """
    max_loc = max(wall_line.wallstatus.keys())
    return sum(
        2 ** (max_loc - key)
        for key in wall_line.wallstatus
        if wall_line.wallstatus[key]
    )


def _maze_to_dict(maze: mz.Maze) -> dict:
    """Convert a maze into a dict."""
    wall_lines: list[mz.WallLine[bool]] = maze.wall_data
    walls: dict[str, dict[int, mz.WallLine[bool]]] = {
        orientation: {
            wl.position: wl for wl in wall_lines if wl.orientation == orientation
        }
        for orientation in ["NS", "EW"]
    }
    outdict = {
        "maze": {
            "rows": maze.rows,
            "cols": maze.cols,
            "row_walls": [
                _WallLine_to_int(walls["EW"][k]) for k in range(maze.rows + 1)
            ],
            "col_walls": [
                _WallLine_to_int(walls["NS"][k]) for k in range(maze.cols + 1)
            ],
        }
    }
    if maze.exits:
        outdict["maze"]["exits"] = [[ex.wall, ex.location] for ex in maze.exits]
    return outdict


def maze_to_json(maze: mz.Maze, solutions: Optional[Sequence[MazePath]] = None) -> str:
    """Convert a maze to a JSON (in string form)."""
    outdict = _maze_to_dict(maze)
    if solutions:
        outdict |= {
            "solutions": [
                [[pos.row, pos.column] for pos in mpath.path]
                for mpath in list(solutions)
            ]
        }
    return dumps(outdict)


def _int_to_wallstatus(value: int, length: int) -> dict[int, bool]:
    """Convert a value back into a ``maze.WallLine[bool]`` object."""
    return {k: bool((value >> (length - k - 1)) % 2) for k in range(length)}


def json_to_maze(json_text: str) -> tuple[mz.Maze, list[MazePath]]:
    """Convert a JSON string to a ``maze.Maze``, and if solutions are provided, corresponding ``solutions.MazePath`` objects."""
    data = loads(json_text)
    mazedata = data["maze"]
    exits: list[mz.MazeExit] = [
        mz.MazeExit(item[0], item[1]) for item in mazedata.get("exits", [])
    ]
    maze = mz.Maze(mazedata["rows"], mazedata["cols"], exits)
    for key, orientation in zip(["row_walls", "col_walls"], ["EW", "NS"]):
        for idx, value in enumerate(mazedata[key]):
            wallstatus = _int_to_wallstatus(value, mazedata[key[:3] + "s"] + 1)
            for j, val in wallstatus.items():
                if not val:
                    maze.remove_wall(
                        orientation,  # type: ignore
                        idx if key[:3] == "row" else j,
                        j if key[:3] == "row" else idx,
                    )
        raw_solutions: list[list[list[int]]] = data.get("solutions", [])
    solns = [
        MazePath([mz.Position(item[0], item[1]) for item in path])
        for path in raw_solutions
    ]
    return maze, solns
