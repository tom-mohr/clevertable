# CleverTable

Consistent and intelligent conversion of tabular data into numerical values.<br>
Minimal configuration required.

Installation:

```bash
pip install clevertable
```

Example:

```python
from clevertable import *

profile = ConversionProfile({
    # optional: specify converters for specific columns
    "Country": OneHot(),
    "Diagnosis": Binary(positive="cancer", negative="benign"),
    "Hospitalized": Ignore(),
}, pre_processing=None)

df = profile.fit_transform("datasets/survey.xlsx")  # transformed pandas.DataFrame
```

# Tutorial

Suppose you want to convert the following table of survey results into a 2D numpy array of numbers:

| Country | Age | Diagnosis | Hospitalized | Education level | Symptoms        |
|---------|-----|-----------|--------------|-----------------|-----------------|
| China   | 32  | benign    | no           | University      | cough, fever    |
| France  | 45  | cancer    | yes          | PhD             | fever           |
| Italy   | 19  | benign    | yes          | High School     | cough           |
| Germany | 56  | cancer    | yes          | High School     | fever and cough |
| Nigeria | 23  | benign    | no           | University      | cough           |
| India   | 34  | benign    | yes          | University      | cough, fever    |
| ...     | ... | ...       | ...          | ...             | ...             |

For example, you might want to convert the `Country` column into a column of integers,
with every integer representing a different country.<br>
However:

- You don't really care which number represents which country.
- But you want to make sure that the same country always gets the same number,
  even if you add more data to the table later.
- You also want to know which integer was chosen for which country.

That's what CleverTable is for:

- First, you call `fit()` on a sample data set, which creates a fixed conversion profile.
- Then, you call `transform()` on the actual data set, and it converts the data according
  to the fixed profile.

Moreover, CleverTable does many things automatically:

- It chooses the best converter if you don't specify it.
- And then, the converter also adapts its internal state to fit the data.

Let's see how that works:

```python
from clevertable import *

table = "datasets/survey.xlsx"  # filename or pandas.DataFrame

profile = ConversionProfile()
profile.fit(table)  # chooses best converters and creates a fixed conversion profile
```

`print(profile)` will show the inferred conversion profile:

```python
{
    "Country": Enumerate('china', 'france', 'germany', ...),  # lots of countries
    "Age": Float(),
    "Diagnosis": Binary(),
    "Hospitalized": Binary(),
    "Education level": OneHot('high school', 'phd', 'university'),
    "Symptoms": ListAndOr(),
}
```

We can access the individual converters and their properties by indexing the profile with the column name:

```python
country_converter = profile["Country"]  # Enumerate('china', 'france', 'germany', ...)

# see which integer corresponds to which country:
countries_list = country_converter.values  # ['china', 'france', 'germany', ...]
```

You can now use this profile to convert data:

```python
# transform the whole table:
df = profile.transform(table)  # pandas.DataFrame
arr = df.to_numpy()  # 2D numpy array

# transform a single data point:
data_point = {"Country": "Germany"}
transformed = profile.transform_single(data_point)  # {'Country': 2}
```

The nice thing is that you can now use the fixed profile
to find out after conversion where the numerical values originated from:

```python
# find out which country corresponds to the number 2:
country_id = 2
country = profile["Country"].values[country_id]  # 'germany'
```

You may have noticed that all the strings appear in lowercase.
That is because the `ConversionProfile` pre-processes all strings to lowercase by default.
You can disable this behavior by passing `pre_processing=None` to the constructor
or setting this property after construction:

```python
profile.pre_processing = None  # disable pre-processing
profile.pre_processing = str.lower  # default behavior
profile.pre_processing = lambda s: s.strip().lower()
```

It's okay to provide a pre-processing function that doesn't work for some entries
(e.g. `str.lower` will fail for non-string entries),
because CleverTable will catch errors and ignore them during pre-processing.

You may also have noticed that the `Education level` column was converted to `OneHot()`,
even though it contains arbitrary words, just like the `Country` column.
That's because CleverTable detected that there are too many different values
in the `Country` column for a `OneHot()` converter, so it chose the `Enumerate()` converter.

