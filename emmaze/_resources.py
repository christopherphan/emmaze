"""A module with some resources."""

from typing import Final

HEX_DIGITS: Final[str] = (
    "".join(chr(k) for k in range(ord("0"), ord("9") + 1))
    + "".join(chr(k) for k in range(ord("A"), ord("F") + 1))
    + "".join(chr(k) for k in range(ord("a"), ord("f") + 1))
)


def _parse_color(hextriplet: str) -> tuple[int, int, int]:
    """
    Convert a 6-digit hex-triplet in string form into a tuple of three integers.

    For example, the string ``"#ff3a75"`` is converted to ``(0xff, 0x3a, 0x75)``.
    """
    cleaned = "".join(k for k in hextriplet if k in HEX_DIGITS)
    if len(cleaned) == 3:
        cleaned = "".join(k + k for k in cleaned)
    elif len(cleaned) != 6:
        raise ValueError(f'"{cleaned}" is not a valid hex triplet.')
    return tuple(
        int("0x" + cleaned[2 * k : 2 * k + 2], 16) for k in range(3)
    )  # type: ignore


def _to_web_color(color_tuple: tuple[int, int, int]) -> str:
    """Convert a tuple into a hex-triplet string."""
    if any(k < 0 or k > 255 for k in color_tuple):
        raise ValueError("Numbers must be between 0 and 255, inclusively.")
    return "#" + "".join(f"{k:02x}" for k in color_tuple)
