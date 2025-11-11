# azhar/lexer.py

from azhar.tokens import *
from azhar.errors import LexerError

class Lexer:
    def __init__(self, text, file="<stdin>"):
        self.text = text
        self.file = file
        self.pos = 0
        self.line = 1
        self.col = 1
        self.current_char = text[0] if text else None

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def peek(self):
        nxt = self.pos + 1
        return self.text[nxt] if nxt < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char in ' \t\r':
            self.advance()

    def skip_comment(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()

    def number(self):
        start_line, start_col = self.line, self.col
        num_str = ''
        while self.current_char is not None and self.current_char.isdigit():
            num_str += self.current_char
            self.advance()
        # v0.6 behavior: reject floats; keep for now
        if self.current_char == '.':
            snippet = self.grab_line(start_line)
            raise LexerError("Floats are not supported.", self.file, start_line, start_col, snippet)
        return Token(TOKEN_NUMBER, int(num_str), start_line, start_col)

    def string(self):
        start_line, start_col = self.line, self.col
        self.advance()  # skip opening "
        s = ''
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    s += '\n'
                elif self.current_char == '"':
                    s += '"'
                elif self.current_char == 't':
                    s += '\t'
                else:
                    s += self.current_char or ''
                self.advance()
                continue
            s += self.current_char
            self.advance()
        if self.current_char != '"':
            snippet = self.grab_line(start_line)
            raise LexerError("Unterminated string.", self.file, start_line, start_col, snippet)
        self.advance()  # closing "
        return Token(TOKEN_STRING, s, start_line, start_col)

    def ident_or_kw(self):
        start_line, start_col = self.line, self.col
        ident = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            ident += self.current_char
            self.advance()
        if ident in KEYWORDS:
            if ident in TYPE_KEYWORDS:
                return Token(TOKEN_TYPE, ident, start_line, start_col)
            return Token(TOKEN_KEYWORD, ident, start_line, start_col)
        return Token(TOKEN_IDENTIFIER, ident, start_line, start_col)

    def grab_line(self, target_line):
        # Return the full line text for diagnostics
        start = self.text.rfind('\n', 0, self.pos)
        end = self.text.find('\n', self.pos)
        if start == -1: start = 0
        else: start += 1
        if end == -1: end = len(self.text)
        return self.text[start:end]

    def tokenize(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char in ' \t\r':
                self.skip_whitespace(); continue
            if self.current_char == '/' and self.peek() == '/':
                self.skip_comment(); continue
            if self.current_char == '\n':
                tokens.append(Token(TOKEN_NEWLINE, None, self.line, self.col))
                self.advance(); continue
            if self.current_char.isdigit():
                tokens.append(self.number()); continue
            if self.current_char == '"':
                tokens.append(self.string()); continue
            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.ident_or_kw()); continue

            ch = self.current_char
            ln, cl = self.line, self.col
            if ch == '+': tokens.append(Token(TOKEN_PLUS, '+', ln, cl)); self.advance(); continue
            if ch == '-':
                if self.peek() == '>':
                    self.advance(); self.advance()
                    tokens.append(Token(TOKEN_ARROW, '->', ln, cl)); continue
                tokens.append(Token(TOKEN_MINUS, '-', ln, cl)); self.advance(); continue
            if ch == '*': tokens.append(Token(TOKEN_MULTIPLY, '*', ln, cl)); self.advance(); continue
            if ch == '/': tokens.append(Token(TOKEN_DIVIDE, '/', ln, cl)); self.advance(); continue
            if ch == '=':
                if self.peek() == '=':
                    self.advance(); self.advance()
                    tokens.append(Token(TOKEN_DOUBLE_EQUALS, '==', ln, cl)); continue
                tokens.append(Token(TOKEN_EQUALS, '=', ln, cl)); self.advance(); continue
            if ch == '!':
                if self.peek() == '=':
                    self.advance(); self.advance()
                    tokens.append(Token(TOKEN_NOT_EQUALS, '!=', ln, cl)); continue
                raise LexerError("Unexpected '!'", self.file, ln, cl, self.grab_line(ln))
            if ch == '<':
                if self.peek() == '=':
                    self.advance(); self.advance()
                    tokens.append(Token(TOKEN_LESS_EQUALS, '<=', ln, cl)); continue
                tokens.append(Token(TOKEN_LESS_THAN, '<', ln, cl)); self.advance(); continue
            if ch == '>':
                if self.peek() == '=':
                    self.advance(); self.advance()
                    tokens.append(Token(TOKEN_GREATER_EQUALS, '>=', ln, cl)); continue
                tokens.append(Token(TOKEN_GREATER_THAN, '>', ln, cl)); self.advance(); continue
            if ch == '(':
                tokens.append(Token(TOKEN_LPAREN, '(', ln, cl)); self.advance(); continue
            if ch == ')':
                tokens.append(Token(TOKEN_RPAREN, ')', ln, cl)); self.advance(); continue
            if ch == '[':
                tokens.append(Token(TOKEN_LBRACK, '[', ln, cl)); self.advance(); continue
            if ch == ']':
                tokens.append(Token(TOKEN_RBRACK, ']', ln, cl)); self.advance(); continue
            if ch == ':':
                tokens.append(Token(TOKEN_COLON, ':', ln, cl)); self.advance(); continue
            if ch == ',':
                tokens.append(Token(TOKEN_COMMA, ',', ln, cl)); self.advance(); continue
            if ch == '.':
                tokens.append(Token(TOKEN_DOT, '.', ln, cl)); self.advance(); continue

            raise LexerError(f"Unexpected character {ch!r}", self.file, ln, cl, self.grab_line(ln))

        tokens.append(Token(TOKEN_EOF, None, self.line, self.col))
        return tokens
