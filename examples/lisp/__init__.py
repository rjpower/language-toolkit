from plt.ast import Node
from plt.eval import ScopedMap, Environment
from plt.parser import bnf, rep, opt, term, seq, parse, Scanner, EOF, IGNORE
from plt.tree import TreeLike
import logging

BUILTINS = Environment()
BUILTINS['+'] = lambda args, env: sum([arg.eval(env) for arg in args])

class Program(Node):
  _required = ['statements']
  
  @staticmethod
  def parser():
    return [('statements', rep(Expr)), EOF]
  
  def eval(self, env):
    return [stmt.eval(env) for stmt in self.statements] 

class Expr(Node):
  _required = ['value']
  
  @staticmethod
  def parser():
    return ('value', opt(SExpr, Atom))
  
  def eval(self, env):
    return self.value.eval(env)

class Atom(Node):
  _required = ['value']
  
  @staticmethod
  def parser():
    return ('value', opt(Integer, String, Variable))
  
  def eval(self, env):
    return self.value.eval(env)

class Integer(Atom):
  parser = ('value', '[0-9]+')
  def eval(self, env):
    return int(self.value)
  
class String(Atom):
  parser = ('value', '"[^"]+"')
  def eval(self, env):
    return self.value[1:-1]

class Variable(Atom):
  parser = ('value', '[^0-9 ()"][^ ()"]*')
  def eval(self, env):
    return env[self.value]
  
class SExpr(Node):
  _required = ['seq']
  
  @staticmethod
  def parser():
    return ['\\(', ('seq', rep(Expr)), '\\)']
  
  def eval(self, env):
    head = self.seq[0].eval(env)
    return head(self.seq[1:], env)

NODES = [Program, Expr, Atom, SExpr]

if __name__ == '__main__':
  print '\n'.join('%s := %s' % (l, r) for (l, r) in bnf(NODES))
  root = parse(Program, Scanner('(+ 1 2 3) (+ 1 2 3)'))
  print root
