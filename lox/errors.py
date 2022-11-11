
import sys


class Error:
    had_error = False

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


err = Error()
