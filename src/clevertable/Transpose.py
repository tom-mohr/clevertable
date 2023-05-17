from __future__ import annotations

from .Converter import Converter
from ._utils import _flatten


class Transpose(Converter):

    def transform(self, row: list) -> list[list]:
        # assume that row is a list of lists
        # and that the nested lists are of equal length
        return [list(item) for item in zip(*row)]

    def labels(self, labels: list) -> list:
        """
        Expects a list of lists.
        The nested lists must all be identical to each other.

        :param labels: A list of lists of labels.
        :return: The first list.
        """
        assert len(labels) > 0
        first_labels = labels[0]
        assert isinstance(first_labels, list), \
            f"Labels passed to Transpose() must be lists," \
            f" but received {repr(first_labels)} of type {type(first_labels)}."
        if len(labels) > 1:
            # ensure that all labels are identical
            if not all(first_labels == labels[i] for i in range(1, len(labels))):
                raise ValueError(f"Labels must be identical for all inputs, but received {repr(labels)}.")
        return first_labels
