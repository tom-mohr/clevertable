from __future__ import annotations

from .Converter import Converter
from ._utils import _flatten_tuples


class Transpose(Converter):

    def transform(self, row: tuple[tuple]) -> tuple[tuple]:
        # assume that row is a tuple of tuples
        # and that the nested tuples are of equal length
        return tuple(tuple(item) for item in zip(*row))

    def labels(self, labels: tuple) -> tuple:
        """
        Expects a tuple of tuples.
        The inner tuples must all be identical to each other.

        :param labels: A tuple of tuples of labels.
        :return: The first tuple.
        """
        assert len(labels) > 0
        first_labels = labels[0]
        assert isinstance(first_labels, tuple), \
            f"Labels passed to Transpose() must be tuples," \
            f" but received {repr(first_labels)} of type {type(first_labels)}."
        if len(labels) > 1:
            # ensure that all labels are identical
            if not all(first_labels == labels[i] for i in range(1, len(labels))):
                raise ValueError(f"Labels must be identical for all inputs, but received {repr(labels)}.")
        return first_labels
