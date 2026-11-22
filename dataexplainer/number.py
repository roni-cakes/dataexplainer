"""NumberDescriber: writes plain-English sentences for a number column."""

from pandas.api.types import is_bool_dtype, is_numeric_dtype

from .base import BaseDescriber


class NumberDescriber(BaseDescriber):
    """Describe a column of numbers in short sentences.

    It reports the average, the lowest value, and the highest value.
    Empty cells are ignored here. Counting them is the job of
    ``MissingDescriber``.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"grade": [62, 85, 98]})
        >>> NumberDescriber("grade").describe(df)
        ['The average grade is 81.67.', 'The lowest grade is 62 and the highest is 98.']
    """

    def describe(self, df):
        """Write sentences about the number column.

        Args:
            df (pandas.DataFrame): The table that holds the column.

        Returns:
            list[str]: One to two sentences about the column.

        Raises:
            KeyError: If the column is not in the table.
            TypeError: If the column does not hold numbers.
        """
        self._check_column(df)
        values = df[self._column]
        if is_bool_dtype(values) or not is_numeric_dtype(values):
            raise TypeError(f"Column '{self._column}' does not hold numbers.")

        values = values.dropna()
        name = self._column

        if values.empty:
            return [f"The {name} column has no numbers to describe."]
        if len(values) == 1:
            return [f"The only value in {name} is {self._format_number(values.iloc[0])}."]

        lowest = values.min()
        highest = values.max()
        if lowest == highest:
            return [f"Every value in {name} is {self._format_number(lowest)}."]

        return [
            f"The average {name} is {self._format_number(values.mean())}.",
            f"The lowest {name} is {self._format_number(lowest)} "
            f"and the highest is {self._format_number(highest)}.",
        ]

    @staticmethod
    def _format_number(value):
        """Turn a number into friendly text, such as 85 instead of 85.0.

        Args:
            value (float): The number to show.

        Returns:
            str: The number with at most 2 decimals and commas for thousands.
        """
        text = f"{float(value):,.2f}"
        return text.rstrip("0").rstrip(".")

