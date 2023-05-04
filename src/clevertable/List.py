from __future__ import annotations

from typing import Iterable

from .Converter import Converter
from .Flatten import Flatten
from .Pipeline import Pipeline
from ._utils import _ensure_list


class List(Pipeline):
    _DEFAULT_DELIMITER = r"\s*,\s*"
    _DEFAULT_STRIP = r"\s+"  # remove whitespaces

    def __init__(self, delimiter: str | Iterable[str] = _DEFAULT_DELIMITER,
                 strip: str | Iterable[str] = _DEFAULT_STRIP):
        # save args for __repr__
        self.__arg_delimiter = delimiter
        self.__arg_strip = strip

        delimiter = _ensure_list(delimiter)
        strip = _ensure_list(strip)
        from .Split import Split
        from .ForEach import ForEach
        from .OneHot import OneHot
        from .Strip import Strip
        from .Transpose import Transpose

        self.__one_hot = OneHot()  # need to access later
        super().__init__(
            Split(*delimiter),
            ForEach(Strip(*strip)),
            Flatten(),
            lambda s: set(s) - {""},  # remove empty string if present
            # row could be [] at this point
            # -> so add 'None' here to ensure there's always at least an all-zeros output
            # (None works because None != None, so it is guaranteed to have all zeros)
            lambda s: set(s) | {None},
            ForEach(self.__one_hot),
            Transpose(),
            ForEach(max),
            Flatten(),
        )

    @property
    def values(self):
        return self.__one_hot.values

    @property
    def converters(self) -> list[Converter]:
        # need to override this because otherwise pipeline will mess with the internal converters of List
        # (e.g. __getitem__ and __repr__), as List is a subclass of Pipeline
        return [self]

    def __repr__(self):
        args = []
        if self.__arg_delimiter != List._DEFAULT_DELIMITER:
            args.append(f"delimiter={repr(self.__arg_delimiter)}")
        if self.__arg_strip != List._DEFAULT_STRIP:
            args.append(f"strip={repr(self.__arg_strip)}")
        return f"List({', '.join(args)})"


class ListAndOr(List):
    _DEFAULT_DELIMITER_AND_OR = [
        r"\s*,\s*and\s+",
        r"\s+and\s+",
        r"\s*,\s*or\s+",
        r"\s+or\s+",
    ]
    _DEFAULT_STRIP_AND_OR = [
        r"\.",  # in case the list contains dots
    ]

    def __init__(self, delimiter: str | Iterable[str] = None, strip: str | Iterable[str] = None):
        # save args for __repr__
        self.__arg_delimiter = delimiter
        self.__arg_strip = strip

        super().__init__(
            delimiter=(ListAndOr._DEFAULT_DELIMITER_AND_OR +
                       _ensure_list(List._DEFAULT_DELIMITER) +
                       _ensure_list(delimiter)),
            strip=(ListAndOr._DEFAULT_STRIP_AND_OR +
                   _ensure_list(List._DEFAULT_STRIP) +
                   _ensure_list(strip))
        )

    def __repr__(self):
        args = []
        if self.__arg_delimiter is not None:
            args.append(f"delimiter={repr(self.__arg_delimiter)}")
        if self.__arg_strip is not None:
            args.append(f"strip={repr(self.__arg_strip)}")
        return f"ListAndOr({', '.join(args)})"
