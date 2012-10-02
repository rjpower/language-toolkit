
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

