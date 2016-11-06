import inspect

import svgwrite

from replicate.replicable import Replicable, preprocessor
from pivot.lexicon.equation import EquationSet
from pivot.lexicon.expression import V, Variable
from pivot.deduction.linear import PlanarEngine
from pivot.ontology.plane import PV

# TODO should have units
cm = 50


class Primitive(Replicable):
    pass


class Text(Primitive):
    @preprocessor
    def preprocess(text, anchor, alignment):
        pass


class Line(Primitive):
    @preprocessor
    def preprocess(start, finish):
        pass


class Arc(Primitive):
    @preprocessor
    def preprocess(start, finish, rotation, radius, large=False):
        pass


class Drawer(object):
    pass


class SVGDrawer(Drawer):
    pass


class DrawableMixin(object):
    pass


class Label(DrawableMixin):
    # TODO test Replicable
    def __init__(self, text, alignment):
        self.text = text
        self.alignment = alignment

    def constraints(self, anchor):
        return {}

    def components(self, anchor):
        yield Text(self.text, anchor, self.alignment)


class MonadicGate(DrawableMixin):
    width = .8 * cm
    height = .5 * cm

    @classmethod
    def constraints(cls, in0, out0):
        # TODO support rotations somehow
        return {out0 == in0 + V(cls.width, 0), }


class NotGate(MonadicGate):
    nib_radius = MonadicGate.width * .1

    def components(self, in0, out0):
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
    width = 1.5 * cm
    height = 1 * cm
    bus_height = height / 4

    @classmethod
    def constraints(cls, in0, in1, out0):
        return {
            in0 == out0 - V(cls.width, cls.bus_height),
            in1 == out0 - V(cls.width, -cls.bus_height),
        }


class AndGate(DyadicGate):
    # TODO after adding rotator check to see if this can be a
    # class method
    def components(self, in0, in1, out0):
        tl = in0 - PV(0, self.bus_height)
        br = tl + PV(self.width - self.height / 2, self.height)
        bl = PV(tl.x, br.y)
        tr = PV(br.x, tl.y)

        lines = [(tr, tl), (tl, bl), (bl, br)]
        for p0, p1 in lines:
            yield Line(p0, p1)
        yield Arc(tr, br, 180, self.height / 2)


class OrGate(DyadicGate):
    def components(self, in0, in1, out0):
        tl = in0 - PV(self.bus_height / 2, self.bus_height)
        bl = in1 + PV(-self.bus_height / 2, self.bus_height)
        tm = tl + PV(self.width / 1.5, 0)
        bm = bl + PV(self.width / 1.5, 0)
        yield Line(tm, tl)
        yield Arc(tl, bl, -10, self.height / 1.5)
        yield Line(bl, bm)
        yield Arc(out0, bm, -10, self.height * 1.2)
        yield Arc(tm, out0, -10, self.height * 1.2)


class ComponentSet(dict):
    @classmethod
    def from_dict(cls, d):
        # TODO support nested structures
        cs = cls({Variable(name): component for name, component in d.items()})
        cs.constraint_set = set().union(
            *(EquationSet.from_set_def(component.constraints, var)
              for var, component in cs.items()))
        cs.connection_set = set()
        cs.pivots = dict()
        return cs

    def apply_constraints_from_def(self, constraint_def):
        # TODO validate constraint def parameters
        self.constraint_set |= EquationSet.from_set_def(constraint_def)

    def add_connections_from_def(self, connections_def):
        self.connection_set |= EquationSet.from_set_def(connections_def)

    def add_pivots_from_def(self, pivot_def):
        expected_arg_names = list(inspect.signature(pivot_def).parameters)
        args = {name: Variable(name) for name in expected_arg_names}
        self.pivots.update(pivot_def(**args))


