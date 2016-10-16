"""
The PlanarDrawer interface
"""

# TODO proper interface
class PlanarDrawer(object):
    """
    Abstract base class and interface for two-dimensional drawers
    """
    def draw_arc(self, arc):
        """
        Draw an Arc primitive
        """
        raise NotImplementedError

    def draw_line(self, line):
        """
        Draw a Line primitive
        """
        raise NotImplementedError

    def draw_text(self, text):
        """
        Draw a Text primitive
        """
        raise NotImplementedError

    def draw_polygon(self, polygon):
        """
        Draw a Polygon primitive
        """
        raise NotImplementedError
