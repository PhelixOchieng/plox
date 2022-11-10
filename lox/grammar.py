from abc import ABC

from lox.token import Token


class Expr(ABC):
    pass


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self._left = left
        self._operator = operator
        self._right = right
