"""
pysh commands for building and testing rasm
"""

import os

from pysh.examples.development import test as test_local
from pysh.interface.command import pyshcommand
from pysh.interface.shell import Shell

SH = Shell(search_path='')


@pyshcommand
def build():
    """
    Build the rasm docker image
    """
    return SH.docker('build', '-t', 'rabrams/rasm', '.')


@pyshcommand
def test():
    """
    Test the rasm package in a docker container
    """
    return SH.docker('run', '--rm', '-it', '--entrypoint=pysh', '-v',
                     '{}:/workdir/rasm/'.format(os.getcwd()),
                     '-e', 'PYSH_PYLINT_RC=.pysh/pylint.rc',
                     '--workdir=/workdir/rasm',
                     'rabrams/rasm', 'test_local')
