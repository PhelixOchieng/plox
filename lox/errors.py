
import sys

from lox.token import Token, TokenType


class LoxRuntimeException(RuntimeError):
    def __init__(self, token: Token, err_message: str) -> None:
        super().__init__(err_message)
        self.message = err_message
        self.token = token


class Error:
    had_error = False
    had_runtime_error = False

    def error(self, line: int, message: str) -> None:
        self.report(line, '', message)

    def report(self, line: int, where: str, message: str) -> None:
        '''
        TODO Implement this fancy error reporting
        Error: Unexpected "," in argument list.

        15 | function(first, second,);
                                ^-- Here.
        '''
        sys.stderr.write(f'[line {line}] Error {where}: {message}\n')
        self.had_error = True

    def error_token(self, token: Token, err_msg: str) -> None:
        if token.type is TokenType.EOF:
            self.report(token.line, ' at end', err_msg)
        else:
            self.report(token.line, f" at '{token.lexeme}'", err_msg)

    def runtime_error(self, error: LoxRuntimeException) -> None:
        sys.stderr.write(f'{error.message}\n[line {error.token.line}]\n')
        self.had_runtime_error = True


err = Error()
