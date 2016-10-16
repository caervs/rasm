"""
An example XOR gate diagram
"""

from pivot.interface.shortcuts import V

from rasm.planar.components.logic import AndGate, OrGate, NotGate
from rasm.planar.components.label import Label
from rasm.planar.diagram import Diagram
from rasm.units import cm

components = {
    "and0": AndGate(),
    "and1": AndGate(),
    "and2": AndGate(),
    "or0": OrGate(),
    "not0": NotGate(),
    "not1": NotGate(),
}

components.update({
    "in0": Label("in_0", "end"),
    "in1": Label("in_1", "end"),
    "out": Label("out", "start"),
    "carry": Label(r"carry", "start"),
})

diagram = Diagram.from_dict(components)


@diagram.apply_constraints_from_def
def constraints(and0, and1, and2, or0, not0, not1, in0, in1, out, carry):
    """
    XOR gate spatial constraints
    """
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


@diagram.add_connections_from_def
def connections(and0, and1, and2, or0, not0, not1, in0, in1, out, carry):
    """
    Additional XOR gate connections
    """
    # TODO can this be merged with the first connection set
    return {
        and1.out0 == or0.in0,
        and2.out0 == or0.in1,
        in0.anchor == and0.in0,
        in1.anchor == and0.in1,
        and0.out0 == carry.anchor,
        or0.out0 == out.anchor,
        in0.anchor == not0.in0,
        in0.anchor == and2.in1,
        in1.anchor == not1.in0,
        in1.anchor == and1.in1,
    }


@diagram.add_pivots_from_def
def pivots(and1, and2, or0, not0, not1, in0, in1):
    """
    XOR gate pivots
    """
    ps = .4 * cm
    # TODO can factor out common pivot point logic
    return {
        (and1.out0, or0.in0):
        [and1.out0 + V(ps, 0), V(and1.out0.x + ps, or0.in0.y)],
        (and2.out0, or0.in1):
        [and2.out0 + V(ps, 0), V(and2.out0.x + ps, or0.in1.y)],
        (in0.anchor, not0.in0):
        [in0.anchor + V(ps, 0), V(in0.anchor.x + ps, not0.in0.y)],
        (in0.anchor, and2.in1): [
            in0.anchor + V(ps, 0), V(in0.anchor.x + ps, and2.in1.y)
        ],
        (in1.anchor, not1.in0): [
            in1.anchor + V(2 * ps, 0), V(in1.anchor.x + 2 * ps, not1.in0.y)
        ],
        (in1.anchor, and1.in1): [
            in1.anchor + V(2 * ps, 0), V(in1.anchor.x + 2 * ps, and1.in1.y)
        ],
    }
