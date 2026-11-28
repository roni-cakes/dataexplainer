"""RuleDescriber: says which values pass or break rules that YOU set.

This describer is optional. The library never decides what is good or bad on
its own, because that depends on the situation (30 degrees is hot in one place
and normal in another). It only reports on the rules the user gives it.
"""

import math

import numpy as np
from pandas.api.types import is_bool_dtype, is_numeric_dtype

from .base import BaseDescriber
from .utils import format_number, format_percent, infinite_note

_INFINITY = float("inf")


def _check_cutoff(label, value):
    """Make sure a cutoff is a plain, finite number (not True/False, not nan).

    Args:
        label (str): The setting's name, used in the error message.
        value (int or float): The cutoff to check.

    Raises:
        ValueError: If it is not a finite number.
    """
    is_number = isinstance(value, (int, float, np.integer, np.floating))
    if isinstance(value, (bool, np.bool_)) or not is_number or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number.")


def _contains(interval, point):
    """Tell whether a number sits inside an interval ``(low, high, low_closed, high_closed)``."""
    low, high, low_closed, high_closed = interval
    above_low = low < point or (low == point and low_closed)
    below_high = point < high or (point == high and high_closed)
    return above_low and below_high


def _overlap(first, second):
    """Tell whether two intervals share at least one number."""
    low = max(first[0], second[0])
    high = min(first[1], second[1])
    if low < high:
        return True
    if low > high:
        return False
    return _contains(first, low) and _contains(second, low)


