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

    assert arr.shape == correct_arr.shape
    assert (arr == correct_arr).all()


def test_ignore_undefined():
    df = pd.DataFrame({
        "Country": ["China", "France", "Italy", "Germany", "Nigeria", "India"],
        "Age": [32, 45, 19, 56, 23, 34],
        "Diagnosis": ["benign", "cancer", "benign", "cancer", "benign", "benign"],
        "Hospitalized": ["no", "yes", "yes", "yes", "no", "yes"],
        "Education level": ["University", "PhD", "High School", "High School", "University", "University"],
        "Symptoms": ["cough, fever", "fever", "cough", "fever and cough", "", "cough, fever"],
    })

    arr = ConversionProfile({
        "Age": Float(),
        "Diagnosis": Binary(positive="cancer", negative="benign"),
        "Hospitalized": Ignore(),
    }, ignore_undefined=True, pre_processing=None).fit_transform(df).astype(float).to_numpy()

    correct_arr = np.array([
        [32., 0.],
        [45., 1.],
        [19., 0.],
        [56., 1.],
        [23., 0.],
        [34., 0.]
    ])

    assert arr.shape == correct_arr.shape
    assert (arr == correct_arr).all()


def test_parsing():
    profile = ConversionProfile()

    profile["Test Ignore"] = None
    assert type(profile["Test Ignore"]) is Ignore

    profile["Test Map"] = {"Hello": 1, "Bye": 2}
    assert type(profile["Test Map"]) is Map

    profile["Test Try"] = Float(), 1
    assert type(profile["Test Try"]) is Try
    assert type(profile["Test Try"][0]) is Float
    assert type(profile["Test Try"][1]) is Const

    profile["Test Pipeline"] = [Strip(), Float(), 1]
    assert type(profile["Test Pipeline"]) is Pipeline
    assert type(profile["Test Pipeline"][0]) is Strip
    assert type(profile["Test Pipeline"][1]) is Float
    assert type(profile["Test Pipeline"][2]) is Const

    profile["Test Function"] = str.lower
    assert type(profile["Test Function"]) is Function
    profile["Test Function"] = lambda s: s.lower()
    assert type(profile["Test Function"]) is Function

    profile["Test Const"] = 1
    assert type(profile["Test Const"]) is Const
    profile["Test Const"] = "Constant"
    assert type(profile["Test Const"]) is Const


def test_binary():
    df = pd.DataFrame({
        "Diagnosis": ["benign", "cancer", "benign", "cancer", "benign", "benign"],
        "Country": ["China", "France", "Italy", "Germany", "Nigeria", "India"],
        "Age": [32, 45, 19, 56, 23, 34],
        "Hospitalized": ["no", "yes", "yes", "yes", "no", "yes"],
    })

    df = ConversionProfile({
        "Diagnosis": Binary(positive="cancer", negative="benign"),
        "Country": Binary(positive={"France", "India"}),
        "Age": Binary(negative=[23, 24]),
        "Hospitalized": Binary(),
    }, pre_processing=None).fit_transform(df)

    assert df["Country"].tolist() == [0, 1, 0, 0, 0, 1]
    assert df["Age"].tolist() == [1, 1, 1, 1, 0, 1]
    assert df["Diagnosis"].tolist() == [0, 1, 0, 1, 0, 0]
    assert df["Hospitalized"].tolist() == [0, 1, 1, 1, 0, 1]


def test_try():
    profile = ConversionProfile({
        "gender": [Try({"div": "diverse"}),
                   Enumerate()],
        "sex": Try(
            {"male": 55, "female": 49},
            {"male": 0, "female": 1, "non-binary": 2},
        ),
    }, pre_processing=lambda s: s.strip().lower())
    profile["numbers"] = Float(), 1000
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
        "numbers": [
            "five",
            "14",
            "42",
            "acb",
            "429",
        ],
    }))
    assert profile["gender"][1].values == ("diverse", "female", "male")
    assert df["gender"].tolist() == [0, 2, 0, 2, 1]
    assert df["sex"].tolist() == [49, 55, 49, 2, 55]
    assert df["numbers"].tolist() == [1000, 14, 42, 1000, 429]


