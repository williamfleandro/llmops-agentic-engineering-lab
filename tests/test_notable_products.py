import pytest

from src.math_solver.notable_products import solve_notable_product


def test_solve_square_of_sum_with_integer():
    solution = solve_notable_product("(x+5)^2")

    assert solution.topic == "Produtos notáveis"
    assert solution.rule_name == "Quadrado da soma"
    assert solution.rule_formula == "(a+b)^2 = a^2 + 2ab + b^2"
    assert solution.identified_terms == {"a": "x", "b": "5"}
    assert solution.result == "x^2 + 10x + 25"
    assert solution.development_line == (
        "(x+5)^2 = x^2 + 2 · x · 5 + 5^2 = x^2 + 10x + 25"
    )


def test_solve_square_of_difference_with_integer():
    solution = solve_notable_product("(x-5)^2")

    assert solution.topic == "Produtos notáveis"
    assert solution.rule_name == "Quadrado da diferença"
    assert solution.rule_formula == "(a-b)^2 = a^2 - 2ab + b^2"
    assert solution.identified_terms == {"a": "x", "b": "5"}
    assert solution.result == "x^2 - 10x + 25"
    assert solution.development_line == (
        "(x-5)^2 = x^2 - 2 · x · 5 + 5^2 = x^2 - 10x + 25"
    )


def test_solve_square_of_sum_with_decimal():
    solution = solve_notable_product("(x+2.5)^2")

    assert solution.identified_terms == {"a": "x", "b": "2.5"}
    assert solution.result == "x^2 + 5x + 6.25"


def test_solve_expression_with_unicode_square_symbol():
    solution = solve_notable_product("(x+3)²")

    assert solution.result == "x^2 + 6x + 9"


@pytest.mark.parametrize(
    "expression",
    [
        "x+5",
        "(x+5)",
        "(x+5)^3",
        "(xy+5)^2",
        "(x+a)^2",
    ],
)
def test_unsupported_expression(expression):
    with pytest.raises(ValueError):
        solve_notable_product(expression)