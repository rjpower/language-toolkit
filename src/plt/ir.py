from plt.ast import Node

class Function(Node):
  _required = ['arguments', 'block']

class Block(Node):
  _required = ['statements']

class Arg(Node):
  _required = ['index']
  
class Return(Node):
  _required = ['value']
  
class Lookup(Node):
  _required = ['name']
  
class Call(Node):
  _required = ['function', 'arguments']

class BinaryOp(Node):
  _required = ['left', 'right']

class Add(BinaryOp):
  _op = '+'
  
class Const(Node):
  _required = ['value']

class Integer(Const): pass
class String(Const): pass
