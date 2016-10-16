"""
SVG implementation of the PlanarDrawer interface and supporting objects
"""
import json

import svgwrite

from pivot.interface.shortcuts import PV

from rasm.planar.drawers.base import PlanarDrawer


class SVGDrawer(PlanarDrawer):
    """
    A PlanarDrawer that outputs SVG
    """

    def __init__(self, path, separate_labels=True):
        """
        Initialize with a path to the output file
        """
        self.path = path
        self.dwg = svgwrite.Drawing("{}.svg".format(path), profile='tiny')
        self.separate_labels = separate_labels
        self._labels = []

    def draw_line(self, line):
        """
        Implement the PlanarDrawer draw_line method
        """
        self.dwg.add(
            self.dwg.line(
                line.start, line.finish, stroke=svgwrite.rgb(10, 10, 16, '%')))

    def draw_arc(self, arc):
        """
        Implement the PlanarDrawer draw_arc method
        """
        p = self.dwg.path(
            'm{},{}'.format(arc.start.x, arc.start.y),
            stroke=svgwrite.rgb(10, 10, 16, '%'),
            fill=svgwrite.rgb(100, 100, 100, '%'),
            fill_opacity="0.0")
        p.push_arc(
            target=arc.finish - arc.start,
            rotation=arc.rotation,
            large_arc=arc.large,
            r=arc.radius)
        self.dwg.add(p)

    def draw_text(self, text):
        """
        Implement the PlanarDrawer draw_text method
        """
        # HACK offset the text slightly to make consistent
        # with LaTeX driver
        anchor = text.anchor - PV(0, 11)
        if self.separate_labels:
            self._labels.append(
                dict(
                    text=text.text,
                    insert=list(anchor),
                    alignment=text.alignment))
        else:
            self.dwg.add(
                self.dwg.text(
                    text.text,
                    insert=anchor,
                    text_anchor=text.alignment, ))

    def draw_polygon(self, polygon):
        """
        Implement the PlanarDrawer draw_polygon method
        """
        self.dwg.add(
            self.dwg.polygon(
                polygon.points, stroke=svgwrite.rgb(10, 10, 16, '%')))

    def save(self):
        """
        Save the produced SVG file
        """
        self.dwg.save()
        if self.separate_labels:
            with open("{}.json".format(self.path), 'w') as f:
                json.dump(dict(labels=self._labels), f, indent=4)

    @staticmethod
    def post_run(artifact_names):
        """
        Aggregate figure metadata
        """
        figures = {}
        for name in artifact_names:
            with open("{}.json".format(name)) as f:
                figures[name] = json.load(f)
        with open("figures.json", 'w') as f:
            json.dump(dict(figures=figures), f, indent=4)
