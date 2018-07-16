#!python
# -*- coding: utf-8 -*-
"""
NumEx: Tk/Matplotlib Graphical User Interface (GUI).
"""

# ======================================================================
# :: Future Imports
from __future__ import (
    division, absolute_import, print_function, unicode_literals, )

# ======================================================================
# :: Python Standard Library Imports
import os  # Miscellaneous operating system interfaces
import argparse  # Argument Parsing
import collections  # Container datatypes
import datetime  # Basic date and time types
import traceback  # Print or retrieve a stack traceback
import textwrap  # Text wrapping and filling

# :: External Imports
import numpy as np  # NumPy (multidimensional numerical arrays library)
import scipy as sp  # SciPy (signal and image processing library)
import matplotlib.cm, matplotlib.lines, matplotlib.markers, matplotlib.colors
from mpl_toolkits.axes_grid1 import make_axes_locatable

# :: Local Imports
import numex as nme
import numex.interactive_tk_mpl
import numex.plugins.synthetic

from numex import INFO, DIRS
from numex import VERB_LVL, D_VERB_LVL
from numex import msg, dbg
from numex import elapsed, report

TITLE = __doc__.strip().split('\n')[0][:-1]

COLORMAPS = sorted(str(v) for v in matplotlib.cm.datad)
COLORS = sorted(str(k) for k, v in matplotlib.colors.cnames.items())
LINESTYLES = sorted(
    str(k) for k, v in matplotlib.lines.lineStyles.items() if str(k).strip())
LINEMARKERS = sorted(
    str(k) for k, v in matplotlib.lines.lineMarkers.items()
    if str(k).strip() and k not in range(5, 12) and k != 0)
INTERACTIVE_BASE = collections.OrderedDict([
    ('cx_mode', dict(
        label='Complex Mode', default='real-imag',
        values=('real-imag', 'mag-phase'))),
    ('cx_display_mode', dict(
        label='Complex Display Mode', default='auto',
        values=('auto', 'horizontal', 'vertical'))),
])


# ======================================================================
def selector(arr, mode=None):
    modes = {
        '1d': '1D',
        '2d_plot_xy': '2D Plot(x,y)',
        '2d_map': '2D Map',
        '2d_map_profile': '2D Map with Profile'}
    if mode is None:
        if len(arr.shape) == 1:
            mode = '1d'
        elif len(arr.shape) >= 2 and any(dim == 2 for dim in arr.shape):
            mode = '2d_plot_xy'
        else:
            mode = '2d_map'
    if mode in modes:
        interactives = INTERACTIVE_BASE
        plotting_func = eval('plot_ndarray_' + mode)
        interactives.update(eval('gen_interactives_' + mode + '(arr)'))
        title = modes[mode]
    else:
        plotting_func, interactives, title = selector(arr, None)
    return plotting_func, interactives, title


# ======================================================================
def gen_interactives_1d(arr):
    interactives = collections.OrderedDict(
        [('axis', dict(
            label='Axis', default=0,
            start=0, stop=len(arr.shape) - 1, step=1))]
        +
        [('index-{}'.format(i), dict(
            label='Index[{:0{n_digits}d}]'.format(i, n_digits=1), default=0,
            start=0, stop=d - 1, step=1)) for i, d in enumerate(arr.shape)]
        +
        [('line-color', dict(
            label='Line Color', default='black', values=COLORS)),
         # ('rgb-color', dict(label='Line Color', default='blue', values='')),
         ('line-width', dict(
             label='Line Width', default=1., start=0., stop=9.5, step=0.5)),
         ('line-style', dict(
             label='Line Style', default='-', values=LINESTYLES)),
         ('line-marker', dict(
             label='Line Marker', default='.', values=LINEMARKERS)),
         ('marker-size', dict(
             label='Marker Size', default=5., start=0., stop=49.5, step=1.)),
         ]
    )
    return interactives


