"""Tests for BaseDescriber. Run from the project folder with: python -m pytest"""

import pandas as pd
import pytest

from pandalogue.base import BaseDescriber


class DemoDescriber(BaseDescriber):
    """A tiny child class used only for testing."""

    def describe(self, df):
        self._check_column(df)
        return ["demo sentence"]


class OtherDescriber(DemoDescriber):
    """A different kind of describer, to test equality."""


def test_cannot_create_base_describer_directly():
    with pytest.raises(TypeError):
        BaseDescriber("grade")


def test_child_can_be_created_and_describes():
    df = pd.DataFrame({"grade": [1, 2, 3]})
    assert DemoDescriber("grade").describe(df) == ["demo sentence"]


def test_column_property_returns_name():
    assert DemoDescriber("grade").column == "grade"


def test_column_is_read_only():
    describer = DemoDescriber("grade")
    with pytest.raises(AttributeError):
        describer.column = "age"


@pytest.mark.parametrize("bad_name", [None, "", "   "])
def test_empty_column_name_is_rejected(bad_name):
    with pytest.raises(ValueError):
        DemoDescriber(bad_name)


def test_missing_column_gives_clear_error():
    df = pd.DataFrame({"grade": [1, 2, 3]})
    with pytest.raises(KeyError):
        DemoDescriber("age").describe(df)


def test_repr_shows_class_and_column():
    assert repr(DemoDescriber("grade")) == "DemoDescriber(column='grade')"


def test_equal_when_same_kind_and_same_column():
    assert DemoDescriber("grade") == DemoDescriber("grade")


def test_not_equal_when_column_differs():
    assert DemoDescriber("grade") != DemoDescriber("age")


def test_not_equal_when_kind_differs():
    assert DemoDescriber("grade") != OtherDescriber("grade")


def test_not_equal_to_other_types():
    assert DemoDescriber("grade") != "grade"


def test_equal_describers_work_in_a_set():
    assert len({DemoDescriber("grade"), DemoDescriber("grade")}) == 1

