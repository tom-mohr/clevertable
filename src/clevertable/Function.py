from __future__ import annotations

from typing import Callable, Iterable

from .StrictFunction import StrictFunction


class Function(StrictFunction):

    def __init__(self, transform: callable, labels: Callable[[any], any] = None):
        """
        Creates a custom converter from a custom ``transform()`` function
        (and optionally, a custom ``labels()`` function).
        This is a handy way to create a converter that doesn't implement ``fit()`` (i.e. doesn't have a state).

        Unlike ``StrictFunction``, this class can handle functions that don't accept or return tuples,
        which often allows for more concise code.

        This is achieved during ``fit()`` as follows:

        1. If all incoming items are 1-element tuples, it sets a flag ``UNPACK_OUTPUT`` to always
           unpack the element before passing them to the wrapped function during ``transform()``.
        2. If during ``fit()`` the wrapped function doesn't return tuples,
           it tries to turn that output into a tuple:
            - If the output is always a non-string iterable, it will simply set a
              flag ``CONVERT_ITERABLE`` to always convert the iterable output into a tuple during ``transform()``.
            - Otherwise, it sets a flag ``WRAP_OUTPUT`` to always wrap the output in a
              1-element tuple during ``transform()``.

        A similar logic is applied to the labels.
        See :class:`StrictFunction` for details.

        :param transform: The function to wrap. Turns input into output.
        :param labels: Turns incoming labels into output labels.
        """
        super().__init__(self.__fixed_transform,
                         labels and self.__fixed_labels)

        self.__transform = transform
        self.__labels = labels

        self._unpack_single_input: bool = None
        self._convert_iterable_output: bool = None
        self._wrap_output: bool = None

    def __fixed_transform(self, row: tuple) -> tuple:
        row = self.__input_processing(row)
        row = self.__transform(row)
        row = self.__output_processing(row)
        return row

    def __fixed_labels(self, labels: tuple) -> tuple:
        # should only be called if given labels func is not None

        if len(labels) == 1:
            labels = labels[0]  # unpack 1-element tuples

        labels = self.__labels(labels)

        if isinstance(labels, tuple):
            return labels
        # turn the output into a tuple:
        if isinstance(labels, Iterable) and not isinstance(labels, str):  # non-string iterable
            return tuple(labels)
        return (labels,)  # wrap single values

    def fit(self, rows: list[tuple]):
        self.__set_flags(rows)
        super().fit(rows)

    def __set_flags(self, rows: list[tuple]):
        """
        This method looks at the fit data and determines how the input and output must be processed
        during ``transform()`` in order to make the wrapped function work.
        """
        # infer from data: unpack if the input is always a 1-element tuple
        self._unpack_single_input = all(isinstance(row, tuple) and len(row) == 1 for row in rows)

        # apply input processing accordingly
        rows = [self.__input_processing(row)
                for row in rows]

        # transform data with func
        rows = [self.__transform(row) for row in rows]

        self._convert_iterable_output = False
        self._wrap_output = False
        if not all(isinstance(o, tuple) for o in rows):
            # turn the output into a tuple:
            if all(isinstance(o, Iterable) and not isinstance(o, str) for o in rows):  # non-string iterables
                self._convert_iterable_output = True
            else:
                self._wrap_output = True

    def __input_processing(self, row: tuple) -> any:
        if self._unpack_single_input:
            assert len(row) == 1, \
                f"Function {self.__transform.__name__} expects a single value, but got {len(row)}!"
            return row[0]
        return row

    def __output_processing(self, output: any) -> tuple:
        if self._wrap_output:
            return (output,)
        if self._convert_iterable_output:
            assert isinstance(output, Iterable) and not isinstance(output, str), \
                f"Function {self.__transform.__name__} did not return" \
                f" a non-string iterable: {repr(output)}"
            return tuple(output)
        assert isinstance(output, tuple), \
            f"Function {self.__transform.__name__} did not return a tuple: {repr(output)}"
        return output

    def __repr__(self):
        if self.__labels is None:
            # callables are parsed to Function()
            return self.__transform.__name__
        return f"Function({self.__transform.__name__}, {self.__labels.__name__})"
