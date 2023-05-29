from __future__ import annotations

from textwrap import indent
from typing import Callable, Optional

import pandas as pd

from .RecordProfile import RecordProfile


class DataFrameProfile:
    def __init__(self, profile: dict[str, any] = None,
                 ignore_undefined: bool = False,
                 ignore_uninferrable: bool = False,
                 pre_processing: Optional[Callable[[any], any]] = str.lower):
        """
        Wraps a RecordProfile and provides a DataFrame interface.
        Behind the scenes, this class simply takes the individual
        entries of a DataFrame and feeds them as records to the
        wrapped RecordProfile.

        :param profile: A dictionary that maps column names to converters.
        :param ignore_undefined: If ``False``, all columns without a converter will be assigned a converter
               automatically. If ``True``, these columns will be ignored instead, i.e. not produce any output columns.
        :param ignore_uninferrable: If True, there is no error when a column cannot be inferred, and it will be
               processed by an Ignore() converter, leading to no output column.
        :param pre_processing: A function that is applied to each value before it is fed to the converters.
               Every time the function fails (i.e. raises an exception), the original value is used.
        """
        self.pre_processing = pre_processing
        self._record_profile = RecordProfile(profile,
                                             ignore_undefined=ignore_undefined,
                                             ignore_uninferrable=ignore_uninferrable)

    def fit(self, df: pd.DataFrame) -> 'DataFrameProfile':
        """
        Fit the profile to the given DataFrame.
        :param df: The DataFrame to fit to.
        :return: self
        """
        dicts = df.to_dict(orient="records")
        dicts = [self.__pre_process_dict(d) for d in dicts]  # pre-process each dict
        rows = [(d,) for d in dicts]  # wrap each dict in a 1-element tuple

        self._record_profile.fit(rows)

        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        dicts = df.to_dict(orient="records")
        transformed_dicts = []
        for i, d in enumerate(dicts):
            try:
                d = self.transform_single(d)
            except Exception as e:
                # add helpful context to error message
                raise Exception(f"Error during transform() of row {i}:\n"
                                f"{indent(str(e), ' ' * 4)}") from e
            transformed_dicts.append(d)
        return pd.DataFrame.from_records(transformed_dicts)

    def transform_single(self, row: dict[str, any]) -> dict[str, any]:
        row = self.__pre_process_dict(row)
        return self._record_profile.transform((row,))[0]  # wrap, transform, and unpack again

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.fit(df)
        return self.transform(df)

    def update(self, profile: dict[str, any]) -> 'DataFrameProfile':
        """
        Update the profile with the given profile. Works like ``dict.update()``.
        :param profile: A dictionary that maps column names to converters.
        :return: self
        """
        self._record_profile.update(profile)
        return self

    @property
    def column_names(self) -> dict[any, tuple]:
        """
        A dictionary that maps input column names to output column names.
        Note that the output column names are tuples, even if there is only a single
        output column for the respective input column.
        """
        return self._record_profile.keys

    def __pre_process_dict(self, d: dict[str, any]) -> dict[str, any]:
        return {k: self.__pre_process(v) for k, v in d.items()}

    def __pre_process(self, value: any) -> any:
        if self.pre_processing is None:
            return value
        try:
            return self.pre_processing(value)
        except:
            return value

    def __getitem__(self, item):
        return self._record_profile[item]

    def __setitem__(self, key, value):
        self._record_profile[key] = value

    def __repr__(self):
        return repr(self._record_profile)
