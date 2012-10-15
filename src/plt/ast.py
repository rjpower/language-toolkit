from plt.parser import unparse
from plt.tree import TreeLike

class Node(TreeLike):
  _optional = ['concrete']
  
  def __init__(self, *args, **kw):
    TreeLike.__init__(self, *args, **kw)
    
  def __repr__(self):
    return unparse(self)


