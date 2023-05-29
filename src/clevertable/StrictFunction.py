from typing import Callable

from .Converter import Converter


class StrictFunction(Converter):

    def __init__(self, transform: callable, labels: Callable[[any], any] = None):
        """
        Creates a custom converter from a custom ``transform()`` function
        (and optionally, a custom ``labels()`` function).
        This is a handy way to create a converter that doesn't implement ``fit()`` (i.e. doesn't have a state).
        Both ``transform`` and ``labels`` must both accept and return lists.
        For a converter that accepts more general functions, see ``Function``.

        If no custom labels function is given, the output labels are generated based on the
        output cardinality inferred during ``fit()`` and according to the following logic:

        - If the number of incoming labels is identical to the output cardinality,
          the labels will be returned unchanged.
        - If there are multiple incoming labels but a single output label,
          the output label is formed by joining the incoming labels with ``, ``.
        - If there is a single incoming label but multiple output labels,
          the output labels are formed by adding suffixes ``_0``, ``_1``, etc.
          to the single input label.

        A special case are functions returning output of varying cardinality during ``fit()``.
        In this case, a single label is returned.
        If only one input label is given, that single label is returned.
        If multiple input labels are given, they are joined with ``_``.

        :param transform: The function to wrap. Turns input into output.
        :param labels: Turns incoming labels into output labels.
        """
        self._transform = transform
        self._labels = labels

        self._output_cardinality: int = None

    def fit(self, rows: list[list]):
        # infer output cardinality (only needed if no labels function is given)
        if self._labels is None:
            rows = [self._transform(row) for row in rows]
            self._output_cardinality = len(rows[0])

            # check if output cardinality varies:
            if not all(len(row) == self._output_cardinality for row in rows):
                self._output_cardinality = -1  # a value of -1 represents varying output cardinality
                return

    def transform(self, row: list) -> list:
        return self._transform(row)

    def labels(self, labels: list) -> list:
        if self._labels is not None:
            return self._labels(labels)  # use custom labels function

        if self._output_cardinality == -1:  # -1 represents varying output cardinality
            return [", ".join(str(x) for x in labels)]

        if len(labels) == self._output_cardinality:
            return labels

        if self._output_cardinality == 0:
            return []

        if self._output_cardinality == 1:
            return [", ".join(str(x) for x in labels)]

        if len(labels) == 1:
            label = labels[0]
            return [f"{label}_{i}" for i in range(self._output_cardinality)]

        raise ValueError(f"Cannot generate {self._output_cardinality} output labels"
                         f" from {len(labels)} input labels: {repr(labels)}")

    def __repr__(self):
        args = [self._transform.__name__]
        if self._labels is not None:
            args.append(self._labels.__name__)
        return f"StrictFunction({', '.join(args)})"
