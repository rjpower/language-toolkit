from plt.ast import Node
from plt.parser import bnf, rep, opt, term, seq, parse, Scanner, EOF, IGNORE
from plt.tree import TreeLike
import logging

class Program(Node):
  _required = ['expressions']
  
  @staticmethod
  def parser():
    return [('expressions', rep(Expr)),
            (IGNORE, EOF)]

class Expr(Node):
  _required = ['value']
  
  @staticmethod
  def parser():
    return ('value', opt(SExpr, Atom))

class Atom(Node):
  _required = ['value']
  
  @staticmethod
  def parser():
    return ('value', opt(Integer, String, Variable))

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
    return [(IGNORE, '\\('), 
            ('seq', rep(Expr)), 
            (IGNORE, '\\)')]
  
  def eval(self, env):
    head = self.seq[0].eval
    return head(self.seq[1:])

NODES = [Program, Expr, Atom, SExpr]

if __name__ == '__main__':
  print '\n'.join('%s := %s' % (l, r) for (l, r) in bnf(NODES))
  root = parse(Program, Scanner('(+ 1 2 3) (+ 1 2 3)'))
  print root
