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

        # make the figure blend in with the native application look
        bgcol = parent.palette().window().color().toRgb()
        bgcol = [bgcol.redF(), bgcol.greenF(), bgcol.blueF()]

        self.fig = Figure()
        self.fig.set_facecolor(bgcol)
        
        # a FigureCanvas can be added as a QWidget, so we use that
        self.plot = FigureCanvas(self.fig)
        self.plot.setParent(parent)

        self.ax = self.fig.add_subplot(111)
        # TODO skip this, just do a redraw() after initialization?
        self.ax.set_xlim(self.spurset.RFmin, self.spurset.RFmax)
        self.ax.set_ylim(-0.5*self.spurset.dspan, 0.5*self.spurset.dspan)
        self.ax.grid(True)
        self.fig.tight_layout()

        # a second figure to hold the legend
        self.legendFig = Figure()
        self.legendFig.set_facecolor(bgcol)
        self.legendCanvas = FigureCanvas(self.legendFig)
        self.legendFig.legend(*self.ax.get_legend_handles_labels(),
                              loc='upper left')

        # connect up the picker watching
        self.picked_obj = None
        self._pick = self.plot.mpl_connect('pick_event', self.onpick)
        self._drag = self.plot.mpl_connect('motion_notify_event', self.ondrag)
        self._drop = self.plot.mpl_connect('button_release_event', self.ondrop)

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
        self.feflines[0].set_picker(10)
        self.feflines[1].set_picker(10)

    def onpick(self, event):
        obj, x, y = event.artist, event.mouseevent.xdata, event.mouseevent.ydata
        self.picked_obj = obj
        self.pick(obj, x, y)
        self.drag(obj, x, y)

    def ondrag(self, event):
        self.drag(self.picked_obj, event.xdata, event.ydata)

    def ondrop(self, event):
        self.drop(self.picked_obj, event.xdata, event.ydata)
        self.picked_obj = None