def test_pipeline():
    profile = ConversionProfile({
        "gender": [
            lambda s: [ord(s[0]), ord(s[-1])], Label("first", "last")
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
        "mode_test": Float(default="mode"),
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
        "mode_test": [
            np.nan,
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
    assert profile["mode_test"].default == 40
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
    assert profile["name"][0].values == ("jane", "john", "tom")
    assert profile.column_names["name"] == ("name=jane", "name=john", "name=tom")
    assert profile["name2"][0].values == ("jane", "john", "tom")
    assert profile.column_names["name2"] == ("name2=jane", "name2=john", "name2=tom")

    # correct values were computed
    assert df["name=tom"].tolist() == [True, False, True, False, False]


def test_function():
    profile = ConversionProfile()

    data = pd.DataFrame({
        "Simple": ["HEY", "BYE", "HI", "BYE"],
        "Multi 1-n": ["a b", "c d", "hi bye", "bye hi"],
        "Ignore": [1, 2, 3, 4],
        "Iterables": ["Hey", "Bye", "Hi", "Bye"],
        "Simple Labels": ["Hey", "Bye", "Hi", "Bye"],
        "Multi n-n": ["a b", "c d", "hi bye", "bye hi"],
        "Func and Labels": ["a b", "c d", "hi bye", "bye hi"],
    })

    profile["Simple"] = str.lower
    profile["Multi 1-n"] = lambda s: s.split(" ")
    profile["Ignore"] = lambda s: []
    profile["Iterables"] = lambda s: (s.lower(), s.upper())
    profile["Simple Labels"] = [lambda s: [s.lower(), s.upper()], Label("Lower", "Upper")]
    profile["Multi n-n"] = [lambda s: s.split(" "), lambda l: [l[1], l[0]]]
    profile["Func and Labels"] = Function(transform=lambda s: s.split(" "),
                                          labels=lambda s: [f"First of '{s}'", f"Second of '{s}'"])

    profile.fit(data)

    # test if labels were generated correctly
    assert profile.column_names["Simple"] == ("Simple",)
    assert profile.column_names["Multi 1-n"] == ("Multi 1-n_0", "Multi 1-n_1")
    assert profile.column_names["Ignore"] == ()
    assert profile.column_names["Iterables"] == ("Iterables_0", "Iterables_1")
    assert profile.column_names["Simple Labels"] == ("Lower", "Upper")
    assert profile.column_names["Multi n-n"] == ("Multi n-n_0", "Multi n-n_1")
    assert profile.column_names["Func and Labels"] == ("First of 'Func and Labels'", "Second of 'Func and Labels'")

    df = profile.transform(data)

    # test values
    assert df["Simple"].tolist() == ["hey", "bye", "hi", "bye"]
    assert df["Multi 1-n_0"].tolist() == ["a", "c", "hi", "bye"]
    assert df["Multi 1-n_1"].tolist() == ["b", "d", "bye", "hi"]
    assert df["Iterables_0"].tolist() == ["hey", "bye", "hi", "bye"]
    assert df["Iterables_1"].tolist() == ["HEY", "BYE", "HI", "BYE"]
    assert df["Multi n-n_0"].tolist() == ["b", "d", "bye", "hi"]
    assert df["Multi n-n_1"].tolist() == ["a", "c", "hi", "bye"]


def test_function_label_generation():
    df = pd.DataFrame({
        "Column 1": [1, 2, 7, 8],
        "Column 2": [5, 6, 3, 4],
        "Column 3": [13, 14, 1, 2],
    })

    profile = ConversionProfile()
    profile["Column 1", "Column 2"] = min
    profile[("Column 1", "Column 2"), "Column 3"] = [Parallel(min, Id()), Flatten(), max]

    profile.fit(df)

    # label generation
    assert profile.column_names["Column 1", "Column 2"] == ("Column 1, Column 2",)
    assert profile.column_names[("Column 1", "Column 2"), "Column 3"] == ("('Column 1', 'Column 2'), Column 3",)


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


def test_parallel():
    pass  # todo


def test_record_multi_column():
    df = pd.DataFrame({
        "Column 1": [1, 2, 7, 8],
        "Column 2": [5, 6, 3, 4],
        "Column 3": [13, 14, 1, 2],
    })

    profile = ConversionProfile()
    profile["Column 1", "Column 2"] = [min, Label("A")]
    profile[("Column 1", "Column 2"), "Column 3"] = [Parallel(min, Id()), Flatten(), max, Label("B")]

    profile.fit(df)
    df = profile.transform(df)

    assert df["A"].tolist() == [1, 2, 3, 4]
    assert df["B"].tolist() == [13, 14, 3, 4]
