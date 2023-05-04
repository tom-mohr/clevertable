from __future__ import annotations

from typing import Literal

from numpy import mean, median, isinf, isnan, isfinite, number
from scipy.stats import mode

from .Converter import Converter


def _try_float(val: any) -> float | None:
    try:
        x = float(val)
    except (TypeError, ValueError, OverflowError):
        return None

    # x is a float, but is it a "good" float?
    if isinf(x):
        return None
    if isnan(x):
        return None

    # all checks passed
    return x


def _is_number(val: any):
    try:
        _check_number(val)
        return True
    except ValueError:
        return False


def _check_number(val: any) -> any:
    """Returns the given value if it is a number, otherwise raises a ValueError."""
    if not isinstance(val, (int, float, number)):
        raise ValueError(f"Value '{val}' is not a number")
    if not isfinite(val):
        raise ValueError(f"Value '{val}' is not a finite number")
    return val


class Float(Converter):

    def __init__(self, default: float | Literal["mean", "median", "mode"] = None):
        """
        Simple conversion to floats.

        - If a string is encountered, it tries to parse it.
        - If a number is encountered, it simply ensures that it is of type float.
        - If an infinite number is encountered, it is replaced with the given default value.
        - If any other value is encountered, it is replaced with the given default value.
        """
        if default is not None:
            # check type of default value
            if default not in ("mean", "median", "mode"):
                if not _is_number(default):
                    raise ValueError(f"Invalid default value '{default}'.")

        self.__default_value = default

    @property
    def default(self):
        return self.__default_value

    def fit(self, rows: list[list]):

        values = [row[0] for row in rows]  # unpack 1-element rows

        if self.__default_value in ("mean", "median", "mode"):
            # replace default value with the corresponding number

            # collect all numbers that can be parsed
            parsed_values = []
            for val in values:
                try:
                    number = float(val)
                except:
                    continue
                parsed_values.append(number)

            if len(parsed_values) == 0:
                raise ValueError(f"Cannot compute {self.__default_value},"
                                 f" because parsing failed for all numbers.")
            if self.__default_value == "mean":
                self.__default_value = float(mean(parsed_values))
            elif self.__default_value == "median":
                self.__default_value = float(median(parsed_values))
            elif self.__default_value == "mode":
                mode_, count = mode(parsed_values, keepdims=False)
                self.__default_value = float(mode_)

    def transform(self, row: list) -> list:
        val = row[0]  # unpack 1-element list
        number = _try_float(val)
        if number is not None:
            return [number]

        # conversion / parsing failed.
        # ensure that a usable default value exists
        if self.__default_value is None:
            raise ValueError(f"Cannot transform value '{val}' to float,"
                             f" because parsing failed and no default value was specified.")
        if self.__default_value in ("mean", "median", "mode"):
            raise ValueError(f"You must call fit() before transform().")

        return [self.__default_value]

    def __repr__(self):
        if self.__default_value is None:
            return "Float()"
        return f"Float(default={repr(self.__default_value)})"
