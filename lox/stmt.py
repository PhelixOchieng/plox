from lox.expr import Expr
from lox.token import Token

from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar('T')

class Stmt(ABC):

    @abstractmethod
    def accept(self, visitor: 'Visitor') -> T:
        pass


class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: 'Expr|None') -> None:
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_var_stmt(self)


class Visitor:

    def visit_expression_stmt(self, stmt: Expression):
        pass

    def visit_print_stmt(self, stmt: Print):
        pass

    def visit_var_stmt(self, stmt: Var):
        pass
