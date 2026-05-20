import re
from dataclasses import asdict, dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MathSolution:
    original_expression: str
    topic: str
    rule_name: str
    rule_formula: str
    identified_terms: dict[str, str]
    steps: list[str]
    development_line: str
    result: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def solve_notable_product(expression: str) -> MathSolution:
    """Solve supported notable product expressions with step-by-step explanation."""

    normalized = (
        expression.strip()
        .replace(" ", "")
        .replace("²", "^2")
        .replace("³", "^3")
    )

    cube_match = re.fullmatch(
        r"\((\d*(?:\.\d+)?[a-zA-Z]|\d+(?:\.\d+)?)"
        r"([+-])"
        r"(\d*(?:\.\d+)?[a-zA-Z]|\d+(?:\.\d+)?)\)\^3",
        normalized,
    )

    if cube_match:
        return _solve_cube(expression, cube_match)

    binomial_match = re.fullmatch(
        r"\((\d*(?:\.\d+)?)([a-zA-Z])([+-])(\d+(?:\.\d+)?)\)"
        r"\*?"
        r"\((\d*(?:\.\d+)?)([a-zA-Z])([+-])(\d+(?:\.\d+)?)\)",
        normalized,
    )

    if binomial_match:
        return _solve_binomial_product(expression, binomial_match)

    square_match = re.fullmatch(
        r"\(([a-zA-Z])([+-])(\d+(?:\.\d+)?)\)\^2",
        normalized,
    )

    if not square_match:
        raise ValueError(
            "Unsupported expression. Use formats like (x+5)^2, "
            "(x-5)^2, (x+2.5)^2, (x+5)*(x+7) or (x+y)^3."
        )

    variable, operator, number_text = square_match.groups()
    number = Decimal(number_text)

    if operator == "+":
        return _solve_square_of_sum(expression, variable, number)

    return _solve_square_of_difference(expression, variable, number)


def _solve_cube(
    expression: str,
    match: re.Match[str],
) -> MathSolution:
    first_term, operator, second_term = match.groups()

    if operator == "+":
        return _solve_cube_of_sum(expression, first_term, second_term)

    return _solve_cube_of_difference(expression, first_term, second_term)


def _solve_cube_of_sum(
    expression: str,
    first_term: str,
    second_term: str,
) -> MathSolution:
    result = _format_cube_result(
        first_term=first_term,
        second_term=second_term,
        operator="+",
    )

    development_line = (
        f"{expression} = {first_term}^3 + 3 · {first_term}^2 · {second_term} + "
        f"3 · {first_term} · {second_term}^2 + {second_term}^3 = {result}"
    )

    return MathSolution(
        original_expression=expression,
        topic="Produtos notáveis",
        rule_name="Cubo da soma",
        rule_formula="(a+b)^3 = a^3 + 3a^2b + 3ab^2 + b^3",
        identified_terms={
            "a": first_term,
            "b": second_term,
        },
        steps=[
            f"Identificamos o primeiro termo: a = {first_term}.",
            f"Identificamos o segundo termo: b = {second_term}.",
            "Aplicamos a regra do cubo da soma.",
            "Calculamos a^3, 3a^2b, 3ab^2 e b^3.",
            f"Resultado final: {result}.",
        ],
        development_line=development_line,
        result=result,
    )


def _solve_cube_of_difference(
    expression: str,
    first_term: str,
    second_term: str,
) -> MathSolution:
    result = _format_cube_result(
        first_term=first_term,
        second_term=second_term,
        operator="-",
    )

    development_line = (
        f"{expression} = {first_term}^3 - 3 · {first_term}^2 · {second_term} + "
        f"3 · {first_term} · {second_term}^2 - {second_term}^3 = {result}"
    )

    return MathSolution(
        original_expression=expression,
        topic="Produtos notáveis",
        rule_name="Cubo da diferença",
        rule_formula="(a-b)^3 = a^3 - 3a^2b + 3ab^2 - b^3",
        identified_terms={
            "a": first_term,
            "b": second_term,
        },
        steps=[
            f"Identificamos o primeiro termo: a = {first_term}.",
            f"Identificamos o segundo termo: b = {second_term}.",
            "Aplicamos a regra do cubo da diferença.",
            "Calculamos a^3, -3a^2b, 3ab^2 e -b^3.",
            f"Resultado final: {result}.",
        ],
        development_line=development_line,
        result=result,
    )


def _format_cube_result(
    first_term: str,
    second_term: str,
    operator: str,
) -> str:
    first = _parse_simple_monomial(first_term)
    second = _parse_simple_monomial(second_term)

    if operator == "+":
        terms = [
            _power_monomial(first, 3),
            _multiply_monomials(
                _constant_monomial(Decimal("3")),
                _power_monomial(first, 2),
                second,
            ),
            _multiply_monomials(
                _constant_monomial(Decimal("3")),
                first,
                _power_monomial(second, 2),
            ),
            _power_monomial(second, 3),
        ]
    else:
        terms = [
            _power_monomial(first, 3),
            _multiply_monomials(
                _constant_monomial(Decimal("-3")),
                _power_monomial(first, 2),
                second,
            ),
            _multiply_monomials(
                _constant_monomial(Decimal("3")),
                first,
                _power_monomial(second, 2),
            ),
            _multiply_monomials(
                _constant_monomial(Decimal("-1")),
                _power_monomial(second, 3),
            ),
        ]

    return _join_monomial_terms(terms)


