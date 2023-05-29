from __future__ import annotations

from .Infer import Infer
from .Converter import Converter
from .Id import Id
from ._utils import _parse_converter


class _Pipeline(Converter):

    def __init__(self, first: any, second: any):
        self.first = _parse_converter(first)
        self.second = _parse_converter(second)

    def fit(self, rows: list[tuple]):
        self.first.fit(rows)
        self.second.fit([self.first.transform(row) for row in rows])

        # replace Infer() converters with the nested inferred converter
        if isinstance(self.first, Infer):
            assert self.first.inferred is not None, \
                f"Infer() converter for did not infer a converter during fit()"
            self.first = self.first.inferred
        if isinstance(self.second, Infer):
            assert self.second.inferred is not None, \
                f"Infer() converter for did not infer a converter during fit()"
            self.second = self.second.inferred

    def labels(self, labels: tuple) -> tuple:
        return self.second.labels(self.first.labels(labels))

    def transform(self, row: tuple) -> tuple:
        return self.second.transform(self.first.transform(row))

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.first)}, {repr(self.second)})"


class Pipeline(_Pipeline):

    def __init__(self, *converters: any):
        if len(converters) == 0:
            super().__init__(Id(), Id())
        elif len(converters) == 1:
            super().__init__(converters[0], Id())
        elif len(converters) == 2:
            super().__init__(converters[0], converters[1])
        else:
            super().__init__(converters[0], Pipeline(*converters[1:]))

    def __getitem__(self, index):
        return self.converters[index]

    @property
    def converters(self) -> list[Converter]:
        convs = []
        if isinstance(self.first, Pipeline):
            convs.extend(self.first.converters)
        else:
            convs.append(self.first)
        if isinstance(self.second, Pipeline):
            convs.extend(self.second.converters)
        else:
            convs.append(self.second)
        return convs

    def __repr__(self):
        converters_without_id = list(filter(lambda conv:
                                            not type(conv) is Id,  # this will not filter out subclasses of Id!
                                            self.converters))
        if len(converters_without_id) <= 1:
            # in one line
            return f"[{', '.join(repr(conv) for conv in converters_without_id)}]"

        # in multiple lines
        s = "[\n"
        for conv in converters_without_id:
            s += "\t" + "\n\t".join(repr(conv).split("\n"))
            s += ",\n"
        s += "]"
        return s
