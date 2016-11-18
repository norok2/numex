NumEx: a quick-and-easy explorer for numerical data
===================================================

This Python library implements intend to implement automatic generation of
User-Interfaces from function/class signatures.

The pseudo-widget semantic follows HTML5 conventions.

There are plans to includes support for:

- Graphical User-Interfaces (through Tk)
- Command-Line Interfaces (with coloring support via ``blessings``/``blessed``)
- Text User-Interfaces (through ``asciimatics``)
- Web Forms (with Flask)


Installation
------------
The recommended way of installing the software is through
`PyPI <https://pypi.python.org/pypi/autoui>`_:

.. code:: shell

    $ pip install autoui

Alternatively, you can clone the source repository from
`Bitbucket <https://bitbucket.org/norok2/autoui>`_:

.. code:: shell

    $ mkdir autoui
    $ cd autoui
    $ git clone git@bitbucket.org:norok2/autoui.git
    $ python setup.py install

(some steps may require additional permissions depending on your configuration)

The software does not have additional dependencies beyond Python and its
standard library.

It was tested with Python 2.7 and 3.5.
Other version were not tested.
