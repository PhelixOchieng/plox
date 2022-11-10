import unittest

from lox.token import Token, TokenType
from lox.scanner import Scanner


class TestScanner(unittest.TestCase):
    def test_tokenizer_simple(self):
        '''
        Tests the tokenizer
        '''
        source = '< (( )'
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        expected = [
            Token(TokenType.LESS, '<', None, 1),
            Token(TokenType.LEFT_PAREN, '(', None, 1),
            Token(TokenType.LEFT_PAREN, '(', None, 1),
            Token(TokenType.RIGHT_PAREN, ')', None, 1),
            Token(TokenType.EOF, '', None, 1),
        ]

        self.assertEqual(tokens, expected)

    def test_tokenizer_multiline(self):
        '''
        Tests the tokenization of multiline source code
        '''
        source = '''!
    ! )
<>
        '''
        # source = '>'
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        expected = [
            Token(TokenType.BANG, '!', None, 1),
            Token(TokenType.BANG, '!', None, 2),
            Token(TokenType.RIGHT_PAREN, ')', None, 2),
            Token(TokenType.LESS, '<', None, 3),
            Token(TokenType.GREATER, '>', None, 3),
            Token(TokenType.EOF, '', None, 4),
        ]

        self.assertEqual(tokens, expected)

    def test_tokenizer_compount(self):
        '''
        Tests the tokenization of compound lexemes
        '''
        source = '''!
    ! !)
<>=
        '''
        # source = '>'
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        expected = [
            Token(TokenType.BANG, '!', None, 1),
            Token(TokenType.BANG, '!', None, 2),
            Token(TokenType.BANG, '!', None, 2),
            Token(TokenType.RIGHT_PAREN, ')', None, 2),
            Token(TokenType.LESS, '<', None, 3),
            Token(TokenType.GREATER_EQUAL, '>=', None, 3),
            Token(TokenType.EOF, '', None, 4),
        ]

        # print(tokens)
        # print(expected)
        self.assertEqual(tokens, expected)


if __name__ == '__main__':
    unittest.main()
