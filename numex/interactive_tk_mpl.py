#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NumEx: Interactive GUI generator using Tk/Matplotlib.

Generate interactive plots from a minimal set of specification.
Uses Tk (Python's default) and MatPlotLib.
In particular, two objects need to be defined:
- a plotting function, which must accept:
    - a `matplotlib.Axes` where the plot is shown (this is used internally)
    - the dictionary of parameters for which interactivity is desired
- an ordered dictionary with interactivity information, where the key
  correspond to the internal name of the parameter (useful for kwargs magic),
  and the value is a dictionary with the following required fields:
    - 'label': the printing name of the variable (will show in GUI)
    - 'default': the default value
    - 'start': the minimum value of the parameter
    - 'stop': the maximum value of the parameter
    - 'step': the step size for the variation

Examples:
    >>> import numpy as np
    >>> interactives = collections.OrderedDict([
    ...     ('a', dict(
    ...         label='a (arb. units)',
    ...         default=10, start=-100, stop=100, step=0.01)), ])
    >>> def plot_func(
    ...         fig,
    ...         params=None,
    ...         title='Test'):
    ...     ax = fig.add_subplot(111)
    ...     x = np.linspace(-100, 100, 128)
    ...     try:
    ...         y = np.sin(x / params['a'])
    ...         ax.plot(x, y, label=r'$\sin(x / a)$')
    ...     except Exception as e:
    ...         print(e)
    ...         ax.set_title('\\n'.join(('WARNING! Some plot failed!', title)))
    ...     else:
    ...         ax.set_title(title)
    ...     finally:
    ...         ax.set_xlabel(r'x (arb. units)')
    ...         ax.set_ylabel(r'y (arb. units)')
    ...         ax.legend()
    ...     return ax
    >>> plotting(plot_func, interactives, title='Test')
    <tkinter.Tk object .>
"""

# ======================================================================
# :: Future Imports
from __future__ import (
    division, absolute_import, print_function, unicode_literals, )

# ======================================================================
# :: Python Standard Library Imports
import os  # Miscellaneous operating system interfaces
import collections  # Container datatypes
import datetime  # Basic date and time types
import doctest  # Test interactive Python examples
import json  # JSON encoder and decoder [JSON: JavaScript Object Notation]

# :: External Imports
import matplotlib as mpl  # Matplotlib (2D/3D plotting library)
import pytk
import pytk.util
import pytk.widgets

import matplotlib.backends.backend_tkagg as tkagg

# :: Local Imports
import numex as nme

from numex import INFO, PATH, MY_GREETINGS
# from numex import VERB_LVL, D_VERB_LVL, VERB_LVL_NAMES
from numex import elapsed, report
from numex import msg, dbg, fmt, fmtm

# ======================================================================
_MIN_WIDTH = 320
_MIN_HEIGHT = 200
_WIDTH = 960
_HEIGHT = 600


# ======================================================================
class PytkAbout(pytk.Window):
    def __init__(self, parent, about=__doc__):
        self.win = super(PytkAbout, self).__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.title('About {}'.format(INFO['name']))
        self.resizable(False, False)
        self.frm = pytk.widgets.Frame(self)
        self.frm.pack(fill='both', expand=True)
        self.frmMain = pytk.widgets.Frame(self.frm)
        self.frmMain.pack(fill='both', padx=1, pady=1, expand=True)

        about_txt = '\n'.join((
            MY_GREETINGS[1:],
            nme.__doc__,
            about,
            '{} - ver. {}\n{} {}\n{}'.format(
                INFO['name'], INFO['version'],
                INFO['copyright'], INFO['author'], INFO['notice'])
        ))
        msg(about_txt)
        self.lblInfo = pytk.widgets.Label(
            self.frmMain, text=about_txt, anchor='center',
            background='#333', foreground='#ccc', font='TkFixedFont')
        self.lblInfo.pack(padx=8, pady=8, ipadx=8, ipady=8)

        self.btnClose = pytk.widgets.Button(
            self.frmMain, text='Close', command=self.destroy)
        self.btnClose.pack(side='bottom', padx=8, pady=8)
        self.bind('<Return>', self.destroy)
        self.bind('<Escape>', self.destroy)

        pytk.util.center(self, self.parent)

        self.grab_set()
        self.wait_window(self)


# ======================================================================
class PytkMain(pytk.widgets.Frame):
    def __init__(
            self, parent, func, interactives,
            title=__doc__.strip().split('\n')[0],
            about=__doc__,
            width=_WIDTH, height=_HEIGHT,
            min_width=_MIN_WIDTH, min_height=_MIN_HEIGHT,
            **func_kwargs):
        self.func = func
        self.func_kwargs = func_kwargs
        self.interactives = interactives
        self.about = about
        self.cwd = '.'

        # :: initialization of the UI
        self.win = super(PytkMain, self).__init__(
            parent, width=width, height=height)
        self.parent = parent
        self.parent.title(title)
        self.parent.protocol('WM_DELETE_WINDOW', self.actionExit)
        self.parent.minsize(min_width, min_height)

        self.style = pytk.Style()
        # print(self.style.theme_names())
        self.style.theme_use('clam')
        self.pack(fill='both', expand=True)
        pytk.util.center(self.parent)

        self._make_menu()

        # :: define UI items
        # : main
        self.frmMain = pytk.widgets.Frame(self)
        self.frmMain.pack(fill='both', padx=4, pady=4, expand=True)
        self.frmSpacers = []

        # : left frame
        self.frmLeft = pytk.widgets.Frame(self.frmMain)
        self.frmLeft.pack(
            side='left', fill='both', padx=4, pady=4, expand=True)

        self.fig = mpl.figure.Figure(figsize=(0.1, 0.1))
        self.canvas = tkagg.FigureCanvasTkAgg(
            self.fig, self.frmLeft)
        self.nav_toolbar = tkagg.NavigationToolbar2Tk(
            self.canvas, self.frmLeft)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # : right frame
        self.frmRight = pytk.widgets.ScrollingFrame(
            self.frmMain,
            label_kws=dict(text='Parameters'),
            label_pack_kws=dict(
                side='top', padx=0, pady=0, expand=False, anchor='n'))
        self.frmRight.pack(
            side='right', fill='both', padx=4, pady=4, expand=False)

        self.frmParams = self.frmRight.scrolling
        spacer = pytk.widgets.Frame(self.frmParams)
        spacer.pack(side='top', padx=4, pady=4)
        self.frmSpacers.append(spacer)
        self.wdgInteractives = collections.OrderedDict()
        for name, info in self.interactives.items():
            if isinstance(info['default'], bool):
                var = pytk.tk.BooleanVar()
                chk = pytk.widgets.Checkbox(
                    self.frmParams, text=info['label'], variable=var)
                chk.pack(fill='x', padx=1, pady=1)
                self.wdgInteractives[name] = dict(var=var, chk=chk)
            elif isinstance(info['default'], (int, float)):
                var = pytk.tk.StringVar()
                var.set(str(info['default']))
                frm = pytk.widgets.Frame(self.frmParams)
                frm.pack(fill='x', padx=1, pady=1, expand=True)
                lbl = pytk.widgets.Label(frm, text=info['label'])
                lbl.pack(side='left', fill='x', padx=1, pady=1, expand=False)
                rng = pytk.widgets.Range(
                    frm,
                    start=info['start'], stop=info['stop'], step=info['step'],
                    orient='horizontal', variable=var)
                rng.pack(
                    side='right', fill='x', anchor='w', padx=1, pady=1,
                    expand=False)
                spb = pytk.widgets.Spinbox(
                    frm,
                    start=info['start'], stop=info['stop'], step=info['step'],
                    textvariable=var)
                spb.pack(
                    side='right', fill='none', anchor='w', padx=1, pady=1,
                    expand=False)
                self.wdgInteractives[name] = dict(
                    var=var, frm=frm, lbl=lbl, spb=spb, rng=rng)
            elif isinstance(info['default'], str):
                var = pytk.tk.StringVar()
                var.set(str(info['default']))
                frm = pytk.widgets.Frame(self.frmParams)
                frm.pack(fill='x', padx=1, pady=1, expand=True)
                lbl = pytk.widgets.Label(frm, text=info['label'])
                lbl.pack(side='left', fill='x', padx=1, pady=1, expand=False)
                cmb = pytk.widgets.Combobox(
                    frm,
                    values=info['values'], textvariable=var)
                cmb.pack(
                    side='right', fill='x', anchor='w', padx=1, pady=1,
                    expand=False)
                self.wdgInteractives[name] = dict(
                    var=var, frm=frm, lbl=lbl, cmb=cmb)
        self._bind_interactions()
        self.actionReset()

    def _make_menu(self):
        self.mnuMain = pytk.widgets.Menu(self.parent, tearoff=False)
        self.parent.config(menu=self.mnuMain)
        self.mnuPlot = pytk.widgets.Menu(self.mnuMain, tearoff=False)
        self.mnuMain.add_cascade(label='Menu', menu=self.mnuPlot)
        self.mnuPlot.add_command(label='Exit', command=self.actionExit)
        self.mnuParams = pytk.widgets.Menu(self.mnuMain, tearoff=False)
        self.mnuMain.add_cascade(label='Parameters', menu=self.mnuParams)
        self.mnuParams.add_command(label='Reset', command=self.actionReset)
        self.mnuParams.add_separator()
        self.mnuParams.add_command(label='Import', command=self.actionImport)
        self.mnuParams.add_command(label='Export', command=self.actionExport)
        self.mnuHelp = pytk.widgets.Menu(self.mnuMain, tearoff=False)
        self.mnuMain.add_cascade(label='Help', menu=self.mnuHelp)
        self.mnuHelp.add_command(label='About', command=self.actionAbout)

    def _bind_interactions(self):
        for k, v in self.wdgInteractives.items():
            v['trace'] = v['var'].trace('w', self.actionPlotUpdate)

    def _unbind_interactions(self):
        for k, v in self.wdgInteractives.items():
            v['var'].trace_vdelete('w', v['trace'])

    def actionPlotUpdate(self, *_args):
        """Update the plot."""
        self.fig.clear()
        if hasattr(self, 'wdgInteractives'):
            params = {}
            for k, v in self.wdgInteractives.items():
                val = v['var'].get()
                my_type = type(self.interactives[k]['default'])
                try:
                    val = my_type(val)
                except ValueError:
                    val = self.interactives[k]['default']
                params[k] = val
        else:
            params = {k: v['default'] for k, v in self.interactives.items()}
        self.func(fig=self.fig, params=params, **self.func_kwargs)
        self.canvas.draw()

    def actionExit(self, event=None):
        """Action on Exit."""
        if pytk.messagebox.askokcancel(
                'Quit', 'Are you sure you want to quit?'):
            self.parent.destroy()

    def actionAbout(self, event=None):
        """Action on About."""
        self.winAbout = PytkAbout(self.parent, self.about)

    def actionReset(self, event=None):
        """Action on Reset."""
        self._unbind_interactions()
        for name, info in self.interactives.items():
            self.wdgInteractives[name]['var'].set(info['default'])
        self._bind_interactions()
        self.actionPlotUpdate()

    def actionImport(self, event=None):
        """Action on Import."""
        self._unbind_interactions()
        filepath = pytk.filedialog.askopenfilename(
            parent=self, title='Import Parameters', defaultextension='.json',
            initialdir=self.cwd, filetypes=[('JSON Files', '*.json')])
        if filepath:
            self.cwd = os.path.dirname(filepath)
            try:
                with open(filepath, 'r') as file_obj:
                    data = json.load(file_obj)
                for k, v in data.items():
                    try:
                        self.wdgInteractives[k]['var'].set(v)
                    except KeyError:
                        pass
            except (AttributeError, json.JSONDecodeError):
                pytk.messagebox.showwarning(
                    'Warning', 'Could not import data from file!')
        self._bind_interactions()
        self.actionPlotUpdate()

    def actionExport(self, event=None):
        """Action on Export."""
        self._unbind_interactions()
        filepath = pytk.filedialog.asksaveasfilename(
            parent=self, title='Import Parameters', defaultextension='.json',
            initialdir=self.cwd, filetypes=[('JSON Files', '*.json')],
            confirmoverwrite=True)
        if filepath:
            self.cwd = os.path.dirname(filepath)
            data = {k: v['var'].get() for k, v in self.wdgInteractives.items()}
            with open(filepath, 'w') as file_obj:
                json.dump(data, file_obj, sort_keys=True, indent=4)
        self._bind_interactions()
        self.actionPlotUpdate()


# ======================================================================
def plotting(
        func,
        interactives,
        gui_main=PytkMain,
        resources_path=None,
        *_args,
        **_kws):
    root = pytk.tk.Tk()
    app = gui_main(root, func, interactives, *_args, **_kws)
    if resources_path is None:
        resources_path = PATH['resources']
    pytk.util.set_icon(root, 'icon', resources_path)
    root.mainloop()
    return root


# ======================================================================
elapsed(__file__[len(PATH['base']) + 1:])

# ======================================================================
if __name__ == '__main__':
    import doctest  # Test interactive Python examples

    msg(__doc__.strip())
    doctest.testmod()
    msg(report())