# ======================================================================
def gen_interactives_2d_plot_xy(arr):
    n_digits = int(np.ceil(np.log10(len(arr.shape))))
    interactives = collections.OrderedDict(
        [('axis', dict(
            label='Axis', default=0,
            start=0, stop=len(arr.shape) - 1, step=1))]
        +
        [('{}-index-{}'.format(x, i), dict(
            label='{} Index[{:0{n_digits}d}]'.format(x, i, n_digits=n_digits),
            default=0 if x is 'x' else 1, start=0, stop=d - 1, step=1))
         for i, d in enumerate(arr.shape) for x in ('x', 'y')]
        +
        [('line-color', dict(
            label='Line Color', default='black', values=COLORS)),
         # ('rgb-color', dict(label='Line Color', default='blue', values='')),
         ('line-width', dict(
             label='Line Width', default=1., start=0., stop=9.5, step=0.5)),
         ('line-style', dict(
             label='Line Style', default='-', values=LINESTYLES)),
         ('line-marker', dict(
             label='Line Marker', default='.', values=LINEMARKERS)),
         ('marker-size', dict(
             label='Marker Size', default=5., start=0., stop=49.5, step=1.)),
         ]
    )
    return interactives


# ======================================================================
def gen_interactives_2d_map(arr):
    n_digits = int(np.ceil(np.log10(len(arr.shape))))
    interactives = collections.OrderedDict(
        [('axis-{}'.format(i), dict(
            label='{} axis'.format('x' if i == 0 else 'y'), default=i,
            start=0, stop=len(arr.shape) - 1, step=1)) for i in range(2)]
        +
        [('index-{}'.format(i), dict(
            label='Index[{:0{n_digits}d}]'.format(i, n_digits=n_digits),
            default=0, start=0, stop=d - 1, step=1))
         for i, d in enumerate(arr.shape)]
        +
        [('cmap-{}'.format(i), dict(
            label='Color Map {}'.format(x.upper()),
            default='gray', values=COLORMAPS))
         for i, x in enumerate(('a', 'b'))]
    )
    return interactives


# ======================================================================
def plot_ndarray_1d(
        fig,
        arr=None,
        params=None,
        plt_title='',
        plt_interactives=None):

    try:
        mask = [v for k, v in params.items() if k.startswith('index-')]
        mask[params['axis']] = slice(None)
        y_arr = arr[mask]
        x_arr = np.arange(len(y_arr))
        if not np.iscomplexobj(y_arr):
            ax = fig.gca()
            ax.plot(
                x_arr, y_arr,
                color=params['line-color'], linewidth=params['line-width'],
                linestyle=params['line-style'], marker=params['line-marker'],
                markersize=params['marker-size'])
            ax.set_xlabel('Index of Axis {}'.format(params['axis']))
            ax.set_ylabel('Values / arb.units')
        else:
            if params['cx_display_mode'] == 'horizontal':
                rows_cols = (1, 2)
            else:  # if params['cx_display_mode'] in ('vertical', 'auto'):
                rows_cols = (2, 1)
            y_arrs = (y_arr.real, y_arr.imag)
            titles = ('Real Part', 'Imaginary Part')
            # data_lim = (
            #     min([np.min(x) for x in y_arrs]),
            #     max([np.max(x) for x in y_arrs]))
            share_y = True
            data_lims = (None, None)
            if params['cx_mode'] == 'mag-phase':
                y_arrs = (np.abs(y_arr), np.arctan2(y_arr.real, y_arr.imag))
                titles = ('Magnitude', 'Phase')
                data_lims = (None, (-np.pi * 1.1, np.pi * 1.1))
                share_y = False
            axs = fig.subplots(
                nrows=rows_cols[0], ncols=rows_cols[1], sharey=share_y)

            for i, infos in enumerate(zip(axs, y_arrs, titles, data_lims)):
                ax, y_arr_, title, data_lim = infos
                ax.plot(
                    x_arr, y_arr_,
                    color=params['line-color'],
                    linewidth=params['line-width'],
                    linestyle=params['line-style'],
                    marker=params['line-marker'],
                    markersize=params['marker-size'])
                if data_lim:
                    ax.set_ylim(data_lim)
                ax.set_xlabel('Index of Axis {}'.format(params['axis']))
                ax.set_ylabel('Values / arb.units')
    except Exception as e:
        fig.clf()
        ax = fig.subplots(1)
        ax.axis('off')
        ax.set_aspect(1)
        text = traceback.format_exc(50)
        # text = '\n'.join(textwrap.wrap(str(e), 50))
        ax.text(-0.15, 0.95, text, ha='left', va='top', family='monospace')
        ax.set_title('WARNING: Plotting failed!', color='#999933')
    else:
        pass
    finally:
        # fig.tight_layout()
        fig.suptitle(plt_title)


