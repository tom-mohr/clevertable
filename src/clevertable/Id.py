from __future__ import annotations

from .Converter import Converter


class Id(Converter):
    """Returns the input value unchanged."""

    def transform(self, row: list) -> list:
        return row
