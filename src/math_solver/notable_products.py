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

    normalized = expression.strip().replace(" ", "").replace("²", "^2")

    binomial_match = re.fullmatch(
    r"\((\d*(?:\.\d+)?)([a-zA-Z])([+-])(\d+(?:\.\d+)?)\)"
    r"\*?"
    r"\((\d*(?:\.\d+)?)([a-zA-Z])([+-])(\d+(?:\.\d+)?)\)",
    normalized,
    )

    if binomial_match:
        return _solve_binomial_product(expression, binomial_match)
    
    match = re.fullmatch(r"\(([a-zA-Z])([+-])(\d+(?:\.\d+)?)\)\^2", normalized)

    if not match:
        raise ValueError(
            "Unsupported expression. Use formats like (x+5)^2, "
             "(x-5)^2, (x+2.5)^2 or (x+5)*(x+7)."
    )

    variable, operator, number_text = match.groups()
    number = Decimal(number_text)

    if operator == "+":
        return _solve_square_of_sum(expression, variable, number)

    return _solve_square_of_difference(expression, variable, number)


def _solve_square_of_sum(expression: str, variable: str, number: Decimal) -> MathSolution:
    b = _format_number(number)
    middle_coefficient = _format_number(Decimal("2") * number)
    square_number = _format_number(number * number)

    result = f"{variable}^2 + {middle_coefficient}{variable} + {square_number}"

    development_line = (
        f"({variable}+{b})^2 = {variable}^2 + 2 · {variable} · {b} + {b}^2 = {result}"
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
        f"({variable}-{b})^2 = {variable}^2 - 2 · {variable} · {b} + {b}^2 = {result}"
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


def _format_binomial(coefficient: Decimal, constant: Decimal, variable: str) -> str:
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

    if normalized == normalized.to_integral():
        return str(normalized.to_integral())

    return format(normalized, "f")