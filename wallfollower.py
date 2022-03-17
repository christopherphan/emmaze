#!/usr/bin/env/python3 python
"""Module for making SVG mazes."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import ceil
from numbers import Real
from typing import Final, Literal, NamedTuple, Optional

import maze as mz
import svgfunctions

WALL_THICKNESS_SETTING = Literal["cellsize", "absolute"]

NEXT_DIRECTION: Final[dict[mz.DIRECTION_TYPE, mz.DIRECTION_TYPE]] = {
    "north": "west",
    "west": "south",
    "south": "east",
    "east": "north",
}

POSITION_ADJUST: Final[dict[mz.DIRECTION_TYPE, mz.Position]] = {
    "north": mz.Position(-1, 0),
    "south": mz.Position(1, 0),
    "east": mz.Position(0, 1),
    "west": mz.Position(0, -1),
}

OPPOSITE: Final[dict[mz.DIRECTION_TYPE, mz.DIRECTION_TYPE]] = {
    "north": "south",
    "south": "north",
    "west": "east",
    "east": "west",
}

DIAG_OPPOSITE: Final[dict[mz.DIAG_DIRECTION_TYPE, mz.DIAG_DIRECTION_TYPE]] = {
    (ns, ew): (OPPOSITE[ns], OPPOSITE[ew])
    for ns in mz.NS_DIRECTIONS
    for ew in mz.EW_DIRECTIONS
}


@dataclass(frozen=True)
class GraphicalCoordinates:
    """Represents a pair of graphical coordinates."""

    x: float
    y: float

    def __add__(self: GraphicalCoordinates, other) -> GraphicalCoordinates:
        """Return ``self + other``."""
        if isinstance(other, GraphicalCoordinates):
            return self.__class__(self.x + other.x, self.y + other.y)
        return NotImplemented

    def __mul__(self: GraphicalCoordinates, other) -> GraphicalCoordinates:
        """
        Return ``self * other``.

        Rescale if ``other`` is a number, or pointwise-multiply if ``other`` is
        a ``GraphicalCoordinates`` or ``maze.Position`` object.
        """
        if isinstance(other, Real):
            return self.__class__(self.x * other, self.y * other)
        if isinstance(other, GraphicalCoordinates):
            return self.__class__(self.x * other.x, self.y * other.y)
        if isinstance(other, mz.Position):
            return self.__class__(self.x * other.column, self.y * other.row)
        return NotImplemented

    def __rmul__(self: GraphicalCoordinates, other) -> GraphicalCoordinates:
        """
        Return ``self * other``.

        Rescale if ``other`` is a number, or pointwise-multiply if ``other`` is
        a ``maze.Position`` object.
        """
        if isinstance(other, Real):
            return self.__class__(self.x * other, self.y * other)
        if isinstance(other, mz.Position):
            return self.__class__(self.x * other.column, self.y * other.row)
        return NotImplemented

    def __neg__(self: GraphicalCoordinates) -> GraphicalCoordinates:
        """Return ``-self``."""
        return self.__class__(-self.x, -self.y)

    def __sub__(self: GraphicalCoordinates, other):
        """Return ``self - other``."""
        if isinstance(other, GraphicalCoordinates):
            return self.__class__(self.x - other.x, self.y - other.y)
        return NotImplemented

    @property
    def length_squared(self: GraphicalCoordinates) -> float:
        """Return the square of the length of the object."""
        return self.x**2 + self.y**2

    def min(self: GraphicalCoordinates) -> float:
        """Return the minimum coordinate."""
        return min(self.x, self.y)


COORD_ZERO: Final[GraphicalCoordinates] = GraphicalCoordinates(0, 0)


class OrientedLineSegment(NamedTuple):
    """Represents a line segment."""

    start: GraphicalCoordinates
    end: GraphicalCoordinates

    def as_GraphicalPath(
        self: OrientedLineSegment, tolerance: float = 0.01
    ) -> GraphicalPath:
        """Convert to a ``GraphicalPath`` object."""
        return GraphicalPath([self.start, self.end], tolerance)

    def __add__(self: OrientedLineSegment, other):
        """Return ``self + other``."""
        if isinstance(other, OrientedLineSegment):
            return self.as_GraphicalPath() + other
        return NotImplemented


class GraphicalPath(Sequence):
    """Represents a path of coordinates."""

    def __init__(
        self: GraphicalPath,
        coords: Sequence[GraphicalCoordinates],
        tolerance: float = 0.01,
        check: bool = True,
    ):
        """Initialize object."""
        if not coords:
            raise ValueError("Argument must be non-empty.")
        if not (
            isinstance(coords, Sequence)
            and all(isinstance(c, GraphicalCoordinates) for c in coords)
        ):
            raise TypeError(
                "Argument must be a sequence of GraphicalCoordinates objects."
            )
        self.tolerance = tolerance
        self._tol_sq = tolerance**2
        if check:
            coord_list: list[GraphicalCoordinates] = [coords[0]]
            for coord in coords[1:]:
                if (coord - coord_list[-1]).length_squared > self._tol_sq:
                    coord_list.append(coord)
            if (coord_list[-1] - coord_list[0]).length_squared < self._tol_sq:
                coord_list = coord_list[:-1]
            self._coords = tuple(coord_list)
        else:
            if (coords[-1] - coords[0]).length_squared > self._tol_sq:
                self._coords = tuple(coords)
            else:
                self._coords = tuple(coords[:-1])

    @classmethod
    def from_OLS_seq(
        cls: type[GraphicalPath],
        seq: Sequence[OrientedLineSegment],
        tolerance: float = 0.01,
    ):
        """Convert a sequence of ``OrientedLineSegment`` objects into a ``GraphicalPath``."""
        coord_list = []
        for ls in seq:
            coord_list.append(ls.start)
            coord_list.append(ls.end)
        return cls(coord_list, tolerance)

    def __repr__(self: GraphicalPath) -> str:
        """Return ``repr(self)``."""
        return (
            f"{self.__class__.__name__}("
            + " ,".join(repr(item) for item in self._coords)
            + f", {self.tolerance})"
        )

    def __add__(self: GraphicalPath, other) -> GraphicalPath:
        """Return ``self + other``."""
        if isinstance(other, OrientedLineSegment):
            if (self._coords[-1] - other.start).length_squared < self._tol_sq:
                return self.__class__(
                    self._coords + (other.end,), self.tolerance, False
                )
            else:
                return self.__class__(
                    self._coords + (other.start, other.end), self.tolerance, False
                )
        if isinstance(other, GraphicalPath):
            if (self._coords[-1] - other._coords[0]).length_squared < max(
                self._tol_sq, other._tol_sq
            ):
                return self.__class__(
                    self._coords[:-1] + other._coords,
                    max(self.tolerance, other.tolerance, False),
                )
            return self.__class__(
                self._coords + other._coords, max(self.tolerance, other.tolerance)
            )
        if isinstance(other, GraphicalCoordinates):
            return self.__class__(self._coords + (other,), self.tolerance)
        return NotImplemented

    def __radd__(self: GraphicalPath, other) -> GraphicalPath:
        """Return ``self + other``."""
        if isinstance(other, OrientedLineSegment):
            if (self._coords[0] - other.end).length_squared < self._tol_sq:
                return self.__class__((other.start,) + self._coords, self.tolerance)
            else:
                return self.__class__(
                    (other.start, other.end) + self._coords, self.tolerance
                )
        if isinstance(other, GraphicalCoordinates):
            return self.__class__((other,) + self._coords, self.tolerance)
        return NotImplemented

    def __hash__(self: GraphicalPath) -> int:
        """Return ``hash(self)``."""
        return hash((tuple(self._coords), self.tolerance, self.__class__.__name__))

    @property
    def svg_polygon(self: GraphicalPath) -> svgfunctions.Element:
        """Return an SVG polygon version of the path."""
        return svgfunctions.Element.make_svg_polygon(
            [(pt.x, pt.y) for pt in self._coords], stroke="none", fill="black"
        )

    def svg_list(self: GraphicalPath, prec: Optional[int] = None) -> str:
        """Return a list suitible for use as an SVG polygon points argument."""
        if prec is None:
            if self.tolerance > 1:
                prec = 0
            if self.tolerance <= 0:
                prec = 20
            else:
                prec = min(20, len(str(int(ceil(1 / self.tolerance)))))
        return " ".join(
            f"{round(pt.x, prec), round(pt.y, prec)}" for pt in self._coords
        )

    def __contains__(self: GraphicalPath, value) -> bool:
        """Return ``value in self``."""
        return any(value - coord < self.tolerance for coord in self._coords)

    def __getitem__(self: GraphicalPath, key):
        """Return ``self[value]``."""
        ret = self._coords[key]
        if isinstance(ret, tuple):
            return self.__class__(ret, self.tolerance)
        elif isinstance(ret, GraphicalCoordinates):
            return ret

    def __len__(self: GraphicalPath) -> int:
        """Return the length of the path."""
        return len(self._coords)


@dataclass(frozen=True)
class ExtendedDirection:
    """Class to represent information about direction and being exterior/interior."""

    direction: mz.DIRECTION_TYPE
    exterior: bool = False


ALL_EXTENDED_DIRS: Final[list[ExtendedDirection]] = [
    ExtendedDirection(direction, truth_val)
    for direction in mz.DIRECTIONS
    for truth_val in (True, False)
]

NEXT_EXTENED_DIRS: Final[dict[ExtendedDirection, ExtendedDirection]] = {
    ExtendedDirection(direction, False): ExtendedDirection(
        NEXT_DIRECTION[direction], False
    )
    for direction in mz.DIRECTIONS
} | {
    ExtendedDirection(direction, True): ExtendedDirection(
        OPPOSITE[NEXT_DIRECTION[direction]], True
    )
    for direction in mz.DIRECTIONS
}

CORNER_POS: Final[dict[mz.DIAG_DIRECTION_TYPE, mz.Position]] = {
    (ns, ew): mz.Position(0 if ns == "north" else 1, 1 if ew == "east" else 0)
    for ns in mz.NS_DIRECTIONS
    for ew in mz.EW_DIRECTIONS
}

THICKNESS_OFFSET_POS: Final[dict[mz.DIAG_DIRECTION_TYPE, mz.Position]] = {
    diag_dir: mz.Position(1 - 2 * cp.row, 1 - 2 * cp.column)
    for diag_dir, cp in CORNER_POS.items()
}

CornerPair = tuple[mz.DIAG_DIRECTION_TYPE, mz.DIAG_DIRECTION_TYPE]

WALL_CORNERS: Final[dict[ExtendedDirection, CornerPair]] = (
    {
        ExtendedDirection(ns, False): (
            (ns, OPPOSITE[NEXT_DIRECTION[ns]]),
            (ns, NEXT_DIRECTION[ns]),
        )
        for ns in mz.NS_DIRECTIONS
    }
    | {
        ExtendedDirection(ew, False): (
            (OPPOSITE[NEXT_DIRECTION[ew]], ew),
            (NEXT_DIRECTION[ew], ew),
        )
        for ew in mz.EW_DIRECTIONS
    }
    | {
        ExtendedDirection(ns, True): (
            (ns, NEXT_DIRECTION[ns]),
            (ns, OPPOSITE[NEXT_DIRECTION[ns]]),
        )
        for ns in mz.NS_DIRECTIONS
    }
    | {
        ExtendedDirection(ew, True): (
            (NEXT_DIRECTION[ew], ew),
            (OPPOSITE[NEXT_DIRECTION[ew]], ew),
        )
        for ew in mz.EW_DIRECTIONS
    }
)


@dataclass(frozen=True)
class WallFace:
    """Class to represent a face of a wall."""

    cell: mz.MazeCell
    ext_dir: ExtendedDirection

    @staticmethod
    def _test_for_exit(cell: mz.MazeCell, direction: mz.DIRECTION_TYPE) -> bool:
        """Return ``True`` if there is an exit in that direction."""
        if cell.maze is None or cell.position is None:
            raise ValueError("Cell must be in a maze.")
        if cell.adjacent[direction]:
            return False
        return any(
            ext.wall == direction
            and (
                (
                    direction in ["north", "south"]
                    and ext.location == cell.position.column
                )
                or (direction in ["east", "west"] and ext.location == cell.position.row)
            )
            for ext in cell.maze.exits
        )

    @classmethod
    def from_cell(
        cls: type[WallFace], cell: mz.MazeCell
    ) -> dict[ExtendedDirection, WallFace]:
        """Return a list of walls from the cell."""
        return {
            (ed := ExtendedDirection(direction, False)): cls(cell, ed)
            for direction in mz.DIRECTIONS
            if cell.walls[direction] and not cls._test_for_exit(cell, direction)
        } | {
            (ed := ExtendedDirection(direction, True)): cls(cell, ed)
            for direction in mz.DIRECTIONS
            if cell.adjacent[direction] is None
            and not cls._test_for_exit(cell, direction)
        }

    @classmethod
    def all_walls(
        cls: type[WallFace], maze: mz.Maze
    ) -> dict[mz.Position, dict[ExtendedDirection, WallFace]]:
        """Return a dictionary of all walls."""
        return {
            mz.Position(row_idx, col_idx): WallFace.from_cell(cell)
            for row_idx, row in enumerate(maze.cells)
            for col_idx, cell in enumerate(row)
            if cell is not None
        }


class WallTracker:
    """Class to keep track of all the walls."""

    def __init__(self: WallTracker, maze: mz.Maze):
        """Initialize object."""
        self.wall_dict = WallFace.all_walls(maze)
        self.track: dict[mz.Position, dict[ExtendedDirection, bool]] = {
            position: {ed: (ed in self.wall_dict[position]) for ed in ALL_EXTENDED_DIRS}
            for position in self.wall_dict
        }

    @property
    def number_remaining_walls(self: WallTracker) -> int:
        """Return the number of ``True`` walls."""
        return sum(
            sum(1 if self.track[position][ed] else 0 for ed in ALL_EXTENDED_DIRS)
            for position in self.wall_dict
        )

    def _get_cell_with_wall(self: WallTracker) -> mz.Position:
        """Find a cell whose walls haven't all been toggled off."""
        for position, data in self.track.items():
            if any(data.values()):
                return position
        raise ValueError("No cells with walls.")

    def _basic_get_wall(self: WallTracker) -> WallFace:
        """Return a wall that hasn't been toggled off."""
        position = self._get_cell_with_wall()
        for direction in ALL_EXTENDED_DIRS:
            if self.track[position][direction]:
                return self.wall_dict[position][direction]
        raise ValueError("No walls left.")

    def get_wall(self: WallTracker) -> Optional[WallFace]:
        """Return a wall that hasn't been toggled off, or ``None`` if none exist."""
        try:
            return self._basic_get_wall()
        except ValueError:
            return None

    def next_wall(self: WallTracker, wall: WallFace) -> WallFace:
        """Return the next wall."""
        if wall.cell.maze is None:
            raise ValueError("Cell maze is not set.")
        if (position := wall.cell.position) is None:
            raise ValueError("Wall has no position.")
        direction = wall.ext_dir.direction
        exterior = wall.ext_dir.exterior
        if (nd := NEXT_EXTENED_DIRS[wall.ext_dir]) in (cp := self.wall_dict[position]):
            return cp[nd]
        new_pos = position + POSITION_ADJUST[nd.direction]
        if new_pos in self.wall_dict and wall.ext_dir in (
            pad := self.wall_dict[new_pos]
        ):
            return pad[wall.ext_dir]
        # Flip around
        if not exterior:
            new_pos = position + POSITION_ADJUST[direction]
            # Check to see if we need to flip to the exterior
            if (
                new_pos.row < 0
                or new_pos.row >= wall.cell.maze.rows
                or new_pos.column < 0
                or new_pos.column >= wall.cell.maze.cols
            ):
                return self.wall_dict[position][ExtendedDirection(direction, True)]
            return self.wall_dict[new_pos][
                ExtendedDirection(OPPOSITE[direction], False)
            ]
        return self.wall_dict[position][ExtendedDirection(direction, False)]

    def mark_wall(self: WallTracker, wall: WallFace):
        """Mark wall off the track."""
        if wall.cell is None:
            raise ValueError(f"{wall} is not in a cell.")
        if wall.cell.position is None:
            raise ValueError(f"{wall.cell} has no position.")
        self.track[wall.cell.position][wall.ext_dir] = False


