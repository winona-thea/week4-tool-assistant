import ast
import operator
from decimal import Decimal, localcontext
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CalcInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    expression: str = Field(min_length=1, max_length=200)


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def evaluate(node: ast.AST, expression: str) -> Decimal:
    if isinstance(node, ast.Expression):
        return evaluate(node.body, expression)

    if isinstance(node, ast.Constant):
        if type(node.value) not in (int, float):
            raise ValueError("Gunakan angka saja.")

        text = ast.get_source_segment(expression, node)

        if text is None:
            raise ValueError("Angka tidak bisa dibaca.")

        value = Decimal(text)

    elif isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        left = evaluate(node.left, expression)
        right = evaluate(node.right, expression)
        value = OPERATORS[type(node.op)](left, right)

    elif isinstance(node, ast.UnaryOp):
        value = evaluate(node.operand, expression)

        if isinstance(node.op, ast.USub):
            value = -value
        elif not isinstance(node.op, ast.UAdd):
            raise ValueError("Operator tidak didukung.")

    else:
        raise ValueError("Gunakan angka, tanda kurung, +, -, *, atau /.")

    if not value.is_finite() or abs(value) > Decimal("1e18"):
        raise ValueError("Angka terlalu besar atau tidak valid.")

    return value


def run(args: dict[str, Any]) -> str:
    try:
        validated = CalcInput.model_validate(args)
        expression = validated.expression.strip()
        tree = ast.parse(expression, mode="eval")

        with localcontext() as context:
            context.prec = 28
            result = evaluate(tree, expression)

        return format(result, "f")

    except Exception as exc:
        return f"ERROR: kalkulator gagal: {exc}"