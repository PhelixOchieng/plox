from abc import ABC

class Expr:
    pass

class Binary(Expr):
    def __init__(self, Expr left, Token operator, Expr right) -> None:
                self.left = left
                    self.Token = Token
                    self.Expr = Expr
        class Grouping(Expr):
    def __init__(self, Expr expression) -> None:
                self.expression = expression
        class Literal(Expr):
    def __init__(self, Object value) -> None:
                self.value = value
        class Unary(Expr):
    def __init__(self, Token operator, Expr right) -> None:
                self.operator = operator
                    self.Expr = Expr
        