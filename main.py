import argparse
import sys
import os

from lox.errors import err
from lox.ast_printer import AstPrinter
from lox.scanner import Scanner
from lox.parser import Parser
from lox.interpreter import Interpreter


def run_file(filepath: str) -> None:
    '''
    Reads and executes the program from the file
    '''

    if not os.path.exists(filepath):
        sys.stderr.write(
            f"Can't open file '{filepath}': No such file or directory\n")
        sys.exit(1)

    print(f'Run File: {filepath}')
    with open(filepath, mode='r') as file:
        run(file.read())

    if err.had_error:
        sys.exit(65)
    if err.had_runtime_error:
        sys.exit(70)


def run_prompt() -> None:
    '''
    Reads and executes the program in a REPL
    '''
    print('Run prompt')
    while True:
        try:
            line = input('> ')
        except EOFError:
            break

        if line == '.exit':
            break
        elif line == '.clear':
            os.system('clear')
            continue

        run(line)
        err.had_error = False


interpreter = Interpreter()


def run(source: str) -> None:
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    parser = Parser(tokens)
    expression = parser.parse()

    if expression == None or err.had_error:
        return

    interpreter.interpret(expression)


def main():
    parser = argparse.ArgumentParser(
        prog='plox', description='The python interpreter for the lox programming language')
    parser.add_argument(
        'program', nargs='?', help='The path to the script file to be run')
    args = parser.parse_args()

    if len(sys.argv) == 2:
        run_file(args.program)
    else:
        try:
            run_prompt()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
