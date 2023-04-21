import re
from typing import Optional

import numpy as np
import pandas as pd


class NumericalConverter:

    def __init__(self, ignore_unknown: bool = False):

        self.ignore_unknown = ignore_unknown

        self._allowed_methods = {
            "ignore",
            "number",
            "binary",
            "id",
            "one_hot",
            "list",
            "list_and_or",
            "map",
        }

        self.profile = {}

    def __getitem__(self, item):
        return self.profile[item]

    def __setitem__(self, key, value):
        type_name, args = self._check_profile_value(value)
        self.profile[key] = type_name, args

    def _check_profile_value(self, value) -> (str, Optional[dict[str, any]]):
        if type(value) == str:
            type_name = value
            args = {}
        elif type(value) in [tuple, list] and len(value) == 2:
            type_name, args = value
            if type(args) != dict:
                raise ValueError(f"Invalid conversion method {value}."
                                 f" Second argument must be a dictionary.")
        else:
            raise ValueError(f"Invalid conversion method {value}."
                             f" Must be either one of {self._allowed_methods} or a tuple of (method, args).")
        if type_name not in self._allowed_methods:
            raise ValueError(f"Invalid conversion method {type_name}."
                             f" Allowed methods are {self._allowed_methods}")
        return type_name, args

    def update_profile(self, profile: dict[str, any]):
        for key, value in profile.items():
            self[key] = value
        return self

    def _convert(self, df: pd.DataFrame) -> pd.DataFrame:
        new_df: pd.DataFrame = pd.DataFrame()

        for col_name in df.columns:
            col = df[col_name]

            # normalize all textual entries
            if col.dtype == object:
                col = col.str.strip()
                col = col.str.lower()

            if col_name in self.profile:
                method, args = self.profile[col_name]
            else:
                # choose the best method based on available data
                if col.dtype == object:
                    # check if this column contains a list of values
                    if col.str.contains(",").any():
                        method = "list"
                        args = {}
                    else:

                        num_unique_entries = len(col.unique())
                        if num_unique_entries <= 2:
                            method = "binary"
                            args = {}
                        elif num_unique_entries < 10:
                            method = "one_hot"
                            args = {}
                        else:
                            method = "id"
                            args = {}
                elif np.issubdtype(col.dtype, np.number):
                    method = "number"
                    args = {}
                else:
                    if self.ignore_unknown:
                        continue
                    raise ValueError(f"Cannot convert column {col_name} of type {col.dtype},"
                                     f" because no conversion method was specified and no"
                                     f" default method is available.")
                # save choice for next invocation
                self[col_name] = method, args

            if method not in self._allowed_methods:
                raise ValueError(f"Unknown conversion method {method} for column {col_name}")

            if method == "ignore":
                # simply ignore this column. It will not be added to the new dataframe.
                continue

            if method == "number":

                # convert this column to a numerical column
                col = pd.to_numeric(col, errors="coerce")

                # fill missing values
                default_value = args.get("default_value", np.nan)
                if default_value == "mean":
                    np.mean(col.to_numpy())
                elif default_value == "median":
                    np.median(col.to_numpy())
                elif default_value == "mode":
                    np.mode(col.to_numpy())
                else:
                    default_value = float(default_value)
                new_df[col_name] = col.fillna(default_value)
                continue

            if method == "binary":
                # assure that at least either positive or negative value is defined
                if "positive" not in args and "negative" not in args:
                    # infer positive and negative values from the data
                    common_positive_strings = {"yes", "true", "positive", "1"}
                    common_negative_strings = {"no", "false", "negative", "0", "none"}
                    all_values = set(col.unique())
                    positive_values = all_values.intersection(common_positive_strings)
                    negative_values = all_values.intersection(common_negative_strings)
                    if len(positive_values) == 1:
                        args["positive"] = positive_values.pop()
                    elif len(positive_values) > 1:
                        args["positive"] = positive_values
                    if len(negative_values) == 1:
                        args["negative"] = negative_values.pop()
                    elif len(negative_values) > 1:
                        args["negative"] = negative_values

                    if "positive" not in args and "negative" not in args:
                        # finally, simply pick the lexically smallest value as negative
                        all_values = list(all_values)
                        all_values.sort()
                        args["negative"] = all_values[0]

                # convert this column to a binary column
                positive = args.get("positive", [])
                negative = args.get("negative", [])
                if type(positive) == str:
                    positive = [positive]
                if type(negative) == str:
                    negative = [negative]
                if positive and negative:
                    # ensure that each value in the column is either in positive or in negative
                    all_values = set(col.unique())
                    if not all_values.issubset(positive + negative):
                        raise ValueError(f"Column {col_name} contains values that are neither positive nor negative.")
                if positive:
                    new_df[col_name] = col.isin(positive).astype(int)
                else:
                    new_df[col_name] = 1 - col.isin(negative).astype(int)
                continue

            if method == "id":
                if "values" not in args:
                    # infer values from data
                    args["values"] = sorted(list(col.unique()))
                values = args["values"]
                new_df[col_name] = col.astype(pd.CategoricalDtype(values)).cat.codes
                continue

            if method == "one_hot":
                if "values" not in args:
                    # infer values from data
                    args["values"] = set(col.unique())
                values = args["values"]
                for value in values:
                    new_df[f"{col_name}={value}"] = col == value
                continue

            if method == "list" or method == "list_and_or":
                if method == "list_and_or":
                    separators = [
                        r"\s?,?\s+and\s+",  # "and" with optional comma before
                        r"\s*,\s*",  # comma
                        r"\s+or\s+",  # "or"
                    ]
                    strips = [
                        r"\s+",
                        r"\.",
                    ]
                    if "sep" in args:
                        separators.extend(args["sep"])
                    if "strip" in args:
                        strips.extend(args["strip"])
                else:
                    separators = args.get("sep", [r"\s*,\s*"])
                    if type(separators) == str:
                        separators = [separators]
                    strips = args.get("strip", [r"\s+"])
                    if type(strips) == str:
                        strips = [strips]

                # fill all empty cells with empty string
                col = col.fillna("")

                # split
                split_col: pd.Series = col.str.split("|".join(separators))

                # strip (remove whole substring either at the end or beginning)
                prefixes = map(lambda s: f'^{s}', strips)
                suffixes = map(lambda s: f'{s}$', strips)
                fixes = list(prefixes) + list(suffixes)
                replace_expression = "|".join(fixes)
                split_col = split_col.map(lambda l: [re.sub(replace_expression, "", s) for s in l])

                if "values" not in args:
                    # infer values from data
                    possible_values = set(split_col.explode().unique())
                    args["values"] = possible_values
                for value in args["values"]:
                    new_df[f"{col_name}={value}"] = split_col.apply(lambda x: value in x)
                continue

            if method == "map":
                if "func" not in args:
                    raise ValueError(f"Missing argument 'func' for method 'map' in column {col_name}")
                func = args["func"]

                if "columns" not in args:
                    # infer number of columns from function
                    test_value = col.iloc[0]  # value to pass to function in order to determine number of columns
                    test_output = func(test_value)
                    if type(test_output) in (list, tuple):
                        num_columns = len(test_output)
                    else:
                        # func returns single value
                        num_columns = 1
                    # create column names
                    if num_columns > 1:
                        args["columns"] = [f"{col_name}[{i}]" for i in range(num_columns)]

                if "columns" not in args:
                    # this means that func returns a single value
                    # therefore, the column name stays the same
                    new_df[col_name] = col.apply(func)
                else:
                    output_column_names = args["columns"]
                    if type(output_column_names) == str:
                        output_column_names = [output_column_names]
                    for output_column_name, series in zip(output_column_names, zip(*col.map(func))):
                        new_df[output_column_name] = series

                continue

        return new_df

    def __call__(self, *args, **kwargs):
        obj = args[0]
        if isinstance(obj, pd.DataFrame):
            df = obj
        elif type(obj) == str:
            # choose read_ method based on the file extension
            if obj.endswith(".csv"):
                df = pd.read_csv(obj)
            elif obj.endswith(".tsv"):
                df = pd.read_csv(obj, sep="\t")
            elif obj.endswith(".xlsx"):
                df = pd.read_excel(obj)
            else:
                raise ValueError(f"Cannot read file {obj} because the file extension is not supported."
                                 f" Supported extensions: .csv, .tsv, .xlsx")
        else:
            raise ValueError(f"Cannot call NumericalConverter on object of type {type(obj)}")
        return self._convert(df)
