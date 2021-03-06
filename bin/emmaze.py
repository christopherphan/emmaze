#!/usr/bin/env python3
"""Command line maze generator."""

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

import argparse
from typing import Final

import emmaze.maze as mz
import emmaze.pngmazes as pngmazes
import emmaze.solutions as solutions
import emmaze.svgmazes as svgmazes
from emmaze._resources import _parse_color
from emmaze.jsonsupport import json_to_maze, maze_to_json

__author__ = "Christopher L. Phan"
__copyright__ = "Copyright \u00A9 2022, Christopher L. Phan"
__license__ = "MIT"
__version__ = "0.0.4"
__date__ = "2022-07-09"
__maintainer__ = "Christopher L. Phan"
__email__ = "cphan@chrisphan.com"


LICENSE: Final[
    str
] = """
MIT License

Copyright (c) 2022 Christopher L. Phan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Define the character for the walls in a text-art maze. \u2588 is a solid block.
WALL_CHARACTER_DICT: Final[dict[str, str]] = {"text": "#", "block": "\u2588"}


def wall_follower_svg(
    maze: mz.Maze,
    cell_size: int = 19,
    wall_size: int = 1,
    cell_color: tuple[int, int, int] = (0xFF, 0xFF, 0xFF),
    wall_color: tuple[int, int, int] = (0, 0, 0),
) -> svgmazes.WallFollowerSVGData:
    """Create a maze and output to SVG using WallFollower approach."""
    wall_thickness = wall_size / (cell_size + wall_size)
    return svgmazes.WallFollowerSVGData(
        maze,
        10 * maze.cols,
        10 * maze.rows,
        svgmazes.GraphicalCoordinates(5, 5),
        wall_thickness,
        cell_color=cell_color,
        wall_color=wall_color,
    )


EXIT_ARGS: Final[dict[str, str]] = {
    "north": "column",
    "east": "row",
    "south": "column",
    "west": "row",
}
OUTPUT_TYPES: Final[list[str]] = ["text", "block", "svg", "json", "png"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate random mazes.")

    parser.add_argument(
        "--import_json",
        "-j",
        type=str,
        metavar="FILE",
        help="import a maze from a JSON file",
    )

    parser.add_argument(
        "--rows",
        "-r",
        metavar="R",
        type=int,
        help="number of rows in the maze",
        default=10,
    )

    parser.add_argument(
        "--cols",
        "-c",
        type=int,
        metavar="C",
        help="number of columns in the maze",
        default=10,
    )

    parser.add_argument(
        "--output-type",
        "-t",
        type=str,
        choices=OUTPUT_TYPES,
        help="type of output to generate",
        default="text",
    )
    parser.add_argument(
        "--output-file",
        "-o",
        metavar="FILE",
        type=str,
        help="file to output to (default is standard output)",
    )

    parser.add_argument(
        "--cell-size",
        "-l",
        metavar="SIZE",
        type=int,
        default=-1,
        help=(
            "dimensions of the maze cells "
            + "(default is 1 for text-art and PNG, 19 for SVG)"
        ),
    )

    parser.add_argument(
        "--wall-size",
        "-w",
        metavar="SIZE",
        type=int,
        default=1,
        help="thickness of the maze walls (default is 1)",
    )

    parser.add_argument(
        "--border-size",
        "-b",
        metavar="SIZE",
        type=int,
        default=0,
        help="thickness of the border (default is 0)",
    )

    parser.add_argument(
        "--cell-color",
        metavar="COLOR",
        type=str,
        default="ffffff",
        help=(
            "color of the cell (for PNG and SVG output) as a hex triplet, e.g."
            + " ffc053. Default is ffffff (white)."
        ),
    )

    parser.add_argument(
        "--wall-color",
        metavar="COLOR",
        type=str,
        default="000000",
        help=(
            "color of the walls (for PNG and SVG output) as a hex triplet, e.g."
            + " ffc053. Default is 000000 (black)."
        ),
    )

    parser.add_argument(
        "--solution-color",
        metavar="COLOR",
        type=str,
        default="ff0000",
        help=(
            "color of the solution (for PNG and SVG output) as a hex triplet, e.g."
            + " ffc053. Default is ff0000 (red)."
        ),
    )

    parser.add_argument(
        "--solutions", "-s", action="store_true", help="include solutions"
    )

    for key, value in EXIT_ARGS.items():
        parser.add_argument(
            f"--{key}-exit",
            metavar=value[0].upper(),
            type=int,
            help=f"place an exit on the {key} wall in {value} {value[0].upper()}",
        )

    parser.add_argument(
        "--copyright",
        action="store_true",
        help="show program's copyright and license information and exit",
    )

    parser.add_argument(
        "--version", action="version", version=f"{parser.prog} version {__version__}"
    )

    args = vars(parser.parse_args())

    if args["copyright"]:
        print(LICENSE)
    else:
        if args["cell_size"] != -1 and args["cell_size"] < 1:
            raise ValueError("Invalid cell size; must be a positive integer.")
        if args["wall_size"] < 1:
            raise ValueError("Invalid wall size; must be a positive integer.")
        if args["border_size"] < 0:
            raise ValueError("Invalid border size; must be a nonnegative integer.")

        if args["output_type"] in ["svg", "png"]:
            cell_color = _parse_color(args["cell_color"])
            wall_color = _parse_color(args["wall_color"])
            solution_color = _parse_color(args["solution_color"])
        maze: mz.Maze
        maze_exits: list[mz.MazeExit]
        solns: list[solutions.MazePath] = []
        if args["import_json"]:
            with open(args["import_json"], "rt") as infile:
                maze, solns = json_to_maze(infile.read())
                maze_exits = maze.exits
        else:
            maze_exits = [
                mz.MazeExit(direction, value)
                for direction in mz.DIRECTIONS
                if (value := args[f"{direction}_exit"]) is not None
            ]

            maze = mz.make_maze(
                args["rows"], args["cols"], maze_exits, spawn_probability=0.1
            )
        maze_text: str = ""
        solution_text: str = ""

        if args["solutions"] and not solns:
            if len(maze_exits) < 2:
                raise ValueError("Need at least two exits.")
            if maze.solutions:
                solns = [solutions.MazePath(k) for k in maze.solutions.values()]
            else:
                maze_solvers = [
                    solutions.MazeSolver(
                        maze, start.cell_position(maze), end.cell_position(maze)
                    )
                    for start, end in zip(maze_exits[:-1], maze_exits[1:])
                ]
                solns = [solver.run() for solver in maze_solvers]

        if args["output_type"] in WALL_CHARACTER_DICT:
            if args["cell_size"] == -1:
                cell_size = 1
            else:
                cell_size = args["cell_size"]
            maze_text = maze.str_version(
                WALL_CHARACTER_DICT[args["output_type"]],
                cell_size,
                args["wall_size"],
                args["border_size"],
            )
            if args["solutions"]:
                solution_text = maze_text
                for mp in solns:
                    solution_text = mp.append_text_solution(
                        solution_text,
                        cell_size=cell_size,
                        wall_size=args["wall_size"],
                        border_size=args["border_size"],
                    )

        elif args["output_type"] == "svg":
            if args["cell_size"] == -1:
                cell_size = 19
            else:
                cell_size = args["cell_size"]
            maze_svg_data = wall_follower_svg(
                maze, cell_size, args["wall_size"], cell_color, wall_color
            )
            maze_text = maze_svg_data.SVG_standalone().output()
            if args["solutions"]:
                solution_text = maze_svg_data.SVG_standalone(
                    [
                        mp.svg_path(
                            maze,
                            maze_svg_data.svg_info.width,
                            maze_svg_data.svg_info.height,
                            maze_svg_data.svg_info.offset,
                            dashpattern="5,5",
                            solution_color=solution_color,
                        )
                        for mp in solns
                    ]
                ).output()

        elif args["output_type"] == "json":
            maze_text = maze_to_json(maze, solns)

        if args["output_file"] is None:
            if args["output_type"] == "png":
                raise ValueError("Filename is required for png output.")
            else:
                print(maze_text)
                if args["solutions"] and solution_text:
                    print("\n\n" + solution_text)
        elif args["output_type"] == "png":
            if args["cell_size"] == -1:
                cell_size = 1
            else:
                cell_size = args["cell_size"]
            maze_text = pngmazes.maze_png(
                maze,
                args["output_file"],
                cell_size,
                args["wall_size"],
                args["border_size"],
                cell_color=cell_color,
                wall_color=wall_color,
            )
            if args["solutions"]:
                pngmazes.soln_png(
                    f"solution_{args['output_file']}",
                    maze_solns=solns,
                    maze_str=maze_text,
                    cell_size=cell_size,
                    wall_size=args["wall_size"],
                    border_size=args["border_size"],
                    cell_color=cell_color,
                    wall_color=wall_color,
                    soln_color=solution_color,
                )
        else:
            with open(args["output_file"], "wt") as outfile:
                outfile.write(maze_text)
            if args["solutions"] and solution_text:
                with open(f"solution_{args['output_file']}", "wt") as outfile:
                    outfile.write(solution_text)
