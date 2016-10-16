"""
Objects for modeling two-dimensional diagrams
"""

import inspect
import math

from pivot.lexicon.expression import Variable
from pivot.lexicon.equation import EquationSet


class Diagram(dict):
    """
    A two-dimensional diagram
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize
        """
        super().__init__(*args, **kwargs)
        self.constraint_set = set()
        self.connection_set = set()
        self.pivots = dict()
        self.curves = dict()
        self.directed = False

    @classmethod
    def from_dict(cls, d, directed=False):
        """
        Create a diagram from a dict mapping component names
        to their corresponding components
        """
        # TODO support nested structures
        diagram = cls(
            {Variable(name): component
             for name, component in d.items()})
        diagram.directed = directed
        return diagram

    def apply_constraints_from_def(self, constraint_def):
        """
        Add constraints from a function that outputs an EquationSet
        """
        # TODO validate constraint def parameters
        self.constraint_set |= EquationSet.from_set_def(constraint_def)

    def add_connections_from_def(self, connections_def):
        """
        Add connections from a function that outputs an EquationSet
        """
        self.connection_set |= EquationSet.from_set_def(connections_def)

    def add_pivots_from_def(self, pivot_def):
        """
        Add pivots from a function that outputs a dict mapping ordered pairs
        of line terminals to lists of the lines' corresponding pivot points
        """
        expected_arg_names = list(inspect.signature(pivot_def).parameters)
        args = {name: Variable(name) for name in expected_arg_names}
        self.pivots.update(pivot_def(**args))

    def add_curves_from_def(self, curve_def):
        """
        Add pivots from a function that outputs a dict mapping ordered pairs
        of line terminals to curvature values for those lines
        """
        expected_arg_names = list(inspect.signature(curve_def).parameters)
        args = {name: Variable(name) for name in expected_arg_names}
        self.curves.update(curve_def(**args))

    def constraint_set_with_rotations(self):
        """
        Return the full constraint set for the diagram as an EquationSet
        """
        es = EquationSet(self.constraint_set)
        for comp_var, component in self.items():
            if comp_var not in self.pivots:
                es |= EquationSet.from_set_def(component.constraints, comp_var)
            else:
                comp_prerot = Variable("{}__prerot".format(comp_var))
                es |= EquationSet.from_set_def(self[comp_var].constraints,
                                               comp_prerot)
                unscoped = EquationSet.from_set_def(self[comp_var].constraints)
                rot_point, angle = self.pivots[comp_var]
                cosangle = math.cos(math.radians(angle))
                sinangle = math.sin(math.radians(angle))
                varnames = set(var.attr_chain[0] for var in unscoped.variables)
                for varname in varnames:
                    prerot = getattr(comp_prerot, varname)
                    postrot = getattr(comp_var, varname)
                    if (comp_var.name, varname) == rot_point.attr_chain:
                        es |= {prerot == postrot, }
                        continue
                    diffx = prerot.x - rot_point.x
                    diffy = prerot.y - rot_point.y
                    additions = {
                        postrot.x ==
                        rot_point.x + cosangle * diffx - sinangle * diffy,
                        postrot.y ==
                        rot_point.y + sinangle * diffx + cosangle * diffy,
                    }
                    es |= additions
        return es
