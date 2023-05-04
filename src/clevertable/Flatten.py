from .Converter import Converter
from ._utils import _flatten


class Flatten(Converter):

    def labels(self, labels: list) -> list[list]:
        return _flatten(labels)

    def transform(self, row: list) -> list:
        return _flatten(row)
