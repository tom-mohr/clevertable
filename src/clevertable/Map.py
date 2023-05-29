from __future__ import annotations

from .Converter import Converter


class Map(Converter):

    def __init__(self, lookup_table: dict, default=None):
        """
        Converts values according to a lookup table.
        If the value is not found in the lookup table, the default value is returned.
        Values may be single values or tuples of values.
        """
        if len(lookup_table) == 0:
            raise ValueError("Empty lookup table is not allowed.")
        # if any value is not a tuple, convert all values to a 1-element tuple
        if any(not isinstance(val, tuple) for val in lookup_table.values()):
            lookup_table = {key: (val,) for key, val in lookup_table.items()}
        self.lookup_table: dict[any, tuple] = lookup_table

        self.__default_arg = default  # save original arg for repr()
        if default is not None and not isinstance(default, tuple):
            default = (default,)
        self.default_value: tuple | None = default

    def transform(self, row: tuple) -> tuple:
        val = row[0]
        if val in self.lookup_table:
            return self.lookup_table[val]
        if self.default_value is not None:
            return self.default_value
        raise KeyError(f"Value '{val}' not found in lookup table and no default value is specified.")

    def __repr__(self):
        if self.__default_arg is None:
            return repr(self.lookup_table)
        else:
            return f"Map({repr(self.lookup_table)}, default={repr(self.__default_arg)})"