# ======================================================================
def plot_ndarray_2d_plot_xy(
        fig,
        arr=None,
        params=None,
        plt_title='',
        plt_interactives=None):
    try:
        x_mask = [v for k, v in params.items() if k.startswith('x-index-')]
        x_mask[params['axis']] = slice(None)
        y_mask = [v for k, v in params.items() if k.startswith('y-index-')]
        y_mask[params['axis']] = slice(None)
        y_arr = arr[x_mask]
        x_arr = arr[y_mask]
        if not np.iscomplexobj(x_arr) and not np.iscomplexobj(y_arr):
            ax = fig.gca()
            ax.plot(
                x_arr, y_arr,
                color=params['line-color'], linewidth=params['line-width'],
                linestyle=params['line-style'], marker=params['line-marker'],
                markersize=params['marker-size'])
            ax.set_xlabel('Values @ {} / arb.units'.format(
                [x if isinstance(x, int) else np.nan for x in x_mask]))
            ax.set_ylabel('Values @ {} / arb.units'.format(
                [x if isinstance(x, int) else np.nan for x in y_mask]))
        else:
            if params['cx_display_mode'] == 'horizontal':
                rows_cols = (1, 2)
            else:  # if params['cx_display_mode'] in ('vertical', 'auto'):
                rows_cols = (2, 1)
            xy_arrs = ((x_arr.real, y_arr.real), (x_arr.imag, y_arr.imag))
            titles = ('Real Part', 'Imaginary Part')
            # data_lim = (
            #     min([np.min(x) for x in y_arrs]),
            #     max([np.max(x) for x in y_arrs]))
            share_xy = True
            data_lims = (None, None)
            if params['cx_mode'] == 'mag-phase':
                xy_arrs = (
                    (np.abs(x_arr), np.abs(y_arr)),
                    (np.arctan2(x_arr.real, x_arr.imag),
                     np.arctan2(y_arr.real, y_arr.imag)))
                titles = ('Magnitude', 'Phase')
                data_lims = (None, (-np.pi * 1.1, np.pi * 1.1))
                share_xy = False
            axs = fig.subplots(
                nrows=rows_cols[0], ncols=rows_cols[1],
                sharex=share_xy, sharey=share_xy)

            for i, infos in enumerate(zip(axs, xy_arrs, titles, data_lims)):
                ax, (x_arr_, y_arr_), title, data_lim = infos
                ax.plot(
                    x_arr_, y_arr_,
                    color=params['line-color'], linewidth=params['line-width'],
                    linestyle=params['line-style'], marker=params['line-marker'],
                    markersize=params['marker-size'])
                ax.set_xlabel('Values @ {} / arb.units'.format(
                    [x if isinstance(x, int) else np.nan for x in x_mask]))
                ax.set_ylabel('Values @ {} / arb.units'.format(
                    [x if isinstance(x, int) else np.nan for x in y_mask]))
                if data_lim:
                    ax.set_xlim(data_lim)
                    ax.set_ylim(data_lim)
    except Exception as e:
        fig.clf()
        ax = fig.subplots(1)
        ax.axis('off')
        ax.set_aspect(1)
        # text = traceback.format_exc(50)
        text = '\n'.join(textwrap.wrap(str(e), 50))
        ax.text(-0.15, 0.95, text, ha='left', va='top', family='monospace')
        ax.set_title('WARNING: Plotting failed!', color='#999933')
    else:
        pass
    finally:
        # fig.tight_layout()
        fig.suptitle(plt_title)


