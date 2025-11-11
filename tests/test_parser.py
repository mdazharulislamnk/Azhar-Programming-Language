from azhar.lexer import Lexer
from azhar.parser import Parser
from azhar import ast as AST

def parse(src):
    tokens = Lexer(src, file="<test>").tokenize()
    return Parser(tokens, file="<test>").parse()

def test_var_decl_and_assign():
    program = parse('let x: int = 1\nx = 2')
    assert isinstance(program.statements[0], AST.VarDecl)  # let x [attached_file:1]
    assert isinstance(program.statements[1], AST.Assign)   # x = 2 [attached_file:1]

def test_if_while_function():
    src = '''
function add(a:int, b:int) -> int do
    return a + b
end
let ok: bool = true
if ok do
    print(1)
else do
    print(2)
end
while ok do
    break
end
'''
    program = parse(src)
    assert any(isinstance(s, AST.FunctionDef) for s in program.statements)  # function parsed [attached_file:1]
    assert any(isinstance(s, AST.While) for s in program.statements)        # while parsed [attached_file:1]
