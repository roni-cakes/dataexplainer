"""Describer for date and datetime columns."""

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

from base import BaseDescriber
from utils import format_number


def _format_timestamp(ts: pd.Timestamp, include_time: bool) -> str:
    if include_time:
        return ts.strftime("%Y-%m-%d %H:%M")
    return ts.strftime("%Y-%m-%d")


def _format_span(first: pd.Timestamp, last: pd.Timestamp) -> str:
    delta = last - first
    total_seconds = delta.total_seconds()
    if total_seconds < 86400:
        return "less than a day"
    days = int(total_seconds // 86400)
    if days == 1:
        return "1 day"
    return f"{format_number(days)} days"


class DateDescriber(BaseDescriber):
    """Describes datetime64 columns (with or without timezone)."""

    def describe(self, df: pd.DataFrame) -> list:
        if self.column not in df.columns:
            raise KeyError(f"Column {self.column!r} is not in the table.")

        series = df[self.column]
        if not is_datetime64_any_dtype(series.dtype):
            raise TypeError(f"Column {self.column!r} is not a date column.")

        valid = pd.to_datetime(series, errors="coerce").dropna()
        if len(valid) == 0:
            return [f"The {self.column} column has no dates to describe."]

        # Normalize to wall-clock/comparable timestamps without tz issues for time-of-day check.
        if getattr(valid.dt, "tz", None) is not None:
            local_ts = valid.dt.tz_convert(None)
        else:
            local_ts = valid

        has_non_midnight = any(
            (ts.hour != 0 or ts.minute != 0 or ts.second != 0 or ts.microsecond != 0)
            for ts in local_ts
        )

        unique_vals = sorted(set(valid.tolist()))
        if len(unique_vals) == 1:
            d_str = _format_timestamp(unique_vals[0], has_non_midnight)
            if len(valid) == 1:
                return [f"The only date in {self.column} is {d_str}."]
            return [f"Every date in {self.column} is {d_str}."]

        first_ts = min(valid)
        last_ts = max(valid)
        first_str = _format_timestamp(first_ts, has_non_midnight)
        last_str = _format_timestamp(last_ts, has_non_midnight)
        span_str = _format_span(first_ts, last_ts)

        return [f"The dates in {self.column} run from {first_str} to {last_str} ({span_str})."]
