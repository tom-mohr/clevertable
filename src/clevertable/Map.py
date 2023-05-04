from __future__ import annotations

from .Converter import Converter


class Map(Converter):

    def __init__(self, lookup_table: dict, default=None):
        """
        Converts values according to a lookup table.
        If the value is not found in the lookup table, the default value is returned.
        Values may be single values or lists of values.
        """
        if len(lookup_table) == 0:
            raise ValueError("Empty lookup table is not allowed.")
        # if any value is not a list, convert all values to a list
        if any(not isinstance(val, list) for val in lookup_table.values()):
            lookup_table = {key: [val] for key, val in lookup_table.items()}
        self.lookup_table = lookup_table
        self.default_value = default

    def transform(self, row: list) -> list:
        val = row[0]
        if val in self.lookup_table:
            return self.lookup_table[val]
        if self.default_value is not None:
            return self.default_value
        raise KeyError(f"Value '{val}' not found in lookup table and no default value is specified.")

    def __repr__(self):
        if self.default_value is None:
            return repr(self.lookup_table)
        else:
            return f"Map({repr(self.lookup_table)}, default={repr(self.default_value)})"
