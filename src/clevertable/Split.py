import re

from .Converter import Converter

_DEFAULT_SPLITS = [
    r"\s*,\s*",
    r"\s*;\s*",
    r"\s*\|\s*"
]


class Split(Converter):

    def __init__(self, *delimiters: str):
        if not delimiters:
            delimiters = _DEFAULT_SPLITS
            self.__default_args = True
        else:
            self.__default_args = False
        self.regex = "|".join(delimiters)

    def transform(self, row: list) -> list[str]:
        val = row[0]  # unpack 1-element list
        if not isinstance(val, str):
            raise ValueError(f"Split() can only be applied to strings, not to value of type {type(val)}: {val}")
        return re.split(self.regex, val)

    def __repr__(self):
        if self.__default_args:
            return "Split()"
        return f"Split({repr(self.regex)})"
