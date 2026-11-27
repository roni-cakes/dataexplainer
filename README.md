# pandalogue

A Python library that turns a table of data into a short summary in plain English.

Tables and charts are hard to read for people who do not code. pandalogue looks at a column and writes simple sentences about it, so programmers can explain their data and everyone else can understand it.

> **Status: version 0.1.0.** All features below are ready. See `docs/report2_notes.md` for what changed after the first version and why.

## What it does

| Feature | Status |
|---|---|
| Number columns: average, middle value (median), lowest, highest (`NumberDescriber`) | Not Ready |
| Small numbers shown properly (`0.0002`, not `0`) and infinite values left out with a note | Not Ready |
| Choice columns: most common answer and each share (`CategoryDescriber`) | Not Ready |
| Empty cells, including blank text: how many and what percent (`MissingDescriber`) | Not Ready |
| Date columns: where they start, end, and how many days (`DateDescriber`) | Not Ready |
| How two number columns move together, never "causes" (`RelationshipDescriber`) | Not Ready |
| Whole-table summary in one call (`DataStory` and `Story`) | Not Ready |
| `DataStory` skips ID-like columns, reads numbers saved as text, warns about mixed columns | Not Ready |
| `DataStory(max_sentences=8)` keeps only the most useful sentences | Not Ready |
| **Optional** rules: you say what counts as good or bad (`RuleDescriber`) | Not Ready |

## Installation

Once it is published on PyPI:

```
pip install pandalogue
```

Until then, install it from GitHub:

```
pip install git+https://github.com/roni-cakes/pandalogue.git
```

It needs Python 3.8 or newer and installs `pandas` for you.

## Quick example

```python
import pandas as pd
from pandalogue import NumberDescriber

students = pd.DataFrame({
    "hours_studied": [2, 5, 8, 10, 4, 7],
    "grade": [62, 78, 88, 98, None, 85],
})

for sentence in NumberDescriber("grade").describe(students):
    print(sentence)
```

Output:

```
The average grade is 82.2, and the middle value is 85.
The lowest grade is 62 and the highest is 98.
```

Empty cells are ignored by `NumberDescriber`. The first sentence says "but" instead of "and" when a few huge or tiny values pull the average far from the middle value. A text column gives a clear `TypeError`, and a column that is not in the table gives a `KeyError`.

### Describe a whole table in one call

```python
from pandalogue import DataStory

story = DataStory().tell(students)
print(story)
```

`DataStory` picks the right describer for each column and collects the sentences into a `Story`:

| The column holds... | It gets... |
|---|---|
| numbers | `NumberDescriber` |
| dates | `DateDescriber` |
| numbers saved as text (`"85"`, `"90"`) | `NumberDescriber`, plus a note that they were saved as text |
| text, categories, True/False | `CategoryDescriber` |
| a mix of numbers and words | `CategoryDescriber`, plus a "mixes numbers and words" warning |
| a name that looks like an ID (`student_id`) | nothing: one sentence says it was skipped |

Other things it does:

