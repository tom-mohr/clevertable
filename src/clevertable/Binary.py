from __future__ import annotations

from typing import Iterable

from .Converter import Converter

_COMMON_POSITIVE_STRINGS = {"yes", "true", "positive", "1", "female"}
_COMMON_NEGATIVE_STRINGS = {"no", "false", "negative", "0", "male", "none"}


class Binary(Converter):

    def __init__(self,
                 positive: any = None,
                 negative: any = None):
        """
        Converts values to 0 or 1.
        :param positive: A value or an iterable of values that should be considered positive.
        ``None`` is equivalent to passing an empty iterable.
        :param negative: A value or an iterable of values that should be considered negative.
        ``None`` is equivalent to passing an empty iterable.
        """
        # save args for __repr__
        self.__args_positive = positive
        self.__args_negative = negative

        if positive is None:
            positive = set()  # empty set
        elif isinstance(positive, Iterable) and not isinstance(positive, str):  # non-string iterable
            positive = set(positive)  # ensure set
        else:
            positive = {positive}  # wrap single value in set

        if negative is None:
            negative = set()  # empty set
        elif isinstance(negative, Iterable) and not isinstance(negative, str):  # non-string iterable
            negative = set(negative)  # ensure set
        else:
            negative = {negative}  # wrap single value in set

        self.positive: set = positive
        self.negative: set = negative

    def fit(self, rows: list[tuple]):
        if self.positive or self.negative:
            # at least either one positive or negative value was passed to the constructor,
            # -> no need to infer them from the data
            return

        values = [row[0] for row in rows]  # unpack 1-element rows

        # infer positive and negative values from the data

        # union with common positive and negative values
        values = set(values)
        common_positive = values.intersection(_COMMON_POSITIVE_STRINGS)
        common_negative = values.intersection(_COMMON_NEGATIVE_STRINGS)

        if len(common_positive) + len(common_negative) == len(values):
            # all values are common positive or negative values
            self.positive = common_positive
            self.negative = common_negative
            return

        # at this point, there are some values that we don't know whether they are positive or negative
        # -> simply pick the lexically smallest value as negative
        self.negative = {sorted(values)[0]}

    def transform(self, row: tuple) -> tuple:
        val = row[0]  # unpack 1-element tuple

        if self.positive and self.negative:
            # ensure the value is either in positive or in negative
            if val not in self.positive and val not in self.negative:
                raise ValueError(f"Value '{val}' is neither in the positive nor in the negative values.")
        if self.positive:
            return (int(val in self.positive),)
        else:
            return (1 - int(val in self.negative),)

    def __repr__(self):
        args = []
        if self.__args_positive is not None:
            args.append(f"positive={repr(self.__args_positive)}")
        if self.__args_negative is not None:
            args.append(f"negative={repr(self.__args_negative)}")
        return f"Binary({', '.join(args)})"