def _parse_simple_monomial(term: str) -> tuple[Decimal, dict[str, int]]:
    number_match = re.fullmatch(r"\d+(?:\.\d+)?", term)

    if number_match:
        return Decimal(term), {}

    monomial_match = re.fullmatch(r"(\d*(?:\.\d+)?)([a-zA-Z])", term)

    if not monomial_match:
        raise ValueError(f"Unsupported monomial: {term}")

    coefficient_text, variable = monomial_match.groups()

    if coefficient_text == "":
        coefficient = Decimal("1")
    else:
        coefficient = Decimal(coefficient_text)

    return coefficient, {variable: 1}


def _constant_monomial(value: Decimal) -> tuple[Decimal, dict[str, int]]:
    return value, {}


def _power_monomial(
    monomial: tuple[Decimal, dict[str, int]],
    power: int,
) -> tuple[Decimal, dict[str, int]]:
    coefficient, variables = monomial

    powered_variables = {
        variable: exponent * power
        for variable, exponent in variables.items()
    }

    return coefficient**power, powered_variables


def _multiply_monomials(
    *monomials: tuple[Decimal, dict[str, int]],
) -> tuple[Decimal, dict[str, int]]:
    coefficient = Decimal("1")
    variables: dict[str, int] = {}

    for monomial_coefficient, monomial_variables in monomials:
        coefficient *= monomial_coefficient

        for variable, exponent in monomial_variables.items():
            variables[variable] = variables.get(variable, 0) + exponent

    return coefficient, variables


def _format_monomial(
    coefficient: Decimal,
    variables: dict[str, int],
) -> str:
    absolute_coefficient = abs(coefficient)

    variable_part = "".join(
        f"{variable}^{exponent}" if exponent > 1 else variable
        for variable, exponent in variables.items()
    )

    if variable_part and absolute_coefficient == Decimal("1"):
        body = variable_part
    else:
        body = f"{_format_number(absolute_coefficient)}{variable_part}"

    if coefficient < 0:
        return f"-{body}"

    return body


def _join_monomial_terms(
    terms: list[tuple[Decimal, dict[str, int]]],
) -> str:
    formatted_terms = [
        _format_monomial(coefficient, variables)
        for coefficient, variables in terms
    ]

    expression = formatted_terms[0]

    for term in formatted_terms[1:]:
        if term.startswith("-"):
            expression += f" - {term[1:]}"
        else:
            expression += f" + {term}"

    return expression


def _solve_square_of_sum(
    expression: str,
    variable: str,
    number: Decimal,
) -> MathSolution:
    b = _format_number(number)
    middle_coefficient = _format_number(Decimal("2") * number)
    square_number = _format_number(number * number)

    result = f"{variable}^2 + {middle_coefficient}{variable} + {square_number}"

    development_line = (
        f"({variable}+{b})^2 = {variable}^2 + 2 · {variable} · {b} + "
        f"{b}^2 = {result}"
    )

    return MathSolution(
        original_expression=expression,
        topic="Produtos notáveis",
        rule_name="Quadrado da soma",
        rule_formula="(a+b)^2 = a^2 + 2ab + b^2",
        identified_terms={
            "a": variable,
            "b": b,
        },
        steps=[
            f"Identificamos o primeiro termo: a = {variable}.",
            f"Identificamos o segundo termo: b = {b}.",
            "Aplicamos a regra do quadrado da soma.",
            f"Calculamos o termo do meio: 2 · {variable} · {b} = "
            f"{middle_coefficient}{variable}.",
            f"Calculamos o quadrado do segundo termo: {b}^2 = {square_number}.",
        ],
        development_line=development_line,
        result=result,
    )


def _solve_square_of_difference(
    expression: str,
    variable: str,
    number: Decimal,
) -> MathSolution:
    b = _format_number(number)
    middle_coefficient = _format_number(Decimal("2") * number)
    square_number = _format_number(number * number)

    result = f"{variable}^2 - {middle_coefficient}{variable} + {square_number}"

    development_line = (
        f"({variable}-{b})^2 = {variable}^2 - 2 · {variable} · {b} + "
        f"{b}^2 = {result}"
    )

    return MathSolution(
        original_expression=expression,
        topic="Produtos notáveis",
        rule_name="Quadrado da diferença",
        rule_formula="(a-b)^2 = a^2 - 2ab + b^2",
        identified_terms={
            "a": variable,
            "b": b,
        },
        steps=[
            f"Identificamos o primeiro termo: a = {variable}.",
            f"Identificamos o segundo termo: b = {b}.",
            "Aplicamos a regra do quadrado da diferença.",
            f"Calculamos o termo do meio: 2 · {variable} · {b} = "
            f"{middle_coefficient}{variable}.",
            f"Calculamos o quadrado do segundo termo: {b}^2 = {square_number}.",
        ],
        development_line=development_line,
        result=result,
    )


