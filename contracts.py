# Contract for the data-description library (package: pandalogue, formerly named dataexplainer).
# Contributors: Marc Ahron C. Alfar (leader), Mark Jay Macaya, Maria Taboclaon, Mc Lloyd Murillo
"""Contract for the library: every class, property and method it must have.

This file is a reference, not part of the installed package. Nothing in the
library imports it, and nothing here runs or prints on import. It exists so
that every class is written to the same rules and they all fit together.

Modules and the ABC each one implements:
    base          -> IDescriber              (BaseDescriber, the parent)
    number        -> IDescriber              (NumberDescriber)
    category      -> ICategoryDescriber      (CategoryDescriber)
    missing       -> IDescriber              (MissingDescriber)
    date          -> IDescriber              (DateDescriber)
    relationship  -> IRelationshipDescriber  (RelationshipDescriber)
    rule          -> IRuleDescriber          (RuleDescriber, OPTIONAL feature)
    story         -> IStory                  (Story)
                  -> IStoryTeller            (DataStory)
    utils         -> no class; its functions are listed at the end of this file

WHO IS ASSIGNED TO WHAT (a guide so everyone knows who to ask)
    BaseDescriber         (assigned person: Marc Ahron C. Alfar)
    NumberDescriber       (assigned person: Maria Taboclaon)
    CategoryDescriber     (assigned person: Mark Jay Macaya)
    MissingDescriber      (assigned person: Mark Jay Macaya)
    DateDescriber         (assigned person: Mark Jay Macaya)
    RelationshipDescriber (assigned person: Mc Lloyd Murillo)
    RuleDescriber         (assigned person: Marc Ahron C. Alfar)
    Story                 (assigned person: Maria Taboclaon)
    DataStory             (assigned person: Maria Taboclaon)
    utils.py              (assigned person: Mc Lloyd Murillo)
    __init__.py           (assigned person: Mc Lloyd Murillo)

HOW THE PIECES FIT
    * Every describer looks at ONE column of a pandas table (DataFrame) and
      returns a list of plain-English sentences. They never talk to each other.
    * DataStory is the only class that uses the others: it picks a describer
      for each column, collects the sentences, and returns a Story.
    * The describers and DataStory share the helper functions in utils.py
      (formatting, the "is this cell empty?" rule, reading numbers saved as text).
    * RuleDescriber is optional. Nothing happens unless the user supplies rules.

CONVENTIONS (apply to every module)
    * A column name must not be None and must not be empty after
      str(name).strip(). The name is stored as given (not changed).
    * Bad settings given to a constructor (empty name, impossible cutoffs,
      wrong type of setting) -> ValueError.
    * A column that is not in the table -> KeyError.
    * A column that holds the wrong kind of data for that describer
      (for example text given to NumberDescriber) -> TypeError.
      True/False columns are NOT numbers.
    * There is no custom exception: the three standard ones above are the rules.
    * describe() returns a list of str. It always returns at least one
      sentence. It never changes the table it is given.
    * An "empty cell" means None, NaN, NaT, or text that is "" or only spaces
      (see utils.empty_mask). Describers that look at values ignore empty cells.
    * Numbers in sentences are written by utils.format_number (85 not 85.0,
      at most 2 decimals, small numbers keep their first digits).
      Percents are written by utils.format_percent (at most 1 decimal).
    * Data is kept in protected attributes (leading underscore) and read
      through read-only properties. Properties that hold a collection return a
      copy, never the original.
    * Import only from the standard library, pandas, numpy and this library's
      own base.py / utils.py (DataStory also imports the describers).
      Print nothing.
    * The library describes data. It never says that one thing causes another
      and never decides on its own what is good or bad.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # only for type hints; nothing is imported when the file runs
    import pandas


# ---------------------------------------------------------------------------
# Describers: one column in, a list of sentences out
# ---------------------------------------------------------------------------

class IDescriber(ABC):
    """Looks at one column and writes sentences about it.  Module: base (and children).

    BaseDescriber (assigned person: Marc Ahron C. Alfar)
    Implemented by the parent class BaseDescriber, which holds the column name,
    checks that the column exists, and supplies the special methods. Every
    child describer inherits from it and only has to write describe().

    Required concrete classes (column is the only constructor argument unless
    shown). "Sentence templates" show the exact wording; {name} is the column
    name, {n} a number written by format_number, {pct} a percent.

    NumberDescriber(column)        number columns (not True/False)
        (assigned person: Maria Taboclaon)
        Ignores empty cells and infinite values (inf, -inf). Returns:
            no numbers left : ["The {name} column has no numbers to describe."]
            one value       : ["The only value in {name} is {n}."]
            all the same    : ["Every value in {name} is {n}."]
            otherwise       : ["The average {name} is {mean}, and the middle value is {median}.",
                               "The lowest {name} is {low} and the highest is {high}."]
        The first sentence says "but" instead of "and" when |mean - median| is
        more than 10% of (highest - lowest); otherwise "and".
        If any infinite values were left out, one more sentence is added last:
        "1 infinite value was left out." / "2 infinite values were left out."
        TypeError if the column is not numbers (text, dates and True/False
        all count as "not numbers").

    CategoryDescriber(column)      text, category and True/False columns
        (assigned person: Mark Jay Macaya)
        Ignores empty cells (including blank text). Answers are shown as text.
        At most MAX_SHOWN (5) answers are named in a sentence; the rest become
        "and N more". Equal counts are listed in alphabetical order. Returns:
            no answers   : ["The {name} column has no answers to describe."]
            one answer   : ["The only answer in {name} is {x}."]
            all the same : ["Every answer in {name} is {x}."]
            all different: ["All {total} answers in {name} are different from each other."]
            otherwise    : ["The most common {name} is {x}, with {c} of {total} answers ({pct}).",
                            "Here is how the answers split: {x} {pct}, {y} {pct} and {z} {pct}."]
        With a tie for first, the first sentence is
            "The most common {name} answers are {x} and {y}, each with {c} of {total} answers ({pct})."
        TypeError if the column holds numbers (True/False is allowed).

    MissingDescriber(column)       any kind of column
        (assigned person: Mark Jay Macaya)
        Counts empty cells with utils.empty_mask. Returns exactly one sentence:
            no rows : "The {name} column has no rows."
            none    : "No cells in {name} are empty."
            all     : "Every cell in {name} is empty ({k} of {k})."
            some    : "The {name} column has {k} empty cell(s) out of {total} ({pct})."
        Never raises TypeError.

    DateDescriber(column)          date/time columns (datetime64, with or without time zone)
        (assigned person: Mark Jay Macaya)
        Ignores empty cells (NaT). Dates are written YYYY-MM-DD, or
        YYYY-MM-DD HH:MM when any value has a time of day other than midnight.
        Returns exactly one sentence:
            no dates     : "The {name} column has no dates to describe."
            one date     : "The only date in {name} is {d}."
            all the same : "Every date in {name} is {d}."
            otherwise    : "The dates in {name} run from {first} to {last} ({k} days)."
        where the length is "1 day", "63 days", or "less than a day".
        TypeError if the column is not a date column (text that looks like a
        date is NOT a date column).

    RelationshipDescriber(column, other)   see IRelationshipDescriber
        (assigned person: Mc Lloyd Murillo)
    RuleDescriber(column, ...)             see IRuleDescriber
        (assigned person: Marc Ahron C. Alfar)

    Special methods (all describers):
        repr(d)      -> "ClassName(column='grade')"  (extra settings are
                        added for RelationshipDescriber and RuleDescriber)
        d == e       -> True only when both are the same class AND have the
                        same column (and the same extra settings, if any)
        hash(d)      -> consistent with ==, so describers work in sets and as
                        dictionary keys
    """

    @property
    @abstractmethod
    def column(self) -> str:
        """The column this describer looks at. Read only."""

    @abstractmethod
    def describe(self, df: "pandas.DataFrame") -> list:
        """Write sentences about the column.

        Returns a list of str (at least one sentence). Does not change df.
        KeyError if the column is not in df; TypeError if the column holds
        the wrong kind of data (see each class above).
        """

    @abstractmethod
    def __repr__(self) -> str:
        """Text such as "NumberDescriber(column='grade')"."""

    @abstractmethod
    def __eq__(self, other) -> bool:
        """Same class and same column (and same extra settings)."""

    @abstractmethod
    def __hash__(self) -> int:
        """Consistent with __eq__."""


class ICategoryDescriber(IDescriber):
    """A describer for choice columns.  Module: category.

    Required concrete class:
        CategoryDescriber(column)   (assigned person: Mark Jay Macaya)
    Adds one class-level setting.
    """

    MAX_SHOWN = 5
    """The most answers named in one sentence; the rest become "and N more"."""


class IRelationshipDescriber(IDescriber):
    """A describer that compares TWO number columns.  Module: relationship.

    Required concrete class:
        RelationshipDescriber(column: str, other: str)   (assigned person: Mc Lloyd Murillo)
    `column` is the first column and `other` is the second. It is still an
    IDescriber: describe(df) returns a list of sentences (exactly one here).

    The constructor raises ValueError if `other` is None or empty, or if
    `other == column` (a relationship needs two different columns).

    It uses Spearman rank correlation ("when one goes up, does the other
    usually go up too?"), computed on the rows where BOTH values are filled in
    and finite. Strength by size of the correlation r:
        |r| >= 0.7  "strong",  |r| >= 0.4  "moderate",  |r| >= 0.2  "weak",
        smaller     no clear link.

    Sentences (a = column, b = other):
        r > 0   : "{a} and {b} tend to go up together (a strong link)."
        r < 0   : "When {a} goes up, {b} tends to go down (a strong link)."
        no link : "{a} and {b} do not show a clear link."
        fewer than MIN_ROWS usable rows:
                  "There are too few rows with both {a} and {b} filled in to compare them."
        one column never changes:
                  "{x} has the same value in every row, so it cannot be compared with {y}."
    The wording only says the columns move together. It NEVER says one causes
    the other.

    KeyError if either column is not in df. TypeError if either column is not
    numbers. repr is "RelationshipDescriber(column='a', other='b')"; equality
    needs the same two columns in the same order.
    """

    MIN_ROWS = 5
    """The fewest rows with both values filled in that a comparison needs."""

    @property
    @abstractmethod
    def other(self) -> str:
        """The second column. Read only."""

    @abstractmethod
    def correlation(self, df: "pandas.DataFrame"):
        """The Spearman correlation as a float from -1 to 1.

        None if it cannot be measured (fewer than MIN_ROWS usable rows, or a
        column that never changes). KeyError / TypeError as for describe().
        """

    @staticmethod
    @abstractmethod
    def strength_word(correlation: float):
        """"strong", "moderate" or "weak" by the sizes above; None if |r| < 0.2."""


class IRuleDescriber(IDescriber):
    """OPTIONAL describer: how many values pass or break rules the USER sets.  Module: rule.

    Required concrete class:
        RuleDescriber(column: str, bad_above=None, bad_below=None,
                      good_above=None, good_below=None, good_between=None)
        (assigned person: Marc Ahron C. Alfar)

    The library never decides what is good or bad. This describer only reports
    on the cutoffs it is given, and every sentence ends with "which you set as
    bad." or "which you set as good." so it is clear the judgment is the user's.

    Rules:
        bad_above=x      values above x are bad
        bad_below=x      values below x are bad
        good_above=x     values above x are good
        good_below=x     values below x are good
        good_between=(low, high)   values from low up to AND including high are good
    "Above" and "below" do NOT include the cutoff itself. Use bad_above and
    bad_below together for "bad outside a range". Use good_between on its own,
    or good_above / good_below (one or both), never both styles.

    The constructor raises ValueError when:
        * no rule at all is given;
        * a cutoff is not a finite number (True/False, nan, inf and text all fail);
        * good_between is not a pair, or low >= high;
        * good_between is mixed with good_above or good_below;
        * a lower cutoff is above the upper one (bad_below=5 with bad_above=3,
          or good_below=5 with good_above=3);
        * some value could be both good and bad (the good and bad ranges overlap).

    describe(df) ignores empty cells and infinite values and returns, in this
    order: one sentence for the bad rule (if any), one for the good rule
    (if any), and the infinite-values sentence (if needed).
        some break it : "{k} of {total} values in {name} ({pct}) are above 3, which you set as bad."
                        ("is" when k is 1)
        none break it : "None of the {total} values in {name} are above 3, which you set as bad."
        all break it  : "All {total} values in {name} are above 3, which you set as bad."
        one value only: "The only value in {name} is above 3, which you set as bad."
                        ("is not above" when it passes)
        both cutoffs  : "... are below 1 or above 9, which you set as bad."
        good_between  : "... are between 20 and 28, which you set as good."
        no numbers    : "The {name} column has no numbers to check against your rules."
    KeyError if the column is not in df; TypeError if it is not numbers.

    repr shows only the rules that were set, e.g.
    "RuleDescriber(column='wait_hours', bad_above=3)". Two RuleDescribers are
    equal when the column and the rules are the same.
    """

    @property
    @abstractmethod
    def bad_above(self):
        """Number or None. Read only."""

    @property
    @abstractmethod
    def bad_below(self):
        """Number or None. Read only."""

    @property
    @abstractmethod
    def good_above(self):
        """Number or None. Read only."""

    @property
    @abstractmethod
    def good_below(self):
        """Number or None. Read only."""

    @property
    @abstractmethod
    def good_between(self):
        """A (low, high) tuple or None. Read only."""

    @property
    @abstractmethod
    def settings(self) -> dict:
        """Only the rules that were set, by name, in the order bad_above,
        bad_below, good_above, good_below, good_between. A new dict each time."""


# ---------------------------------------------------------------------------
# Story: the finished report, and the class that builds it
# ---------------------------------------------------------------------------

class IStory(ABC):
    """The finished summary: sentences grouped by topic.  Module: story.

    Required concrete class:
        Story(left_out: int = 0)   (assigned person: Maria Taboclaon)

    A topic is normally a column name. A sentence about two columns is filed
    under a topic such as "hours_studied and grade". A new story is empty.
    Topics keep the order in which they were first added.
    """

    @property
    @abstractmethod
    def columns(self) -> list:
        """The topics, in the order they were added. A new list each time."""

    @property
    @abstractmethod
    def sentences(self) -> list:
        """Every sentence, as one flat list, topic by topic. A new list each time."""

    @property
    @abstractmethod
    def skipped(self) -> list:
        """The columns that were skipped on purpose (such as ID columns).
        Each still has a sentence saying so. A new list each time."""

    @property
    @abstractmethod
    def left_out(self) -> int:
        """How many sentences were dropped to fit a max_sentences limit
        (0 when nothing was dropped)."""

    @abstractmethod
    def add(self, column, sentences, skipped: bool = False) -> None:
        """Add sentences to a topic.

        `sentences` is one str or a list of str. If the topic already exists,
        the new sentences go after the old ones. skipped=True records the
        column in `skipped` (once only)."""

    @abstractmethod
    def for_column(self, column) -> list:
        """A copy of one topic's sentences. KeyError if the topic is not in the story."""

    @abstractmethod
    def __len__(self) -> int:
        """The number of sentences."""

    @abstractmethod
    def __iter__(self):
        """Go through the sentences one by one."""

    @abstractmethod
    def __str__(self) -> str:
        """A readable report, one block per topic, blocks separated by a blank line:
            About grade:
              - The average grade is 80, and the middle value is 80.
        An empty story gives an empty string."""

    @abstractmethod
    def __repr__(self) -> str:
        """Text such as "Story(2 columns, 5 sentences)"."""


class IStoryTeller(ABC):
    """Picks a describer for every column and builds a Story.  Module: story.

    Required concrete class:
        DataStory(columns=None, include_missing=True, skip_ids=True,
                  include_relationships=True, max_sentences=None, rules=None)
        (assigned person: Maria Taboclaon)

    The constructor raises ValueError if max_sentences is not a whole number
    >= 1 (True/False fail), or if rules is not a dictionary of rule settings
    ({column: {setting: value}}). The rule settings are checked immediately
    (unknown setting names and bad values -> ValueError). `columns` may be a
    single name or a list.

    tell(df) works column by column, in table order (or the order of `columns`):
        1. A name that looks like an ID (skip_ids=True): the only sentence is
           "{name} looks like an ID, so it was skipped." and the column is
           recorded in Story.skipped. "Looks like an ID" means the word "id"
           is the first or last word of the name (student_id, StudentID, id).
        2. Otherwise the kind of column decides the describer (see kind_of):
               "number"       -> NumberDescriber
               "date"         -> DateDescriber
               "text_number"  -> NumberDescriber on the text read as numbers,
                                 plus "The numbers in {name} were saved as
                                 text, so they were read as numbers."
               "mixed"        -> CategoryDescriber, plus "The {name} column
                                 mixes numbers and words."
               "category"     -> CategoryDescriber
        3. If include_missing and the column has empty cells: the
           MissingDescriber sentence is added after the above.
        4. If a rule was set for the column: the RuleDescriber sentences are
           added after that. With NO rules, no good/bad wording appears at all.
        5. If include_relationships: every pair of number columns (including
           text_number) with |correlation| >= MIN_LINK (0.4) adds a topic
           "{a} and {b}" with the RelationshipDescriber sentence, after all
           the columns.
        6. If max_sentences is set and there are more sentences than that,
           the most useful are kept: every column's first sentence first,
           then link and rule sentences and each column's later sentences in
           table order; skipped-ID sentences go last. The kept sentences go
           back in their normal order and Story.left_out says how many were
           dropped.
    Rules for a column that is not in the table -> KeyError. Rules for a column
    that is not being described, or that was skipped, are ignored. A rule on a
    column that is not numbers -> TypeError.

    tell() never changes the table it is given.
    """

    MIN_LINK = 0.4
    """How strong a link (0 to 1) must be before a relationship sentence is added."""

    @property
    @abstractmethod
    def columns(self):
        """The columns to describe, as a new list; None means every column."""

    @property
    @abstractmethod
    def include_missing(self) -> bool:
        """Whether empty-cell sentences are added."""

    @property
    @abstractmethod
    def skip_ids(self) -> bool:
        """Whether ID-like columns are skipped."""

    @property
    @abstractmethod
    def include_relationships(self) -> bool:
        """Whether sentences about linked number columns are added."""

    @property
    @abstractmethod
    def max_sentences(self):
        """The most sentences a story keeps, or None for no limit."""

    @property
    @abstractmethod
    def rules(self) -> dict:
        """The rules set by the user as {column: {setting: value}}; {} when none.
        A new dict each time, so changing it changes nothing."""

    @staticmethod
    @abstractmethod
    def kind_of(series) -> str:
        """What a column really holds: "number", "date", "text_number",
        "mixed" or "category". True/False columns are "category"."""

    @staticmethod
    @abstractmethod
    def describer_for(df: "pandas.DataFrame", column) -> IDescriber:
        """The describer that fits the column: NumberDescriber for "number" and
        "text_number", DateDescriber for "date", CategoryDescriber otherwise.
        KeyError if the column is not in df."""

    @abstractmethod
    def tell(self, df: "pandas.DataFrame") -> IStory:
        """Write the story for a table.

        TypeError if df is not a pandas DataFrame. KeyError if a requested
        column (or a column in rules) is not in df."""

    @abstractmethod
    def __repr__(self) -> str:
        """Text that shows every setting, e.g.
        "DataStory(columns=None, include_missing=True, skip_ids=True,
        include_relationships=True, max_sentences=None, rules={})"."""


# ---------------------------------------------------------------------------
# utils.py: shared helper functions (functions, not classes, so listed here)
# (assigned person: Mc Lloyd Murillo)
# ---------------------------------------------------------------------------
#
# Text:
#   format_percent(part, whole) -> str      "50%", "16.7%"; "0%" if whole is 0
#   format_number(value) -> str             "85", "200,082.46", "0.0002"
#   join_with_and(items, limit=None) -> str "A, B and C"; "A, B and 2 more"
#   count_text(count, noun) -> str          "1 empty cell", "3 empty cells"
#   infinite_note(count) -> str             "1 infinite value was left out."
#
# The one agreed rule for "is this cell empty?":
#   empty_mask(series) -> Series of bool    None/NaN/NaT, "" and blank spaces are empty
#   count_empty(series) -> int
#   drop_empty(series) -> Series
#
# Reading columns that are not what they look like:
#   parse_number(text) -> float or None     plain numbers only; "007", "nan", "50%" -> None
#   text_to_numbers(series) -> Series or None   float column if EVERY filled cell is a number
#   mixes_numbers_and_words(series) -> bool
#   looks_like_id(name) -> bool             "id" is the first or last word of the name
