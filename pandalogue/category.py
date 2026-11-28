"""Describer for category, text, and boolean columns."""

from collections import Counter
import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype

from base import BaseDescriber
from category import ICategoryDescriber  # or `from interfaces import ICategoryDescriber` if kept in one file
from utils import empty_mask, format_number, format_percent


class CategoryDescriber(BaseDescriber, ICategoryDescriber):
    """Describes text, category, and True/False columns (not numbers)."""

    MAX_SHOWN = 5

    def describe(self, df: pd.DataFrame) -> list:
        if self.column not in df.columns:
            raise KeyError(f"Column {self.column!r} is not in the table.")

        series = df[self.column]

        # True/False is allowed; other numeric types (int/float/etc.) are not.
        if is_numeric_dtype(series.dtype) and not is_bool_dtype(series.dtype):
            raise TypeError(f"Column {self.column!r} holds numbers, not categories.")

        not_empty = ~empty_mask(series)
        values = [str(v) for v in series[not_empty]]
        total = len(values)

        if total == 0:
            return [f"The {self.column} column has no answers to describe."]

        counts = Counter(values)
        # Sort by count descending, then alphabetically ascending for ties.
        ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))

        distinct_count = len(ordered)
        if distinct_count == 1:
            only_val, only_count = ordered[0]
            if total == 1:
                return [f"The only answer in {self.column} is {only_val}."]
            return [f"Every answer in {self.column} is {only_val}."]

        if distinct_count == total:
            return [f"All {format_number(total)} answers in {self.column} are different from each other."]

        top_count = ordered[0][1]
        top_tied = [val for val, cnt in ordered if cnt == top_count]
        pct_top = format_percent((top_count / total) * 100)
        total_fmt = format_number(total)

        if len(top_tied) >= 2:
            x, y = top_tied[0], top_tied[1]
            first = (
                f"The most common {self.column} answers are {x} and {y}, "
                f"each with {format_number(top_count)} of {total_fmt} answers ({pct_top})."
            )
        else:
            x = ordered[0][0]
            first = (
                f"The most common {self.column} is {x}, "
                f"with {format_number(top_count)} of {total_fmt} answers ({pct_top})."
            )

        shown = ordered[: self.MAX_SHOWN]
        remaining = distinct_count - len(shown)
        parts = [f"{val} {format_percent((cnt / total) * 100)}" for val, cnt in shown]

        if remaining > 0:
            split_text = ", ".join(parts) + f" and {format_number(remaining)} more"
        elif len(parts) > 1:
            split_text = ", ".join(parts[:-1]) + f" and {parts[-1]}"
        else:
            split_text = parts[0]

        second = f"Here is how the answers split: {split_text}."
        return [first, second]
