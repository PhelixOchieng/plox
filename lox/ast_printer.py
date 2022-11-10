from lox import expr as Expr


class AstPrinter(Expr.Visitor):
    def _parenthesize(self, name: str, *exprs) -> str:
        print_string = f'({name}'

        for expr in exprs:
            print_string += f' {expr.accept(self)}'

        print_string += ')'
        return print_string

    def print(self, expr: Expr.Expr) -> str:
        return expr.accept(self)

    def visit_binary_expr(self, expr: Expr.Binary) -> str:
        return self._parenthesize(expr.operator.lexeme,
                                  expr.left, expr.right)

    def visit_grouping_expr(self, expr: Expr.Grouping) -> str:
        return self._parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Expr.Literal) -> str:
        if (expr.value == None):
            return "nil"

        return str(expr.value)

    def visit_unary_expr(self, expr: Expr.Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)
