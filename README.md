# dataexplainer
A Python library that turns a table of data into a short summary in plain English.

Tables and charts are hard to read for people who do not code. dataexplainer looks at a column and writes simple sentences about it, so programmers can explain their data and everyone else can understand it.

> **Status: version 0.1.0, in development.** The number describer works today. The category describer, missing-values describer, and the all-in-one `DataStory` are coming in the next phases.

## What it does

| Feature | Status |
|---|---|
| Number columns: average, lowest, highest (`NumberDescriber`) | Ready |
| Choice columns: most common answer and each share (`CategoryDescriber`) | Planned |
| Empty cells: how many and what percent (`MissingDescriber`) | Planned |
| Whole-table summary in one call (`DataStory` and `Story`) | Planned |

## Installation

Once it is published on PyPI:

```
pip install dataexplainer
```

Until then, install it from GitHub:

```
pip install git+https://github.com/roni-cakes/dataexplainer.git
```

It needs Python 3.8 or newer and installs `pandas` for you.

## Quick example

```python
import pandas as pd
from dataexplainer.number import NumberDescriber

students = pd.DataFrame({
    "hours_studied": [2, 5, 8, 10, 4, 7],
    "grade": [62, 78, 88, 98, None, 85],
})

for sentence in NumberDescriber("grade").describe(students):
    print(sentence)
```

Output:

```
The average grade is 82.2.
The lowest grade is 62 and the highest is 98.
```

Empty cells are ignored by `NumberDescriber`. A text column gives a clear `TypeError`, and a column that is not in the table gives a `KeyError`.

For a longer walk-through, run the demo:

```
python demo.py
```

## How the code is organized

```
dataexplainer/
├── dataexplainer/
│   ├── __init__.py       version information
│   ├── base.py           BaseDescriber (the parent class)
│   ├── number.py         NumberDescriber
│   ├── category.py       CategoryDescriber (planned)
│   ├── missing.py        MissingDescriber (planned)
│   ├── story.py          Story and DataStory (planned)
│   └── utils.py          small helpers
├── tests/
│   ├── test_base.py      tests for BaseDescriber
│   ├── test_number.py    tests for NumberDescriber
│   ├── test_category.py  tests for CategoryDescriber (planned)
│   ├── test_missing.py   tests for MissingDescriber (planned)
│   ├── test_story.py     tests for Story and DataStory (planned)
│   └── test_utils.py     tests for the helpers (planned)
├── demo.py               example usage
├── README.md             this file
├── setup.py              packaging
├── requirements.txt      libraries needed
└── LICENSE
```

Each source file has a matching test file, so it is easy to find the checks for any class.

- `BaseDescriber` is the parent. It stores the column name and requires every child to write its own `describe()`.
- Each describer (number, category, missing) is a child that writes sentences in its own way.
- `DataStory` will pick a describer for each column and collect the sentences into a `Story`.

## Running the tests

```
pip install pytest
python -m pytest
```

## Contributors

| Member | Classes | Tests |
|---|---|---|
| Marc Ahron Alfar (A) | `BaseDescriber`, `NumberDescriber` | `test_base.py`, `test_number.py` |
| [Unknown] (B) | `CategoryDescriber`, `MissingDescriber` | `test_category.py`, `test_missing.py` |
| [Unknown] (C) | `Story`, `DataStory` | `test_story.py` |
| [Unknown] (D) | `utils`, packaging, documentation, demo, PyPI | `test_utils.py` |

## License

MIT. See the `LICENSE` file.
