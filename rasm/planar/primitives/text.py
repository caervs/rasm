"""
Textual drawing primitives
"""

from replicate.replicable import preprocessor

from rasm.planar.primitives.base import Primitive


class Text(Primitive):
    """
    Text drawing primitive
    """
    @preprocessor
    def preprocess(text, anchor, alignment):
        """
        Initialize
        """
        pass
