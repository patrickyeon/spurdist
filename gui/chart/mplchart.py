#!/usr/bin/python2

from PyQt4.QtGui import QWidget

import matplotlib as mpl
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from gui.chart import chart

class mplchart(chart):
    colours = dict(zip('red green blue yellow magenta black'.split(),
                       'r   g     b    y      m       k'.split()))

    def __init__(self, spurset, fef, parent):
        chart.__init__(self, spurset, fef, parent)
        bgcol = parent.palette().window().color().toRgb()
        bgcol = [bgcol.redF(), bgcol.greenF(), bgcol.blueF()]

        self.fig = Figure()
        self.plot = FigureCanvas(self.fig)
        self.plot.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(self.spurset.RFmin, self.spurset.RFmax)
        self.ax.set_ylim(-0.5*self.spurset.dspan, 0.5*self.spurset.dspan)
        self.ax.grid(True)
        self.fig.tight_layout()
        self.fig.set_facecolor(bgcol)

        self.legendFig = Figure(figsize=(1,1))
        self.legendCanvas = FigureCanvas(self.legendFig)
        self.legendFig.legend(*self.ax.get_legend_handles_labels(),
                              loc='upper left')
        self.legendFig.set_facecolor(bgcol)

    def legend(self):
        return self.legendCanvas
    
    def mkline(self, xdata, ydata, style, title):
        return mpl.lines.Line2D(xdata, ydata, label=title,
                                color=self.colours[style[0]], ls=style[1])

    def add_line(self, line):
        self.ax.add_line(line)

    def del_line(self, line):
        self.ax.lines.remove(line)

    def draw_spurs(self, obj):
        chart.draw_spurs(self, obj)

    def redraw(self):
        self.ax.set_ylim(-0.5*self.spurset.dspan, 0.5*self.spurset.dspan)
        self.ax.set_xlim(self.spurset.RFmin, self.spurset.RFmax)
        # WHO WANTS TO BET THIS IS UNSUPPORTED?
        # but damn, it works :/
        self.legendFig.legends = []
        self.legendFig.legend(*self.ax.get_legend_handles_labels(),
                              loc='upper left')
        self.legendCanvas.draw()
        self.plot.draw()

    def draw_fef(self, obj):
        chart.draw_fef(self, obj)
        self.feflines[0].set_pickradius(10)
        self.feflines[1].set_pickradius(10)
