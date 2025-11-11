# azhar/interp.py

import sys
from azhar.errors import RuntimeErrorEx
from azhar import ast as AST
from azhar.builtins import install_builtins, call_builtin

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}
        self.functions = {}

    def set(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values: return self.values[name]
        if self.parent: return self.parent.get(name)
        raise RuntimeErrorEx(f"Undefined variable '{name}'")

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value; return
        if self.parent:
            self.parent.assign(name, value); return
        raise RuntimeErrorEx(f"Cannot assign to undeclared variable '{name}'")

    def set_func(self, name, func_def):
        self.functions[name] = func_def

    def get_func(self, name):
        if name in self.functions: return self.functions[name]
        if self.parent: return self.parent.get_func(name)
        raise RuntimeErrorEx(f"Undefined function '{name}'")

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class BreakSignal(Exception):
    pass

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        install_builtins(self.global_env)

    def run(self, node):
        m = getattr(self, f'visit_{type(node).__name__}', None)
        if not m: raise RuntimeErrorEx("Internal: missing interpreter method")
        return m(node)

    def visit_Program(self, node):
        for st in node.statements:
            self.run(st)

    def visit_Number(self, node): return node.value
    def visit_String(self, node): return node.value
    def visit_Bool(self, node): return node.value

    def visit_VarAccess(self, node):
        return self.current_env.get(node.name)

    def visit_VarDecl(self, node):
        val = self.run(node.value_node)
        self.current_env.set(node.name, val)
        return None

    def visit_Assign(self, node):
        val = self.run(node.value_node)
        self.current_env.assign(node.name, val)
        return None

    def visit_BinOp(self, node):
        if node.op_token.type == 'KEYWORD':
            if node.op_token.value == 'and':
                return bool(self.run(node.left)) and bool(self.run(node.right))
            if node.op_token.value == 'or':
                return bool(self.run(node.left)) or bool(self.run(node.right))
        left = self.run(node.left)
        right = self.run(node.right)
        t = node.op_token.type
        if t == 'PLUS': return left + right
        if t == 'MINUS': return left - right
        if t == 'MULTIPLY': return left * right
        if t == 'DIVIDE': return left // right
        if t == 'DOUBLE_EQUALS': return left == right
        if t == 'NOT_EQUALS': return left != right
        if t == 'LESS_THAN': return left < right
        if t == 'LESS_EQUALS': return left <= right
        if t == 'GREATER_THAN': return left > right
        if t == 'GREATER_EQUALS': return left >= right
        raise RuntimeErrorEx("Unknown binary operator")

    def visit_UnaryOp(self, node):
        v = self.run(node.node)
        if node.op_token.type == 'PLUS': return +v
        if node.op_token.type == 'MINUS': return -v
        return v

    def visit_If(self, node):
        if self.run(node.cond):
            self.run(node.then_block)
        else:
            if node.else_block: self.run(node.else_block)
        return None

    def visit_While(self, node):
        try:
            while self.run(node.cond):
                try:
                    self.run(node.body)
                except BreakSignal:
                    break
        finally:
            return None

    def visit_Break(self, node):
        raise BreakSignal()

    def visit_Block(self, node):
        prev = self.current_env
        self.current_env = Environment(prev)
        try:
            for st in node.statements:
                self.run(st)
        finally:
            self.current_env = prev
        return None

    def visit_FunctionDef(self, node):
        self.current_env.set_func(node.name, node)
        return None

    def visit_Call(self, node):
        # built-ins
        if node.name in ('print','output','read_string','read_int'):
            vals = [self.run(arg) for arg in node.args]
            return call_builtin(node.name, vals)
        func_def = self.current_env.get_func(node.name)
        prev_env = self.current_env
        call_env = Environment(prev_env)
        if len(node.args) != len(func_def.params):
            raise RuntimeErrorEx(f"function '{node.name}' arg count mismatch")
        for (p_name_tok, _p_type_tok), arg_expr in zip(func_def.params, node.args):
            call_env.set(p_name_tok.value, self.run(arg_expr))
        self.current_env = call_env
        try:
            self.run(func_def.body)
        except ReturnSignal as rs:
            self.current_env = prev_env
            return rs.value
        self.current_env = prev_env
        return None

    def visit_Return(self, node):
        val = None if node.expr is None else self.run(node.expr)
        raise ReturnSignal(val)

    def visit_Print(self, node):
        v = self.run(node.expr); print(v); return None

    def visit_Output(self, node):
        v = self.run(node.expr); sys.stdout.write(str(v)); sys.stdout.flush(); return None

    def visit_ReadInput(self, node):
        if node.kind == 'read_string':
            return sys.stdin.readline().rstrip('\n')
        s = sys.stdin.readline().strip()
        try: return int(s)
        except: raise RuntimeErrorEx("read_int got non-integer input")
