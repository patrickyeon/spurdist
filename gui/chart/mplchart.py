#!/usr/bin/python2

from PyQt4.QtGui import QWidget

import matplotlib as mpl
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from gui.chart import chart

class mplchart(chart):
    def __init__(self, spurset, fef, parent):
        chart.__init__(self, spurset, fef, parent)

        self.fig = Figure()
        self.plot = FigureCanvas(self.fig)
        self.plot.setParent(parent)
        self.ax = mpl.axes.Axes(self.fig, [0.1, 0.1, 0.7, 0.9])
        self.ax.set_xlim(self.spurset.RFmin, self.spurset.RFmax)
        self.ax.set_ylim(-0.5*self.spurset.dspan, 0.5*self.spurset.dspan)
        self.ax.grid(True)
        self.fig.add_axes(self.ax)

    def legend(self):
        return QWidget(self.parent)
    
    def mkline(self, xdata, ydata, style, title):
        return mpl.lines.Line2D(xdata, ydata,
                                color=style.c, ls=style.s, label=title)

    def add_line(self, line):
        self.ax.add_line(line)

    def del_line(self, line):
        self.ax.lines.remove(line)

    def draw_spurs(self, obj):
        chart.draw_spurs(self, obj)

        self.ax.legend(loc=(1.03,0))

    def redraw(self):
        self.ax.set_ylim(-0.5*self.spurset.dspan, 0.5*self.spurset.dspan)
        self.ax.set_xlim(self.spurset.RFmin, self.spurset.RFmax)
        self.plot.draw()

    def draw_fef(self, obj):
        chart.draw_fef(self, obj)
        self.feflines[0].set_pickradius(10)
        self.feflines[1].set_pickradius(10)
