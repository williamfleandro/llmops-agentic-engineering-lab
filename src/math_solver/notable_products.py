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

    match = re.fullmatch(r"\(([a-zA-Z])([+-])(\d+(?:\.\d+)?)\)\^2", normalized)

    if not match:
        raise ValueError(
            "Unsupported expression. Use formats like (x+5)^2, (x-5)^2 or (x+2.5)^2."
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


def _format_number(value: Decimal) -> str:
    normalized = value.normalize()
    text = format(normalized, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text

    if normalized == normalized.to_integral():
        return str(normalized.to_integral())

    return format(normalized, "f")