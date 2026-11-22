"""Tests for NumberDescriber. Run from the project folder with: python -m pytest"""

import pandas as pd
import pytest

from dataexplainer.base import BaseDescriber
from dataexplainer.number import NumberDescriber


def test_is_a_base_describer():
    assert isinstance(NumberDescriber("grade"), BaseDescriber)


def test_normal_column_gives_two_sentences():
    df = pd.DataFrame({"grade": [62, 85, 98]})
    assert NumberDescriber("grade").describe(df) == [
        "The average grade is 81.67.",
        "The lowest grade is 62 and the highest is 98.",
    ]


def test_whole_numbers_have_no_decimals():
    df = pd.DataFrame({"grade": [80, 90]})
    assert NumberDescriber("grade").describe(df)[0] == "The average grade is 85."


def test_one_decimal_is_kept_when_needed():
    df = pd.DataFrame({"grade": [80, 91]})
    assert NumberDescriber("grade").describe(df)[0] == "The average grade is 85.5."


def test_big_numbers_get_commas():
    df = pd.DataFrame({"pay": [1000, 2000000]})
    assert NumberDescriber("pay").describe(df)[1] == (
        "The lowest pay is 1,000 and the highest is 2,000,000."
    )


def test_empty_cells_are_ignored():
    df = pd.DataFrame({"grade": [60, None, 100]})
    assert NumberDescriber("grade").describe(df)[0] == "The average grade is 80."


def test_all_empty_column():
    df = pd.DataFrame({"grade": [None, None]}, dtype=float)
    assert NumberDescriber("grade").describe(df) == [
        "The grade column has no numbers to describe."
    ]


def test_single_value():
    df = pd.DataFrame({"grade": [90]})
    assert NumberDescriber("grade").describe(df) == ["The only value in grade is 90."]


def test_all_values_the_same():
    df = pd.DataFrame({"grade": [75, 75, 75]})
    assert NumberDescriber("grade").describe(df) == ["Every value in grade is 75."]


def test_returns_list_of_strings():
    df = pd.DataFrame({"grade": [1, 2, 3]})
    result = NumberDescriber("grade").describe(df)
    assert isinstance(result, list)
    assert all(isinstance(sentence, str) for sentence in result)


def test_missing_column_raises_key_error():
    df = pd.DataFrame({"grade": [1, 2, 3]})
    with pytest.raises(KeyError):
        NumberDescriber("age").describe(df)


def test_text_column_raises_type_error():
    df = pd.DataFrame({"choice": ["A", "B", "A"]})
    with pytest.raises(TypeError):
        NumberDescriber("choice").describe(df)


def test_true_false_column_raises_type_error():
    df = pd.DataFrame({"passed": [True, False, True]})
    with pytest.raises(TypeError):
        NumberDescriber("passed").describe(df)


def test_repr_comes_from_the_parent():
    assert repr(NumberDescriber("grade")) == "NumberDescriber(column='grade')"

