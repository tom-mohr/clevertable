import re

from .Converter import Converter

_DEFAULT_STRIP = [
    r"\s+"
]


class Strip(Converter):

    def __init__(self, *strip: str):
        if not strip:
            strip = _DEFAULT_STRIP
            self.__default_args = True
        else:
            self.__default_args = False

        # remove whole substring either at the end or beginning
        prefixes = map(lambda s: f'^{s}', strip)
        suffixes = map(lambda s: f'{s}$', strip)
        fixes = list(prefixes) + list(suffixes)
        self.regex = "|".join(fixes)

    def transform(self, row: list) -> list:
        val = row[0]  # unpack 1-element list
        if not isinstance(val, str):
            raise ValueError(f"Strip() can only be applied to strings, not to value of type {type(val)}: {val}")
        return [re.sub(self.regex, "", val)]

    def __repr__(self):
        if self.__default_args:
            return "Strip()"
        return f"Strip({repr(self.regex)})"
