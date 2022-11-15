from typing import List, Any

from lox.lox_callable import LoxCallable
from lox.stmt import Function
from lox.environment import Environment
from lox.return_value import ReturnValue


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function) -> None:
        self._declaration = declaration

    def arity(self) -> int:
        return len(self._declaration.params)

    def call(self, interpreter, arguments: List[Any]):
        env = Environment(interpreter.globals)
        for param, argument in zip(self._declaration.params, arguments):
            env.define(param.lexeme, argument)

        try:
            interpreter.execute_block(self._declaration.body, env)
        except ReturnValue as e:
            return e.value

        return None

    def __str__(self) -> str:
        return f'<function {self._declaration.name.lexeme}>'
