from plt.tree import TreeLike
import logging
import re
import types

IGNORE = '_'

def as_list(lst):
  if isinstance(lst, list): return lst
  return [lst]

class ParseError(Exception):
  def __init__(self, scanner, msg):
    self.pos = scanner.pos
    self.msg = msg
    self.scanner = scanner
    
  def __str__(self):
    return 'Parse error at position %s.  Expected %s, found "%s..."' % (
            self.pos, self.msg, self.scanner.source[self.pos:self.pos + 5])

class Scanner(object):
  def __init__(self, source):
    self.source = source
    self.pos = 0
    self.marks = []
    self.whitespace = re.compile('\s+')
  
  def nomnom(self):
    'Eat any characters matching the whitespace regex.'
    m = self.whitespace.match(self.source[self.pos:])
    if m is None:
      return
    self.pos += m.end()
    
  def scan(self, pattern):
    self.nomnom()
    
    p = re.compile(pattern)
#    logging.info('Looking for "%s", position "%s"', pattern, self.source[self.pos:self.pos+2])
    m = p.match(self.source[self.pos:])
    if m is None:
      raise ParseError(self, 'Searching for pattern %s' % pattern) 
    
#    logging.info('Ate "%s" -- "%s"', pattern, m.group(0))
    self.pos += m.end()
    
    if m.groups(): return m.groups()
    result = m.group(0)
    return result
    
  def push_mark(self):
    self.marks.append(self.pos)
    
  def pop_mark(self):
    self.pos = self.marks.pop()


class Parser(object):
  pass

class EndOfFile(Parser):
  def parse(self, scanner):
    scanner.nomnom()
    if scanner.pos == len(scanner.source):
      return None
    raise ParseError(scanner, 'EOF')
  
  def __repr__(self): return 'EOF'    

EOF = EndOfFile()

def pretty(obj):
  if hasattr(obj, '__name__'): return obj.__name__
  return repr(obj)
  
def get_parser(obj):
  if isinstance(obj, str): return term(obj)
  if isinstance(obj, list): return seq(*obj)
  if not hasattr(obj, 'parser'): return obj
  return ObjParser(obj)

def parse(obj, scanner):
  if isinstance(scanner, str): scanner = Scanner(scanner)
  return get_parser(obj).parse(scanner)
  
def unparse(obj):
  if isinstance(obj, list): return ' '.join(map(unparse, obj))
  if isinstance(obj, str): return obj
  if obj is None: return ''
  
  r = ''
  for v in obj.concrete:
    r += unparse(v)
  return r
    
def bnf(nodes):
  rules = []
  for n in nodes:
    left = n.__name__
    right = n.parser()
    rules.append((left, repr(right)))
  
  return rules

class ObjParser(Parser):
  def __init__(self, klass):
    self.klass = klass
    p = klass.parser
    if isinstance(p, types.FunctionType): p = p()
    self.assignments = as_list(p)
  
  def parse(self, scanner):
    args = {}
    concrete = []
    for name, p in self.assignments:
      v = parse(p, scanner)
      concrete.append(v)
      if name != IGNORE: args[name] = v
    args['concrete'] = concrete
    return self.klass(**args) 

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
        logging.debug('Error parsing option %s, trying next', o)
      scanner.pop_mark()
    raise ParseError(scanner, '\n'.join((str(e) for e in errors)))

class rep(Parser):
  def __init__(self, v, minrep=0, maxrep=None):
    self.v = v
    self.minrep = minrep
    self.maxrep = maxrep

  def __repr__(self):
    return '%s*' % pretty(self.v)
  
  def parse(self, scanner):
    result = []
    while len(result) < self.minrep:
      result.append(parse(self.v, scanner))
    
    while len(result) < self.maxrep or self.maxrep is None:
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
