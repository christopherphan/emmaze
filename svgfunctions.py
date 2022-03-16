from __future__ import annotations

from collections.abc import Sequence
from textwrap import indent
from typing import Literal, Optional


class Element:
    def __init__(
        self: Element,
        name: str,
        attributes: Optional[dict[str, str]] = None,
        interior: Optional[Sequence[str | Element]] = None,
        self_closing: bool = False,
        seperate_interior: bool = True,
    ) -> None:
        self.name = name
        self.attributes = attributes if attributes else dict()
        self.interior = interior if interior else []
        self.self_closing = self_closing
        self.seperate_interior = seperate_interior

    def output(
        self: Element, indentation: int = 0, additional_indentation: int = 2
    ) -> str:
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
                    if self.seperate_interior:
                        out_str += "\n" + indent(item, " " * additional_indentation)
                    else:
                        out_str += item
            if self.seperate_interior:
                out_str += "\n"
            out_str += f"</{self.name}>"
        else:
            out_str += "/>"
        return indent(out_str, " " * indentation)

    def __str__(self: Element) -> str:
        return self.output()

    @classmethod
    def make_svg_group(
        cls: type[Element],
        objects: Sequence[Element],
    ) -> Element:
        return cls("g", interior=objects)

    @classmethod
    def _make_svg_polything(
        cls: type[Element],
        coords: Sequence[tuple[int | float, int | float]],
        type_: Literal["polyline", "polygon"],
        stroke: str = "none",
        fill: str = "none",
        id_: Optional[str] = None,
        attributes: Optional[dict[str, str]] = None,
    ) -> Element:
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
        attributes: Optional[dict[str, str]] = None,
    ) -> Element:
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
        return cls._make_svg_polything(coords, "polygon", stroke, fill, id_, attributes)

    @classmethod
    def make_svg_line(
        cls: type[Element],
        corners: tuple[
            tuple[int | float, int | float], tuple[int | float, int | float]
        ],
        stroke: str = "black",
        id_: Optional[str] = None,
        attributes: Optional[dict[str, str]] = None,
    ) -> Element:
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
        attributes: Optional[dict[str, str]] = None,
    ) -> Element:
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
        attributes: Optional[dict[str, str]] = None,
    ) -> Element:
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