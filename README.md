# CleverTable

Low effort conversion of tabular data into numerical values,
built on top of Pandas and NumPy.

```bash
pip install clevertable
```

```python
from clevertable import NumericalConverter

nc = NumericalConverter()
df = nc("datasets/survey.xlsx")  # pandas DataFrame, containing only numerical values
arr = df.to_numpy()  # 2D numpy array
```

NumericalConverter tries to intelligently choose the best conversion method
for each column.
If you want to specify the conversion method for a column, you can do so
by passing a dictionary to the `update_profile()` method:

```python
profile = {
    "age": "number",  # already a numerical column, keep as-is
    "hospitalized": "binary",  # positive and negative values are chosen lexically
    "education_level": "one_hot",  # one-hot encoding
    "country": "id",
    "symptoms": "list",
    # a tuple can be used to pass a dict with additional arguments:
    "diagnosis": ("binary", dict(positive="cancer", negative="benign")),
}
nc = NumericalConverter()
nc.update_profile(profile)
df = nc("datasets/survey.xlsx")
```

You can also define the conversion method for columns
individually by indexing the `NumericalConverter` instance:

```python
nc["country"] = "id"
nc["diagnosis"] = "binary", dict(positive="cancer", negative="benign")
```

You can see the automatically chosen conversion methods for a
given column by indexing the `NumericalConverter` instance:

```python
method, args = nc["country"]  # indexing NumericalConverter always returns a 2-tuple
print(method)  # "id"
print(args)  # {'values': ['France', 'Germany', 'Italy']}
```

If no conversion method was defined for a given column,
(which is true for all columns if you don't pass a profile),
`NumericalConverter` chooses the most suitable conversion method
based on the provided data.
Worst case, `NumericalConverter` cannot find a suitable conversion
method, in which case it raises an exception.
You can disable this exception by passing `ignore_unknown=True`
to the constructor:
```python
nc = NumericalConverter(ignore_unknown=True)
```
However, it is safer to explicitly set the conversion
method to `"ignore"` for all columns you want to ignore.

## Supported Conversion Methods

### ignore

Drops the column.

```python
profile = {
    "registration_timestamp": "ignore",
}
```

This is chosen if no appropriate conversion method could be found.

### number

Converts a column of numbers into a column of numbers.
If invalid values are encountered (`NaN`, `inf`, `None`, etc.),
a warning is printed and the value is replaced with `np.nan`.
This can be circumvented by passing a value to the `default` argument:

```python
profile = {
    "temperature": ("number", dict(default=37.0)),
}
```

You can also specify "mean", "median", or "mode" as the default value.
This will choose the default value based on the data in the specified column:

```python
profile = {
    "temperature": ("number", dict(default="mean")),
}
```

| temperature | temperature |
|-------------|-------------|
| 37.5        | 37.5        |
| 40.0        | 40.0        |
| 38.5        | 38.5        |
|             | 38.75       |
| 39.0        | 39.0        |

### binary

For columns that only contain two possible values.
You can specify the positive and negative values
via the `positive` and `negative` arguments:

```python
profile = {
    "hospitalized": ("binary", dict(positive="yes", negative="no")),
}
```

| hospitalized | hospitalized |
|--------------|--------------|
| yes          | 1            |
| no           | 0            |
| no           | 0            |
| yes          | 1            |

If only one value is specified, all other values present in the data
are treated as instances of the other class.

It is also possible to specify more than one values for the positive and negative values:

```python
profile = {
    "hospitalized": ("binary", dict(positive={"yes", "true"}, negative={"no", "false"})),
}
```

If no positive or negative value is specified,
a set of strings commonly used to indicate positive / negative values
is tested against the available data.
If this approach is not successful, the lexically
smallest value is chosen as the `negative` argument and
the `positive` argument is left empty,
causing all other values to be treated as positive.

### id

This is the extension of the `binary` conversion method
to columns with more than two possible values.
The values are converted into integers starting at 0,
resulting in a single column of integers.

The possible values can be specified via the `values` argument:

```python
profile = {
    "country": ("id", dict(values=["France", "Germany", "Italy"])),
}
```

| country | country |
|---------|---------|
| France  | 0       |
| Italy   | 2       |
| Germany | 1       |

Their index in the list is used as the numerical value,
starting from 0.
If no values are specified, the values found in the provided
data are sorted in lexically ascending order.

### one_hot

If each entry contains one of multiple possible values.
The possible values can be specified via the `values` argument:

```python
profile = {
    "education_level": ("one_hot", dict(values={"primary", "secondary", "tertiary"})),
}
```

| education_level | education_level=primary | education_level=secondary | education_level=tertiary |
|-----------------|-------------------------|---------------------------|--------------------------|
| primary         | 1                       | 0                         | 0                        |
| secondary       | 0                       | 1                         | 0                        |
| tertiary        | 0                       | 0                         | 1                        |

If no values are specified, the possible values are inferred from the data.

### list, list_and_or

Converts lists of values into multiple binary columns.

```python
profile = {
    "symptoms": "list_and_or",
}
```

| symptoms                  | symptoms=cough | symptoms=fever | symptoms=headache |
|---------------------------|----------------|----------------|-------------------|
| fever, cough and headache | 1              | 1              | 1                 |
| headache or cough         | 1              | 0              | 1                 |

The default separator for `list` is a comma,
the default separators for `list_and_or` are comma, "and" and "or".
To specify custom separators, define a list
of strings or regular expressions via the `sep` argument:

```python
profile = {
    "symptoms": ("list", dict(sep=[
        r"\s*,\s*",  # comma
        r"\s?,?\s+and\s+",  # "and" with optional comma before
        r"\s+or\s+",  # "or"
    ], strip=[
        r"\s+",
        r"\.",
    ])),  # equivalent to using "list_and_or"
}
```

### map

This can be used to specify a custom conversion function.

The following example turns a text-column into two columns
containing the ascii code of the first and last letter.

```python
profile = {
    "name": ("map", dict(func=lambda x: (ord(x[0]), ord(x[-1])),
                         columns=("name_first_letter_ord", "name_last_letter_ord"))),
}
```

| name  | name_first_letter_ord | name_last_letter_ord |
|-------|-----------------------|----------------------|
| Alice | 97                    | 101                  |
| Bob   | 98                    | 98                   |

(Remember that by default, all text entries are converted to
lowercase before further processing.)

If no columns are specified, the number of columns is inferred
directly from the return value of the conversion function:

```python
profile = {
    "name": ("map", dict(func=lambda x: (ord(x[0]), ord(x[-1])))),
}
```

| name  | name[0] | name[1] |
|-------|---------|---------|
| Alice | 97      | 101     |
| Bob   | 98      | 98      |

If the function returns a single value,
the column name stays the same.
