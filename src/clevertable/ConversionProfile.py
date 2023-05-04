from __future__ import annotations

import math
from typing import Optional, Callable

import pandas as pd

from .DataFrameProfile import DataFrameProfile


def _get_dataframe(obj: pd.DataFrame | str) -> pd.DataFrame:
    if isinstance(obj, pd.DataFrame):
        return obj
    elif type(obj) is str:
        # choose read_ method based on the file extension
        if obj.endswith(".csv"):
            return pd.read_csv(obj)
        elif obj.endswith(".tsv"):
            return pd.read_csv(obj, sep="\t")
        elif obj.endswith(".xlsx"):
            return pd.read_excel(obj)
        else:
            raise ValueError(f"Cannot read file {obj} because the file extension is not supported."
                             f" Supported extensions: .csv, .tsv, .xlsx")
    else:
        raise ValueError(f"Cannot load DataFrame from object of type {type(obj)}")


def default_preprocessing(val: any) -> any:
    if type(val) is float:
        if math.isnan(val):
            return ""
        else:
            return val
    if type(val) == str:
        return val.strip().lower()
    return val


class ConversionProfile(DataFrameProfile):
    def __init__(self, profile: dict[str, any] = None,
                 ignore_uninferrable: bool = False,
                 pre_processing: Optional[Callable[[any], any]] = default_preprocessing):
        super().__init__(profile, ignore_uninferrable, pre_processing)

    def fit(self, obj: pd.DataFrame | str) -> 'ConversionProfile':
        """
        Fit the conversion profile to the given DataFrame.
        If a filename is given, the DataFrame is loaded from the file first.
        :param obj: DataFrame or filename
        :return: self
        """
        super().fit(_get_dataframe(obj))
        return self

    def transform(self, obj: pd.DataFrame | str) -> pd.DataFrame:
        """
        Transform the given DataFrame according to the conversion profile.
        If a filename is given, the DataFrame is loaded from the file first.
        :param obj: DataFrame or filename
        :return: transformed DataFrame
        """
        return super().transform(_get_dataframe(obj))

    def fit_transform(self, obj: pd.DataFrame | str) -> pd.DataFrame:
        """
        Fit the conversion profile to the given DataFrame and transform it.
        If a filename is given, the DataFrame is loaded from the file first.
        :param obj: DataFrame or filename
        :return: transformed DataFrame
        """
        return super().fit_transform(_get_dataframe(obj))

    def update(self, profile: dict[str, any]) -> 'ConversionProfile':
        """
        Update the conversion profile with the given profile. Works like ``dict.update()``.
        :param profile: A dictionary that maps column names to converters.
        :return: self
        """
        super().update(profile)
        return self
