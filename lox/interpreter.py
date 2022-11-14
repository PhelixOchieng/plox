from typing import List

from lox import expr as Expr
from lox import stmt
from lox.token import TokenType, Token
from lox.errors import err, LoxRuntimeException
from lox.environment import Environment


class Interpreter(Expr.Visitor, stmt.Visitor):
    _environment = Environment()

    def interpret(self, statements: List[stmt.Stmt]) -> None:
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeException as e:
            err.runtime_error(e)

    def visit_var_stmt(self, stmt: stmt.Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)

        self._environment.define(stmt.name.lexeme, value)

    def visit_variable_expr(self, expr: Expr.Variable):
        return self._environment.get(expr.name)

    def visit_assign_expr(self, expr: Expr.Assign):
        value = self._evaluate(expr.value)
        self._environment.assign(expr.name, value)
        return value

    def visit_expression_stmt(self, stmt: stmt.Expression) -> None:
        self._evaluate(stmt.expression)

    def visit_print_stmt(self, stmt: stmt.Print) -> None:
        value = self._evaluate(stmt.expression)
        print(self._stringify(value))

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

    def _execute(self, statement: stmt.Stmt) -> None:
        statement.accept(self)

    def _stringify(self, value) -> str:
        if value == None:
            return 'nil'

        if isinstance(value, float):
            text = str(value)
            if text.endswith('.0'):
                text = text[0:len(text) - 2]

            return text

        return str(value)

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

        # # TODO: Specify type of operand received
        raise LoxRuntimeException(operator, "Operand must be a number.")

    def _check_number_operands(self, operator: Token, left, right) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return

        # TODO: Specify which operand exactly isn't the number
        raise LoxRuntimeException(operator, "Operands must be a number.")
