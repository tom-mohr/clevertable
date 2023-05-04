from __future__ import annotations

from .Converter import Converter


class Ignore(Converter):
    """Doesn't do anything. This converter doesn't result in an additional column."""

    def labels(self, labels: list) -> []:
        return []

    def transform(self, row: any) -> []:
        return []

    def __repr__(self):
        return "None"
