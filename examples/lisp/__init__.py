from plt import eval, ir
from plt.ast import Node
from plt.parser import bnf, rep, opt, term, seq, parse, Scanner, EOF, IGNORE
from plt.tree import TreeLike
import logging

BUILTINS = {}
BUILTINS['+'] = ir.Function(
  ir.Return(
    ir.Add(ir.Arg(0), ir.Arg(1))))

class Program(Node):
  _required = ['statements']
  
  @staticmethod
  def parser():
    return [('statements', rep(Expr)), EOF]
  
  def eval(self):
    return [stmt.eval() for stmt in self.statements] 

class Expr(Node):
  _required = ['value']
  
  @staticmethod
  def parser():
    return ('value', opt(SExpr, Atom))
  
  def eval(self):
    return self.value.eval()

class Atom(Node):
  _required = ['value']
  
  @staticmethod
  def parser():
    return ('value', opt(Integer, String, Variable))
  
  def eval(self): return self.value.eval()

class Integer(Atom):
  parser = ('value', '[0-9]+')
  def eval(self):
    return ir.Integer(int(self.value))
  
class String(Atom):
  parser = ('value', '"[^"]+"')
  def eval(self):
    return ir.String(self.value[1:-1])

class Variable(Atom):
  parser = ('value', '[^0-9 ()"][^ ()"]*')
  def eval(self):
    return ir.Lookup(self.value)
  
class SExpr(Node):
  _required = ['seq']
  
  @staticmethod
  def parser():
    return ['\\(', ('seq', rep(Expr)), '\\)']
  
  def eval(self):
    return ir.Call(
             self.seq[0].eval(),
             [v.eval() for v in self.seq[1:]])

NODES = [Program, Expr, Atom, SExpr]

if __name__ == '__main__':
  print '\n'.join('%s := %s' % (l, r) for (l, r) in bnf(NODES))
  root = parse(Program, Scanner('(+ 1 2 3) (+ 1 2 3)'))
  print root
