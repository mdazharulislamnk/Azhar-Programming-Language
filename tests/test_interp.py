from azhar.lexer import Lexer
from azhar.parser import Parser
from azhar.types import TypeChecker
from azhar.interp import Interpreter
from io import StringIO
import sys

def run(src, stdin_data=""):
    tokens = Lexer(src, file="<test>").tokenize()
    program = Parser(tokens, file="<test>").parse()
    TypeChecker(file="<test>").check(program)
    interp = Interpreter()
    old_in, old_out = sys.stdin, sys.stdout
    try:
        sys.stdin = StringIO(stdin_data)
        sys.stdout = StringIO()
        interp.run(program)
        return sys.stdout.getvalue()
    finally:
        sys.stdin, sys.stdout = old_in, old_out

def test_print_and_assign():
    out = run('let x: int = 1\nx = x + 2\nprint(x)')
    assert out.strip() == "3"  # 1 + 2 printed [attached_file:1]

def test_read_int():
    out = run('let n: int = read_int()\nprint(n + 5)', stdin_data="7\n")
    assert out.strip() == "12"  # read 7, add 5 [attached_file:1]
