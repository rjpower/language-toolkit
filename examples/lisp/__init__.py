from plt import eval, ir
from plt.ast import Node
from plt.parser import bnf, rep, opt, term, seq, parse, Scanner, EOF, IGNORE
from plt.tree import TreeLike
import logging
import os.path

class Program(Node):
  _required = ['statements']
  
  @staticmethod
  def parser():
    return [('statements', rep(Expr)), EOF]
  
  def code(self): 
    return ir.Block([stmt.code() for stmt in self.statements]) 

class Expr(Node):
  _required = ['value']
  
  @staticmethod
  def parser():
    return ('value', opt(SExpr, Atom))
  
  def code(self):
    return self.value.code()

class Atom(Node):
  _required = ['value']
  
  @staticmethod
  def parser():
    return ('value', opt(Integer, String, Variable))
  
  def code(self): return self.value.code()

class Integer(Atom):
  parser = ('value', '[0-9]+')
  def code(self):
    return ir.Integer(int(self.value))
  
class String(Atom):
  parser = ('value', '"[^"]+"')
  def code(self):
    return ir.String(self.value[1:-1])

class Variable(Atom):
  parser = ('value', '[^0-9 ()"][^ ()"]*')
  def code(self):
    return ir.Lookup(self.value)
  
class SExpr(Node):
  _required = ['seq']
  
  @staticmethod
  def parser():
    return ['\\(', ('seq', rep(Expr)), '\\)']
  
  def code(self):
    return ir.Call(
             self.seq[0].code(),
             [v.code() for v in self.seq[1:]])

ROOT = os.path.dirname(__file__)
BUILTINS = eval.InterpreterEnv()
PRELUDE = parse(Program, Scanner(open(ROOT + '/prelude.plisp').read()))
BUILTINS.eval(PRELUDE.code())

NODES = [SExpr, Variable, String, Integer, Atom, Expr, Program]

if __name__ == '__main__':
  print '\n'.join('%s := %s' % (l, r) for (l, r) in bnf(NODES))
  root = parse(Program, Scanner('(+ 1 2) (+ 1 2)'))
  print root
