from typing import Dict, Any

from lox.token import Token
from lox.errors import LoxRuntimeException


class Environment:
    def __init__(self, enclosing: 'Environment|None' = None) -> None:
        self._enclosing = enclosing
        self._values: Dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self._values[name] = value

    def assign(self, name: Token, value: Any) -> None:
        local_value = self._values.get(name.lexeme)
        if local_value is None:
            if self._enclosing is not None:
                self._enclosing.assign(name, value)
                return

            raise LoxRuntimeException(
                name, f"Undefined variable '{name.lexeme}'.")

        self._values[name.lexeme] = value

    def get(self, name: Token) -> Any:
        '''
        Looks up the variable first from this (local) scope before
        looking for it up the chain of enclosing scopes
        '''
        # print(self._values)
        # print()
        try:
            return self._values[name.lexeme]
        except KeyError:
            pass

        if self._enclosing is not None:
            return self._enclosing.get(name)

        raise LoxRuntimeException(name, f"Undefined variable '{name.lexeme}'.")
