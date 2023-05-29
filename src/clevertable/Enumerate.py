from __future__ import annotations

from .Converter import Converter


class Enumerate(Converter):

    def __init__(self, *values: any):
        self.values = values or ()

    def fit(self, rows: list[tuple]):
        # if values were not specified, infer them from the data
        if not self.values:
            values = [row[0] for row in rows]  # unpack 1-element rows
            values = set(values)

            # try sorting
            values = list(values)
            try:
                values.sort()
            except TypeError:
                pass
            values = tuple(values)

            self.values = values

    def transform(self, row: tuple) -> tuple:
        val = row[0]  # unpack 1-element row
        if val in self.values:
            return (self.values.index(val),)
        raise ValueError(f"Unknown value: {val}. Known values: {self.values}")

    def __repr__(self):
        return f"Enumerate({', '.join(repr(val) for val in self.values)})"
