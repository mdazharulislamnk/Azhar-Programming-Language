import io
from azhar.lexer import Lexer
from azhar.tokens import *

def lex(src):
    return [t for t in Lexer(src, file="<test>").tokenize() if t.type != TOKEN_NEWLINE]

def test_tokens_basics():
    ts = lex('let x: int = 3 + 4 // comment\n')
    kinds = [t.type for t in ts]
    assert kinds[:6] == [TOKEN_KEYWORD, TOKEN_IDENTIFIER, TOKEN_COLON, TOKEN_TYPE, TOKEN_EQUALS, TOKEN_NUMBER]  # let x: int = 3 [attached_file:1]
    assert kinds[-3:] == [TOKEN_PLUS, TOKEN_NUMBER, TOKEN_EOF]  # + 4 EOF [attached_file:1]

def test_strings_and_ops():
    ts = lex('print("hi")\nif true do end\nx == 1 and 2 != 3')
    kinds = [t.type for t in ts]
    assert TOKEN_STRING in kinds and TOKEN_DOUBLE_EQUALS in kinds and TOKEN_NOT_EQUALS in kinds  # string and ==, != present [attached_file:1]
