import pytest

from stack import EmptyStackError, Stack


def test_pop_empty_raises():
    with pytest.raises(EmptyStackError):
        Stack().pop()
