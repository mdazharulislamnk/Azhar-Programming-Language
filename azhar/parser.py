# azhar/parser.py

from azhar.tokens import *
from azhar.errors import ParseError
from azhar import ast as AST

class Parser:
    def __init__(self, tokens, file="<stdin>"):
        # drop NEWLINE tokens for v0.6 newline-insensitive grammar
        self.tokens = [t for t in tokens if t.type != TOKEN_NEWLINE]
        self.file = file
        self.pos = 0
        self.current = self.tokens[0] if self.tokens else Token(TOKEN_EOF)

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]

    def peek(self, k=1):
        idx = self.pos + k
        return self.tokens[idx] if idx < len(self.tokens) else Token(TOKEN_EOF, None, self.current.line, self.current.col)

    def eat(self, type_):
        if self.current.type == type_:
            tok = self.current
            self.advance()
            return tok
        raise ParseError(f"Expected {type_}, got {self.current}", self.file, self.current.line, self.current.col)

    def parse(self):
        stmts = []
        while self.current.type != TOKEN_EOF:
            stmts.append(self.statement())
        return AST.Program(stmts)

    def statement(self):
        tok = self.current

        if tok.type == TOKEN_KEYWORD and tok.value == 'function':
            return self.function_def()

        if tok.type == TOKEN_KEYWORD and tok.value == 'let':
            return self.let_decl()

        if tok.type == TOKEN_KEYWORD and tok.value == 'if':
            return self.if_stmt()

        if tok.type == TOKEN_KEYWORD and tok.value == 'while':
            return self.while_stmt()

        if tok.type == TOKEN_KEYWORD and tok.value == 'break':
            line, col = tok.line, tok.col
            self.advance()
            return AST.Break(line, col)

        if tok.type == TOKEN_KEYWORD and tok.value == 'return':
            line, col = tok.line, tok.col
            self.advance()
            # return may be bare or with expression
            if self.current.type == TOKEN_KEYWORD and self.current.value in ('end','else'):
                return AST.Return(None, line, col)
            expr = self.expression()
            return AST.Return(expr, line, col)

        if tok.type == TOKEN_KEYWORD and tok.value == 'print':
            line, col = tok.line, tok.col
            self.advance()
            self.eat(TOKEN_LPAREN)
            expr = self.expression()
            self.eat(TOKEN_RPAREN)
            return AST.Print(expr, line, col)

        if tok.type == TOKEN_KEYWORD and tok.value == 'output':
            line, col = tok.line, tok.col
            self.advance()
            self.eat(TOKEN_LPAREN)
            expr = self.expression()
            self.eat(TOKEN_RPAREN)
            return AST.Output(expr, line, col)

        # assignment statement
        if tok.type == TOKEN_IDENTIFIER and self.peek().type == TOKEN_EQUALS:
            name_tok = tok
            self.advance()  # ident
            self.eat(TOKEN_EQUALS)
            value = self.expression()
            return AST.Assign(name_tok, value)

        # call as statement
        if tok.type == TOKEN_IDENTIFIER and self.peek().type == TOKEN_LPAREN:
            return self.call()

        # fallback: expression statement
        expr = self.expression()
        return expr

    def let_decl(self):
        self.eat(TOKEN_KEYWORD)  # let
        name_tok = self.eat(TOKEN_IDENTIFIER)
        self.eat(TOKEN_COLON)
        type_tok = self.eat(TOKEN_TYPE)
        self.eat(TOKEN_EQUALS)
        value = self.expression()
        return AST.VarDecl(name_tok, type_tok, value)

    def function_def(self):
        kw_tok = self.eat(TOKEN_KEYWORD)  # function
        name_tok = self.eat(TOKEN_IDENTIFIER)
        self.eat(TOKEN_LPAREN)
        params = []
        if self.current.type != TOKEN_RPAREN:
            while True:
                p_name = self.eat(TOKEN_IDENTIFIER)
                self.eat(TOKEN_COLON)
                p_type = self.eat(TOKEN_TYPE)
                params.append((p_name, p_type))
                if self.current.type == TOKEN_COMMA:
                    self.advance()
                    continue
                break
        self.eat(TOKEN_RPAREN)
        ret_type = None
        if self.current.type == TOKEN_ARROW:
            self.advance()
            ret_type = self.eat(TOKEN_TYPE)
        self.expect_do()
        body = self.block_until_end_or_else()
        if self.current.type == TOKEN_KEYWORD and self.current.value == 'end':
            self.advance()
        else:
            raise ParseError("Expected 'end' to close function", self.file, kw_tok.line, kw_tok.col)
        return AST.FunctionDef(name_tok, params, ret_type, body, kw_tok.line, kw_tok.col)

    def expect_do(self):
        if self.current.type == TOKEN_KEYWORD and self.current.value == 'do':
            self.advance(); return
        raise ParseError("Expected 'do'", self.file, self.current.line, self.current.col)

    def block_until_end_or_else(self):
        stmts = []
        while not (self.current.type == TOKEN_KEYWORD and self.current.value in ('end','else')):
            if self.current.type == TOKEN_EOF:
                raise ParseError("Unexpected EOF in block", self.file, self.current.line, self.current.col)
            stmts.append(self.statement())
        return AST.Block(stmts, self.current.line, self.current.col)

    def if_stmt(self):
        if_tok = self.eat(TOKEN_KEYWORD)  # if
        cond = self.expression()
        self.expect_do()
        then_block = self.block_until_end_or_else()
        else_block = None
        if self.current.type == TOKEN_KEYWORD and self.current.value == 'else':
            self.advance()
            if self.current.type == TOKEN_KEYWORD and self.current.value == 'if':
                else_block = AST.Block([self.if_stmt()], if_tok.line, if_tok.col)
            else:
                self.expect_do()
                else_block = self.block_until_end_or_else()
        if self.current.type == TOKEN_KEYWORD and self.current.value == 'end':
            self.advance()
        else:
            raise ParseError("Expected 'end' after if", self.file, if_tok.line, if_tok.col)
        return AST.If(cond, then_block, else_block, if_tok.line, if_tok.col)

    def while_stmt(self):
        w_tok = self.eat(TOKEN_KEYWORD)
        cond = self.expression()
        self.expect_do()
        body = self.block_until_end_or_else()
        if self.current.type == TOKEN_KEYWORD and self.current.value == 'end':
            self.advance()
        else:
            raise ParseError("Expected 'end' after while", self.file, w_tok.line, w_tok.col)
        return AST.While(cond, body, w_tok.line, w_tok.col)

    # Expressions
    def expression(self): return self.bool_or()

    def bool_or(self):
        node = self.bool_and()
        while self.current.type == TOKEN_KEYWORD and self.current.value == 'or':
            op = self.current; self.advance()
            right = self.bool_and()
            node = AST.BinOp(node, op, right)
        return node

    def bool_and(self):
        node = self.equality()
        while self.current.type == TOKEN_KEYWORD and self.current.value == 'and':
            op = self.current; self.advance()
            right = self.equality()
            node = AST.BinOp(node, op, right)
        return node

    def equality(self):
        node = self.comparison()
        while self.current.type in (TOKEN_DOUBLE_EQUALS, TOKEN_NOT_EQUALS):
            op = self.current; self.advance()
            right = self.comparison()
            node = AST.BinOp(node, op, right)
        return node

    def comparison(self):
        node = self.term()
        while self.current.type in (TOKEN_LESS_THAN, TOKEN_LESS_EQUALS, TOKEN_GREATER_THAN, TOKEN_GREATER_EQUALS):
            op = self.current; self.advance()
            right = self.term()
            node = AST.BinOp(node, op, right)
        return node

    def term(self):
        node = self.factor()
        while self.current.type in (TOKEN_PLUS, TOKEN_MINUS):
            op = self.current; self.advance()
            right = self.factor()
            node = AST.BinOp(node, op, right)
        return node

    def factor(self):
        node = self.unary()
        while self.current.type in (TOKEN_MULTIPLY, TOKEN_DIVIDE):
            op = self.current; self.advance()
            right = self.unary()
            node = AST.BinOp(node, op, right)
        return node

    def unary(self):
        if self.current.type in (TOKEN_PLUS, TOKEN_MINUS):
            op = self.current; self.advance()
            node = self.unary()
            return AST.UnaryOp(op, node)
        return self.primary()

    def primary(self):
        tok = self.current
        if tok.type == TOKEN_NUMBER:
            self.advance(); return AST.Number(tok)
        if tok.type == TOKEN_STRING:
            self.advance(); return AST.String(tok)
        if tok.type == TOKEN_KEYWORD and tok.value in ('true','false'):
            self.advance(); return AST.Bool(tok.value == 'true', tok.line, tok.col)
        if tok.type == TOKEN_IDENTIFIER:
            if self.peek().type == TOKEN_LPAREN:
                return self.call()
            self.advance(); return AST.VarAccess(tok)
        if tok.type == TOKEN_LPAREN:
            self.advance()
            expr = self.expression()
            self.eat(TOKEN_RPAREN)
            return expr
        if tok.type == TOKEN_KEYWORD and tok.value in ('read_string','read_int'):
            kind = tok.value; line, col = tok.line, tok.col
            self.advance(); self.eat(TOKEN_LPAREN); self.eat(TOKEN_RPAREN)
            return AST.ReadInput(kind, line, col)
        raise ParseError(f"Unexpected token in expression: {tok}", self.file, tok.line, tok.col)

    def call(self):
        name_tok = self.eat(TOKEN_IDENTIFIER)
        self.eat(TOKEN_LPAREN)
        args = []
        if self.current.type != TOKEN_RPAREN:
            while True:
                args.append(self.expression())
                if self.current.type == TOKEN_COMMA:
                    self.advance(); continue
                break
        self.eat(TOKEN_RPAREN)
        return AST.Call(name_tok, args)
