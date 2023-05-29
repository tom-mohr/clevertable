from __future__ import annotations

from abc import ABC, abstractmethod


class Converter(ABC):
    """
    Base class for all converters.
    A converter is used to convert a single column of data into one or multiple columns of data."""

    def fit(self, rows: list[tuple]):
        """The converter is presented representative sample data.
        In this method, the converter should adapt its internal state so that there will
        be no errors when transform() is called with the same data.
        Implementations of this method can make the following assumptions:

        - The given list of values contains at least one element.
        - This method will only be called once per instance.
        """
        pass

    def labels(self, labels: tuple) -> tuple:
        """Returns the labels that should be associated with the output data of this converter.
        For top-level converters, this will result in the names of the output columns.
        If the converter only results in one output column, this method should still return the
        name of the output column as a 1-element tuple.

        This method can be called as soon this converter's fit() method has been called.

        For converters for which the values returned by transform() vary in size even after fit() was called,
        this method can simply return a tuple of labels whose length matches the length of one possible output.
        This could for example simply be a one-element tuple.
        If these converters are not used as top-level converters, this is not a problem if other converters
        handle this output further and ensure a constant output size.

        If top-level converters return labels with identical names,
        the duplicated names will be made unique, e.g. by appending an index number.

        By default, this method simply returns the given labels unchanged.

        :param labels: The labels of the input data.
                       For top-level converters, this is a 1-element tuple containing the name of the
                       original column that will be converted.
        """
        return labels

    @abstractmethod
    def transform(self, row: tuple) -> tuple:
        """
        Transforms a tuple of input values into a tuple of output values.
        Input and output may be of different size, but they must be tuples.
        I.e. if the input is a single value, it will still be passed to this method as a 1-element tuple.
        If the output is a single value, it must still be returned as a 1-element tuple.

        For top-level converters, the length of the output will determine the number of columns in the converted table
        resulting from this converter.

        :param row: Tuple of values to be converted. Single values will be passed as 1-element tuples.
        """
        raise NotImplementedError()

    def __repr__(self):
        """
        Returns a string representation of this converter.
        If possible, this should be a string that can be used to create a new instance.
        A converter instantiated from this string should behave identical to this converter
        if fitted with the same data.
        """
        return f"{self.__class__.__name__}()"

    def __str__(self):
        """
        Returns a string representation of this converter.
        If possible, this should be a string that can be used to create a new instance.
        If possible, a converter instantiated from this string should behave identical to this converter
        even if fitted with different data.
        """
        return repr(self)

    def __add__(self, other):
        return [self, other]