But you can always override this behavior by explicitly setting the conversion method
before calling `fit()`:

```python
from clevertable import *

table = "datasets/survey.xlsx"

profile = ConversionProfile()

# explicitly specify some converters:
profile["Country"] = OneHot()
profile["Diagnosis"] = Binary(positive="cancer", negative="benign")

profile.fit(table)
```

In this example, we also made sure that the "Diagnosis" column
is choosing the correct positive and negative values.

You can also achieve the same by passing a dictionary to the constructor:

```python
from clevertable import *

table = "datasets/survey.xlsx"

profile = ConversionProfile({
    "Country": OneHot(),
    "Diagnosis": Binary(positive="cancer", negative="benign"),
}).fit(table)  # fit() returns self
```

Two final notes:

- You can ignore columns by setting their converter to `Ignore()"`.
- You can use `fit_transform()` to perform `fit()` and `transform()`
  in one step on the same data.

This leaves us with this very concise code:

```python
from clevertable import *

df = ConversionProfile({
    "Country": OneHot(),
    "Diagnosis": Binary(positive="cancer", negative="benign"),
    "Hospitalized": Ignore(),
}, pre_processing=None).fit_transform("datasets/survey.xlsx")
```

Which produces the following transformed table:

| Country=China | Country=France | ... | Country=Zimbabwe | Age | Diagnosis | Education level=High School | Education level=PhD | Education level=University | Symptoms=cough | Symptoms=fever |
|---------------|----------------|-----|------------------|-----|-----------|-----------------------------|---------------------|----------------------------|----------------|----------------|
| 1             | 0              | ... | 0                | 32  | 0         | 0                           | 0                   | 1                          | 1              | 1              |
| 0             | 1              | ... | 0                | 45  | 1         | 0                           | 1                   | 0                          | 0              | 1              |
| 0             | 0              | ... | 0                | 19  | 0         | 1                           | 0                   | 0                          | 1              | 0              |
| 0             | 0              | ... | 0                | 56  | 1         | 1                           | 0                   | 0                          | 1              | 1              |
| 0             | 0              | ... | 0                | 23  | 0         | 0                           | 0                   | 1                          | 1              | 0              |
| 0             | 0              | ... | 0                | 34  | 0         | 0                           | 0                   | 1                          | 1              | 1              |

# CLI

`pip install clevertable` also makes the command `clevertable` available
in the command line.
It can convert files with tabular data.
Execute `clevertable --help` to see what arguments can be passed to the tool:
```text
usage: clevertable [-h] [-i IGNORE [IGNORE ...]] src out

Consistent and intelligent conversion of tabular data into numerical values.

positional arguments:
  src                   Path to input file.
  out                   Path to output file.

optional arguments:
  -h, --help            show this help message and exit
  -i IGNORE [IGNORE ...], --ignore IGNORE [IGNORE ...]
                        Column names to ignore.
```
# How to Contribute

Basic workflow of contribution:

- Fork the repository
- Create a new branch
- Make your changes
- Create a pull request
- Wait for the pull request to be accepted or rejected
- If accepted, you can delete your branch
- If rejected, make the requested changes and push them to your branch
- Repeat until pull request is accepted

What to contribute:

- New converters (classes that inherit from `Converter`)
- Improvements to converter inference (logic in `Infer()` converter)
- Improvements to default preprocessing
- Make more features available through the CLI
- New tests
- New documentation, tutorials, examples
- New ideas, suggestions, bug reports → create an issue or contact me directly

# Documentation

There are only two classes that:

- `ConversionProfile`: A collection of converters.
- `Converter`: Transforms columns of data into columns of data.

## Converters

Here's a quick overview of all converters:

