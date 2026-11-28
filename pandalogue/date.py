"""Describe date and datetime columns in plain English.

This module provides DateDescriber, which summarizes datetime columns in a
pandas DataFrame by reporting the earliest date, latest date, and the total
span of time covered.

Empty cells (``NaT``) are excluded before summarizing. Times of day are
included only when at least one timestamp is not at midnight.
"""

from pandas.api.types import is_datetime64_any_dtype

from .base import BaseDescriber
from .utils import count_text


class DateDescriber(BaseDescriber):
    """Describe a column of date or datetime values.

    DateDescriber inherits from BaseDescriber. It reports the start date,
    end date, and the span in days between them. If all timestamps occur
    at midnight, only the calendar date is shown; otherwise, hours and
    minutes are included.

    Missing values (``NaT``) are ignored by this describer.

    Attributes:
        column (str): The name of the column being described. Read only.

    Example:
        >>> import pandas as pd
        >>> from pandalogue.date import DateDescriber
        >>> df = pd.DataFrame({"when": pd.to_datetime(["2026-01-01", "2026-03-05"])})
        >>> DateDescriber("when").describe(df)
        ['The dates in when run from 2026-01-01 to 2026-03-05 (63 days).']
    """

    def describe(self, df):
        """Generate a plain-English sentence describing the date column.

        Args:
            df (pandas.DataFrame): DataFrame containing the date column.

        Returns:
            list[str]: A list containing exactly one descriptive sentence.

        Raises:
            KeyError: If the requested column is missing from the DataFrame.
            TypeError: If the column does not contain datetime values.
        """
        self._check_column(df)
        values = df[self._column]
        name = self._column
        if not is_datetime64_any_dtype(values):
            raise TypeError(f"Column '{name}' does not hold dates.")

        values = values.dropna()
        if values.empty:
            return [f"The {name} column has no dates to describe."]

        pattern = "%Y-%m-%d"
        if (values != values.dt.normalize()).any():
            pattern = "%Y-%m-%d %H:%M"
        first = values.min()
        last = values.max()

        if len(values) == 1:
            return [f"The only date in {name} is {first.strftime(pattern)}."]
        if first == last:
            return [f"Every date in {name} is {first.strftime(pattern)}."]

        days = (last - first).days
        length = count_text(days, "day") if days >= 1 else "less than a day"
        return [
            f"The dates in {name} run from {first.strftime(pattern)} "
            f"to {last.strftime(pattern)} ({length})."
        ]
