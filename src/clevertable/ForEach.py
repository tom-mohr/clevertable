from __future__ import annotations

from .Converter import Converter
from ._utils import _parse_converter


class ForEach(Converter):

    def __init__(self, conv: any):
        """
        Applies the converter to all elements of the input and returns a tuple of all outputs.
        :param conv: The converter that is to be applied to all elements in the input.
        """
        self.conv = _parse_converter(conv)

    def fit(self, rows: list[tuple]):
        flattened_rows = [(element,) for row in rows for element in row]
        self.conv.fit(flattened_rows)

    def labels(self, labels: tuple) -> tuple:
        return tuple(self.conv.labels((label,)) for label in labels)

    def transform(self, row: tuple) -> tuple:
        return tuple(self.conv.transform((item,)) for item in row)

    def __repr__(self):
        return f"ForEach({repr(self.conv)})"
