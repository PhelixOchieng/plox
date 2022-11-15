from typing import List

from lox.expr import Expr
from lox.token import Token

from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar('T')

class Stmt(ABC):

    @abstractmethod
    def accept(self, visitor: 'Visitor') -> T:
        pass


class Block(Stmt):
    def __init__(self, statements: List[Stmt]) -> None:
        self.statements = statements

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_block_stmt(self)


class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_expression_stmt(self)


class Function(Stmt):
    def __init__(self, name: Token, params: List[Token], body: List[Stmt]) -> None:
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_function_stmt(self)


class If(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: 'Stmt|None') -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_if_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_print_stmt(self)


class Return(Stmt):
    def __init__(self, keyword: Token, value: 'Expr|None') -> None:
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_return_stmt(self)


class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt) -> None:
        self.condition = condition
        self.body = body

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_while_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: 'Expr|None') -> None:
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_var_stmt(self)


class Visitor:

    def visit_block_stmt(self, stmt: Block):
        pass

    def visit_expression_stmt(self, stmt: Expression):
        pass

    def visit_function_stmt(self, stmt: Function):
        pass

    def visit_if_stmt(self, stmt: If):
        pass

    def visit_print_stmt(self, stmt: Print):
        pass

    def visit_return_stmt(self, stmt: Return):
        pass

    def visit_while_stmt(self, stmt: While):
        pass

    def visit_var_stmt(self, stmt: Var):
        pass
