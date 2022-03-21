#!/usr/bin/env python3
"""Command line maze generator."""

from __future__ import annotations

import argparse
from typing import Final

import mazeing.maze as mz
import mazeing.svgfunctions as svgfunctions
import mazeing.svgmazes as svgmazes

__author__ = "Christopher L. Phan"
__copyright__ = "Copyright \u00A9 2022, Christopher L. Phan"
__license__ = "MIT"
__version__ = "development 2022-03-20"
__date__ = "2022-03-20"
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


def wall_follower_svg(maze: mz.Maze) -> str:
    """Create a maze and output to SVG using WallFollower approach."""
    svg_data = svgmazes.WallFollowerSVGData(
        maze, 10 * maze.rows, 10 * maze.cols, svgmazes.GraphicalCoordinates(5, 5)
    )
    # HTML file
    style_info = """
          body {
            background-color: white;
          }

          div.pic {
            width: 95vw;
            margin: 2vw;
          }
    """
    docstring = "<!doctype html>"
    style_elt = svgfunctions.Element("style", interior=[style_info])
    title = svgfunctions.Element("title", interior="MAZE!", separate_interior=False)
    head = svgfunctions.Element("head", interior=[title, style_elt])
    pic = svgfunctions.Element(
        "div", interior=[svg_data.SVG], attributes={"class": "pic"}
    )
    body = svgfunctions.Element("body", interior=[pic])
    html = svgfunctions.Element("html", interior=[head, body])

    return docstring + "\n" + str(html)


EXIT_ARGS: Final[dict[str, str]] = {
    "north": "column",
    "east": "row",
    "south": "column",
    "west": "row",
}
OUTPUT_TYPES: Final[list[str]] = ["text", "block", "svg"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate random mazes.")
    parser.add_argument(
        "--rows",
        "-r",
        nargs="?",
        type=int,
        help="number of rows in the maze",
        default=10,
    )
    parser.add_argument(
        "--cols",
        "-c",
        nargs="?",
        type=int,
        help="number of columns in the maze",
        default=10,
    )
    parser.add_argument(
        "--output_type",
        "-t",
        type=str,
        nargs="?",
        choices=OUTPUT_TYPES,
        help="type of output to generate",
        default="text",
    )
    parser.add_argument(
        "--output_file",
        "-o",
        nargs="?",
        metavar="FILE",
        type=str,
        help="file to output to (default is standard output)",
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
        help="Display copyright and license information, and then exit",
    )

    parser.add_argument(
        "--version", action="version", version=f"{parser.prog} version {__version__}"
    )

    args = vars(parser.parse_args())

    if args["copyright"]:
        print(LICENSE)
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

        if args["output_type"] == "text":
            maze_text = maze.str_version("#")
        elif args["output_type"] == "block":
            maze_text = maze.str_version("\u2588")
        elif args["output_type"] == "svg":
            maze_text = wall_follower_svg(maze)

        if args["output_file"] is None:
            print(maze_text)
        else:
            with open(args["output_file"], "wt") as outfile:
                outfile.write(maze_text)
