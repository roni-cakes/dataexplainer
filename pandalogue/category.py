"""Describe categorical, text, and Boolean columns in plain English.

This module provides CategoryDescriber, which summarizes non-numerical
columns in a pandas DataFrame by reporting the most frequent value(s)
and the percentage breakdown of the top categories.

Empty cells and blank strings are excluded before summarizing.
"""

from __future__ import annotations

import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype

from .base import BaseDescriber
from .utils import drop_empty, format_percent, join_with_and


class CategoryDescriber(BaseDescriber):
    """Describe a column of categorical, text, or Boolean values.

    CategoryDescriber inherits from BaseDescriber. It identifies the
    most common value(s) and summarizes how answers are distributed across
    categories. If every value is unique, it reports that all answers
    differ instead.

    Empty cells (including missing values and blank strings) are ignored
    by this describer.

    Attributes:
        column (str): The name of the column being described. Read only.
        MAX_SHOWN (int): Maximum number of values listed in a single
            sentence before remaining values are summarized as
            ``"and N more"``.

    Example:
        >>> import pandas as pd
        >>> from pandalogue.category import CategoryDescriber
        >>> df = pd.DataFrame({"pet": ["cat", "dog", "cat", "bird"]})
        >>> CategoryDescriber("pet").describe(df)
        ['The most common pet is cat, with 2 of 4 answers (50%).', 'Here is how the answers split: cat 50%, bird 25% and dog 25%.']
    """

    MAX_SHOWN: int = 5
    """int: Maximum number of distinct answers displayed per sentence."""

    def describe(self, df: pd.DataFrame) -> list[str]:
        """Generate plain-English sentences describing the categorical column.

        Args:
            df (pandas.DataFrame): DataFrame containing the column.

        Returns:
            list[str]: One or two descriptive sentences summarizing the
                column's values.

        Raises:
            KeyError: If the requested column is missing from the DataFrame.
            TypeError: If the column contains numerical (non-Boolean) data.
        """
        self._check_column(df)
        values = df[self._column]
        name = self._column
        if is_numeric_dtype(values) and not is_bool_dtype(values):
            raise TypeError(
                f"Column '{name}' holds numbers, not choices. "
                "Use NumberDescriber instead."
            )

        values = drop_empty(values)
        if values.empty:
            return [f"The {name} column has no answers to describe."]

        total = len(values)
        # Sort by frequency descending, then alphabetically ascending for ties.
        groups = sorted(
            values.value_counts().items(), key=lambda pair: (-pair[1], str(pair[0]))
        )

        if total == 1:
            return [f"The only answer in {name} is {groups[0][0]}."]
        if len(groups) == 1:
            return [f"Every answer in {name} is {groups[0][0]}."]

        top_count = groups[0][1]
        if top_count == 1:
            return [f"All {total} answers in {name} are different from each other."]

        winners = [label for label, count in groups if count == top_count]
        share = f"{top_count} of {total} answers ({format_percent(top_count, total)})"
        if len(winners) == 1:
            first = f"The most common {name} is {winners[0]}, with {share}."
        else:
            names = join_with_and(winners, limit=self.MAX_SHOWN)
            first = f"The most common {name} answers are {names}, each with {share}."

        parts = [
            f"{label} {format_percent(count, total)}" for label, count in groups
        ]
        second = (
            "Here is how the answers split: "
            f"{join_with_and(parts, limit=self.MAX_SHOWN)}."
        )
        return [first, second]
