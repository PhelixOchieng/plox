from lox import expr as Expr
from lox.token import TokenType, Token
from lox.errors import LoxRuntimeException


class Interpreter(Expr.Visitor):

    def _evaluate(self, expr: Expr.Expr):
        return expr.accept(self)

    def _is_truthy(self, value) -> bool:
        if value == None:
            return False
        if isinstance(value, bool):
            return bool(value)

        return True

    def _check_number_operand(self, operator: Token, operand) -> None:
        if isinstance(operand, float):
            return

        raise LoxRuntimeException(operator, "Operand must be a number.")

    def _check_number_operands(self, operator: Token, left, right) -> None:
        # # TODO: Specify which operator exactly isn't the number
        if isinstance(left, float) and isinstance(right, float):
            return

        raise LoxRuntimeException(operator, "Operands must be a number")

    def visit_literal_expr(self, expr: Expr.Literal):
        return expr.value

    def visit_grouping_expr(self, expr: Expr.Grouping):
        return self._evaluate(expr.expression)

    def visit_unary_expr(self, expr: Expr.Unary):
        right = self._evaluate(expr.right)

        operator_type = expr.operator.type
        if operator_type is TokenType.MINUS:
            self._check_number_operand(expr.operator, right)
            return -float(right)
        elif operator_type is TokenType.BANG:
            return not self._is_truthy(right)

        return None

    def visit_binary_expr(self, expr: Expr.Binary):
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        operator_type = expr.operator.type
        if operator_type is TokenType.GREATER:
            self._check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        if operator_type is TokenType.GREATER_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        if operator_type is TokenType.LESS:
            self._check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        if operator_type is TokenType.LESS_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        if operator_type is TokenType.EQUAL_EQUAL:
            return left == right
        if operator_type is TokenType.BANG_EQUAL:
            return left != right
        if operator_type is TokenType.SLASH:
            self._check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        if operator_type is TokenType.STAR:
            # TODO: Add support for repeating a string a number of times
            self._check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        if operator_type is TokenType.MINUS:
            self._check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        if operator_type is TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return f'{str(left)}{str(right)}'

            raise LoxRuntimeException(
                expr.operator, "Operands must be two numbers or two strings.")

        return None