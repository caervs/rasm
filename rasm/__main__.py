"""
Entrypoint for running rasm at the command-line
"""
import json
import os

from rasm.planar.arranger import Arranger
from rasm.planar.drawers.latex import LatexDrawer
from rasm.planar.drawers.svg import SVGDrawer
from rasm.textual.drivers import latex
from rasm.textual.drivers import html
from rasm.textual.parsers import org
from rasm.textual.primitives import article


def gen_graphics(drivers, sources):
    artifact_names = list(sources)

    for driver in drivers:
        if hasattr(driver, 'pre_run'):
            driver.pre_run(artifact_names)

    for artifact_name, source_name in sources.items():
        mod_globals = {}
        with open(source_name) as f:
            code = compile(f.read(), source_name, 'exec')
            exec (code, mod_globals)
            driver_objs = [driver(artifact_name) for driver in drivers]
            diagram = mod_globals['diagram']
            arranger = Arranger(driver_objs, diagram.directed)
            arranger.draw(diagram)

    for driver in drivers:
        if hasattr(driver, 'post_run'):
            driver.post_run(artifact_names)


def main():
    """
    Command-line interface for rasm
    """
    outdir = "artifacts"
    sources = {
        "test": "rasm/planar/examples/xor_gate.py",
        "test2": "rasm/planar/examples/state_transition.py",
    }

    drivers = [LatexDrawer, SVGDrawer]
    run(drivers, sources, outdir)


def main2():
    outdir = "artifacts"
    source = "rasm.org"
    parser = org.Parser()
    with open(source) as f:
        contents = list(parser.parse(f.read()))
    drivers = [html.Driver("rasm"), latex.Driver("rasm")]
    drawers = [LatexDrawer, SVGDrawer]
    sources = {}
    for i, obj in enumerate(contents):
        if isinstance(obj, article.CodeBlock) and \
           obj.contents[0].startswith("#+BEGIN_SRC python rasm planar "):
            args = obj.contents[0][len("#+BEGIN_SRC python rasm planar "):]
            name, source = args.split(" ")
            sources[name] = os.path.abspath(source)
            contents[i] = article.Figure(name)

    if not os.path.exists(outdir):
        os.mkdir(outdir)
    if not os.path.isdir(outdir):
        raise Exception(
            "Cannot use: {} as output dir. It is a file".format(outdir))
    os.chdir(outdir)
    gen_graphics(drawers, sources)

    for obj in contents:
        if isinstance(obj, article.Header):
            for driver in drivers:
                driver.write_header(obj)
        elif isinstance(obj, article.TextLine):
            for driver in drivers:
                driver.write_text_line(obj)
        elif isinstance(obj, article.ListBlock):
            for driver in drivers:
                driver.write_list_block(obj)
        elif isinstance(obj, article.Figure):
            for driver in drivers:
                driver.add_figure(obj)
    for driver in drivers:
        driver.save()


if __name__ == "__main__":
    # main()
    main2()
