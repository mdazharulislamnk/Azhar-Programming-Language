# azhar/cli.py

import sys
from azhar.lexer import Lexer
from azhar.parser import Parser
from azhar.typechecker import TypeChecker
from azhar.interp import Interpreter
from azhar.errors import AzharError
from azhar.repl import start_repl

def run_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    lexer = Lexer(src, file=path)
    tokens = lexer.tokenize()
    parser = Parser(tokens, file=path)
    program = parser.parse()
    tc = TypeChecker(file=path)
    tc.check(program)
    interp = Interpreter()
    interp.run(program)

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        start_repl()
        return 0
    if len(args) == 1:
        path = args[0]
        try:
            run_file(path)
            return 0
        except AzharError as e:
            print(e.render(), file=sys.stderr)
            return 1
        except FileNotFoundError:
            print(f"File not found: {path}", file=sys.stderr)
            return 2
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 3
    print("Usage: azhar [script.azhar]", file=sys.stderr)
    return 64  # EX_USAGE

if __name__ == "__main__":
    sys.exit(main())
