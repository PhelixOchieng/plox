from typing import Any

from lox.token import Token

from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar('T')

class Expr(ABC):

    @abstractmethod
    def accept(self, visitor: 'Visitor') -> T:
        pass


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_binary_expr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self, value: Any) -> None:
        self.value = value

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_literal_expr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr) -> None:
        self.operator = operator
        self.right = right

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_unary_expr(self)


class Variable(Expr):
    def __init__(self, name: Token) -> None:
        self.name = name

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_variable_expr(self)


class Visitor:

    def visit_binary_expr(self, expr: Binary):
        pass

    def visit_grouping_expr(self, expr: Grouping):
        pass

    def visit_literal_expr(self, expr: Literal):
        pass

    def visit_unary_expr(self, expr: Unary):
        pass

    def visit_variable_expr(self, expr: Variable):
        pass
