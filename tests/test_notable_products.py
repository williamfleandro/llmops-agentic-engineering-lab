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

def test_solve_binomial_product_with_positive_and_negative_constants():
    solution = solve_notable_product("(5x+6)*(5x-2)")

    assert solution.result == "25x^2 + 20x - 12"
    assert solution.development_line == (
        "(5x+6)*(5x-2) = 5x · 5x + 5x · (-2) + 6 · 5x + "
        "6 · (-2) = 25x^2 - 10x + 30x - 12 = 25x^2 + 20x - 12"
    )

def test_solve_binomial_product_with_implicit_multiplication():
    solution = solve_notable_product("(5x+6)(5x-2)")

    assert solution.result == "25x^2 + 20x - 12"

def test_solve_square_of_sum_with_decimal():
    solution = solve_notable_product("(x+2.5)^2")

    assert solution.identified_terms == {"a": "x", "b": "2.5"}
    assert solution.result == "x^2 + 5x + 6.25"


def test_solve_expression_with_unicode_square_symbol():
    solution = solve_notable_product("(x+3)²")

    assert solution.result == "x^2 + 6x + 9"


def test_solve_binomial_product_with_unit_coefficients():
    solution = solve_notable_product("(x+5)*(x+7)")

    assert solution.topic == "Produtos notáveis"
    assert solution.rule_name == "Produto de binômios"
    assert solution.rule_formula == "(a+b)(c+d) = ac + ad + bc + bd"
    assert solution.result == "x^2 + 12x + 35"
    assert solution.development_line == (
        "(x+5)*(x+7) = x · x + x · 7 + 5 · x + 5 · 7 = "
        "x^2 + 7x + 5x + 35 = x^2 + 12x + 35"
    )


def test_solve_binomial_product_with_coefficients_and_negative_constant():
    solution = solve_notable_product("(6x+1)*(6x-9)")

    assert solution.topic == "Produtos notáveis"
    assert solution.rule_name == "Produto de binômios"
    assert solution.rule_formula == "(a+b)(c+d) = ac + ad + bc + bd"
    assert solution.result == "36x^2 - 48x - 9"
    assert solution.development_line == (
        "(6x+1)*(6x-9) = 6x · 6x + 6x · (-9) + 1 · 6x + "
        "1 · (-9) = 36x^2 - 54x + 6x - 9 = 36x^2 - 48x - 9"
    )


@pytest.mark.parametrize(
    "expression",
    [
        "x+5",
        "(x+5)",
        "(xy+5)^2",
        "(x+a)^2",
        "(x+5)^4",
    ],
)
def test_unsupported_expression(expression):
    with pytest.raises(ValueError):
        solve_notable_product(expression)