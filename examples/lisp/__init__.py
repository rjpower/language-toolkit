import plt
import logging
import pprint
import re
import types

class Node(object):
  pass

class ParseError(Exception):
  def __init__(self, scanner, msg):
    self.pos = scanner.pos
    self.msg = msg
    
  def __str__(self):
    return 'Parse error at position %s: %s' % (self.pos, self.msg)

class Scanner(object):
  def __init__(self, source):
    self.source = source
    self.pos = 0
    self.marks = []
    self.whitespace = re.compile('\s+')
  
  def eat_whitespace(self):
    m = self.whitespace.match(self.source[self.pos:])
    if m is None:
      return
    self.pos += m.end()
    
  def scan(self, pattern):
    self.eat_whitespace()
    
    p = re.compile(pattern)
    logging.info('Looking for %s at %s', pattern, self.source[self.pos:self.pos+10])
    m = p.match(self.source[self.pos:])
    if m is None:
      raise ParseError(self, 'Searching for pattern %s' % pattern) 
    
    self.pos += m.end()
    
    if m.groups(): return m.groups()
    return m.group(0)
    
  def push_mark(self):
    self.marks.append(self.pos)
    
  def pop_mark(self):
    self.pos = self.marks.pop()


class Parser(object):
  pass
    
def pretty(obj):
  if hasattr(obj, '__name__'): return obj.__name__
  return repr(obj)
  
def parse(obj, scanner):
  logging.debug('Parsing... %s', obj)
  if hasattr(obj, 'parser'): 
    p = obj.parser()
  else:
    p = obj
  
  result = p.parse(scanner)
  logging.info('Result for %s : %s', obj, result)
  return result

class opt(Parser):
  def __init__(self, *seq):
    self.seq = seq
  
  def __repr__(self): 
    return ' | '.join(map(pretty, self.seq))
  
  def parse(self, scanner):
    errors = []
    for o in self.seq:
      scanner.push_mark()
      try:
        return parse(o, scanner)
      except ParseError, e:
        errors.append(e)
        logging.info('Error parsing option %s, trying next', o)
      scanner.pop_mark()
    raise ParseError(scanner, '\n'.join((str(e) for e in errors)))

class rep(Parser):
  def __init__(self, v, min=0, max=None):
    self.v = v
    self.min = min
    self.max = max

  def __repr__(self):
    return '%s*' % pretty(self.v)
  
  def parse(self, scanner):
    result = []
    while len(result) < self.min:
      result.append(parse(self.v, scanner))
    
    while len(result) < self.max or self.max is None:
      try:
        result.append(parse(self.v, scanner))
      except ParseError:
        return result

class seq(Parser):
  def __init__(self, *seq):
    self.seq = seq

  def __repr__(self):
    return ' '.join(map(pretty, self.seq))
  
  def parse(self, scanner):
    return [parse(v, scanner) for v in self.seq]
  
class term(Parser):
  def __init__(self, pattern):
    self.pattern = pattern
    
  def parse(self, scanner):
    return scanner.scan(self.pattern)
  
  def __repr__(self):
    return '%s' % self.pattern 

class Program(Node):
  @staticmethod
  def parser():
    return rep(Expr)

class Expr(Node):
  @staticmethod
  def parser():
    return opt(SExpr, Primitive)

class Primitive(Node):
  @staticmethod
  def parser():
    return opt(term('[0-9]+'), term('"[^"]+"'))

class SExpr(Node):
  @staticmethod
  def parser():
    return seq(term('[(]'), rep(Expr), term('[)]'))
  
def bnf():
  nodes = [v for v in globals().values() if hasattr(v, 'parser')]
  rules = []
  for n in nodes:
    left = n.__name__
    right = n.parser()
    rules.append((left, repr(right)))
  
  return rules

print '\n'.join('%s := %s' % (l, r) for (l, r) in bnf())
root = parse(Program, Scanner('(1 2 3)'))
print root
