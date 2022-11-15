from typing import List, Any

from lox import expr as Expr
from lox import stmt
from lox.lox_callable import LoxCallable
from lox.token import TokenType, Token
from lox.errors import err, LoxRuntimeException
from lox.environment import Environment
from lox.lox_function import LoxFunction
from lox.return_value import ReturnValue

import time


class Clock(LoxCallable):
    '''
    Return the current time in seconds since the Epoch.
    Fractions of a second may be present if the system clock provides them.
    '''

    def arity(self) -> int:
        return 0

    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> float:
        return time.time()

    def __str__(self) -> str:
        return '<built-in function call>'


class Interpreter(Expr.Visitor, stmt.Visitor):
    def __init__(self) -> None:
        self.globals = Environment()
        self._environment = self.globals

        self.globals.define('clock', Clock())

    def interpret(self, statements: List[stmt.Stmt]) -> None:
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeException as e:
            err.runtime_error(e)

    def visit_function_stmt(self, stmt: stmt.Function) -> None:
        function = LoxFunction(stmt)
        self._environment.define(stmt.name.lexeme, function)

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

    def visit_return_stmt(self, stmt: stmt.Return) -> None:
        value = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)

        raise ReturnValue(value)

    def visit_literal_expr(self, expr: Expr.Literal):
        return expr.value

    def visit_logical_expr(self, expr: Expr.Logical):
        left = self._evaluate(expr.left)

        if expr.operator.type is TokenType.OR:
            if self._is_truthy(left):
                return left
        else:
            if not self._is_truthy(left):
                return left

        return self._evaluate(expr.right)

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
        if operator_type is TokenType.MODULO:
            self._check_number_operands(expr.operator, left, right)
            return float(left) % float(right)
        if operator_type is TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return f'{str(left)}{str(right)}'

            raise LoxRuntimeException(
                expr.operator, "Operands must be two numbers or two strings.")

        return None

    def visit_call_expr(self, expr: Expr.Call):
        callee = self._evaluate(expr.callee)

        arguments: List[Any] = []
        for argument in expr.arguments:
            arguments.append(self._evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeException(
                expr.paren, 'Can only call functions and classes.')

        function: LoxCallable = callee
        if len(arguments) != function.arity():
            raise LoxRuntimeException(
                expr.paren, f'Expected {function.arity()} arguments but got {len(arguments)}.'
            )

        return function.call(self, arguments)

    def visit_block_stmt(self, stmt: stmt.Block):
        self.execute_block(stmt.statements, Environment(self._environment))

    def visit_if_stmt(self, stmt: stmt.If) -> None:
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)

    def visit_while_stmt(self, stmt: stmt.While):
        while self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.body)

    def _execute(self, statement: stmt.Stmt) -> None:
        statement.accept(self)

    def execute_block(self, statements: List[stmt.Stmt], env: Environment) -> None:
        previous_env = self._environment

        try:
            self._environment = env

            for statement in statements:
                self._execute(statement)
        finally:
            self._environment = previous_env

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
