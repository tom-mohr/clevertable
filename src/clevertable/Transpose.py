from __future__ import annotations

from .Converter import Converter


class Transpose(Converter):

    def transform(self, row: list) -> list[list]:
        # assume that row is a list of lists
        # and that the nested lists are of equal length
        return [list(item) for item in zip(*row)]
