"""The parent class for every describer in pandalogue.

A describer looks at ONE column of a table and writes short sentences about it.
NumberDescriber, CategoryDescriber and MissingDescriber all build on this class.
"""

from abc import ABC, abstractmethod


class BaseDescriber(ABC):
    """Parent class for all describers.

    It keeps the settings every describer shares (the column name) and sets one
    rule: every child must write its own ``describe()`` method.

    Because this class is abstract, you cannot create a ``BaseDescriber``
    directly. You create one of its children instead.

    Attributes:
        column (str): The name of the column this describer looks at.
            Read only.

    Example:
        >>> class ShoutDescriber(BaseDescriber):
        ...     def describe(self, df):
        ...         return [f"Look at {self.column}!"]
        >>> ShoutDescriber("grade")
        ShoutDescriber(column='grade')
    """

    def __init__(self, column):
        """Create a describer for one column.

        Args:
            column (str): The name of the column to describe.

        Raises:
            ValueError: If the column name is empty or None.
        """
        if column is None or str(column).strip() == "":
            raise ValueError("column must be the name of a column, not empty.")
        self._column = column  # protected: children may use it, outsiders should not change it

    @property
    def column(self):
        """str: The name of the column this describer looks at (read only)."""
        return self._column

    @abstractmethod
    def describe(self, df):
        """Write sentences about the column.

        Every child class must override this method with its own version.

        Args:
            df (pandas.DataFrame): The table that holds the column.

        Returns:
            list[str]: Plain-English sentences, one per finding.
        """

    def _check_column(self, df):
        """Make sure the column exists in the table.

        Children call this at the start of their ``describe()`` method.

        Args:
            df (pandas.DataFrame): The table to check.

        Raises:
            KeyError: If the column is not in the table.
        """
        if self._column not in df.columns:
            raise KeyError(f"Column '{self._column}' was not found in the table.")

    def __repr__(self):
        """Return a short text such as ``NumberDescriber(column='grade')``."""
        return f"{self.__class__.__name__}(column={self._column!r})"

    def __eq__(self, other):
        """Two describers are equal if they are the same kind and use the same column."""
        if not isinstance(other, BaseDescriber):
            return NotImplemented
        return type(self) is type(other) and self._column == other._column

    def __hash__(self):
        """Keep describers usable in sets and as dictionary keys."""
        return hash((type(self).__name__, self._column))
