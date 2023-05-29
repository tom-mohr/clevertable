from __future__ import annotations

from typing import Iterable, Callable

from .Converter import Converter


def _parse_converter(value: any) -> Converter:
    # dynamic imports in order to break circular dependency
    from .Const import Const
    from .Ignore import Ignore
    from .Map import Map
    from .Function import Function
    from .Pipeline import Pipeline
    from .Try import Try

    if isinstance(value, Converter):
        return value
    if value is None:
        return Ignore()
    if isinstance(value, dict):
        return Map(value)
    if isinstance(value, tuple):
        return Try(*value)
    if isinstance(value, list):
        return Pipeline(*value)
    if callable(value):
        return Function(value)
    return Const(value)


def _ensure_list(obj: list | None | str | Iterable | any) -> list:
    if type(obj) is list:
        return obj
    if obj is None:
        return []
    if type(obj) is str:  # strings are iterable, but we don't want to split them into characters
        return [obj]
    if isinstance(obj, Iterable):
        return list(obj)
    return [obj]


def _index_duplicates(labels: tuple[str], index_func: Callable[[str, int], str]) -> tuple[str]:
    """
    Add index suffix to all duplicate strings.
    This is done repeatedly until no duplicates are left,
    i.e. the returned list is guaranteed to have no duplicates.
    :param labels: Tuple of strings, may contain duplicates.
    :param index_func: (label, occurrence_count) -> new_label
    :return:
    """
    if len(labels) == 1:
        return labels
    # add index suffix to all duplicate strings
    # e.g. ["apple", "banana", "apple"] -> ["apple_1", "banana", "apple_2"]
    # for complete safety, repeat this until no duplicates are left
    while len(set(labels)) != len(labels):  # while duplicates are present
        counts = {label: labels.count(label) for label in set(labels)}
        occurrence_count = {label: 0 for label in set(labels)}
        labels = list(labels)  # need write access
        for i, label in enumerate(labels):
            count = counts[label]
            occurrence_count[label] += 1
            if count > 1:
                labels[i] = index_func(label, occurrence_count[label])
        labels = tuple(labels)
    return labels


def _flatten_tuples(tuple_of_tuples: tuple[tuple]) -> tuple:
    return tuple(e for inner_list in tuple_of_tuples for e in inner_list)
