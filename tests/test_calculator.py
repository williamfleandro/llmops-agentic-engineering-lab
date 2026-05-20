import pytest

from src.sample_app.calculator import add, subtract, divide


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 5),
        (-2, -3, -5),
        (2.5, 3.1, 5.6),
        (-2.5, 1.5, -1.0),
    ],
)
def test_add(a, b, expected):
    assert add(a, b) == pytest.approx(expected)


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 4, 6),
        (-10, -4, -6),
        (5.5, 2.2, 3.3),
        (-2.5, 1.5, -4.0),
    ],
)
def test_subtract(a, b, expected):
    assert subtract(a, b) == pytest.approx(expected)


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 2, 5),
        (-10, 2, -5),
        (5.5, 2, 2.75),
        (-9.0, 3, -3.0),
    ],
)
def test_divide(a, b, expected):
    assert divide(a, b) == pytest.approx(expected)


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)
