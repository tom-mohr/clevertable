from __future__ import annotations

from typing import Callable, Iterable

from .Converter import Converter


class Function(Converter):

    def __init__(self, func: callable, labels: Callable[[any], any] = None,
                 unpack_single_input: bool = None, wrap_output: bool = None):
        """

        :param func:
        :param unpack_single_input: If None, this will be determined automatically during fit(), i.e. if all values seen
        during fit() are 1-element lists, this will be set to True, otherwise False.
        If True, the input is assumed to be a 1-element list and the contained value will be passed to the function
        instead of the list itself.
        :param wrap_output: If None, this will be determined automatically during fit().
        If all outputs are non-string iterables, this will be set to False, otherwise True.
        """
        # save args for __repr__
        self.__arg_unpack_single_input = unpack_single_input
        self.__arg_wrap_output = wrap_output

        self.func = func
        self.labels_ = labels
        self.unpack_single_input = unpack_single_input
        self.wrap_output = wrap_output

    def fit(self, rows: list[list]):
        if self.unpack_single_input is None:
            # infer from data: unpack if the input is always a single value
            self.unpack_single_input = all(len(row) == 1 for row in rows)
        if self.wrap_output is None:
            # infer from data: do not wrap if output is always a non-string iterable

            rows = [self.__input_processing(row)  # this already applies the input processing chosen above
                    for row in rows]
            outputs = [self.func(row) for row in rows]
            self.wrap_output = not all(isinstance(o, Iterable) and not isinstance(o, str) for o in outputs)

    def labels(self, labels: list) -> list:
        labels = self.__input_processing(labels)

        if self.labels_ is not None:
            labels = self.labels_(labels)

        if isinstance(labels, Iterable) and not isinstance(labels, str):  # non-string iterable
            return list(labels)
        return [labels]  # wrap single values

    def __input_processing(self, row: list) -> any:
        if self.unpack_single_input:
            assert len(row) == 1, \
                f"Function {self.func.__name__} expects a single value, but got {len(row)}!"
            return row[0]
        return row

    def __output_processing(self, output: any) -> list:
        if self.wrap_output:
            return [output]
        assert isinstance(output, Iterable) and not isinstance(output, str), \
            f"Function {self.func.__name__} did not return" \
            f" a non-string iterable: {repr(output)}"
        return list(output)

    def transform(self, row: list) -> list:
        row = self.__input_processing(row)
        output = self.func(row)
        output = self.__output_processing(output)
        return output

    def __repr__(self):
        if self.labels_ is None and \
                self.__arg_unpack_single_input is None and \
                self.__arg_wrap_output is None:
            # default args have been used, so we can just print the function name
            return self.func.__name__
        else:
            # list all non-default args
            args = [self.func.__name__]
            if self.labels_ is not None:
                args.append(f"labels={self.labels_.__name__}")
            if self.__arg_unpack_single_input is not None:
                args.append(f"unpack_single_input={self.__arg_unpack_single_input}")
            if self.__arg_wrap_output is not None:
                args.append(f"wrap_output={self.__arg_wrap_output}")
            return f"Function({', '.join(args)})"
