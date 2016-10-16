"""
An example state-transition diagram
"""

from pivot.interface.shortcuts import V

from rasm.planar.components.graphs import Node
from rasm.planar.diagram import Diagram
from rasm.units import cm

components = {
    "a": Node("A"),
    "b": Node("B"),
    "c_0": Node("C_0"),
    "c_1": Node("C_1"),
    "d": Node("D"),
    "e": Node("E"),
    "f": Node("F"),
}

diagram = Diagram.from_dict(components, True)


@diagram.add_connections_from_def
def connections(a, b, c_0, c_1, d, e, f):
    """
    Connections for the state transition diagram
    """
    return {
        a.e == b.w, b.e == c_0.w, c_0.n == c_1.n, c_1.s == c_0.s, c_1.e == d.e,
        d.w == e.e, e.w == f.e
    }


@diagram.apply_constraints_from_def
def constraints(a, b, c_0, c_1, d, e, f):
    """
    Spatial constraints for the state transition diagram
    """
    spacing = cm
    padv = V(spacing, 0)
    return {
        a.w == 3 * V(cm, cm),
        b.w == a.e + padv,
        c_0.w == b.e + padv,
        c_1.w == c_0.e + padv,
        d.n == c_1.s + V(0, spacing),
        e.e == d.w - padv,
        f.e == e.w - padv,
    }


@diagram.add_curves_from_def
def curves(c_0, c_1, d, _e):
    """
    Curves for the state transition diagram
    """
    return {
        (c_0.n, c_1.n): 4 * cm,
        (c_1.s, c_0.s): 4 * cm,
        (c_1.e, d.e): 4 * cm,
    }
