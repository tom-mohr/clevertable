from .Converter import Converter
from ._utils import _flatten_tuples


class Flatten(Converter):

    def labels(self, labels: tuple[tuple]) -> tuple[tuple]:
        return _flatten_tuples(labels)

    def transform(self, row: tuple) -> tuple:
        return _flatten_tuples(row)
