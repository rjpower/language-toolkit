import copy
import logging
import sys

FunctionType = sys.modules.get('types').FunctionType

def dict_like(value): return isinstance(value, dict)
def tree_like(value): return isinstance(value, TreeLike)
def list_like(value): return (hasattr(value, '__iter__') 
                              and not dict_like(value) 
                              and not isinstance(value, tuple))

def flatten(lst):
  res = []
  for elem in lst:
    if list_like(elem): res.extend(flatten(elem))
    else: res.append(elem)
  return res

class memoized(object):
  def __init__(self, key_fn):
    self.key_fn = key_fn
  
  def __call__(self, f):
    _cache = {}
    def cached(*args, **kw):
      key = self.key_fn(*args, **kw)
      if not key in _cache:
        _cache[key] = f(*args, **kw)
      return _cache[key]
    return cached

@memoized(lambda t: t.__class__)
def all_children(tree):
  return required_children(tree) + optional_children(tree)

@memoized(lambda t: t.__class__)
def required_children(tree):
  m = set()
  for c in tree.__class__.mro():
    m.update(getattr(c, '_required', []))
  return list(m)

@memoized(lambda t: t.__class__)
def optional_children(tree):
  m = set()
  for c in tree.__class__.mro():
    m.update(getattr(c, '_optional', []))
  return list(m)
  
class TreeLike(object):
  def __init__(self, *args, **kw):
    self.parent = None
    if len(args) > len(all_children(self)):
      raise Exception('Too many arguments for ' + self.__class__.__name__ + 
                      '.  Expected: ' + str(all_children(self)) + 
                      '.  Got: %s %s' % (args, kw))
    
    for i in range(len(args), len(required_children(self))):
      arg = required_children(self)[i]
      if not arg in kw:
        logging.debug("Missing initializer for %s.%s", self.node_type(), all_children(self)[i])

    for field in all_children(self):
      setattr(self, field, None)

    for field, a in zip(all_children(self), args):
      setattr(self, field, a)

    for k, v in kw.items():
      if not k in all_children(self):
        logging.warn('Keyword argument %s not recognized for %s: %s', k, self.node_type(), all_children(self))
      setattr(self, k, v)
      
  def ancestor(self, filter_fn=lambda n: True):
    'Return the first ancestor of this node matching filter_fn'
    assert isinstance(filter_fn, FunctionType)
    n = self.parent
    while n is not None:
      if filter_fn(n):
        return n
      n = n.parent
    raise Exception, 'Missing ancestor??'
    
  def node_type(self):
    return self.__class__.__name__
  
  def path(self):
    p = []
    n = self
    while n is not None:
      repr = '%s' % n.__class__.__name__
      if hasattr(n, 'name'):
        repr += '(%s)' % n.name 
      p.append(repr)
      n = n.parent
    return '.'.join(reversed(p))

  def copy(self):
    return copy.deepcopy(self)

  def child_dict(self):
    d = {}
    for k in all_children(self):
      d[k] = getattr(self, k)
    return d
  
  def children(self):
    return [v for (_, v) in self.child_dict().iteritems()]
  
  def __cmp__(self, o):
    if not isinstance(o, self.__class__):
      return 1
    return cmp(self.children(), o.children())
  
  def __str__(self):
    return repr(self)
  
  def __repr__(self):
    return tree_repr(self, {})

def tree_repr(tree, only_once):
  def _(node):
    if tree_like(node):
      return tree_repr(node, only_once)
    return repr(node)
  
  if id(tree) in only_once: 
    return only_once[id(tree)]
  
  only_once[id(tree)] = '<circular reference>'
  
  rv = tree.node_type() + ':\n'
  for k, v in tree.child_dict().items():
    if dict_like(v):
      for kk, vv in v.iteritems(): rv += '%s.%s : %s\n' % (k, kk, _(vv))
    elif list_like(v):
      for elem in v: rv += '%s: %s\n' % (k, _(elem))
    else:
      rv += '%s: %s\n' % (k, _(v))
  rv = rv.strip()
  only_once[id(tree)] = rv.replace('\n', '\n  |')
  return only_once[id(tree)]


def transform(tree, filter_fn, replace_fn):
  tree.mark_children()
  for k in all_children(tree):
    v = getattr(tree, k)
    if tree_like(v):
      v.parent = tree
      transform(v, filter_fn, replace_fn)
      if filter_fn(v): setattr(tree, k, replace_fn(v))
    elif dict_like(v):
      for kk, vv in v.iteritems():
        if filter_fn(vv): v[kk] = replace_fn(vv)
        if tree_like(v[kk]): 
          v[kk].parent = tree
          transform(v[kk], filter_fn, replace_fn)
    elif list_like(v):
      for i in range(len(v)):
        if tree_like(v[i]): 
          v[i].parent = tree
          transform(v[i], filter_fn, replace_fn)
        if filter_fn(v[i]): 
          v[i] = replace_fn(v[i])

def expand_children(tree, filter_fn=lambda n: True, depth= -1):
  if filter_fn(tree):
    yield tree
    
  if depth == 0:
    return
  
  for v in tree.children():  
    if tree_like(v): 
      yield expand_children(v, filter_fn, depth - 1)
    elif dict_like(v):
      for kk, vv in v.iteritems():
        if tree_like(v[kk]): 
          yield expand_children(v[kk], filter_fn, depth - 1)
    elif list_like(v):
      for vv in v:
        if tree_like(vv): 
          yield expand_children(vv, filter_fn, depth - 1) 

def find_all(tree, node_type):
  return flatten(expand_children(tree, filter_fn=lambda n: isinstance(n, node_type)))