class SVGData:
    """Make SVGs of the maze."""

    def __init__(
        self: SVGData,
        maze: mz.Maze,
        width: float,
        height: float,
        offset: GraphicalCoordinates = COORD_ZERO,
        wall_thickness: float = 0.05,
        wall_thickness_units: WALL_THICKNESS_SETTING = "cellsize",
    ) -> None:
        """Initialize the object."""
        self.maze = maze
        self.width = width
        self.height = height
        self.offset = offset
        tracker = WallTracker(maze)
        wall_components: list[list[WallFace]] = []
        while (w := tracker.get_wall()) is not None:
            current_component: list[WallFace] = [w]
            tracker.mark_wall(w)
            while (w := tracker.next_wall(w)) not in current_component:
                current_component.append(w)
                tracker.mark_wall(w)
            wall_components.append(current_component)
        self.wall_components = wall_components
        self.cell_dimension = GraphicalCoordinates(
            width / self.maze.rows, height / self.maze.cols
        )
        if wall_thickness_units == "cellsize":
            self.wall_thickness = wall_thickness * self.cell_dimension.min()
        else:
            self.wall_thickness = wall_thickness
        self._wall_thickness_gc = GraphicalCoordinates(
            self.wall_thickness, self.wall_thickness
        )

    def cell_coordinates(self: SVGData, position: mz.Position) -> GraphicalCoordinates:
        """Return the upper-left corner of the cell."""
        return self.offset + position * self.cell_dimension

    def wall_coordinates_from_position(
        self: SVGData, position: mz.Position, ext_dir: ExtendedDirection
    ) -> OrientedLineSegment:
        """Return coordinates for a wall given position and direction."""
        if ext_dir.exterior:
            return self.wall_coordinates_from_position(
                position + POSITION_ADJUST[ext_dir.direction],
                ExtendedDirection(OPPOSITE[ext_dir.direction], False),
            )

        top_left = self.cell_coordinates(position)
        corners = WALL_CORNERS[ext_dir]
        corner_positions = (CORNER_POS[corners[0]], CORNER_POS[corners[1]])
        return OrientedLineSegment(
            top_left
            + corner_positions[0] * self.cell_dimension
            + THICKNESS_OFFSET_POS[corners[0]] * self._wall_thickness_gc,
            top_left
            + corner_positions[1] * self.cell_dimension
            + THICKNESS_OFFSET_POS[corners[1]] * self._wall_thickness_gc,
        )

    def wall_coordinates(self: SVGData, wall: WallFace) -> OrientedLineSegment:
        """Return coordinates for the wall."""
        if wall.cell.position is None:
            raise ValueError("Cell position is not defined.")
        return self.wall_coordinates_from_position(wall.cell.position, wall.ext_dir)

    @property
    def graphical_path_components(self: SVGData) -> list[GraphicalPath]:
        """Make ``GraphicalPath`` objects for the wall components."""
        return [
            GraphicalPath.from_OLS_seq([self.wall_coordinates(wall) for wall in cmpt])
            for cmpt in self.wall_components
        ]

    @property
    def walls_SVG(self: SVGData) -> svgfunctions.Element:
        """Return a SVG group of the wall components."""
        return svgfunctions.Element.make_svg_group(
            [gp.svg_polygon for gp in self.graphical_path_components]
        )

    @property
    def SVG(self: SVGData) -> svgfunctions.Element:
        """Return the SVG of the maze."""
        return svgfunctions.Element.make_inline_svg(
            self.width + 2 * self.offset.x,
            self.height + 2 * self.offset.y,
            [self.walls_SVG],
        )


if __name__ == "__main__":
    maze = mz.make_maze(
        10,
        10,
        (mz.MazeExit("north", 1), mz.MazeExit("east", 9)),
        mz.Position(5, 5),
        0.05,
    )
    svg_data = SVGData(maze, 1000, 700, GraphicalCoordinates(100, 100))
    # HTML file
    style_info = """
          body {
            background-color: white;
          }

          div.pic {
            width: 50vw;
            margin: 2vw;
          }
    """
    docstring = "<!doctype html>"
    style_elt = svgfunctions.Element("style", interior=[style_info])
    title = svgfunctions.Element("title", interior="MAZE!", seperate_interior=False)
    head = svgfunctions.Element("head", interior=[title, style_elt])
    pic = svgfunctions.Element(
        "div", interior=[svg_data.SVG], attributes={"class": "pic"}
    )
    body = svgfunctions.Element("body", interior=[pic])
    html = svgfunctions.Element("html", interior=[head, body])

    with open("maze_output.html", "wt") as outfile:
        outfile.write(docstring + "\n" + str(html))
