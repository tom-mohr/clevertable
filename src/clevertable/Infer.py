from __future__ import annotations

import re

from .Converter import Converter
from .Ignore import Ignore


class Infer(Converter):

    def __init__(self, ignore_uninferrable: bool = False):
        self.ignore_uninferrable = ignore_uninferrable
        self.inferred = None

    def __repr__(self):
        return repr(self.inferred)

    def __getitem__(self, item):
        return self.inferred[item]

    def fit(self, rows: list[tuple]):
        """
        Tries to infer this converter from the given data.
        If a converter could be inferred, it is fitted with the data and stored in self.inferred.
        :raises ValueError: if no converter can be inferred and ignore_uninferrable is False
        """
        try:
            self.inferred = _infer_converter_from_data(rows)
        except ValueError as e:
            if self.ignore_uninferrable:
                self.inferred = Ignore()
                return
            raise e
        self.inferred.fit(rows)

    def labels(self, labels: tuple) -> tuple:
        return self.inferred.labels(labels)

    def transform(self, row: tuple) -> tuple:
        return self.inferred.transform(row)


def _infer_converter_from_data(rows: list[tuple]) -> Converter:
    """Tries to infer the best converter from the given data.
    If no converter can be inferred, a ValueError is raised."""
    # dynamic imports in order to break circular dependency
    from .Binary import Binary
    from .Enumerate import Enumerate
    from .Float import Float
    from .List import List, ListAndOr
    from .OneHot import OneHot

    # if only contains 1-element rows:
    if all(len(row) == 1 for row in rows):

        values = [row[0] for row in rows]  # unpack 1-element rows

        def _is_parseable_float(val: any) -> bool:
            try:
                float(val)
            except (ValueError, TypeError, OverflowError):
                return False
            return True

        if all(map(_is_parseable_float, values)):
            return Float()

        # since numerical approach failed,
        # we now try categorical approaches
        string_values = [val for val in values if isinstance(val, str)]

        # check if it can be split according to List()
        regex_list = re.compile(List._DEFAULT_DELIMITER)
        if any(map(regex_list.search, string_values)):
            # check if there are also "and" or "or" in the values
            regex_list_and_or = re.compile("|".join(ListAndOr._DEFAULT_DELIMITER_AND_OR))
            if any(map(regex_list_and_or.search, string_values)):
                return ListAndOr()
            return List()

        num_unique_entries = len(set(values))
        if num_unique_entries <= 2:
            return Binary()
        elif num_unique_entries <= 10:
            return OneHot()
        elif num_unique_entries <= 100 or num_unique_entries < 0.1 * len(values):
            return Enumerate()

    raise ValueError(f"Cannot infer converter from values: {rows[:5]} ...")
