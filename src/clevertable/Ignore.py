from __future__ import annotations

from .Converter import Converter


class Ignore(Converter):
    """Doesn't do anything. This converter doesn't result in an additional column."""

    def labels(self, labels: tuple) -> ():
        return ()

    def transform(self, row: tuple) -> ():
        return ()

    def __repr__(self):
        return "None"
