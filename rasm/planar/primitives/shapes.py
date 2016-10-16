"""
Basic two-dimensional geometric shape primitives
"""

import math

from pivot.interface.shortcuts import PV
from replicate.replicable import preprocessor

from rasm.planar.primitives.base import Primitive


class Line(Primitive):
    """
    A line drawing primitive
    """
    @preprocessor
    def preprocess(start, finish):
        """
        Initialize
        """
        pass


class Polygon(Primitive):
    """
    A polygon drawing primitive
    """
    @preprocessor
    def preprocess(points):
        """
        Initialize
        """
        pass


class Arc(Primitive):
    """
    An arc drawing primitive
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._centre_point = None

    @preprocessor
    def preprocess(start, finish, rotation, radius, large=False):
        """
        Initialize
        """
        pass

    @property
    def centre_point(self):
        """
        The center of the circle of which the arc is a sub-arc
        """
        if self._centre_point:
            return self._centre_point
        # TODO factor out common logic with other parts
        diff = self.finish - self.start
        midpoint = self.start + diff / 2
        inverted = self.radius < 0
        angle = -90 if inverted else 90
        cosangle = math.cos(math.radians(angle))
        sinangle = math.sin(math.radians(angle))
        to_centre_dir = PV(diff.x * cosangle - diff.y * sinangle,
                           diff.x * sinangle + diff.y * cosangle)
        length = math.sqrt(to_centre_dir.x**2 + to_centre_dir.y**2)
        l0 = diff / 2
        l0_len = math.sqrt(l0.x**2 + l0.y**2)
        # NOTE because of floating point errors we might get
        # slightly below zero
        desired_length = math.sqrt(abs(self.radius**2 - l0_len**2))
        to_centre = (to_centre_dir / length) * desired_length
        self._centre_point = midpoint + to_centre
        return self._centre_point

    # TODO angle logic should probably be in latex module
    @staticmethod
    def angle(x, y):
        """
        Return the angle of a vector relative to a cartesian frame
        given the vector's cartesian coordinates
        """
        if y == 0:
            return 180 if x < 0 else 0
        elif x == 0:
            return 90 if y > 0 else 270
        else:
            ratio = float(y) / x
            # TODO better float truncation
            angled = int(math.degrees(math.atan(ratio)))
            return angled if x > 0 else angled + 180

    @property
    def anglea(self):
        """
        Return the angle of the first point of the arc
        """
        start = self.start if self.large else self.finish
        v = start - self.centre_point
        return self.angle(v.x, v.y)

    @property
    def angleb(self):
        """
        Return the angle of the second point of the arc
        """
        start = self.finish if self.large else self.start
        v = start - self.centre_point
        return self.angle(v.x, v.y)
