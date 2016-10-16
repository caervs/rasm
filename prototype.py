import svgwrite


class Arranger(object):
    pass


class Drawer(object):
    pass


class SVGDrawer(Drawer):
    pass


class DrawableMixin(object):
    pass


class DyadicGate(DrawableMixin):
    width = 2 * cm
    height = 1 * cm
    bus_height = height / 4

    @classmethod
    def constraints(cls, in0, in1, out0, rot=I):
        return {
            in0 <= out0 - rot * (cls.width, cls.bus_height),
            in1 <= out0 - rot * (cls.width, -cls.bus_height),
        }


class AndGate(DrawableMixin):
    def components(self, in0, in1, out0):
        return {
            Line(),
            Line(),
            Line(),
            Arc()
        }


def example():
    and0 = AndGate(in0=(0, 0))
    and1 = AndGate(in0=and0.out0, rot=Rot(90))