class RuleDescriber(BaseDescriber):
    """Say how many values in a number column pass or break your own rules.

    You choose what counts as bad and what counts as good. Nothing is built in.

    Bad rules (use one or both):
        * ``bad_above``: values above this number are bad.
        * ``bad_below``: values below this number are bad.

    Good rules (use ``good_between`` on its own, or one or both of the other two):
        * ``good_above``: values above this number are good.
        * ``good_below``: values below this number are good.
        * ``good_between``: a pair ``(low, high)``; values from ``low`` up to
          and including ``high`` are good.

    "Above" and "below" do not include the cutoff itself. At least one rule is
    needed. Empty cells and infinite values are ignored (infinite values are
    mentioned in a last sentence).

    Every sentence ends with "which you set as bad" or "which you set as good",
    so it is clear that the judgment came from you.

    Attributes:
        column (str): The column to check (read only).
        bad_above, bad_below, good_above, good_below (int, float or None):
            The cutoffs you set (read only).
        good_between (tuple or None): The ``(low, high)`` range (read only).
        settings (dict): Only the rules that were set, by name (read only).

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"wait_hours": [1, 2, 4, 5, 1, 2, 1, 2, 1, 2]})
        >>> RuleDescriber("wait_hours", bad_above=3).describe(df)
        ['2 of 10 values in wait_hours (20%) are above 3, which you set as bad.']
    """

    def __init__(
        self,
        column,
        bad_above=None,
        bad_below=None,
        good_above=None,
        good_below=None,
        good_between=None,
    ):
        """Create a describer for one column and your rules.

        Args:
            column (str): The column to check.
            bad_above (int or float, optional): Values above this are bad.
            bad_below (int or float, optional): Values below this are bad.
            good_above (int or float, optional): Values above this are good.
            good_below (int or float, optional): Values below this are good.
            good_between (tuple, optional): ``(low, high)``; values in this
                range (ends included) are good.

        Raises:
            ValueError: If the column name is empty, no rule is given, a cutoff
                is not a finite number, ``good_between`` is not a pair with
                ``low`` smaller than ``high``, ``good_between`` is mixed with
                ``good_above`` or ``good_below``, a lower cutoff is above the
                upper one (such as ``bad_below=5`` with ``bad_above=3``), or a
                value could be both good and bad.
        """
        super().__init__(column)

        singles = {
            "bad_above": bad_above,
            "bad_below": bad_below,
            "good_above": good_above,
            "good_below": good_below,
        }
        for label, value in singles.items():
            if value is not None:
                _check_cutoff(label, value)

        if good_between is not None:
            if not isinstance(good_between, (tuple, list)) or len(good_between) != 2:
                raise ValueError("good_between must be a pair like (20, 28).")
            low, high = good_between
            _check_cutoff("good_between low", low)
            _check_cutoff("good_between high", high)
            if low >= high:
                raise ValueError(
                    "good_between must be (low, high) with low smaller than high."
                )
            good_between = (low, high)

        if all(value is None for value in singles.values()) and good_between is None:
            raise ValueError(
                "Give at least one rule, such as bad_above=3 or good_between=(20, 28)."
            )
        if good_between is not None and (good_above is not None or good_below is not None):
            raise ValueError(
                "Use good_between on its own, not together with good_above or good_below."
            )

        # Each rule as a stretch of the number line: (low, high, low_closed, high_closed)
        def above(x):
            """Return the stretch of the number line above x (x itself is not included)."""
            return (x, _INFINITY, False, False)

        def below(x):
            """Return the stretch of the number line below x (x itself is not included)."""
            return (-_INFINITY, x, False, False)

        if bad_above is not None and bad_below is not None:
            if _overlap(above(bad_above), below(bad_below)):
                raise ValueError("bad_below must not be higher than bad_above.")
        if good_above is not None and good_below is not None:
            if _overlap(above(good_above), below(good_below)):
                raise ValueError("good_below must not be higher than good_above.")

        bad_ranges = []
        if bad_above is not None:
            bad_ranges.append(above(bad_above))
        if bad_below is not None:
            bad_ranges.append(below(bad_below))
        good_ranges = []
        if good_above is not None:
            good_ranges.append(above(good_above))
        if good_below is not None:
            good_ranges.append(below(good_below))
        if good_between is not None:
            good_ranges.append((good_between[0], good_between[1], True, True))
        for bad_range in bad_ranges:
            for good_range in good_ranges:
                if _overlap(bad_range, good_range):
                    raise ValueError(
                        "A value could be both good and bad. "
                        "Change the cutoffs so the good and bad rules do not overlap."
                    )

        self._bad_above = bad_above
        self._bad_below = bad_below
        self._good_above = good_above
        self._good_below = good_below
        self._good_between = good_between

    @property
    def bad_above(self):
        """int, float or None: Values above this are bad (read only)."""
        return self._bad_above

    @property
    def bad_below(self):
        """int, float or None: Values below this are bad (read only)."""
        return self._bad_below

    @property
    def good_above(self):
        """int, float or None: Values above this are good (read only)."""
        return self._good_above

    @property
    def good_below(self):
        """int, float or None: Values below this are good (read only)."""
        return self._good_below

    @property
    def good_between(self):
        """tuple or None: The ``(low, high)`` range that is good (read only)."""
        return self._good_between

    @property
    def settings(self):
        """dict: Only the rules that were set, by name (a new dict each time)."""
        everything = {
            "bad_above": self._bad_above,
            "bad_below": self._bad_below,
            "good_above": self._good_above,
            "good_below": self._good_below,
            "good_between": self._good_between,
        }
        return {label: value for label, value in everything.items() if value is not None}

    def describe(self, df):
        """Write one sentence for the bad rule and one for the good rule.

        Args:
            df (pandas.DataFrame): The table that holds the column.

        Returns:
            list[str]: One sentence per kind of rule that was set (bad first,
            then good), plus a last sentence if infinite values were left out.
            If the column has no usable numbers, one sentence says so.

        Raises:
            KeyError: If the column is not in the table.
            TypeError: If the column does not hold numbers.
        """
        self._check_column(df)
        values = df[self._column]
        name = self._column
        if is_bool_dtype(values) or not is_numeric_dtype(values):
            raise TypeError(f"Column '{name}' does not hold numbers.")

        numbers = values.dropna().astype(float).to_numpy()
        infinite = np.isinf(numbers)
        notes = [infinite_note(int(infinite.sum()))] if infinite.any() else []
        numbers = numbers[~infinite]

        if len(numbers) == 0:
            return [f"The {name} column has no numbers to check against your rules."] + notes

        sentences = []
        if self._bad_above is not None or self._bad_below is not None:
            mask, condition = self._one_sided(numbers, self._bad_above, self._bad_below)
            sentences.append(self._sentence(name, int(mask.sum()), len(numbers), condition, "bad"))

        if self._good_between is not None:
            low, high = self._good_between
            mask = (numbers >= low) & (numbers <= high)
            condition = f"between {format_number(low)} and {format_number(high)}"
            sentences.append(self._sentence(name, int(mask.sum()), len(numbers), condition, "good"))
        elif self._good_above is not None or self._good_below is not None:
            mask, condition = self._one_sided(numbers, self._good_above, self._good_below)
            sentences.append(self._sentence(name, int(mask.sum()), len(numbers), condition, "good"))

        return sentences + notes

    @staticmethod
    def _one_sided(numbers, above, below):
        """Find the values above and/or below a cutoff, and name the condition.

        Returns:
            tuple: ``(mask, text)``, where ``mask`` marks the matching values
            and ``text`` is such as ``"above 3"`` or ``"below 1 or above 3"``.
        """
        mask = np.zeros(len(numbers), dtype=bool)
        parts = []
        if below is not None:
            mask |= numbers < below
            parts.append(f"below {format_number(below)}")
        if above is not None:
            mask |= numbers > above
            parts.append(f"above {format_number(above)}")
        return mask, " or ".join(parts)

    @staticmethod
    def _sentence(name, count, total, condition, label):
        """Write the sentence for one kind of rule (see ``describe``)."""
        ending = f"which you set as {label}."
        if total == 1:
            verb = "is" if count else "is not"
            return f"The only value in {name} {verb} {condition}, {ending}"
        if count == 0:
            return f"None of the {total} values in {name} are {condition}, {ending}"
        if count == total:
            return f"All {total} values in {name} are {condition}, {ending}"
        verb = "is" if count == 1 else "are"
        share = format_percent(count, total)
        return f"{count} of {total} values in {name} ({share}) {verb} {condition}, {ending}"

    def __repr__(self):
        """Return text such as ``RuleDescriber(column='wait_hours', bad_above=3)``."""
        shown = "".join(f", {label}={value!r}" for label, value in self.settings.items())
        return f"{self.__class__.__name__}(column={self._column!r}{shown})"

    def __eq__(self, other):
        """Equal when it is the same kind, with the same column and the same rules."""
        if not isinstance(other, RuleDescriber):
            return NotImplemented
        return self._column == other._column and self.settings == other.settings

    def __hash__(self):
        """Keep describers usable in sets and as dictionary keys."""
        return hash((type(self).__name__, self._column, tuple(self.settings.items())))

