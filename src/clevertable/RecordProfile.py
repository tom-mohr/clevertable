from .Converter import Converter
from .Ignore import Ignore
from .Infer import Infer
from ._utils import _parse_converter, _flatten, _index_duplicates


def _check_and_unpack(row: list) -> dict:
    # unpack a 1-element list with a dict
    assert len(row) == 1, "Expects a 1-element list with a dict"
    val = row[0]  # unpack 1-element list
    assert isinstance(val, dict), "Expects a 1-element list with a dict"
    return val


class RecordProfile(Converter):
    def __init__(self, profile: dict[any, any] = None,
                 ignore_undefined: bool = False,
                 ignore_uninferrable: bool = False):
        """
        Works on records (dicts).
        Takes a record, applies a different converter for each key (according to the given profile)
        and outputs a record with transformed keys and values.
        The new keys are computed using the label() function of the respective converter.
        Their cardinality must match the cardinality of the output of the converter.

        For keys that are not present in the profile but appear during fit(), the Infer() converter is used.

        Keys that are not present in the profile and weren't present during fit() are simply ignored.

        :param profile: Maps keys to converters.
        :param ignore_undefined: If ``False``, all columns without a converter will be assigned a converter
               automatically. If ``True``, these columns will be ignored instead, i.e. not produce any output columns.
        :param ignore_uninferrable: If ``True``, keys which are not present in the profile and for which the converter
               cannot be inferred during ``fit()`` are ignored during transform().
        """
        self.profile: dict[any, Converter] = {}
        if profile:
            self.update(profile)  # parses converters

        self.keys: dict[any, list[any]] = {}  # cache for the output keys computed during fit()

        self.ignore_undefined = ignore_undefined
        self.ignore_uninferrable = ignore_uninferrable

    def fit(self, rows: list[list]):
        # unpack each row and check the type
        dicts = [_check_and_unpack(row) for row in rows]

        all_keys = {key for d in dicts for key in d.keys()}  # collect all possible keys present in the dicts

        # replace missing converters with Infer() or Ignore()
        for key in all_keys:
            if key not in self.profile:
                if self.ignore_undefined:
                    self.profile[key] = Ignore()
                else:
                    self.profile[key] = Infer(ignore_uninferrable=self.ignore_uninferrable)

        # now actual fit
        for key, conv in self.profile.items():
            rows = [[d[key]] for d in dicts if key in d]
            if not rows:
                raise ValueError(f"Not a single value for key '{key}' present int fit()!"
                                 f" You must at least provide one value to fit() for this key.")
                pass

            try:
                conv.fit(rows)
            except Exception as e:
                # add helpful context to error message
                raise ValueError(f"Key '{key}': {conv.__class__.__name__} converter"
                                 f" raised {e.__class__.__name__} during fit: {e}") from e

        # replace all Infer() converters with the nested inferred converter
        for key, conv in self.profile.items():
            if isinstance(conv, Infer):
                assert conv.inferred is not None, \
                    f"Infer() converter for key '{key}' did not infer a converter during fit()"
                self.profile[key] = conv.inferred

        # save the output keys
        for key, conv in self.profile.items():
            try:
                self.keys[key] = conv.labels([key])
            except Exception as e:
                # add helpful context to error message
                raise ValueError(f"Key '{key}': {conv.__class__.__name__} converter"
                                 f" raised {e.__class__.__name__} during label computation: {e}") from e

        # handle duplicate output keys
        input_keys = list(self.keys.keys())
        output_keys_flat = _flatten([self.keys[k] for k in self.keys])  # not using self.keys.values() because of order
        output_keys_flat = _index_duplicates(output_keys_flat, lambda s, i: f"{s}_{i}")
        # "unflatten" the output keys and write them back
        for input_key in input_keys:
            n = len(self.keys[input_key])  # number of output keys for this input key
            self.keys[input_key] = output_keys_flat[:n]  # take n first
            output_keys_flat = output_keys_flat[n:]  # remove n first

    def labels(self, labels: list) -> [dict[any, list]]:
        """
        :param labels: Will be ignored, as labels have been inferred from the given records during fit() already.
        """
        return [self.keys]

    def transform(self, row: list) -> list:
        """
        Transforms each value in the given dict with the respective converter.
        The returned dict has the same keys as the input dict.

        :param row: Must be a 1-element list with a dict
        :return:
        """
        input_record = _check_and_unpack(row)
        output_record = {}
        for key in input_record:
            if key not in self.profile:
                raise KeyError(f"Key not present in the profile: '{key}'")
            converter = self.profile[key]
            input_values = [input_record[key]]
            try:
                output_values = converter.transform(input_values)
            except Exception as e:
                # add helpful context to error message
                raise ValueError(f"Key '{key}': {converter.__class__.__name__} converter"
                                 f" raised {e.__class__.__name__} during transform: {e}") from e
            output_keys = self.keys[key]
            assert len(output_values) == len(output_keys), \
                f"Key '{key}': Output length of {converter.__class__.__name__} converter" \
                f" mismatches number of labels: {len(output_values)}!={len(output_keys)}." \
                f"\n\tInput:\t{[input_record[key]]}" \
                f"\n\tOutput (length {len(output_values)}):\t{output_values}" \
                f"\n\tOutput Labels (length {len(output_keys)}):\t{output_keys}"
            for out_val, out_key in zip(output_values, output_keys):
                output_record[out_key] = out_val
        return [output_record]

    def update(self, profile: dict[str, any]):
        for key, value in profile.items():
            self[key] = value

    def __getitem__(self, item):
        return self.profile[item]

    def __setitem__(self, key, value):
        self.profile[key] = _parse_converter(value)

    def __repr__(self):
        s = "{\n"
        for key, conv in self.profile.items():
            s += "\t"
            s += f"{repr(key)}: "
            s += "\n\t".join(repr(conv).split("\n"))
            s += ",\n"
        s += "}"
        return s
