from typing import Dict, Any

from lox.token import Token
from lox.errors import LoxRuntimeException


class Environment:
    _values: Dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self._values[name] = value

    def assign(self, name: Token, value: Any) -> None:
        value = self._values.get(name.lexeme)
        if not value:
            raise LoxRuntimeException(
                name, f"Undefined variable '{name.lexeme}'.")

        self._values[name.lexeme] = value

    def get(self, name: Token) -> Any:
        value = self._values.get(name.lexeme)
        if value:
            return value

        raise LoxRuntimeException(name, f"Undefined variable '{name.lexeme}'.")