| Converters                  | Description                                                                       | Shorthand        | Example Usage                                                   |
|-----------------------------|-----------------------------------------------------------------------------------|------------------|-----------------------------------------------------------------|
| Basic:                      |                                                                                   |                  |                                                                 |
| [`Float()`](#float)         | Converts numbers into floats.                                                     |                  |                                                                 |
| [`Enumerate()`](#enumerate) |                                                                                   |                  |                                                                 |
| [`OneHot()`](#onehot)       |                                                                                   |                  |                                                                 |
| [`Binary()`](#binary)       | Converts a column of text into a column of integers.                              |                  |                                                                 |
| [`List()`](#list)           |                                                                                   |                  |                                                                 |
| [`ListAndOr()`](#listandor) |                                                                                   |                  |                                                                 |
| [`Map()`](#map)             |                                                                                   | dict             | {<br>&nbsp;&nbsp;"foo": 1,<br>&nbsp;&nbsp;"bar": -2,<br>}       |
| [`Const()`](#const)         | Returns a constant value.                                                         | *any*            | 42<br>"foo"                                                     |
| Text Processing:            |                                                                                   |                  |                                                                 |
| [`Strip()`](#strip)         |                                                                                   |                  |                                                                 |
| [`Split()`](#split)         |                                                                                   |                  |                                                                 |
| Combining Converters:       |                                                                                   |                  |                                                                 |
| [`Pipeline()`](#pipeline)   | Applies multiple converters in sequence.                                          | list             | [<br>&nbsp;&nbsp;Split(),<br>&nbsp;&nbsp;ForEach(Strip()),<br>] |
| [`Try()`](#try)             | Try multiple converters and returns the first one that succeeds.                  |                  |                                                                 |
| [`ForEach()`](#foreach)     | Apply the same converter to all items.                                            |                  |                                                                 |
| [`Parallel()`](#parallel)   | Apply different converters to the respective items.                               | tuple[Converter] | `(Strip(), Id(), lambda s: s[:3])`                              |
| Special:                    |                                                                                   |                  |                                                                 |
| [`Id()`](#id)               |                                                                                   |                  |                                                                 |
| [`Ignore()`](#ignore)       | Drops the column.                                                                 | None             | None                                                            |
| [`Infer()`](#infer)         |                                                                                   |                  |                                                                 |
| [`Label()`](#label)         |                                                                                   | tuple[str]       | ("A", "B", "C")<br>("A",)<br>Label("A")<br>Label("A", "B", "C") |
| Dimensionality:             |                                                                                   |                  |                                                                 |
| [`Flatten()`](#flatten)     | Flattens a list of lists into a single list. This is often needed after ForEach() |                  |                                                                 |
| [`Transpose()`](#transpose) |                                                                                   |                  |                                                                 |
| Arbitrary Functions:        |                                                                                   |                  |                                                                 |
| [`Function()`](#function)   | Applies a user-defined function to the data.                                      | *callable*       | lambda x: x**2                                                  |

---

### Float

Converts a column of numbers into a column of numbers.
If invalid values are encountered (`NaN`, `inf`, `None`, etc.),
a warning is printed and the value is replaced with `np.nan`.
This can be circumvented by passing a value to the `default` argument:

```python
"Temperature": Float(default=37.0)
```

You can also specify `"mean"`, `"median"`, or `"mode"` as the default value.
This will choose the default value based on the data in the specified column:

```python
"Temperature": Float(default="mean")
```

| Temperature | ⇒ | Temperature |
|-------------|---|-------------|
| 37.5        |   | 37.5        |
| 40.0        |   | 40.0        |
| 38.5        |   | 38.5        |
|             |   | 38.75       |
| 39.0        |   | 39.0        |

Results in:

```python
"Temperature": Float(default=38.75)
```

---

### Enumerate

This is the extension of the [`Binary()`](#binary) conversion method
to columns with more than two possible values.
The values are converted into integers starting at 0,
resulting in a single column of integers.

The possible values can be passed to the constructor:

```python
"Country": Enumerate("france", "germany", "italy")
```

| Country | ⇒ | Country |
|---------|---|---------|
| france  |   | 0       |
| italy   |   | 2       |
| germany |   | 1       |

Their index in the list is used as the numerical value.
If no values are specified, the values found in the provided
data are sorted in lexically ascending order.

---

### OneHot

If each entry contains one of multiple possible values.
The possible values can be specified via the `values` argument:

```python
"Education Level": OneHot("primary", "secondary", "tertiary")
```

| Education Level | ⇒ | Education Level=primary | Education Level=secondary | Education Level=tertiary |
|-----------------|---|-------------------------|---------------------------|--------------------------|
| primary         |   | 1                       | 0                         | 0                        |
| secondary       |   | 0                       | 1                         | 0                        |
| tertiary        |   | 0                       | 0                         | 1                        |

If no values are specified, the possible values are inferred from the data.

---

### Binary

Similar to [`Enumerate()`](#enumerate), but only for columns with two possible values,
and with some extra intelligence for this purpose.
For example, it can detect words commonly used for positive and negative values:

- Positive: `yes`, `true`, `positive`, `1`, `female`
- Negative: `no`, `false`, `negative`, `0`, `male`, `none`

Example:

```python
"Hospitalized": Binary()
```

| Hospitalized | ⇒ | Hospitalized |
|--------------|---|--------------|
| no           |   | 0            |
| yes          |   | 1            |
| false        |   | 0            |
| true         |   | 1            |
| none         |   | 0            |

Results in:

```python
"Hospitalized": Binary(positive={"yes", "true"},
                       negative={"no", "false", "none"})
```

You can also specify the positive and negative values via the `positive` and `negative` arguments:

```python
"Hospitalized": Binary(positive="yes", negative="no")
```

| Hospitalized | ⇒ | Hospitalized |
|--------------|---|--------------|
| yes          |   | 1            |
| no           |   | 0            |
| no           |   | 0            |
| yes          |   | 1            |

If only one value is specified, all other values present in the data
are treated as instances of the other class:

```python
"Time served": Binary(negative="none")
```

| Time served | ⇒ | Time served |
|-------------|---|-------------|
| none        |   | 0           |
| 1 year      |   | 1           |
| 4 years     |   | 1           |
| none        |   | 0           |

It is also possible to specify more than one values for the positive and negative values.
Example:

```python
"Hospitalized": Binary(positive={"yes", "true"}, negative={"no", "false"})
```

| Hospitalized | ⇒ | Hospitalized |
|--------------|---|--------------|
| yes          |   | 1            |
| no           |   | 0            |
| false        |   | 0            |
| true         |   | 1            |

If no positive or negative value is specified, a set of strings commonly used
to indicate positive / negative values is tested against the available data.
For instance, in the example above, the specified arguments would have been
identified automatically as positive and negative.

If this approach is not successful, the lexically smallest value is chosen as the `negative` argument and
the `positive` argument is left empty, causing all other values to be treated as positive:

```python
"Fruits": Binary()
```

| Fruits | ⇒ | Fruits |
|--------|---|--------|
| banana |   | 1      |
| apple  |   | 0      |
| kiwi   |   | 1      |
| apple  |   | 0      |

Results in:

```python
"Fruits": Binary(negative="apple")
```

---

### List

Converts lists of values into multiple binary columns.

```python
"Symptoms": List()
```

| Symptoms               | ⇒ | Symptoms=cough | Symptoms=fever | Symptoms=headache |
|------------------------|---|----------------|----------------|-------------------|
| fever, cough, headache |   | 1              | 1              | 1                 |
| headache, cough        |   | 1              | 0              | 1                 |

The default separator for `list` is a comma.<br>
The passed strings are interpreted as regular expressions.

### ListAndOr

```python
"Symptoms": ListAndOr()
```

| Symptoms                  | ⇒ | Symptoms=cough | Symptoms=fever | Symptoms=headache |
|---------------------------|---|----------------|----------------|-------------------|
| fever, cough and headache |   | 1              | 1              | 1                 |
| headache or cough         |   | 1              | 0              | 1                 |

The default separators for `list_and_or` are comma, "and" and "or".<br>
The passed strings are interpreted as regular expressions.

### Map

### Strip

### Split

### Pipeline

### Try

```python
Try(converter1, converter2, ...)
```

Returns value of the first converter that does not raise an exception,
or the original value if all converters raise an exception.
`Try()` always only applies one converter and returns its output (if it didn't fail).

```python
"Product": Try(Float(), Infer()),  # will infer the converter for the samples that cannot be converted to floats
```

| Product | ⇒ | Product |
|---------|---|---------|
| Kiwi    |   | 48      |
| Apple   |   | 0       |
| 712356  |   | 712356  |
| 261382  |   | 261382  |
| Banana  |   | 1       |
| Kiwi    |   | 48      |
| ...     |   | ...     |

This would result in the following profile after `fit()`:

```python
"Product": Try(Float(), Enumerate("Apple", "Banana", ...))
```

### ForEach

Apply the same converter to all items.

### Parallel

```python
Parallel(converter1, converter2, ...)
```

Apply different converters to the respective items.
Usually used in a Pipeline after other converters that create outputs with multiple items (e.g. `Split()`).
Also, you usually want to use `Flatten()` after this, as each individual converter will return a list of items,
even if it only contains one item.
Example:

```python
"Latitude;Longitude": [
    Split(";"),  # must always result in two items, because Parallel() has 2 converters
    Parallel(Ignore(), Float()),  # ignore latitude, convert longitude to float -> [[], [longitude]]
    Flatten(),  # -> [longitude]
]
```

| Latitude;Longitude  | ⇒ | Longitude |
|---------------------|---|-----------|
| 52.520008;13.404954 |   | 13.404954 |
| 48.137154;11.576124 |   | 11.576124 |

### Const

### Id

Identity.
Keeps the input unchanged.

### Ignore

Drops the column.

```python
"registration_timestamp": None
```

This is chosen if no appropriate conversion method could be found.

### Infer

Tries to infer the conversion method from the column name.
After `fit()`, this converter will be replaced with the inferred converter in the profile.

This is the default converter for columns where no converter is specified.
This converter can however also be used anywhere else explicitly.
Examples:

```python
"col1": [
    str.upper,
    Infer()
],
"col2": Try(Float(), Infer()),  # will infer the converter for the samples that cannot be converted to floats
```

### Label

### Flatten

### Transpose

Can transpose nested lists, given that the nested lists are of equal length.

For example, look at this elegant implementation of the [`List()`](#list) converter:

```python
"Symptoms": [
    Split(r"\s*,\s*"),  # split at comma
    ForEach(OneHot()),
    Transpose(),
    ForEach(max),
    Flatten()
]
```

`Transpose()` allows us to apply `max` to each column of the one-hot encodings
across all list elements.

### Function

This can be used to specify a custom conversion function.

The following example turns a text column into two columns containing the ascii code of the first and last letter.

```python
"Name": lambda x: (ord(x[0]), ord(x[-1]))
```

| Name  | ⇒ | Name_0 | Name_1 |
|-------|---|--------|--------|
| Alice |   | 97     | 101    |
| Bob   |   | 98     | 98     |

(Remember that by default, all text entries are converted to
lowercase before further processing.)

As you can see, the number of columns is inferred directly from the return value of the conversion function.
If the function returns a list, the resulting column names are indexed.

You can also set the labels explicitly with a lambda function
that takes the input column name as an argument and returns output column names:

```python
"Name": Function(lambda x: (ord(x[0]), ord(x[-1])),
                 labels=lambda s: [f"ord(first letter of {s})", f"ord(last letter of {s})"]),
```

| Name  | ⇒ | ord(first letter of Name) | ord(last letter of Name) |
|-------|---|---------------------------|--------------------------|
| Alice |   | 97                        | 101                      |
| Bob   |   | 98                        | 98                       |

---

## Understanding Multi-Column Converters

A converter returns two things:

- `transform()`: the items of the transformed data
- `labels()`: a label for each item

Both return values are lists.

For top-level converters, this then creates the corresponding amount of columns.
This includes the case of

- a 1-element list `[item]`, which is the case for most converters.
- an empty list `[]`, in which the result is ignored.
  (In fact, this is exactly how `Ignore()` is implemented.)

This means, however, that for top-level converters, `labels()` and `transform()`
must return the same number of items.
That is because `labels()` is used to create the output column names.
If `transform()` returns a different number of items, that will raise an error for top-level converters.

However, for nested converters, `labels()` and `transform()` can return different numbers of items.
For example `Split.labels()` always returns only one item,
because the number of items returned by `Split.transform()` varies from input to input.
Therefore, `Split()` can't be used as a top-level converter
and has to be used inside a `Pipeline` or similar devices,
so that other converters can ensure that the final output is of constant size.
