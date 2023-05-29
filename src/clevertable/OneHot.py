from __future__ import annotations

from .Converter import Converter


class OneHot(Converter):

    def __init__(self, *values: any):
        self.values = values

    def fit(self, rows: list[tuple]):
        if not self.values:
            # infer values from data
            values = [row[0] for row in rows]  # unpack 1-element rows
            unique_values = set(values)

            # now remove None, because we want to keep None a special value
            # that can be used for generating all-zeros output
            unique_values -= {None}

            # try sorting
            unique_values = list(unique_values)
            try:
                unique_values.sort()
            except TypeError:
                pass
            unique_values = tuple(unique_values)

            self.values = unique_values

    def labels(self, labels: tuple) -> tuple[str]:
        label = labels[0]  # unpack 1-element tuple
        assert isinstance(label, str), f"Expected label to be a string, but got {label} of type {type(label)}!"
        return tuple(f"{label}={value}" for value in self.values)

    def transform(self, row: tuple) -> tuple[int]:
        val = row[0]  # unpack 1-element tuple

        # note that if val is None, then the output is all-zeros
        # (even if an entry in self.values would be None, because None != None)

        return tuple(int(val == val_) for val_ in self.values)

    def __repr__(self):
        return f"OneHot({', '.join(repr(val) for val in self.values)})"
