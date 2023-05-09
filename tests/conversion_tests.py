import numpy as np
import pandas as pd

from clevertable import *


def general_test():
    df = pd.DataFrame({
        "Country": ["China", "France", "Italy", "Germany", "Nigeria", "India"],
        "Age": [32, 45, 19, 56, 23, 34],
        "Diagnosis": ["benign", "cancer", "benign", "cancer", "benign", "benign"],
        "Hospitalized": ["no", "yes", "yes", "yes", "no", "yes"],
        "Education level": ["University", "PhD", "High School", "High School", "University", "University"],
        "Symptoms": ["cough, fever", "fever", "cough", "fever and cough", "", "cough, fever"],
    })

    arr = ConversionProfile({
        "Country": OneHot(),
        "Diagnosis": Binary(positive="cancer", negative="benign"),
        "Hospitalized": Ignore(),
    }, pre_processing=None).fit_transform(df).astype(float).to_numpy()

    correct_arr = np.array([
        [1., 0., 0., 0., 0., 0., 32., 0., 0., 0., 1., 1., 1.],
        [0., 1., 0., 0., 0., 0., 45., 1., 0., 1., 0., 0., 1.],
        [0., 0., 0., 0., 1., 0., 19., 0., 1., 0., 0., 1., 0.],
        [0., 0., 1., 0., 0., 0., 56., 1., 1., 0., 0., 1., 1.],
        [0., 0., 0., 0., 0., 1., 23., 0., 0., 0., 1., 1., 0.],
        [0., 0., 0., 1., 0., 0., 34., 0., 0., 0., 1., 1., 1.]
    ])

    assert (arr == correct_arr).all()


def test_parsing():
    profile = ConversionProfile()

    profile["ignore"] = None
    assert type(profile["ignore"]) is Ignore

    profile["pipeline"] = [None, None]
    assert type(profile["pipeline"]) is Pipeline

    profile["function"] = lambda s: s[:3]
    assert type(profile["function"]) is Function


def test_try():
    profile = ConversionProfile({
        "gender": [Try({"div": "diverse"}),
                   Enumerate()],
        "sex": Try(
            {"male": 55, "female": 49},
            {"male": 0, "female": 1, "non-binary": 2},
        ),
    }, pre_processing=lambda s: s.strip().lower())
    df = profile.fit_transform(pd.DataFrame({
        "gender": [
            "diverse",
            "male",
            "div",
            "male",
            "female",
        ],
        "sex": [
            "female",
            "male",
            " Female",
            "non-binary",
            "MALE",
        ],
    }))
    assert profile["gender"][1].values == ["diverse", "female", "male"]
    assert df["gender"].tolist() == [0, 2, 0, 2, 1]
    assert df["sex"].tolist() == [49, 55, 49, 2, 55]


def test_pipeline():
    profile = ConversionProfile({
        "gender": [
            lambda s: [ord(s[0]), ord(s[-1])], ("first", "last")
        ],
    })
    df = profile.fit_transform(pd.DataFrame({
        "gender": [
            "diverse",
            "male",
            "div",
            "male",
            "female",
        ],
    }))
    assert df["first"].tolist() == [100, 109, 100, 109, 102]
    assert df["last"].tolist() == [101, 101, 118, 101, 101]


def test_numbers():
    profile = ConversionProfile({
        "age": Float(default="mean"),
        "numbers_with_nan": Float(default=-1),
    })
    df_src = pd.DataFrame({
        "age": [
            "retired",
            "12.5",
            39,
            "40",
            40,
        ],
        "numbers_with_nan": [
            np.nan,
            "12.5",
            39,
            "40",
            40,
        ],
    })
    profile.fit(df_src)
    df = profile.transform(df_src)

    assert profile["age"].default == 32.875
    assert df["age"].tolist() == [32.875, 12.5, 39.0, 40.0, 40.0]
    assert df["numbers_with_nan"].tolist() == [-1.0, 12.5, 39.0, 40.0, 40.0]


def tests_lists():
    profile = ConversionProfile()
    df = profile.fit_transform(pd.DataFrame({
        "name": [
            "Tom, Jane, John, Jane",
            "Jane, John",
            "Tom,John,,and Jane",
            "Jane",
            "",  # important check: empty entries
        ],
        "name2": [
            "Tom, John, Jane",
            "Jane, John",
            "Tom, ,John,",  # empty entries should be ignored
            "Jane",
            "",
        ]
    }))

    # correct converters were inferred
    assert type(profile["name"]) is ListAndOr
    assert type(profile["name2"]) is List

    # correct columns were created
    assert profile["name"][0].values == ["jane", "john", "tom"]
    assert profile.column_names["name"] == ["name=jane", "name=john", "name=tom"]
    assert profile["name2"][0].values == ["jane", "john", "tom"]
    assert profile.column_names["name2"] == ["name2=jane", "name2=john", "name2=tom"]

    # correct values were computed
    assert df["name=tom"].tolist() == [True, False, True, False, False]


def test_inference():
    pass  # todo


def test_multi_column():
    pass  # todo


def test_duplicated_column_names():
    pass  # todo


def test_add_to_pipeline():
    profile = ConversionProfile()
    profile["Test"] = Float()
    profile["Test"] += Binary()
    profile["Test"] += OneHot()
    assert type(profile["Test"]) == Pipeline
    assert type(profile["Test"][0]) == Float
    assert type(profile["Test"][1]) == Binary
    assert type(profile["Test"][2]) == OneHot
