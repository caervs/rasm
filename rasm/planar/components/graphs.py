"""
Components for drawing vertex-edge graphs
"""

from pivot.interface.shortcuts import V

from rasm.planar.components.base import DrawableMixin
from rasm.planar.primitives.shapes import Arc
from rasm.planar.primitives.text import Text
from rasm.units import cm


class Node(DrawableMixin):
    """
    A graph vertex
    """
    radius = cm * .75

    def __init__(self, text):
        """
        Initialize with some text
        """
        self.text = text

    def components(self, e, w):
        """
        Drawing primitives for a graph vertex
        """
        yield Arc(e, w, 360, self.radius)
        yield Arc(w, e, 360, self.radius)
        c = w + ((e - w) / 2)
        yield Text(self.text, c, 'middle')

    @classmethod
    def constraints(cls, e, n, w, s):
        """
        Sptial constraints for a graph vertex
        """
        return {
            n == e - V(cls.radius, cls.radius),
            w == e - V(2 * cls.radius, 0),
            s == e - V(cls.radius, -cls.radius),
        }
