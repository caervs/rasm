"""
Tools for converting spatially constrained diagram models into actual drawings
"""

import inspect
import math

from pivot.deduction.linear import PlanarEngine
from pivot.interface.shortcuts import PV
from pivot.lexicon.expression import Variable

from rasm.planar.primitives.shapes import Arc, Line, Polygon
from rasm.planar.primitives.text import Text


class Drawerset(object):
    """
    A relay between an Arranger and the multiple Drawer objects that
    will produce the output files
    """
    def __init__(self, drivers):
        """
        Initialize with the drawers
        """
        self.drivers = drivers

    def __getattr__(self, attr):
        """
        Proxy getting a method from multiple drawers
        """
        # TODO attr validation
        def multi_do(*args, **kwargs):
            """
            Perform the method call on each driver
            """
            for driver in self.drivers:
                getattr(driver, attr)(*args, **kwargs)

        return multi_do


# TODO abstract out common characteristics with 3d drawing
class Arranger(object):
    """
    Calls the drawing primitives necessary to convert a Diagram object
    into output files via Drawer objects
    """
    def __init__(self, drivers, directional=True):
        """
        Initialize
        """
        self.drawerset = Drawerset(drivers)
        self.directional = directional

    def _draw_component(self, var, component, components, solutions):
        postrot_solutions = {
            constraint.attr_name: value
            for constraint, value in solutions.items()
            if constraint.variable == var
        }
        prerot_solutions = {
            constraint.attr_name: value
            for constraint, value in solutions.items()
            if constraint.variable == Variable("{}__prerot".format(var))
        }
        component_solutions = prerot_solutions if prerot_solutions else postrot_solutions
        vars_for_subcomps = set(component_solutions).intersection(
            inspect.signature(component.components).parameters)
        sols_for_subcomps = {var: component_solutions[var] for var in
                             vars_for_subcomps}
        for subcomponent in component.components(**sols_for_subcomps):
            if prerot_solutions:
                # TODO fix leaky abstraction
                rot_point, angle = components.pivots[var]
                subcomponent = self._rotate_primitive(
                    subcomponent, solutions[rot_point], angle)
            # TODO support nested components
            if isinstance(subcomponent, Line):
                self.drawerset.draw_line(subcomponent)
            elif isinstance(subcomponent, Arc):
                self.drawerset.draw_arc(subcomponent)
            elif isinstance(subcomponent, Text):
                self.drawerset.draw_text(subcomponent)
            else:
                raise TypeError(type(subcomponent))

    def draw(self, components):
        """
        Draw a diagram
        """
        eng = PlanarEngine()
        solutions = eng.solve_equation_set(
            components.constraint_set_with_rotations())
        for var, component in components.items():
            self._draw_component(var, component, components, solutions)

        for equation in components.connection_set:
            p0, p1 = equation.subj, equation.obj
            points = [solutions[p0]]
            pivots = components.pivots.get((p0, p1))
            if pivots is not None:
                for pivot_point_expr in pivots:
                    points.append(
                        eng.evaluate_expression(pivot_point_expr, solutions))
            points.append(solutions[p1])
            points = [PV(*map(float, point)) for point in points]
            for i in range(len(points) - 1):
                if (p0, p1) not in components.curves:
                    self.drawerset.draw_line(
                        Line(
                            start=points[i], finish=points[i + 1]))

                else:
                    r = components.curves[(p0, p1)]
                    start, end = points[i], points[i + 1]
                    if r < 0:
                        r = -r
                        start, end = end, start
                    self.drawerset.draw_arc(
                        Arc(start=start, finish=end, rotation=360, radius=r))
                if self.directional:
                    self.add_arrowhead(points[0], points[-1], points[-2], p0,
                                       p1, components)
        # TODO automated connection intersection testing to insert blips
        self.drawerset.save()

    def add_arrowhead(self, start, head, tail, p0, p1, components):
        """
        Add an arrowhead to a line
        """
        triangle_height = 10
        direction = tail - head
        # TODO add normalization to pivot vectors
        n_direction = direction / math.sqrt(direction.x**2 + direction.y**2)
        if (p0, p1) in components.curves:
            orig_r = components.curves[(p0, p1)]
            r = abs(orig_r)
            inverted = orig_r < 0
            l0 = (start - head) / 2
            l0_len = math.sqrt(l0.x**2 + l0.y**2)
            l1_len = math.sqrt(r**2 - l0_len**2)
            angled = 90 if inverted else -90
            l0_rot_n = self._rotate_vector(l0, angled=angled) / l0_len
            l1 = l0_rot_n * l1_len
            to_centre = l1 + l0
            to_centre_n = to_centre / math.sqrt(to_centre.x**2 + to_centre.y**
                                                2)
            n_direction = self._rotate_vector(to_centre_n, angled=-angled)

        dir_rot = self._rotate_vector(n_direction, angled=90) / 2
        triangle_points = [
            head,
            head + n_direction * triangle_height + dir_rot * triangle_height,
            head + n_direction * triangle_height - dir_rot * triangle_height
        ]
        self.drawerset.draw_polygon(Polygon(points=triangle_points))

    @staticmethod
    def _rotate_primitive(primitive, centre_point, angle):
        """
        Rotate a drawing primitive
        """
        cosangle = math.cos(math.radians(angle))
        sinangle = math.sin(math.radians(angle))

        def rotate_point(p):
            """
            Rotate a single point about the center point
            """
            diff = p - centre_point
            return centre_point + PV(diff.x * cosangle - diff.y * sinangle,
                                     diff.x * sinangle + diff.y * cosangle)

        if isinstance(primitive, Line):
            return Line(
                start=rotate_point(primitive.start),
                finish=rotate_point(primitive.finish))
        elif isinstance(primitive, Arc):
            return Arc(start=rotate_point(primitive.start),
                       finish=rotate_point(primitive.finish),
                       rotation=primitive.rotation,
                       radius=primitive.radius,
                       large=primitive.large)
        elif isinstance(primitive, Text):
            return Line(
                anchor=rotate_point(primitive.anchor),
                text=primitive.text,
                alignment=primitive.aligment)
        else:
            raise TypeError(type(primitive))

    @staticmethod
    def _rotate_vector(pv, angler=None, angled=None):
        """
        Rotate a vector
        """
        assert (angler is not None) ^ (angled is not None)
        if angled:
            angler = math.radians(angled)
        # TODO pivot should make this easy with rot matrices and spinors
        sin = math.sin(angler)
        cos = math.cos(angler)
        return PV(cos * pv.x - sin * pv.y, sin * pv.x + cos * pv.y)
