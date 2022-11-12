from typing import List

from lox import stmt
from lox.errors import err
from lox.token import Token, TokenType
from lox.expr import Expr, Binary, Unary, Literal, Grouping, Variable


class ParserException(Exception):
    pass


class Parser:
    _current = 0

    def __init__(self, tokens: List[Token]) -> None:
        self._tokens = tokens

    def parse(self) -> List[stmt.Stmt]:
        statements: List[stmt.Stmt] = []
        while not self._is_at_end():
            statements.append(self._declaration())

        return statements

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False

        return self._peek().type == token_type

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self._tokens[self._current]

    def _previous(self) -> Token:
        return self._tokens[self._current - 1]

    def _advance(self) -> Token:
        if not self._is_at_end():
            self._current += 1
        return self._previous()

    def _match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True

        return False

    def _error(self, token: Token, err_msg: str) -> ParserException:
        err.error_token(token, err_msg)
        return ParserException()

    def _synchronize(self) -> None:
        self._advance()

        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return

            current_token_type = self._peek().type
            if current_token_type in [
                    TokenType.CLASS,
                    TokenType.FUN,
                    TokenType.VAR,
                    TokenType.FOR,
                    TokenType.IF,
                    TokenType.WHILE,
                    TokenType.PRINT,
                    TokenType.RETURN, ]:
                return

            self._advance()

    def _consume(self, token_type: TokenType, err_msg: str) -> Token:
        '''
        Checks to see if the current token to be consumed is of the expected type and consumes it
        If a different token is received throw an error
        '''

        if self._check(token_type):
            return self._advance()

        raise self._error(self._peek(), err_msg)

    def _declaration(self) -> stmt.Stmt:
        try:
            if self._match(TokenType.VAR):
                return self._var_declaration()
            return self._statement()
        except ParserException as e:
            self._synchronize()
            return None

    def _var_declaration(self) -> stmt.Stmt:
        name = self._consume(TokenType.IDENTIFIER, 'Expect variable name.')

        initializer: 'Expr|None' = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after variable declaration.")
        return stmt.Var(name, initializer)

    def _statement(self) -> stmt.Stmt:
        if self._match(TokenType.PRINT):
            return self._print_statement()

        return self._expression_statement()

    def _print_statement(self) -> stmt.Stmt:
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(value)

    def _expression_statement(self) -> stmt.Stmt:
        expression = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt.Expression(expression)

    def _expression(self) -> Expr:
        return self._equality()

    def _equality(self) -> Expr:
        expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr = self._term()

        while self._match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self._previous()
            right = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self) -> Expr:
        expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)

        return self._primary()

    def _primary(self) -> Expr:
        if self._match(TokenType.TRUE):
            return Literal(True)
        if self._match(TokenType.FALSE):
            return Literal(False)
        if self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN,
                          "Expect ')' after expression.")
            return Grouping(expr)

        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())

        raise self._error(self._peek(), 'Expect expression.')
