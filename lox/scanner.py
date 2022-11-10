from typing import Any, List

from .token import Token, TokenType
from .errors import err


class Scanner:
    _tokens: List[Token] = []
    _start = 0
    _current = 0
    _line = 1
    _err = err

    def __init__(self, source: str) -> None:
        self.source = source
        self._tokens = []
        self._start = 0
        self._current = 0
        self._line = 1

    def _is_at_end(self) -> bool:
        return self._current >= len(self.source)

    def _add_token(self, type: TokenType, literal: Any = None) -> None:
        text = self.source[self._start:self._current]
        self._tokens.append(Token(type, text, literal, self._line))

    def _advance(self) -> str:
        char = self.source[self._current]
        self._current += 1
        return char

    def _match(self, expected: str) -> bool:
        if (self._is_at_end()):
            return False
        if (self.source[self._current] != expected):
            return False

        self._advance()
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return '\0'
        return self.source[self._current]

    def _scan_token(self) -> None:
        char = self._advance()
        if char == '(':
            self._add_token(TokenType.LEFT_PAREN)
        elif char == ')':
            self._add_token(TokenType.RIGHT_PAREN)
        elif char == '{':
            self._add_token(TokenType.LEFT_BRACE)
        elif char == '}':
            self._add_token(TokenType.RIGHT_BRACE)
        elif char == ',':
            self._add_token(TokenType.COMMA)
        elif char == '.':
            self._add_token(TokenType.DOT)
        elif char == '-':
            self._add_token(TokenType.MINUS)
        elif char == '+':
            self._add_token(TokenType.PLUS)
        elif char == ';':
            self._add_token(TokenType.SEMICOLON)
        elif char == '*':
            self._add_token(TokenType.STAR)
        elif char == '!':
            self._add_token(TokenType.BANG_EQUAL if self._match(
                '=') else TokenType.BANG)
        elif char == '=':
            self._add_token(TokenType.EQUAL_EQUAL if self._match(
                '=') else TokenType.EQUAL)
        elif char == '<':
            self._add_token(TokenType.LESS_EQUAL if self._match(
                '=') else TokenType.LESS)
        elif char == '>':
            self._add_token(TokenType.GREATER_EQUAL if self._match(
                '=') else TokenType.GREATER)
        elif char == '/':
            if self._match('/'):
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
            else:
                self._add_token(TokenType.SLASH)
        elif char == ' ' or char == '\r' or char == '\t':
            # Ignore whitespace
            pass
        elif char == '\n':
            self._line += 1
        else:
            self._err.error(self._line, f"Unexpected character. '{char}'")

    def scan_tokens(self) -> List[Token]:
        while not self._is_at_end():
            self._start = self._current
            self._scan_token()

        self._tokens.append(Token(TokenType.EOF, "", None, self._line))
        return self._tokens
