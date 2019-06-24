#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NumEx: Numpy-ndarray Explorer.
"""

# Copyright (c) Riccardo Metere <rick@metere.it>

# ======================================================================
# :: Future Imports
from __future__ import (
    division, absolute_import, print_function, unicode_literals, )

# ======================================================================
# :: Python Standard Library Imports
import os  # Miscellaneous operating system interfaces

# ======================================================================
# :: External Imports
# import flyingcircus as fc  # Everything you always wanted to have in Python.*
from flyingcircus import msg, dbg, elapsed, report, pkg_paths
from flyingcircus import VERB_LVL, VERB_LVL_NAMES, D_VERB_LVL

# ======================================================================
# :: Version
from numex._version import __version__

# ======================================================================
# :: Project Details
INFO = {
    'name': 'NumEx',
    'author': 'NumEx developers',
    'contrib': (
        'Riccardo Metere <rick@metere.it>',
    ),
    'copyright': 'Copyright (C) 2017-2018',
    'license': 'GNU General Public License version 3 or later (GPLv3+)',
    'notice':
        """
This program is free software and it comes with ABSOLUTELY NO WARRANTY.
It is covered by the GNU General Public License version 3 (GPLv3+).
You are welcome to redistribute it under its terms and conditions.
        """,
    'version': __version__
}

# ======================================================================
# :: quick and dirty timing facility
_EVENTS = []

# ======================================================================
# Greetings
MY_GREETINGS = r"""
 _   _                 _____
| \ | |_   _ _ __ ___ | ____|_  __
|  \| | | | | '_ ` _ \|  _| \ \/ /
| |\  | |_| | | | | | | |___ >  <
|_| \_|\__,_|_| |_| |_|_____/_/\_\

"""
# generated with: figlet 'NumEx' -f standard

# :: Causes the greetings to be printed any time the library is loaded.
print(MY_GREETINGS)

# ======================================================================
PATH = pkg_paths(__file__, INFO['name'], INFO['author'], INFO['version'])

# ======================================================================
elapsed(os.path.basename(__file__))

# ======================================================================
if __name__ == '__main__':
    import doctest  # Test interactive Python examples

    msg(__doc__.strip())
    msg('Running `doctest.testmod()`... ', fmt='bold')
    results = doctest.testmod()  # RUN TESTS HERE!
    results_ok = results.attempted - results.failed
    results_fmt = '{t.bold}{t.red}' \
        if results.failed > 0 else '{t.bold}{t.green}'
    msg('Tests = {results.attempted}; '.format(**locals()),
        fmt='{t.bold}{t.cyan}', end='')
    msg('OK = {results_ok}; '.format(**locals()),
        fmt='{t.bold}{t.green}', end='')
    msg('Fail = {results.failed}'.format(**locals()), fmt=results_fmt)
    msg(report())
