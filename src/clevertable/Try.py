from __future__ import annotations

import warnings

from .Infer import Infer
from .Converter import Converter
from ._utils import _parse_converter


class Try(Converter):
    def __init__(self, *converters: any, exceptions: list[type[Exception]] = None):
        """
        Returns value of the first converter that does not raise an exception,
        or the original value if all converters raise an exception.
        :param converters: Converters to try, in the given order.
        :param exceptions: List of exceptions to ignore. If this is None, all exceptions will be ignored.
        """
        if exceptions is None:
            self.exceptions = (Exception,)
        else:
            self.exceptions = tuple(exceptions)
        self.converters = [_parse_converter(conv) for conv in converters]

    def fit(self, rows: list[list]):
        convs = list(self.converters)
        while convs:
            conv = convs.pop(0)
            conv.fit(rows)

            if not convs:
                return  # no need to transform with last converter

            next_rows = []  # values that raise an exception
            for row in rows:
                try:
                    conv.transform(row)
                except Exception as e:
                    if not isinstance(e, self.exceptions):
                        raise e
                    next_rows.append(row)
            rows = next_rows
            if not rows:
                warnings.warn(f"All rows raised exceptions for {conv.__class__.__name__} converter,"
                              f" therefore the remaining converters ({len(convs)}) can not be fitted")
                break

        # replace Infer() converters with the nested inferred converter
        for i, conv in enumerate(self.converters):
            if isinstance(conv, Infer):
                assert conv.inferred is not None, \
                    f"Infer() converter for did not infer a converter during fit()"
                self.converters[i] = conv.inferred

    def labels(self, labels: list) -> list:
        if self.converters:
            return self.converters[0].labels(labels)
        return labels

    def transform(self, row: list) -> list:
        for conv in self.converters:
            try:
                return conv.transform(row)
            except Exception as e:
                if not isinstance(e, self.exceptions):
                    raise e
        return row

    def __getitem__(self, item):
        return self.converters[item]

    def __setitem__(self, key, value):
        self.converters[key] = _parse_converter(value)

    def __repr__(self):
        return repr(tuple(self.converters))
