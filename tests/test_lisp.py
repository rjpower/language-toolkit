#!/usr/bin/env python
from lisp import Program, Atom, SExpr
from plt.eval import InterpreterEnv
from plt.parser import parse, unparse
import lisp
import unittest


class TestLisp(unittest.TestCase):
  def _parse_test(self, klass, expr):
    self.assertEqual(unparse(parse(klass, expr)), expr)
     
  def test_parse_program(self):
    self._parse_test(Program, '(+ 1 2 3) (+ 123 123)')

  def test_parse_atom(self):
    self._parse_test(Atom, '123')
    
  def test_parse_sexpr(self):
    self._parse_test(SExpr, '(1 2 3)')

  def test_eval_int(self):
    p = parse(Atom, '123')
    env = InterpreterEnv(lisp.BUILTINS)
    self.assertEqual(p.eval(env), 123)
    
  def test_eval_sexpr(self):
    p = parse(SExpr, '(+ 123 456)')
    env = InterpreterEnv(lisp.BUILTINS)
    self.assertEqual(p.eval(env), 579)
    
  def test_eval_program(self):
    p = parse(Program, '(+ 123 456) (+ 1 2) (+ 4 5 6)')
    env = InterpreterEnv(lisp.BUILTINS)
    self.assertSequenceEqual([579, 3, 15], p.eval(env))
    