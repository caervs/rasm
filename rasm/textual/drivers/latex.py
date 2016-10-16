"""
The Latex article writer and supporting objects
"""

import subprocess

LATEX_TEMPLATE_START = r"""
\documentclass{article}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{pstricks}
\begin{document}
"""

LATEX_TEMPLATE_END = r"""
\end{document}
"""

LATEX_FIGURE_TEMPLATE = r"""\begin{figure}[h!]
\centering
\includegraphics[scale=2]{{name}.eps}
\end{figure}
"""


class Driver(object):
    def __init__(self, path):
        """
        Initialize with a path to the output file
        """
        self.path = path
        self.body = ""

    def _format_text(self, text):
        # TODO handle all LaTeX espace characters
        return text.replace("&", "\\&").replace("#", "\\#")

    def write_header(self, header):
        level = header.level
        if level > 3:
            level = 3
        command = "\\{}section*".format("sub" * (level - 1))
        self.body += "{}{{{}}}\n".format(command,
                                         self._format_text(header.text))

    def write_text_line(self, line):
        self.body += self._format_text(line.text) + "\n"

    def add_figure(self, figure):
        self.body += LATEX_FIGURE_TEMPLATE.replace("{name}", figure.name)

    def write_list_block(self, lst):
        lines = [r"\begin{itemize}"] + ["\item {}\n".format(item) for item in lst.items] + \
                [r"\end{itemize}", ""]
        self.body += "\n".join(lines)

    def save(self):
        """
        Save the produced Latex file
        """
        latex = "{}.tex".format(self.path)
        with open(latex, 'w') as f:
            f.write(LATEX_TEMPLATE_START + self.body + LATEX_TEMPLATE_END)
        subprocess.check_call(["pdflatex", latex])
