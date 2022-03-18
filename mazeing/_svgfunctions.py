"""Helper functions for making SVG files."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from textwrap import indent
from typing import Literal, Optional


class Element:
    """
    Represents an HTML/XML element.

    :param name: The name of the element
    :type name: str

    :param attributes: The attributes of the element. Defaults to ``dict()``.
    :type attributes: Optional[Mapping[str, str]]

    :param interior: The contents of the element. Defaults to ``[]``.
    :type interior: Optional[Sequence[str | Element]]

    :param self_closing: When set to ``True``, the element will be self closing
        (e.g. ``<br />``). Defaults to ``False``.
    :type self_closing: bool

    :param separate_interior: When set to ``True``, place the interior on separate lines
        in the output. Defaults to ``True``.
    :type separate_interior: bool
    `
    """

    def __init__(
        self: Element,
        name: str,
        attributes: Optional[Mapping[str, str]] = None,
        interior: Optional[Sequence[str | Element]] = None,
        self_closing: bool = False,
        separate_interior: bool = True,
    ) -> None:
        """Initialize object."""
        self.name = name
        self.attributes = dict(attributes) if attributes else dict()
        self.interior = interior if interior else []
        self.self_closing = self_closing
        self.separate_interior = separate_interior

    def output(
        self: Element, indentation: int = 0, additional_indentation: int = 2
    ) -> str:
        """
        Generate the HTML/XML of the element.

        :param indentation: The number of spaces to indent the element. Defaults
            to 0.
        :type indentation: int

        :param additional_indentation: The number of spaces to indent elements in the
            interior. Defaults to 2.
        :type additional_indentation: int

        :returns: The HTML/XML of the element.
        :rtype: str
        """
        out_str = f"<{self.name} " + " ".join(
            [f'{key}="{self.attributes[key]}" ' for key in self.attributes]
        )
        if not self.self_closing:
            out_str += ">"
            for item in self.interior:
                if isinstance(item, Element):
                    out_str += "\n" + indent(
                        item.output(
                            0,
                            additional_indentation,
                        ),
                        " " * additional_indentation,
                    )
                elif isinstance(item, str):
                    if self.separate_interior:
                        out_str += "\n" + indent(item, " " * additional_indentation)
                    else:
                        out_str += item
            if self.separate_interior:
                out_str += "\n"
            out_str += f"</{self.name}>"
        else:
            out_str += "/>"
        return indent(out_str, " " * indentation)

    def __str__(self: Element) -> str:
        """
        Return ``str(self)``.

        Equivalaent to ``self.output()``.

        """
        return self.output()

    @classmethod
    def make_svg_group(
        cls: type[Element],
        objects: Sequence[Element],
    ) -> Element:
        """
        Make an SVG group.

        Wrapps the ``Element`` objects in ``objects`` in a ``<g>`` SVG element.

        :param objects: the elements to include in the group.
        :type objects: Sequence[Element]

        :returns: A ``g`` element with the ``objects`` as the interior.
        :rtype: Element
        """
        return cls("g", interior=objects)

    @classmethod
    def _make_svg_polything(
        cls: type[Element],
        coords: Sequence[tuple[int | float, int | float]],
        type_: Literal["polyline", "polygon"],
        stroke: str = "none",
        fill: str = "none",
        id_: Optional[str] = None,
        attributes: Optional[Mapping[str, str]] = None,
    ) -> Element:
        """
        Create an SVG polygon or polyline.

        :param coords: Coordinates for the polygon/line.
        :type coords: Sequence[tuple[int | float, int | float]]

        :param type_: Element to create (``polygon`` or ``polyline``)
        :type type_: Literal["polyline", "polygon"]

        :param stroke: Value of the SVG ``stroke`` attribute. Defaults to ``"none"``.
        :type stroke: str

        :param fill: Value of the SVG ``fill`` attribute. Defaults to ``"none"``.
        :type fill: str

        :param id_: Value of the SVG ``id`` attribute. If omitted, the attribute is
            not provided.
        :type id_: Optional[str]

        :param attributes: Other attributes to be included in the element. Defaults to
            ``dict()``.
        :type attributes: Optional[Mapping[str, str]]

        :returns: An SVG ``polygon`` or ``polyline`` element.
        :rtype: Element
        """
        attribs = (
            (
                {
                    "points": " ".join([f"{item[0]},{item[1]}" for item in coords]),
                    "stroke": stroke,
                    "fill": fill,
                }
            )
            | ({"id": id_} if id_ else {})
            | (attributes if attributes else {})
        )
        return cls(type_, attribs, self_closing=True)

    @classmethod
    def make_svg_polyline(
        cls: type[Element],
        coords: Sequence[tuple[int | float, int | float]],
        stroke: str = "none",
        fill: str = "none",
        id_: Optional[str] = None,
        attributes: Optional[Mapping[str, str]] = None,
    ) -> Element:
        """
        Create an SVG ``polyline`` element.

        :param coords: Coordinates for the polyline.
        :type coords: Sequence[tuple[int | float, int | float]]

        :param stroke: Value of the SVG ``stroke`` attribute. Defaults to ``"none"``.
        :type stroke: str

        :param fill: Value of the SVG ``fill`` attribute. Defaults to ``"none"``.
        :type fill: str

        :param id_: Value of the SVG ``id`` attribute. If omitted, the attribute is
            not provided.
        :type id_: Optional[str]

        :param attributes: Other attributes to be included in the element. Defaults to
            ``dict()``.
        :type attributes: Optional[Mapping[str, str]]

        :returns: An SVG ``polyline`` element.
        :rtype: Element
        """
        return cls._make_svg_polything(
            coords, "polyline", stroke, fill, id_, attributes
        )

    @classmethod
    def make_svg_polygon(
        cls: type[Element],
        coords: Sequence[tuple[int | float, int | float]],
        stroke: str = "none",
        fill: str = "none",
        id_: Optional[str] = None,
        attributes: Optional[dict[str, str]] = None,
    ) -> Element:
        """
        Create an SVG ``polygon`` element.

        :param coords: Coordinates for the polygon.
        :type coords: Sequence[tuple[int | float, int | float]]

        :param stroke: Value of the SVG ``stroke`` attribute. Defaults to ``"none"``.
        :type stroke: str

        :param fill: Value of the SVG ``fill`` attribute. Defaults to ``"none"``.
        :type fill: str

        :param id_: Value of the SVG ``id`` attribute. If omitted, the attribute is
            not provided.
        :type id_: Optional[str]

        :param attributes: Other attributes to be included in the element. Defaults to
            ``dict()``.
        :type attributes: Optional[Mapping[str, str]]

        :returns: An SVG ``polygon`` element.
        :rtype: Element
        """
        return cls._make_svg_polything(coords, "polygon", stroke, fill, id_, attributes)

    @classmethod
    def make_svg_line(
        cls: type[Element],
        corners: tuple[
            tuple[int | float, int | float], tuple[int | float, int | float]
        ],
        stroke: str = "black",
        id_: Optional[str] = None,
        attributes: Mapping[dict[str, str]] = None,
    ) -> Element:
        """
        Make an SVG ``line`` element.

        :param corners: The endpoints of the line.
        :type corners: tuple[tuple[int | float, int | float],
            tuple[int | float, int | float]]

        :param stroke: Value of the SVG ``stroke`` attribute. Defaults to ``"black"``.
        :type stroke: str

        :param id_: Value of the SVG ``id`` attribute. If omitted, the attribute is
            not provided.
        :type id_: Optional[str]

        :param attributes: Other attributes to be included in the element. Defaults to
            ``dict()``.
        :type attributes: Optional[Mapping[str, str]]

        :returns: An SVG ``line`` element.
        :rtype: Element
        """
        attribs = (
            ({"id": id_} if id_ else {})
            | (
                {
                    f"{'x' if k == 0 else 'y'}{j + 1}": str(corners[j][k])
                    for j in range(2)
                    for k in range(2)
                }
            )
            | {"stroke": stroke}
        ) | (attributes if attributes else {})
        return cls("line", attributes=attribs, self_closing=True)

    @classmethod
    def make_svg_rect(
        cls: type[Element],
        corners: tuple[
            tuple[int | float, int | float], tuple[int | float, int | float]
        ],
        stroke: str = "none",
        fill: str = "none",
        id_: Optional[str] = None,
        attributes: Mapping[dict[str, str]] = None,
    ) -> Element:
        """
        Make an SVG ``rect`` element.

        :param corners: Opposite corners of the rectangle.
        :type corners: tuple[tuple[int | float, int | float],
            tuple[int | float, int | float]]

        :param stroke: Value of the SVG ``stroke`` attribute. Defaults to ``"none"``.
        :type stroke: str

        :param fill: Value of the SVG ``fill`` attribute. Defaults to ``"none"``.
        :type stroke: str

        :param id_: Value of the SVG ``id`` attribute. If omitted, the attribute is
            not provided.
        :type id_: Optional[str]

        :param attributes: Other attributes to be included in the element. Defaults to
            ``dict()``.
        :type attributes: Optional[Mapping[str, str]]

        :returns: An SVG ``rect`` element.
        :rtype: Element
        """
        width = abs(corners[0][0] - corners[1][0])
        height = abs(corners[0][1] - corners[1][1])
        x = min(corners[0][0], corners[1][0])
        y = min(corners[0][1], corners[1][1])
        attribs = (
            ({"id": id_} if id_ else {})
            | {
                "x": str(x),
                "y": str(y),
                "width": str(width),
                "height": str(height),
                "fill": fill,
                "stroke": stroke,
            }
        ) | (attributes if attributes else {})
        return cls("rect", attributes=attribs, self_closing=True)

    @classmethod
    def make_inline_svg(
        cls: type[Element],
        width: int | float,
        height: int | float,
        interior: Sequence[str | Element],
        background: Optional[str] = None,
        defs: Optional[str] = None,
        id_: Optional[str] = None,
        attributes: Optional[Mapping[str, str]] = None,
    ) -> Element:
        """
        Make an inline SVG element for use in an HTML page.

        :param width: The width of the SVG viewbox
        :type width: int | float

        :param height: The height of the SVG viewbox
        :type height: int | float

        :param interior: Elements that will be inside the SVG.
        :type interior: Sequence[str | Element]

        :param background: The  ``fill`` attribute of an SVG ``rect`` that occupies the
            entire Viewport but is underneath the other elements. Defaults to ``None``.
            If ``None``, no such ``rect`` is constructed.
        :type background: Optional[str]

        :param defs: Any text to be passed along as the ``def`` attribute.
        :type defs: Optional[str]

        :param id_: Value of the HTML ``id`` attribute. If omitted, the attribute is
            not provided.
        :type id_: Optional[str]

        :param attributes: Other attributes to be included in the element. Defaults to
            ``dict()``.
        :type attributes: Optional[Mapping[str, str]]

        :returns: An inline ``svg`` element.
        :rtype: Element
        """
        basic_attribs = {
            "viewBox": f"0 0 {width} {height}",
            "xmlns": "http://www.w3.org/2000/svg",
        }
        if id_:
            basic_attribs["id"] = id_
        attribs = basic_attribs | attributes if attributes else basic_attribs
        def_list: list[str | Element] = (
            [Element("defs", interior=[defs])] if defs else []
        )
        back_list: list[str | Element] = (
            [cls.make_svg_rect(((0, 0), (width, height)), fill=background)]
            if background
            else []
        )
        full_interior = def_list + back_list + list(interior)

        return cls(name="svg", attributes=attribs, interior=full_interior)
