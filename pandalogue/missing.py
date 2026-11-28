"""Describer for missing/empty cells in any column."""

import pandas as pd

from base import BaseDescriber
from utils import empty_mask, format_number, format_percent


class MissingDescriber(BaseDescriber):
    """Counts empty cells in a column without raising TypeError."""

    def describe(self, df: pd.DataFrame) -> list:
        if self.column not in df.columns:
            raise KeyError(f"Column {self.column!r} is not in the table.")

        series = df[self.column]
        total = len(series)

        if total == 0:
            return [f"The {self.column} column has no rows."]

        empty_count = int(empty_mask(series).sum())
        total_fmt = format_number(total)
        k_fmt = format_number(empty_count)

        if empty_count == 0:
            return [f"No cells in {self.column} are empty."]

        if empty_count == total:
            return [f"Every cell in {self.column} is empty ({k_fmt} of {k_fmt})."]

        pct = format_percent((empty_count / total) * 100)
        return [f"The {self.column} column has {k_fmt} empty cell(s) out of {total_fmt} ({pct})."]
