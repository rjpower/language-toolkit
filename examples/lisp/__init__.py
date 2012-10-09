from plt.parser import bnf, rep, opt, term, seq, parse, Scanner, EOF
from plt.tree import TreeLike
import logging

class Node(TreeLike):
  def __init__(self, *args, **kw):
    TreeLike.__init__(self, *args, **kw)

class Program(Node):
  _required = ['expressions']
  
  @staticmethod
  def parser():
    return rep(Expr), EOF

class Expr(Node):
  _required = ['value']
  
  @staticmethod
  def parser():
    return opt(SExpr, Primitive)

class Primitive(Node):
  _required = ['value']
  
  @staticmethod
  def parser():
    return opt('[0-9]+', '"[^"]+"', '[^() ]+')

class SExpr(Node):
  _required = ['seq']
  
  @staticmethod
  def parser():
    return '\\(', rep(Expr), '\\)'

NODES = [Program, Expr, Primitive, SExpr]

if __name__ == '__main__':
  print '\n'.join('%s := %s' % (l, r) for (l, r) in bnf(NODES))
  root = parse(Program, Scanner('(+ 1 2 3) (+ 1 2 3)'))
  print root