def make_svg(name, components):
    dwg = svgwrite.Drawing('test.svg', profile='tiny')
    eng = PlanarEngine()
    solutions = eng.solve_equation_set(components.constraint_set)
    for var, component in components.items():
        component_solutions = {constraint.attr_name: value
                               for constraint, value in solutions.items()
                               if constraint.variable == var}
        for subcomponent in component.components(**component_solutions):
            # TODO support nested components
            if isinstance(subcomponent, Line):
                dwg.add(dwg.line(subcomponent.start,
                                 subcomponent.finish,
                                 stroke=svgwrite.rgb(10, 10, 16, '%')))
            elif isinstance(subcomponent, Arc):
                p = dwg.path('m{},{}'.format(subcomponent.start.x,
                                             subcomponent.start.y),
                             stroke=svgwrite.rgb(10, 10, 16, '%'),
                             fill=svgwrite.rgb(100, 100, 100, '%'),
                             fill_opacity="0.0")
                p.push_arc(target=subcomponent.finish - subcomponent.start,
                           rotation=subcomponent.rotation,
                           large_arc=subcomponent.large,
                           r=subcomponent.radius)
                dwg.add(p)
            elif isinstance(subcomponent, Text):
                dwg.add(dwg.text(subcomponent.text, insert=subcomponent.anchor,
                                 text_anchor=subcomponent.alignment,
                             ))
            else:
                raise TypeError(type(subcomponent))

    for equation in components.connection_set:
        p0, p1 = equation.subj, equation.obj
        points = [solutions[p0]]
        pivots = components.pivots.get((p0, p1))
        if pivots is not None:
            for pivot_point_expr in pivots:
                points.append(eng.evaluate_expression(pivot_point_expr,
                                                      solutions))
        points.append(solutions[p1])
        for i in range(len(points) - 1):
            dwg.add(dwg.line(points[i],
                             points[i + 1],
                             stroke=svgwrite.rgb(10, 10, 16, '%')))
    # TODO automated connection intersection testing to insert blips
    dwg.save()


def poc():
    """
    make a diagram for a simple one-bit adder
    """
    components = {
        "and0": AndGate(),
        "and1": AndGate(),
        "and2": AndGate(),
        "or0": OrGate(),
        "not0": NotGate(),
        "not1": NotGate(),
    }

    components.update({
        "in0": Label("in0", "end"),
        "in1": Label("in1", "end"),
        "out": Label("out", "start"),
        "carry": Label("carry", "start"),
    })

    cs = ComponentSet.from_dict(components)

    @cs.add_connections_from_def
    def connections(and0, and1, and2, or0, not0, not1):
        return {and1.out0 == or0.in0, and2.out0 == or0.in1, }

    @cs.apply_constraints_from_def
    def constraints(and0, and1, and2, or0, not0, not1,
                    in0, in1, out, carry):
        spacing = cm * 2
        vertical_spacing = V(0, spacing)
        return {
            and0.in0 == 3 * V(cm, cm),
            not0.in0 == and0.in0 + vertical_spacing,
            and1.in0 == not0.out0,
            not1.in0 == and0.in0 + 2 * vertical_spacing,
            and2.in0 == not1.out0,
            or0.in0.x == and0.out0.x + .8 * spacing,
            or0.out0.y == and1.out0.y + (and2.out0.y - and1.out0.y) / 2,

            in0.anchor == and0.in0 - V(spacing, 0),
            in1.anchor == and0.in1 - V(spacing, 0),
            out.anchor == or0.out0 + V(spacing, 0) / 2,
            carry.anchor == V(out.anchor.x, and0.out0.y),
        }

    @cs.add_connections_from_def
    def connections(and0, and1, and2, or0, not0, not1,
                    in0, in1, out, carry):
        return {
            in0.anchor == and0.in0,
            in1.anchor == and0.in1,

            and0.out0 == carry.anchor,
            or0.out0 == out.anchor,

            in0.anchor == not0.in0,
            in0.anchor == and2.in1,

            in1.anchor == not1.in0,
            in1.anchor == and1.in1,
        }

    @cs.add_pivots_from_def
    def pivots(and0, and1, and2, or0, not0, not1,
               in0, in1):
        ps = .4 * cm
        # TODO can factor out common pivot point logic
        return {
            (and1.out0, or0.in0):
            [and1.out0 + V(ps, 0), V(and1.out0.x + ps, or0.in0.y)],
            (and2.out0, or0.in1):
            [and2.out0 + V(ps, 0), V(and2.out0.x + ps, or0.in1.y)],

            (in0.anchor, not0.in0):
            [in0.anchor + V(ps, 0), V(in0.anchor.x + ps, not0.in0.y)],
            (in0.anchor, and2.in1):
            [in0.anchor + V(ps, 0), V(in0.anchor.x + ps, and2.in1.y)],

            (in1.anchor, not1.in0):
            [in1.anchor + V(2 * ps, 0), V(in1.anchor.x + 2 * ps, not1.in0.y)],
            (in1.anchor, and1.in1):
            [in1.anchor + V(2 * ps, 0), V(in1.anchor.x + 2 * ps, and1.in1.y)],
        }

    make_svg('test.svg', cs)


poc()
