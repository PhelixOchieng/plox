from abc import ABC
from typing import List, Any


class LoxCallable(ABC):
    def call(self, interpreter, arguments: List[Any]) -> Any:
        pass

    def arity(self) -> int:
        pass
