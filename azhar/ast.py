# azhar/ast.py

class Node: pass

class Program(Node):
    def __init__(self, statements): self.statements = statements

class Number(Node):
    def __init__(self, token): self.token = token; self.value = token.value

class String(Node):
    def __init__(self, token): self.token = token; self.value = token.value

class Bool(Node):
    def __init__(self, value, line, col): self.value = value; self.line = line; self.col = col

class VarAccess(Node):
    def __init__(self, name_token): self.name = name_token.value; self.token = name_token

class VarDecl(Node):
    def __init__(self, name_token, type_token, value_node):
        self.name = name_token.value; self.name_token = name_token
        self.type_name = type_token.value; self.type_token = type_token
        self.value_node = value_node

class Assign(Node):
    def __init__(self, name_token, value_node):
        self.name = name_token.value; self.name_token = name_token
        self.value_node = value_node

class BinOp(Node):
    def __init__(self, left, op_token, right):
        self.left = left; self.op_token = op_token; self.right = right

class UnaryOp(Node):
    def __init__(self, op_token, node): self.op_token = op_token; self.node = node

class If(Node):
    def __init__(self, cond, then_block, else_block, line, col):
        self.cond = cond; self.then_block = then_block; self.else_block = else_block; self.line = line; self.col = col

class While(Node):
    def __init__(self, cond, body, line, col): self.cond = cond; self.body = body; self.line = line; self.col = col

class Break(Node):
    def __init__(self, line, col): self.line = line; self.col = col

class Block(Node):
    def __init__(self, statements, line, col): self.statements = statements; self.line = line; self.col = col

class FunctionDef(Node):
    def __init__(self, name_token, params, return_type_token, body, line, col):
        self.name = name_token.value; self.name_token = name_token
        self.params = params; self.return_type_token = return_type_token
        self.body = body; self.line = line; self.col = col

class Call(Node):
    def __init__(self, name_token, args): self.name = name_token.value; self.name_token = name_token; self.args = args

class Return(Node):
    def __init__(self, expr, line, col): self.expr = expr; self.line = line; self.col = col

class Print(Node):
    def __init__(self, expr, line, col): self.expr = expr; self.line = line; self.col = col

class Output(Node):
    def __init__(self, expr, line, col): self.expr = expr; self.line = line; self.col = col

class ReadInput(Node):
    def __init__(self, kind, line, col): self.kind = kind; self.line = line; self.col = col
