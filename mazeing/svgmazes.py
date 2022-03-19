#!/usr/bin/env/python3 python
"""Module for making SVG mazes."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import ceil
from numbers import Real
from typing import Final, Literal, NamedTuple, Optional

import mazeing._svgfunctions as svgfunctions
import mazeing.maze as mz

WALL_THICKNESS_SETTING = Literal["cellsize", "absolute"]

NEXT_DIRECTION: Final[dict[mz.DIRECTION_TYPE, mz.DIRECTION_TYPE]] = {
    direction: mz.DIRECTIONS[(idx + 1) % 4]
    for idx, direction in enumerate(mz.DIRECTIONS)
}

OPPOSITE: Final[dict[mz.DIRECTION_TYPE, mz.DIRECTION_TYPE]] = {
    direction: mz.DIRECTIONS[(idx + 2) % 4]
    for idx, direction in enumerate(mz.DIRECTIONS)
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

WALL_CORNERS: Final[dict[mz.DIRECTION_TYPE, CornerPair]] = {
    ns: (
        (ns, OPPOSITE[NEXT_DIRECTION[ns]]),
        (ns, NEXT_DIRECTION[ns]),
    )
    for ns in mz.NS_DIRECTIONS
} | {
    ew: (
        (OPPOSITE[NEXT_DIRECTION[ew]], ew),
        (NEXT_DIRECTION[ew], ew),
    )
    for ew in mz.EW_DIRECTIONS
}


@dataclass(frozen=True)
class WallFace:
    """Class to represent a face of a wall."""

    maze: mz.Maze
    cell: mz.Position
    direction: mz.DIRECTION_TYPE

    @classmethod
    def from_cell(
        cls: type[WallFace], maze: mz.Maze, cell: mz.Position
    ) -> mz.DirectionInfo[Optional[WallFace]]:
        """Return the walls from a cell position."""
        return mz.DirectionInfo.from_mapping(
            {
                direction: WallFace(maze, cell, direction)
                for direction in maze.cell_walls(cell).with_value(True)
            },
            None,
        )

    @classmethod
    def all_walls(
        cls: type[WallFace], maze: mz.Maze
    ) -> dict[mz.Position, mz.DirectionInfo[Optional[WallFace]]]:
        """Return a dictionary of all walls."""
        return {
            (pos := mz.Position(row, col)): WallFace.from_cell(maze, pos)
            for row in range(-1, maze.rows + 1)
            for col in range(-1, maze.cols + 1)
        }


class WallTracker:
    """Class to keep track of all the walls."""

    def __init__(self: WallTracker, maze: mz.Maze):
        """Initialize object."""
        self.wall_dict = WallFace.all_walls(maze)
        self.track: dict[mz.Position, mz.DirectionInfo[bool]] = {
            position: maze.cell_walls(position) for position in self.wall_dict
        }
        self.maze = maze

    @property
    def number_remaining_walls(self: WallTracker) -> int:
        """Return the number of ``True`` walls."""
        return sum(self.track[position].number for position in self.track)

    def _get_cell_with_wall(self: WallTracker) -> mz.Position:
        """Find a cell whose walls haven't all been toggled off."""
        for position, data in self.track.items():
            if data.any:
                return position
        raise ValueError("No cells with walls.")

    def _basic_get_wall(self: WallTracker) -> WallFace:
        """Return a wall that hasn't been toggled off."""
        position = self._get_cell_with_wall()
        for direction in mz.DIRECTIONS:
            if self.track[position][direction]:
                assert (w := self.wall_dict[position][direction])
                return w
        raise ValueError("No walls left.")

    def get_wall(self: WallTracker) -> Optional[WallFace]:
        """Return a wall that hasn't been toggled off, or ``None`` if none exist."""
        try:
            return self._basic_get_wall()
        except ValueError:
            return None

    def next_wall(self: WallTracker, wall: WallFace) -> WallFace:
        """Return the next wall."""
        # If we rotate the maze mentally so that the wall face we are on points to
        # 12-o'clock, then the potential next walls are pointing at 9-, 12-, 3-, and
        # 6-o'clock.
        #
        #       (c)
        #
        #        ^ ::
        #        | ::
        #        | ::
        #          :: ---> (d)
        #    ::::::::::::
        # (b) <--- ##
        #       (a)## |
        #        ^ ## |
        #        $ ## V
        #        $ ##(e)
        #
        # (a) is the current wall.

        possible_next_walls: list[tuple[mz.Position, mz.DIRECTION_TYPE]] = [
            (wall.cell, NEXT_DIRECTION[wall.direction]),  # (b)
            (wall.cell.neighbor[NEXT_DIRECTION[wall.direction]], wall.direction),  # (c)
            (
                wall.cell.neighbor[NEXT_DIRECTION[wall.direction]].neighbor[
                    wall.direction
                ],
                OPPOSITE[NEXT_DIRECTION[wall.direction]],
            ),  # (d)
            (wall.cell.neighbor[wall.direction], OPPOSITE[wall.direction]),  # (e)
        ]
        for position, direction in possible_next_walls:
            if (
                position in self.wall_dict
                and self.wall_dict[position][direction] is not None
            ):
                return self.wall_dict[position][direction]  # type: ignore
        raise ValueError("No next wall found.")

    def mark_wall(self: WallTracker, wall: WallFace):
        """Mark wall off the track."""
        if wall.cell is None:
            raise ValueError(f"{wall} is not in a cell.")
        self.track[wall.cell][wall.direction] = False


