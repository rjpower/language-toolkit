from plt.tree import TreeLike
import logging

class Node(TreeLike):
  _optional = ['concrete']
  def __init__(self, *args, **kw):
    TreeLike.__init__(self, *args, **kw)


