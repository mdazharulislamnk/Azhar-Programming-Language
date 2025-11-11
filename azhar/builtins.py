# azhar/builtins.py

import sys
from azhar.errors import RuntimeErrorEx

def install_builtins(env):
    # print, output, read_string, read_int are dispatched in interpreter's Call
    env.set_func('print', ('__builtin__',))
    env.set_func('output', ('__builtin__',))
    env.set_func('read_string', ('__builtin__',))
    env.set_func('read_int', ('__builtin__',))

def call_builtin(name, args):
    if name == 'print':
        if len(args) != 1: raise RuntimeErrorEx("print expects 1 argument")
        print(args[0]); return None
    if name == 'output':
        if len(args) != 1: raise RuntimeErrorEx("output expects 1 argument")
        sys.stdout.write(str(args[0])); sys.stdout.flush(); return None
    if name == 'read_string':
        if len(args) != 0: raise RuntimeErrorEx("read_string takes no arguments")
        return sys.stdin.readline().rstrip('\n')
    if name == 'read_int':
        if len(args) != 0: raise RuntimeErrorEx("read_int takes no arguments")
        s = sys.stdin.readline().strip()
        try: return int(s)
        except: raise RuntimeErrorEx("read_int got non-integer input")
    return None
