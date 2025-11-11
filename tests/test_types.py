import pytest
from azhar.lexer import Lexer
from azhar.parser import Parser
from azhar.types import TypeChecker
from azhar.errors import TypeErrorEx

def typecheck(src):
    tokens = Lexer(src, file="<test>").tokenize()
    program = Parser(tokens, file="<test>").parse()
    TypeChecker(file="<test>").check(program)

def test_good_types():
    typecheck('let a: int = 3\nfunction f(x:int)->int do return x end\n')  # valid decls and function [attached_file:1]

def test_assignment_type_mismatch():
    with pytest.raises(TypeErrorEx):
        typecheck('let a: int = 3\na = "s"')  # cannot assign string to int [attached_file:1]

def test_undeclared_var():
    with pytest.raises(TypeErrorEx):
        typecheck('a = 1')  # a not declared [attached_file:1]