# ======================================================================
def plot_ndarray_2d_map(
        fig,
        arr=None,
        params=None,
        plt_title='',
        plt_interactives=None):
    try:
        mask = [v for k, v in params.items() if k.startswith('index-')]
        mask[params['axis-0']] = slice(None)
        mask[params['axis-1']] = slice(None)
        if params['axis-0'] == params['axis-1']:
            text = '`{}` and `{}` must be different!'.format(
                plt_interactives['axis-0']['label'],
                plt_interactives['axis-1']['label'])
            raise ValueError(text)
        img = arr[mask]
        if params['axis-1'] > params['axis-0']:
            img = img.T

        if not np.iscomplexobj(img):
            ax = fig.gca()
            pax = ax.imshow(img, cmap=params['cmap-0'], origin='bottom')
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            cbar = ax.figure.colorbar(pax, cax=cax)
            cbar.ax.get_yaxis().labelpad = 15
            cbar.ax.set_ylabel('Values / arb.units', rotation=-90)
            ax.set_xlabel('Index of Axis {}'.format(params['axis-0']))
            ax.set_ylabel('Index of Axis {}'.format(params['axis-1']))
            # ax.set_title()
        else:
            if params['cx_display_mode'] == 'horizontal':
                rows_cols = (1, 2)
            elif params['cx_display_mode'] == 'vertical':
                rows_cols = (2, 1)
            else:  # if params['cx_display_mode'] == 'auto':
                rows_cols = (2, 1) if img.shape[0] < img.shape[1] else (1, 2)
            axs = fig.subplots(nrows=rows_cols[0], ncols=rows_cols[1])
            imgs = (img.real, img.imag)
            titles = ('Real Part', 'Imaginary Part')
            data_lim = (
                min([np.min(x) for x in imgs]), max([np.max(x) for x in imgs]))
            data_lims = (data_lim, data_lim)
            if params['cx_mode'] == 'mag-phase':
                imgs = (np.abs(img), np.arctan2(img.real, img.imag))
                titles = ('Magnitude', 'Phase')
                data_lims = ((0, np.max(imgs[0])), (-np.pi, np.pi))

            for i, infos in enumerate(zip(axs, imgs, titles, data_lims)):
                ax, img_, title, data_lim = infos
                pax = ax.imshow(
                    img_, vmin=data_lim[0], vmax=data_lim[1],
                    cmap=params['cmap-{}'.format(i)], origin='bottom')
                divider = make_axes_locatable(ax)
                cax = divider.append_axes('right', size='5%', pad=0.05)
                cbar = ax.figure.colorbar(pax, cax=cax)
                cbar.ax.get_yaxis().labelpad = 12
                cbar.ax.set_ylabel('Values / arb.units', rotation=-90)
                ax.set_xlabel('Index of Axis {}'.format(params['axis-0']))
                ax.set_ylabel('Index of Axis {}'.format(params['axis-1']))
                ax.set_title(title)
    except Exception as e:
        fig.clf()
        ax = fig.subplots(1)
        ax.axis('off')
        ax.set_aspect(1)
        # text = traceback.format_exc(50)
        text = '\n'.join(textwrap.wrap(str(e), 50))
        ax.text(-0.15, 0.95, text, ha='left', va='top', family='monospace')
        ax.set_title('WARNING: Plotting failed!', color='#999933')
    else:
        pass
    finally:
        # fig.tight_layout()
        fig.suptitle(plt_title)


# ======================================================================
def explore(arr, mode=None):
    plotting_func, interactives, title = selector(arr, mode)
    nme.interactive_tk_mpl.plotting(
        plotting_func, interactives=interactives,
        title=TITLE, about=__doc__, arr=arr,
        plt_title=title, plt_interactives=interactives)


# ======================================================================
def handle_arg():
    """
    Handle command-line application arguments.
    """
    # :: Create Argument Parser
    arg_parser = argparse.ArgumentParser(
        description=__doc__,
        epilog='v.{} - {}\n{}'.format(
            INFO['version'], INFO['author'], INFO['license']),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # :: Add POSIX standard arguments
    arg_parser.add_argument(
        '--ver', '--version',
        version='%(prog)s - ver. {}\n{}\n{} {}\n{}'.format(
            INFO['version'],
            next(line for line in __doc__.splitlines() if line),
            INFO['copyright'], INFO['author'], INFO['notice']),
        action='version')
    arg_parser.add_argument(
        '-v', '--verbose',
        action='count', default=D_VERB_LVL,
        help='increase the level of verbosity [%(default)s]')
    arg_parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='override verbosity settings to suppress output [%(default)s]')
    # :: Add additional arguments
    arg_parser.add_argument(
        '-i', '--in_filepath', metavar='FILEPATH',
        help='Input filepath [%(default)s]')
    return arg_parser


# ======================================================================
def main():
    # :: handle program parameters
    arg_parser = handle_arg()
    args = arg_parser.parse_args()
    # fix verbosity in case of 'quiet'
    if args.quiet:
        args.verbose = VERB_LVL['none']
    # :: print debug info
    if args.verbose >= VERB_LVL['debug']:
        arg_parser.print_help()
        msg('\nARGS: ' + str(vars(args)), args.verbose, VERB_LVL['debug'])

    arr = nme.plugins.synthetic.gen_random((128, 128, 64, 32), dtype=complex)
    explore(arr, '2d_plot_xy')

    elapsed(__file__[len(DIRS['base']) + 1:])
    msg(report())


# ======================================================================
if __name__ == '__main__':
    main()
