# azhar/repl.py

from azhar.lexer import Lexer
from azhar.parser import Parser
from azhar.typechecker import TypeChecker
from azhar.interp import Interpreter
from azhar.errors import AzharError


def start_repl():
    print("Azhar v0.6+ REPL (type 'exit' to quit)")
    buffer = ""
    depth = 0
    interp = Interpreter()
    while True:
        try:
            prompt = "... " if depth > 0 else ">>> "
            line = input(prompt)
        except EOFError:
            print()
            break
        if line.strip() == "exit":
            break
        buffer += line + "\n"
        opens = len(re.findall(r'\bdo\b', line))
        closes = len(re.findall(r'\bend\b', line))
        depth += opens - closes
        if depth <= 0:
            try:
                lexer = Lexer(buffer)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                program = parser.parse()
                tc = TypeChecker()
                tc.check(program)
                interp.run(program)
            except AzharError as e:
                print(e.render())
            buffer = ""
            depth = 0
