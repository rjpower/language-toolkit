#!/usr/bin/env python
from plt.ast import Node
import logging

class ScopedMap(object):
  def __init__(self, parent=None):
    self.parent = parent
    self.locals = {}
    self.referenced = {}
    
  def __iter__(self):
    return iter(dict(self.items()))
  
  def keys(self):
    return [k for k, _ in self.items()]
  
  def tree(self):
    m = self
    r = []
    while m:
      r.append(m)
      m = m.parent
    r.reverse()
    return r
  
  def items(self):
    combined = {}
    all_dicts = self.tree()
    for d in all_dicts:
      combined.update(d.locals)
    return combined.items()
  
  def get(self, k, defval):
    if k in self:
      return self[k]
    return defval
  
  def __setitem__(self, k, v):
    assert isinstance(k, str), 'Non-string key in binding map? %s' % k
    # check parent scopes first
    p = self.parent
    while p:
      if k in p.locals: 
        p.locals[k] = v
        return
      p = p.parent
    self.locals[k] = v
  
  def __contains__(self, k):
    if k in self.locals: return True
    if self.parent: return k in self.parent
    return False
  
  def __getitem__(self, k):
    self.referenced[k] = 1
    if k in self.locals: return self.locals[k]
    if self.parent: return self.parent[k]
    raise KeyError, 'Missing key %s' % k
  
  def __repr__(self):
    return 'ScopedMap(%s)' % dict(self.items())
  
class ReturnException(Exception):
  def __init__(self, value):
    self.value = value

class InterpreterEnv(ScopedMap):
  def eval(self, tree):
    def Add():
      return self.eval(tree.left) + self.eval(tree.right)
    def Integer():
      return tree.value
    def Block():
      logging.info('BLOCK')
      try:
        last = None
        for stmt in tree.statements:
          last = self.eval(stmt)
        return last
      except ReturnException, e:
        return e.value
    def Lookup():
      return self[tree.name]
    def Return():
      raise ReturnException(self.eval(tree.value))
    def Call():
      f = self.eval(tree.function)
      s = InterpreterEnv(self)
      for (name, vref) in zip(f.arguments, tree.arguments):
        s[name] = self.eval(vref)
      logging.info('Call: %s', f.block.node_type()) 
      return s.eval(f.block)
    return locals()[tree.node_type()]()
    
    
