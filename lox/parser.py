from typing import List

from lox import stmt
from lox import expr as Expr
from lox.errors import err
from lox.token import Token, TokenType


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

        initializer: 'Expr.Expr|None' = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after variable declaration.")
        return stmt.Var(name, initializer)

    def _statement(self) -> stmt.Stmt:
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.LEFT_BRACE):
            return stmt.Block(self._block())
        if self._match(TokenType.FOR):
            return self._for_statement()

        # Looping statements
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.PRINT):
            return self._print_statement()

        return self._expression_statement()

    def _if_statement(self) -> stmt.Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after if")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition")

        then_branch = self._statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()

        return stmt.If(condition, then_branch, else_branch)

    def _block(self) -> List[stmt.Stmt]:
        statements: List[stmt.Stmt] = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._declaration())

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def _print_statement(self) -> stmt.Stmt:
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(value)

    def _while_statement(self) -> stmt.Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after while.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN,
                      "Expect ')' after while condition.")

        body = self._statement()
        return stmt.While(condition, body)

    def _expression_statement(self) -> stmt.Stmt:
        expression = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt.Expression(expression)

    def _for_statement(self) -> stmt.Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after for.")

        initializer: 'stmt.Stmt|None' = None
        if self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition: 'Expr.Expr|None' = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment: 'Expr.Expr|None' = None
        if not self._check(TokenType.SEMICOLON):
            increment = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self._statement()

        if increment:
            body = stmt.Block([body, stmt.Expression(increment)])

        if condition is None:
            condition = Expr.Literal(True)

        body = stmt.While(condition, body)

        if initializer:
            body = stmt.Block([initializer, body])

        return body

    def _expression(self) -> Expr.Expr:
        return self._assignment()

    def _assignment(self) -> Expr.Expr:
        expr = self._or()

        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, Expr.Variable):
                name = expr.name
                return Expr.Assign(name, value)

            self._error(equals, 'Invalid assignment target.')

        return expr

    def _or(self) -> Expr.Expr:
        expr = self._and()

        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._and()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def _and(self) -> Expr.Expr:
        expr = self._equality()

        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def _equality(self) -> Expr.Expr:
        expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr.Expr:
        expr = self._term()

        while self._match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self._previous()
            right = self._term()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def _term(self) -> Expr.Expr:
        expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def _factor(self) -> Expr.Expr:
        expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR, TokenType.MODULO):
            operator = self._previous()
            right = self._unary()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def _unary(self) -> Expr.Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Expr.Unary(operator, right)

        return self._primary()

    def _primary(self) -> Expr.Expr:
        if self._match(TokenType.TRUE):
            return Expr.Literal(True)
        if self._match(TokenType.FALSE):
            return Expr.Literal(False)
        if self._match(TokenType.NIL):
            return Expr.Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self._previous().literal)

        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN,
                          "Expect ')' after expression.")
            return Expr.Grouping(expr)

        if self._match(TokenType.IDENTIFIER):
            return Expr.Variable(self._previous())

        raise self._error(self._peek(), 'Expect expression.')
