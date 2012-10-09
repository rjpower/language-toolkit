#!/usr/bin/env python
from lisp import Program, Atom, SExpr
from plt.parser import parse, Scanner, unparse
import unittest

class TestLisp(unittest.TestCase):
  def test_parse_program(self):
    root = parse(Program, Scanner('(+ 1 2 3) (+ 123 123)'))
    print unparse(root)

  def test_parse_atom(self):
    print unparse(parse(Atom, '123'))
    
  def test_parse_sexpr(self):
    print unparse(parse(SExpr, '(1 2 3)'))
