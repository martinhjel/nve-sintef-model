#coding=cp1252

import numpy as np
import matplotlib.pyplot as plt

def makeplot(figsize=[9,6], ncols=1,nrows=1, sharex=False, sharey=False):
    """
    Initializes matplotlib plot with a chosen design.
    
    Convenience function so that you don't have to set lots of parameters every
    time you make a chart for it to look nice.
    
    
    Parameters
    -----------
    figsize : list of two ints, optional
        Figure width and height in inches
    ncols : int, optional
        Number of columns
    nrows : int, optional
        Number of rows
    sharex : boolean, optional
        True if all charts should share x-axis
        
    sharey : bool, optional
        True if all charts should share y-axis
        
    Returns
    -------
    fig : object
        matplotlib figure object
    ax : object
        matplotlib axis object

        
    """

    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.serif'] = 'Source Sans Pro'
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.linewidth'] = 0
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['axes.titlesize'] = 11
    #plt.rcParams['axes.titleweight'] = 'bold'

    #plt.rcParams['axes.grid.axis'] = 'y'
    #plt.rcParams['axes.grid'] = True

    #plt.rcParams['axes.ymargin'] = True
    #plt.rcParams['axes.xmargin'] = True

    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['xtick.bottom'] = 'on'
    plt.rcParams['xtick.top'] = 'off'
    plt.rcParams['xtick.labelbottom'] = 'on'

    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['ytick.left'] = 'on'
    plt.rcParams['ytick.right'] = 'off'
    plt.rcParams['ytick.labelleft'] = 'on'

    plt.rcParams['legend.fontsize'] = 11
    plt.rcParams['legend.frameon'] = False

    plt.rcParams['figure.subplot.wspace'] = 0.5
    plt.rcParams['figure.subplot.hspace'] = 0.5
    plt.rcParams['figure.facecolor'] = 'w'

    plt.rcParams['font.size'] = 14

    fig,ax = plt.subplots(figsize=figsize,ncols=ncols, nrows=nrows, sharex=sharex, sharey=sharey)

    fig.align_labels()
    fig.subplots_adjust(left=0.1, right=0.9)

    def apply_axis(b):
        b.yaxis.grid()
    
    #at en ax fungerer også
    if isinstance(ax, np.ndarray):
        for a in ax.reshape(-1):
            apply_axis(a)
    else:
        apply_axis(ax)

    return fig, ax
