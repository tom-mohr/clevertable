from .Infer import Infer
from .Converter import Converter
from ._utils import _parse_converter


class Parallel(Converter):

    def __init__(self, *converters: any):
        """
        Apply multiple converters to the respective elements of the input.
        During fit(), top-level Infer() converters are replaced with the inferred converter.
        :param converters: The converters in the same order as the input elements which they should be applied to.
        """
        self.converters = [_parse_converter(conv) for conv in converters]

    def fit(self, rows: list[tuple]):

        # transpose rows
        cols = list(zip(*rows))

        for conv, col in zip(self.converters, cols):
            values = [(val,) for val in col]  # each row must be a tuple
            conv.fit(values)

        # replace all Infer converters with the nested inferred converter
        for i, conv in enumerate(self.converters):
            if isinstance(conv, Infer):
                assert conv.inferred is not None, \
                    f"Infer() converter at index {i} did not infer a converter during fit()"
                self.converters[i] = conv.inferred

    def labels(self, labels: tuple) -> tuple:
        assert isinstance(labels, tuple)
        assert len(labels) == len(self.converters)
        return tuple(conv.labels((label,)) for label, conv in zip(labels, self.converters))

    def transform(self, row: tuple) -> tuple:
        assert len(row) == len(self.converters), \
            f"Parallel converter expected {len(self.converters)} elements, but got {len(row)}: {row}"
        return tuple(conv.transform((val,)) for val, conv in zip(row, self.converters))

    def __repr__(self):
        return f"Parallel({', '.join(repr(conv) for conv in self.converters)})"
