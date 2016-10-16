"""
Components for drawing discrete logic system diagrams
"""

from pivot.interface.shortcuts import PV, V

from rasm.planar.components.base import DrawableMixin
from rasm.planar.primitives.shapes import Arc, Line
from rasm.units import cm


class MonadicGate(DrawableMixin):
    """
    Abstract base class for monadic gate components
    """
    width = .8 * cm
    height = .5 * cm

    @classmethod
    def constraints(cls, in0, out0):
        """
        spatial constraints for monadic gates
        """
        # TODO support rotations somehow
        return {out0 == in0 + V(cls.width, 0), }


class NotGate(MonadicGate):
    """
    A not gate
    """
    nib_radius = MonadicGate.width * .1

    def components(self, in0, out0):
        """
        Drawing primitives for a not gate
        """
        nib_left = out0 - PV(self.nib_radius * 2, 0)
        tl = in0 - PV(0, self.height / 2)
        bl = in0 + PV(0, self.height / 2)
        yield Line(bl, tl)
        yield Line(tl, nib_left)
        yield Line(nib_left, bl)
        # TODO change to Circle when exists
        yield Arc(nib_left, out0, 360, self.nib_radius)
        yield Arc(out0, nib_left, 360, self.nib_radius)


class DyadicGate(DrawableMixin):
    """
    Abstract base class for dyadic gate components
    """
    width = 1.5 * cm
    height = 1 * cm
    bus_height = height / 4

    @classmethod
    def constraints(cls, in0, in1, out0):
        """
        Spatial constraints for dyadic gates
        """
        return {
            in0 == out0 - V(cls.width, cls.bus_height),
            in1 == out0 - V(cls.width, -cls.bus_height),
        }


class AndGate(DyadicGate):
    """
    An and gate component
    """
    # TODO after adding rotator check to see if this can be a
    # class method
    def components(self, in0):
        """
        Drawing primitives for and gates
        """
        tl = in0 - PV(0, self.bus_height)
        br = tl + PV(self.width - self.height / 2, self.height)
        bl = PV(tl.x, br.y)
        tr = PV(br.x, tl.y)

        lines = [(tr, tl), (tl, bl), (bl, br)]
        for p0, p1 in lines:
            yield Line(p0, p1)
        yield Arc(tr, br, 180, self.height / 2)


class OrGate(DyadicGate):
    """
    An or gate
    """
    def components(self, in0, in1, out0):
        """
        Drawing primitives for or gates
        """
        tl = in0 - PV(self.bus_height / 2, self.bus_height)
        bl = in1 + PV(-self.bus_height / 2, self.bus_height)
        tm = tl + PV(self.width / 1.5, 0)
        bm = bl + PV(self.width / 1.5, 0)
        yield Line(tm, tl)
        yield Arc(tl, bl, -10, self.height / 1.5)
        yield Line(bl, bm)
        yield Arc(out0, bm, -10, self.height * 1.2)
        yield Arc(tm, out0, -10, self.height * 1.2)
