from io import StringIO
import sys
from azhar.lexer import Lexer
from azhar.parser import Parser
from azhar.types import TypeChecker
from azhar.interp import Interpreter

TICTACTOE_SMOKE = '''
let b1: string = "1"
let b2: string = "2"
let b3: string = "3"
function draw()->void do
    output(b1); output(b2); print(b3)
end
print("AZHAR")
draw()
'''

def run(src):
    tokens = Lexer(src, file="<test>").tokenize()
    program = Parser(tokens, file="<test>").parse()
    TypeChecker(file="<test>").check(program)
    interp = Interpreter()
    old = sys.stdout
    try:
        sys.stdout = StringIO()
        interp.run(program)
        return sys.stdout.getvalue()
    finally:
        sys.stdout = old

def test_integration_smoke():
    out = run(TICTACTOE_SMOKE)
    assert "AZHAR" in out  # prints banner [attached_file:1]
    assert "123" in out.replace("\n","")  # draw outputs 1 2 3 inline then newline [attached_file:1]
