"""
Textual two-dimensional components for diagrams
"""

from rasm.planar.components.base import DrawableMixin
from rasm.planar.primitives.text import Text


class Label(DrawableMixin):
    """
    A simple 2d component that renders as a text label
    """
    # TODO test Replicable
    def __init__(self, text, alignment):
        """
        Initialize
        """
        self.text = text
        self.alignment = alignment

    @staticmethod
    def constraints():
        """
        Spatial constraints for the Label
        """
        return {}

    def components(self, anchor):
        """
        Drawing primitives for the Label
        """
        yield Text(self.text, anchor, self.alignment)