class WallFollowerSVGData:
    """Make SVGs of the maze."""

    def __init__(
        self: WallFollowerSVGData,
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
            (width - 2 * offset.x) / self.maze.cols,
            (height - 2 * offset.y) / self.maze.rows,
        )
        if wall_thickness_units == "cellsize":
            self.wall_thickness = wall_thickness * self.cell_dimension.min()
        else:
            self.wall_thickness = wall_thickness
        self._wall_thickness_gc = GraphicalCoordinates(
            self.wall_thickness, self.wall_thickness
        )

    def cell_coordinates(
        self: WallFollowerSVGData, position: mz.Position
    ) -> GraphicalCoordinates:
        """Return the upper-left corner of the cell."""
        return self.offset + position * self.cell_dimension

    def wall_coordinates_from_position(
        self: WallFollowerSVGData, position: mz.Position, direction: mz.DIRECTION_TYPE
    ) -> OrientedLineSegment:
        """Return coordinates for a wall given position and direction."""
        top_left = self.cell_coordinates(position)
        corners = WALL_CORNERS[direction]
        corner_positions = (CORNER_POS[corners[0]], CORNER_POS[corners[1]])
        return OrientedLineSegment(
            top_left
            + corner_positions[0] * self.cell_dimension
            + THICKNESS_OFFSET_POS[corners[0]] * self._wall_thickness_gc,
            top_left
            + corner_positions[1] * self.cell_dimension
            + THICKNESS_OFFSET_POS[corners[1]] * self._wall_thickness_gc,
        )

    def wall_coordinates(
        self: WallFollowerSVGData, wall: WallFace
    ) -> OrientedLineSegment:
        """Return coordinates for the wall."""
        return self.wall_coordinates_from_position(wall.cell, wall.direction)

    @property
    def graphical_path_components(self: WallFollowerSVGData) -> list[GraphicalPath]:
        """Make ``GraphicalPath`` objects for the wall components."""
        return [
            GraphicalPath.from_OLS_seq([self.wall_coordinates(wall) for wall in cmpt])
            for cmpt in self.wall_components
        ]

    @property
    def walls_SVG(self: WallFollowerSVGData) -> svgfunctions.Element:
        """Return a SVG group of the wall components."""
        return svgfunctions.Element.make_svg_group(
            [gp.svg_polygon for gp in self.graphical_path_components]
        )

    @property
    def SVG(self: WallFollowerSVGData) -> svgfunctions.Element:
        """Return the SVG of the maze."""
        return svgfunctions.Element.make_inline_svg(
            self.width + 2 * self.offset.x,
            self.height + 2 * self.offset.y,
            [self.walls_SVG],
        )


if __name__ == "__main__":
    maze = mz.make_maze(
        100,
        70,
        (mz.MazeExit("north", 50), mz.MazeExit("east", 50)),
        mz.Position(50, 50),
        0.05,
    )
    svg_data = WallFollowerSVGData(maze, 700, 1000, GraphicalCoordinates(50, 50))
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

    with open("maze_output.html", "wt") as outfile:
        outfile.write(docstring + "\n" + str(html))
