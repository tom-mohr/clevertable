from __future__ import annotations

import math
from typing import Literal

from numpy import mean, median, isfinite
from scipy.stats import mode

from .Converter import Converter


class Float(Converter):

    def __init__(self, default: float | Literal["mean", "median", "mode"] = None):
        """
        Simple conversion to floats.

        - If a string is encountered, it tries to parse it.
        - If a number is encountered, it simply ensures that it is of type float.
        - If an infinite number is encountered, it is replaced with the given default value.
        - If any other value is encountered, it is replaced with the given default value.
        """
        self.__default_value = default

    @property
    def default(self):
        return self.__default_value

    def fit(self, rows: list[tuple]):

        values = [row[0] for row in rows]  # unpack 1-element rows

        if self.__default_value in ("mean", "median", "mode"):
            # replace default value with the corresponding number

            # collect all numbers that can be parsed
            usable_numbers = []
            for val in values:
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    continue
                except OverflowError:
                    # todo: issue warning
                    continue

                if not isfinite(val):
                    continue

                usable_numbers.append(val)

            if len(usable_numbers) == 0:
                raise ValueError(f"Cannot compute {self.__default_value},"
                                 f" because no usable numbers were found in the given data.")
            if self.__default_value == "mean":
                self.__default_value = float(mean(usable_numbers))
            elif self.__default_value == "median":
                self.__default_value = float(median(usable_numbers))
            elif self.__default_value == "mode":
                mode_, count = mode(usable_numbers, keepdims=False)
                self.__default_value = float(mode_)

    def transform(self, row: tuple) -> tuple:
        val = row[0]  # unpack 1-element tuple
        try:
            num = float(val)
        except (ValueError, TypeError):
            num = float("nan")
        except OverflowError:
            # todo: issue warning
            num = float("nan")

        if math.isfinite(num):
            return (num,)

        # conversion / parsing failed.
        # ensure that a usable default value exists
        if self.__default_value is None:
            raise ValueError(f"Cannot transform value '{val}' to float,"
                             f" because parsing failed and no default value was specified.")
        if self.__default_value in ("mean", "median", "mode"):
            raise ValueError(f"You must call fit() before transform().")

        return (self.__default_value,)

    def __repr__(self):
        if self.__default_value is None:
            return "Float()"
        return f"Float(default={repr(self.__default_value)})"