def _solve_binomial_product(
    expression: str,
    match: re.Match[str],
) -> MathSolution:
    (
        left_coefficient_text,
        left_variable,
        left_operator,
        left_constant_text,
        right_coefficient_text,
        right_variable,
        right_operator,
        right_constant_text,
    ) = match.groups()

    if left_variable != right_variable:
        raise ValueError("Unsupported expression. Both binomials must use the same variable.")

    variable = left_variable

    left_coefficient = _parse_variable_coefficient(left_coefficient_text)
    right_coefficient = _parse_variable_coefficient(right_coefficient_text)
    left_constant = _parse_signed_constant(left_operator, left_constant_text)
    right_constant = _parse_signed_constant(right_operator, right_constant_text)

    x2_coefficient = left_coefficient * right_coefficient
    outer_coefficient = left_coefficient * right_constant
    inner_coefficient = left_constant * right_coefficient
    constant = left_constant * right_constant
    x_coefficient = outer_coefficient + inner_coefficient

    first_product = _format_power_term(x2_coefficient, variable)
    second_product = _format_linear_term(outer_coefficient, variable)
    third_product = _format_linear_term(inner_coefficient, variable)
    fourth_product = _format_number(constant)

    partial_result = _join_polynomial_terms(
        [
            first_product,
            second_product,
            third_product,
            fourth_product,
        ]
    )

    final_result = _format_polynomial(
        x2_coefficient=x2_coefficient,
        x_coefficient=x_coefficient,
        constant=constant,
        variable=variable,
    )

    left_variable_term = _format_variable_factor(left_coefficient, variable)
    right_variable_term = _format_variable_factor(right_coefficient, variable)
    left_constant_factor = _format_factor(left_constant)
    right_constant_factor = _format_factor(right_constant)

    development_line = (
        f"{expression} = {left_variable_term} · {right_variable_term} + "
        f"{left_variable_term} · {right_constant_factor} + "
        f"{left_constant_factor} · {right_variable_term} + "
        f"{left_constant_factor} · {right_constant_factor} = "
        f"{partial_result} = {final_result}"
    )

    return MathSolution(
        original_expression=expression,
        topic="Produtos notáveis",
        rule_name="Produto de binômios",
        rule_formula="(a+b)(c+d) = ac + ad + bc + bd",
        identified_terms={
            "first_binomial": _format_binomial(left_coefficient, left_constant, variable),
            "second_binomial": _format_binomial(
                right_coefficient,
                right_constant,
                variable,
            ),
        },
        steps=[
            "Identificamos dois binômios multiplicados.",
            "Aplicamos a propriedade distributiva.",
            "Multiplicamos cada termo do primeiro binômio por cada termo do segundo.",
            "Somamos os termos semelhantes.",
            f"Resultado final: {final_result}.",
        ],
        development_line=development_line,
        result=final_result,
    )


def _parse_variable_coefficient(coefficient_text: str) -> Decimal:
    if coefficient_text == "":
        return Decimal("1")

    return Decimal(coefficient_text)


def _parse_signed_constant(operator: str, number_text: str) -> Decimal:
    number = Decimal(number_text)

    if operator == "-":
        return -number

    return number


def _format_variable_factor(coefficient: Decimal, variable: str) -> str:
    if coefficient == Decimal("1"):
        return variable

    return f"{_format_number(coefficient)}{variable}"


def _format_factor(value: Decimal) -> str:
    formatted = _format_number(value)

    if value < 0:
        return f"({formatted})"

    return formatted


def _format_binomial(
    coefficient: Decimal,
    constant: Decimal,
    variable: str,
) -> str:
    variable_term = _format_variable_factor(coefficient, variable)
    constant_text = _format_number(abs(constant))

    if constant < 0:
        return f"{variable_term}-{constant_text}"

    return f"{variable_term}+{constant_text}"


def _format_power_term(coefficient: Decimal, variable: str) -> str:
    if coefficient == Decimal("1"):
        return f"{variable}^2"

    if coefficient == Decimal("-1"):
        return f"-{variable}^2"

    return f"{_format_number(coefficient)}{variable}^2"


def _format_linear_term(coefficient: Decimal, variable: str) -> str:
    if coefficient == Decimal("1"):
        return variable

    if coefficient == Decimal("-1"):
        return f"-{variable}"

    return f"{_format_number(coefficient)}{variable}"


def _join_polynomial_terms(terms: list[str]) -> str:
    expression = terms[0]

    for term in terms[1:]:
        if term.startswith("-"):
            expression += f" - {term[1:]}"
        else:
            expression += f" + {term}"

    return expression


def _format_polynomial(
    x2_coefficient: Decimal,
    x_coefficient: Decimal,
    constant: Decimal,
    variable: str,
) -> str:
    terms = [_format_power_term(x2_coefficient, variable)]

    if x_coefficient != 0:
        terms.append(_format_linear_term(x_coefficient, variable))

    if constant != 0:
        terms.append(_format_number(constant))

    return _join_polynomial_terms(terms)


def _format_number(value: Decimal) -> str:
    normalized = value.normalize()
    text = format(normalized, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text