- A column with empty cells (including blank text such as `""` or spaces) gets one extra sentence about them.
- Two number columns that clearly move together get a sentence such as `hours_studied and grade tend to go up together (a strong link).` It never says that one causes the other. A link needs at least 5 rows where both values are filled in, and with only a handful of rows a link can be a coincidence.
- Rules are optional: `DataStory(rules={"wait_hours": {"bad_above": 3}})` (see the next section). Without rules the story has no good or bad wording.
- Settings: `DataStory(columns=[...])` describes only some columns, `include_missing=False` leaves out empty-cell sentences, `skip_ids=False` describes ID-like columns anyway, `include_relationships=False` leaves out link sentences, and `max_sentences=8` keeps only the 8 most useful sentences (every column's first sentence first, then the rest in table order; skipped-ID sentences go last). After a trimmed story, `story.left_out` says how many sentences were dropped, and `story.skipped` lists the skipped columns.

### Optional: say what counts as good or bad

The library never decides what is good or bad. A temperature of 30 is hot in one place and normal in another, and a 3-hour wait is bad at a clinic but fine for a delivery. So by default it only describes. If you want it to say what the numbers mean for you, you set the rule yourself:

```python
from pandalogue import RuleDescriber

waits = pd.DataFrame({"wait_hours": [1, 2, 4, 5, 1, 2, 1, 2, 1, 2]})

RuleDescriber("wait_hours", bad_above=3).describe(waits)
# ['2 of 10 values in wait_hours (20%) are above 3, which you set as bad.']
```

The ending "which you set as bad" shows that the judgment came from you. The rules:

| Setting | Meaning |
|---|---|
| `bad_above=3` / `bad_below=1` | values above / below this number are bad (use both for "bad outside a range") |
| `good_above=4` / `good_below=2` | values above / below this number are good |
| `good_between=(20, 28)` | values from 20 up to and including 28 are good |

"Above" and "below" do not include the cutoff itself. A rule that makes no sense is refused right away with a `ValueError`: a lower cutoff above the upper one (`bad_below=5, bad_above=3`), a reversed range (`good_between=(28, 20)`), or good and bad rules that overlap.

To use rules inside a whole-table story, pass them to `DataStory`:

```python
DataStory(rules={"wait_hours": {"bad_above": 3}}).tell(waits)
```

For the Philippine 1.0 to 5.0 grading scale, where lower is better, `RuleDescriber("grade", good_below=2, bad_above=3)` says how many grades are good and how many are failing.

Rules only work on number columns, and only on columns being described (a skipped ID column ignores its rule).

### The describers on their own

```python
from pandalogue import (
    CategoryDescriber, DateDescriber, MissingDescriber, RelationshipDescriber,
)

pets = pd.DataFrame({"pet": ["cat", "dog", "cat", "bird", None]})

CategoryDescriber("pet").describe(pets)
# ['The most common pet is cat, with 2 of 4 answers (50%).',
#  'Here is how the answers split: cat 50%, bird 25% and dog 25%.']

MissingDescriber("pet").describe(pets)
# ['The pet column has 1 empty cell out of 5 (20%).']

RelationshipDescriber("hours_studied", "grade").describe(students)
# ['hours_studied and grade tend to go up together (a strong link).']
```

`CategoryDescriber` names at most 5 answers per sentence and sums up the rest as "and N more". It gives a `TypeError` for number columns, so use `NumberDescriber` for those. `DateDescriber` gives a `TypeError` for anything that is not a date column.

For a longer walk-through, including a messy table, run the demo:

```
python demo.py
```

## How the code is organized

```
pandalogue/
├── pandalogue/
│   ├── __init__.py       version information and the public names
│   ├── base.py           BaseDescriber (the parent class)
│   ├── number.py         NumberDescriber
│   ├── category.py       CategoryDescriber
│   ├── missing.py        MissingDescriber
│   ├── date.py           DateDescriber
│   ├── relationship.py   RelationshipDescriber
│   ├── rule.py           RuleDescriber (optional)
│   ├── story.py          Story and DataStory
│   └── utils.py          shared helpers (see below)
├── tests/                unit tests
├── docs/
│   ├── uml.md            class diagram
│   ├── report2_notes.md  what changed after version one, and why
│   └── report3_notes.md  the optional rules and the contract
├── contracts.py          the contract: every class, property and method (reference only)
├── demo.py               example usage
├── setup.py              packaging
├── requirements.txt
└── LICENSE
```

- `BaseDescriber` is the parent. It stores the column name and requires every child to write its own `describe()`, which always returns a list of sentences.
- Each describer is a child that writes sentences in its own way. `RelationshipDescriber` is the only one with two columns: the first is `column`, the second is `other`. `RuleDescriber` is the optional one: it only speaks when you give it rules.
- `contracts.py` is the contract that all of these classes follow. It lists every class, property, method and error rule, and the exact sentence wording, so the parts always fit together. It is a reference file: the library does not import it.
- `DataStory` picks a describer for each column and collects the sentences into a `Story`.
- `Story` keeps the sentences grouped by column. Print it for a readable report.
- `utils.py` holds the helpers every part shares, most importantly one agreed rule for "is this cell empty?" (`None`, `NaN`, `NaT`, `""` and blank spaces all count), so the missing, category and story code always agree.

## Running the tests

```
pip install pytest
python -m pytest
python -m pytest --doctest-modules pandalogue
```

## Contributors

| Member | Letter | Owns | Tests |
|---|---|---|---|
| Marc Ahron C. Alfar (leader) | A | `base.py`, `rule.py`, `contracts.py`, `requirements.txt`, `README.md`, `docs/`, `setup.py`, `demo.py`, PyPI upload | `test_base.py`, `test_rule.py` |
| Mark Jay Macaya | B | `category.py`, `missing.py`, `date.py` | `test_category.py`, `test_missing.py`, `test_date.py` |
| Maria Taboclaon | C | `story.py`, `number.py` | `test_story.py`, `test_number.py` |
| Mc Lloyd Murillo | D | `utils.py`, `relationship.py`, `__init__.py` | `test_utils.py`, `test_relationship.py`, `test_init.py` |

## License

MIT. See the `LICENSE` file.
