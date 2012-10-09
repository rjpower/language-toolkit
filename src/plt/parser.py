import logging
import re

class ParseError(Exception):
  def __init__(self, scanner, msg):
    self.pos = scanner.pos
    self.msg = msg
    self.scanner = scanner
    
  def __str__(self):
    return 'Parse error at position %s.  Expected %s, found "%s..."' % (
            self.pos, self.msg, self.scanner.source[self.pos:self.pos+5])

class Parser(object):
  pass

def pretty(obj):
  if hasattr(obj, '__name__'): return obj.__name__
  return repr(obj)
  
def parse(obj, scanner):
  logging.debug('Parsing... %s', obj)
  if isinstance(obj, str):
    obj = term(obj)
  
  if hasattr(obj, 'parser'):
    p = obj.parser()
    if isinstance(p, tuple): p = seq(*p)
    result = p.parse(scanner)
    return obj(result)
  else:
    return obj.parse(scanner)

def bnf(nodes):
  rules = []
  for n in nodes:
    left = n.__name__
    right = n.parser()
    rules.append((left, repr(right)))
  
  return rules

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
    logging.debug('Looking for %s at %s', pattern, self.source[self.pos:self.pos + 10])
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

class EndOfFile(Parser):
  def parse(self, scanner):
    scanner.nomnom()
    if scanner.pos == len(scanner.source):
      return
    raise ParseError(scanner, 'EOF')    

EOF = EndOfFile()

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
