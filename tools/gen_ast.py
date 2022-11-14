from io import TextIOWrapper
from typing import List

import argparse
import os


def define_type(file: TextIOWrapper, base_name: str, class_name: str, fields: str) -> None:
    file.write(f'''\
class {class_name}({base_name}):
    def __init__(self, {fields}) -> None:
''')

    fields_list = fields.split(',')
    for field in fields_list:
        field_name = field.split(':')[0].strip()
        file.write(f'''\
        self.{field_name} = {field_name}
''')

    file.write(f'''\

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)
'''
               )


def define_visitor(file: TextIOWrapper, base_name: str, expr_types: List[str]) -> None:
    file.write('class Visitor:\n')

    for expr_type in expr_types:
        type_name = expr_type.split('->')[0].strip()
        file.write(f'''
    def visit_{type_name.lower()}_{base_name.lower()}(self, {base_name.lower()}: {type_name}):
        pass
'''
                   )


def define_ast(output_dir: str, base_name: str, expr_types: List[str], imports: 'str|None' = None) -> None:
    '''
    Generates the code and saves it to a file
    '''
    path = os.path.join(output_dir, f'{base_name.lower()}.py')

    with open(path, 'w') as file:
        if imports:
            file.write(f'{imports}\n')

        file.write(f'''\
from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar('T')

class {base_name}(ABC):

    @abstractmethod
    def accept(self, visitor: 'Visitor') -> T:
        pass


'''
                   )
        for expr_type in expr_types:
            split = expr_type.split('->')
            class_name = split[0].strip()
            fields = split[1].strip()
            define_type(file, base_name, class_name, fields)
            file.write('\n\n')

        define_visitor(file, base_name, expr_types)


def main():
    parser = argparse.ArgumentParser(
        description='Generate AST and output the source to a folder')
    parser.add_argument('dir', nargs='?', default='.',
                        help='Output directory for the generated files')

    args = parser.parse_args()
    output_dir = args.dir
    define_ast(output_dir, "Expr", [
        'Binary   -> left: Expr, operator: Token, right: Expr',
        'Grouping -> expression: Expr',
        'Literal  -> value: Any',
        'Logical  -> left: Expr, operator: Token, right: Expr',
        'Unary    -> operator: Token, right: Expr',
        'Variable -> name: Token',
        'Assign   -> name: Token, value: Expr'
    ],
        imports='''\
from typing import Any

from lox.token import Token
'''
    )

    define_ast(output_dir, 'Stmt', [
        'Block       -> statements: List[Stmt]',
        'Expression  -> expression: Expr',
        "If          -> condition: Expr, then_branch: Stmt, else_branch: 'Stmt|None'",
        'Print       -> expression: Expr',
        "Var         -> name: Token, initializer: 'Expr|None'",
    ],
        imports='''\
from typing import List

from lox.expr import Expr
from lox.token import Token
'''
    )


if __name__ == '__main__':
    main()
