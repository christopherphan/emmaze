"""Command line maze generator."""

from __future__ import annotations

import maze as mz


def main():
    """Create a maze and print it on the screen."""
    maze = mz.make_maze(
        20,
        30,
        (mz.MazeExit("north", 10), mz.MazeExit("east", 18)),
        mz.Position(10, 15),
        0.05,
    )
    print(maze.ascii_version("\u2588"))


if __name__ == "__main__":
    main()
