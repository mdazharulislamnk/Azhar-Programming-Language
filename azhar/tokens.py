# azhar/tokens.py

from dataclasses import dataclass

# Token types
TOKEN_NUMBER = 'NUMBER'
TOKEN_STRING = 'STRING'
TOKEN_IDENTIFIER = 'IDENTIFIER'
TOKEN_KEYWORD = 'KEYWORD'
TOKEN_TYPE = 'TYPE'
TOKEN_PLUS = 'PLUS'
TOKEN_MINUS = 'MINUS'
TOKEN_MULTIPLY = 'MULTIPLY'
TOKEN_DIVIDE = 'DIVIDE'
TOKEN_INTDIV = 'INTDIV'  # for future use if you add //
TOKEN_EQUALS = 'EQUALS'
TOKEN_DOUBLE_EQUALS = 'DOUBLE_EQUALS'
TOKEN_NOT_EQUALS = 'NOT_EQUALS'
TOKEN_LESS_THAN = 'LESS_THAN'
TOKEN_LESS_EQUALS = 'LESS_EQUALS'
TOKEN_GREATER_THAN = 'GREATER_THAN'
TOKEN_GREATER_EQUALS = 'GREATER_EQUALS'
TOKEN_LPAREN = 'LPAREN'
TOKEN_RPAREN = 'RPAREN'
TOKEN_LBRACK = 'LBRACK'   # reserved for future arrays
TOKEN_RBRACK = 'RBRACK'   # reserved for future arrays
TOKEN_COLON = 'COLON'
TOKEN_ARROW = 'ARROW'
TOKEN_NEWLINE = 'NEWLINE'
TOKEN_EOF = 'EOF'
TOKEN_COMMA = 'COMMA'
TOKEN_DOT = 'DOT'         # reserved for future field access

KEYWORDS = {
    'let','function','do','end','if','else','return','true','false',
    'print','output','and','or','read_string','read_int','while','break','void',
    'int','string','bool'
}

TYPE_KEYWORDS = {'int','string','bool','void'}

@dataclass
class Token:
    type: str
    value: object = None
    line: int = 1
    col: int = 1
    def __repr__(self):
        if self.value is None:
            return f"Token({self.type})"
        return f"Token({self.type}, {repr(self.value)})"
