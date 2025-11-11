# azhar/types.py

from azhar.errors import TypeErrorEx

class Symbol:
    def __init__(self, name, type_name): self.name = name; self.type_name = type_name

class FunctionSymbol:
    def __init__(self, name, params, return_type):
        self.name = name
        self.params = params  # list of (name, type_name)
        self.return_type = return_type

class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}     # vars
        self.functions = {}   # funcs

    def define(self, name, type_name):
        self.symbols[name] = Symbol(name, type_name)

    def lookup(self, name):
        if name in self.symbols: return self.symbols[name]
        if self.parent: return self.parent.lookup(name)
        return None

    def define_func(self, name, params, return_type):
        self.functions[name] = FunctionSymbol(name, params, return_type)

    def lookup_func(self, name):
        if name in self.functions: return self.functions[name]
        if self.parent: return self.parent.lookup_func(name)
        return None

class TypeChecker:
    def __init__(self, file="<stdin>"):
        self.global_scope = Scope()
        self.current = self.global_scope
        self.file = file

    def check(self, node):
        m = getattr(self, f'visit_{type(node).__name__}', None)
        if not m: raise TypeErrorEx("Internal: missing type check method", self.file)
        return m(node)

    def visit_Program(self, node):
        for st in node.statements:
            self.check(st)

    def visit_Number(self, node): return 'int'
    def visit_String(self, node): return 'string'
    def visit_Bool(self, node): return 'bool'

    def visit_VarAccess(self, node):
        sym = self.current.lookup(node.name)
        if sym is None:
            raise TypeErrorEx(f"Undeclared variable '{node.name}'", self.file, node.token.line, node.token.col)
        return sym.type_name

    def visit_VarDecl(self, node):
        val_type = self.check(node.value_node)
        if val_type != node.type_name:
            raise TypeErrorEx(f"Cannot assign {val_type} to {node.type_name}", self.file, node.name_token.line, node.name_token.col)
        self.current.define(node.name, node.type_name)
        return 'void'

    def visit_Assign(self, node):
        sym = self.current.lookup(node.name)
        if sym is None:
            raise TypeErrorEx(f"Variable '{node.name}' not declared", self.file, node.name_token.line, node.name_token.col)
        val_type = self.check(node.value_node)
        if val_type != sym.type_name:
            raise TypeErrorEx(f"Cannot assign {val_type} to {sym.type_name}", self.file, node.name_token.line, node.name_token.col)
        return 'void'

    def visit_BinOp(self, node):
        # logical and/or tokens are KEYWORD type with values
        if node.op_token.type == 'KEYWORD':
            if node.op_token.value in ('and','or'):
                lt = self.check(node.left); rt = self.check(node.right)
                if lt != 'bool' or rt != 'bool':
                    raise TypeErrorEx("Logical operations require bool", self.file)
                return 'bool'
        lt = self.check(node.left); rt = self.check(node.right)
        t = node.op_token.type
        if t in ('PLUS','MINUS','MULTIPLY','DIVIDE'):
            if lt != 'int' or rt != 'int':
                raise TypeErrorEx("Arithmetic requires int", self.file)
            return 'int'
        if t in ('LESS_THAN','LESS_EQUALS','GREATER_THAN','GREATER_EQUALS'):
            if lt != 'int' or rt != 'int':
                raise TypeErrorEx("Comparison requires int", self.file)
            return 'bool'
        if t in ('DOUBLE_EQUALS','NOT_EQUALS'):
            if lt != rt:
                raise TypeErrorEx("Equality requires same types", self.file)
            return 'bool'
        raise TypeErrorEx("Unknown binary operator", self.file)

    def visit_UnaryOp(self, node):
        t = self.check(node.node)
        if node.op_token.type in ('PLUS','MINUS'):
            if t != 'int':
                raise TypeErrorEx("Unary +/- require int", self.file)
            return 'int'
        return t

    def visit_If(self, node):
        ct = self.check(node.cond)
        if ct != 'bool':
            raise TypeErrorEx("if condition must be bool", self.file, node.line, node.col)
        self.check(node.then_block)
        if node.else_block: self.check(node.else_block)
        return 'void'

    def visit_While(self, node):
        ct = self.check(node.cond)
        if ct != 'bool':
            raise TypeErrorEx("while condition must be bool", self.file, node.line, node.col)
        self.check(node.body)
        return 'void'

    def visit_Block(self, node):
        prev = self.current
        self.current = Scope(prev)
        for st in node.statements:
            self.check(st)
        self.current = prev
        return 'void'

    def visit_FunctionDef(self, node):
        ret_type = node.return_type_token.value if node.return_type_token else 'void'
        params = [(p[0].value, p[1].value) for p in node.params]
        self.current.define_func(node.name, params, ret_type)
        prev = self.current
        func_scope = Scope(prev)
        for pname, ptype in params:
            func_scope.define(pname, ptype)
        self.current = func_scope
        self.check(node.body)
        self.current = prev
        return 'void'

    def visit_Call(self, node):
        fsym = self.current.lookup_func(node.name)
        if fsym is None:
            raise TypeErrorEx(f"Undefined function '{node.name}'", self.file, node.name_token.line, node.name_token.col)
        if len(node.args) != len(fsym.params):
            raise TypeErrorEx(f"Function '{node.name}' expects {len(fsym.params)} args, got {len(node.args)}", self.file)
        for arg, (_, ptype) in zip(node.args, fsym.params):
            at = self.check(arg)
            if at != ptype:
                raise TypeErrorEx(f"Argument type mismatch for '{node.name}'", self.file, node.name_token.line, node.name_token.col)
        return fsym.return_type

    def visit_Return(self, node):
        if node.expr is None: return 'void'
        return self.check(node.expr)

    def visit_Print(self, node): self.check(node.expr); return 'void'
    def visit_Output(self, node): self.check(node.expr); return 'void'
    def visit_ReadInput(self, node): return 'string' if node.kind == 'read_string' else 'int'
