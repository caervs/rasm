"""
The Latex two-dimensional drawer and supporting objects
"""

import subprocess

from pivot.interface.shortcuts import PV

from rasm.planar.drawers.base import PlanarDrawer

LATEX_TEMPLATE_START = r"""
\documentclass{article}
\usepackage{pstricks}
\pagenumbering{gobble}
\begin{document}
\begin{figure}
\begin{pspicture}(10,10)
"""

LATEX_TEMPLATE_END = r"""
\end{pspicture}
\end{figure}
\end{document}
"""


class LatexDrawer(PlanarDrawer):
    """
    A PlanarDrawer that outputs PStricks Latex
    """
    SCALE = 70

    def __init__(self, path):
        """
        Initialize with a path to the output file
        """
        self.path = path
        self.body = ""

    def _scale(self, point):
        return PV(point.x / self.SCALE, 10 - point.y / self.SCALE)

    def draw_line(self, line):
        """
        Implement the PlanarDrawer draw_line method
        """
        self.body += '\\psline[linewidth=.2pt]({},{})({},{})\n'.format(
            line.start.x / self.SCALE, 10 - line.start.y / self.SCALE,
            line.finish.x / self.SCALE, 10 - line.finish.y / self.SCALE)

    def draw_arc(self, arc):
        """
        Implement the PlanarDrawer draw_arc method
        """
        self.body += '\\psarc[linewidth=.2pt](%(x)s,%(y)s){%(r)s}{%(a)s}{%(b)s}\n' % dict(
            x=arc.centre_point.x / self.SCALE,
            y=10 - arc.centre_point.y / self.SCALE,
            r=arc.radius / self.SCALE,
            # TODO fix leaky abstraction
            a=-arc.anglea,
            b=-arc.angleb, )

    def draw_text(self, text):
        """
        Implement the PlanarDrawer draw_text method
        """
        if text.alignment == 'start':
            align = 'Bl'
        elif text.alignment == 'end':
            align = 'Br'
        else:
            align = 'B'

        # HACK pad the text slightly
        hpad = PV(0, 0)
        if text.alignment == 'start':
            hpad = PV(5, 0)
        elif text.alignment == 'end':
            hpad = PV(-5, 0)
        anchor = text.anchor + PV(0, 3.5) + hpad

        # TODO factor out scaling down by self.SCALE and translating
        self.body += '\\rput[%(align)s](%(x)s,%(y)s){\\tiny{%(text)s}}\n' % dict(
            align=align,
            x=anchor.x / self.SCALE,
            # HACK no way to vertically center text so offset baseline slightly
            y=10 - anchor.y / self.SCALE,
            text="${}$".format(text.text))

    def draw_polygon(self, polygon):
        """
        Implement the PlanarDrawer draw_polygon method
        """
        point_text = ''.join("({},{})".format(*self._scale(point))
                             for point in polygon.points)
        self.body += '\\pspolygon*{}'.format(point_text)

    def save(self):
        """
        Save the produced Latex file
        """
        latex = "{}.tex".format(self.path)
        with open(latex, 'w') as f:
            f.write(LATEX_TEMPLATE_START + self.body + LATEX_TEMPLATE_END)
        subprocess.check_call(["latex", latex])
        subprocess.check_call(["dvips", "{}.dvi".format(self.path)])
        subprocess.check_call(["ps2eps", "-f", "{}.ps".format(self.path)])
