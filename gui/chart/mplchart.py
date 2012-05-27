#!/usr/bin/python2

import matplotlib as mpl
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from gui.chart import chart as chart

class mplchart(chart):
    def __init__(self, spurset, fef, parent):
        chart.__init__(self, spurset, fef, parent)

        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.ax = mpl.axes.Axes(self.fig, [0.1, 0.1, 0.7, 0.9])
        self.ax.set_xlim(self.spurset.RFmin, self.spurset.RFmax)
        self.ax.set_ylim(-0.5*self.spurset.dspan, 0.5*self.spurset.dspan)
        self.ax.grid(True)
        self.fig.add_axes(self.ax)

    def setParent(self, parent):
        chart.setParent(self, parent)
        self.canvas.setParent(parent)

    def redraw(self, obj):
        if obj is self.spurset or obj is self.mx:
            lines = self.spurset.spurset()
            legend_flag = (set(lines) != set(self.spurlines))
            remove = set(self.spurlines) - set(lines)
            new = set(lines) - set(self.spurlines)

            # remove invalid lines
            for key in set(self.spurlines) & set(lines):
                for line in self.spurlines[key]:
                    if line['xys'] not in lines[key]:
                        remove.add(key)
                        new.add(key)
            for key in remove:
                for line in self.spurlines[key]:
                    self.ax.lines.remove(line['mpl'])
                del self.spurlines[key]

            # draw new ones
            for m,n in new:
                xys  = lines[(m,n)]
                c,s = self.spurstyles[(m,n)]
                mplines = [mpl.lines.Line2D((li[0][0], li[1][0]),
                                            (li[0][1], li[1][1]),
                                            color=c, ls=s,
                                            label=leg)
                           for (li, leg) in zip(xys, (fmt_mn(m,n), None))]
                self.spurlines[(m,n)] = [{'xys': li, 'mpl': line}
                                         for li, line in zip(xys, mplines)]
                for li in mplines:
                    self.ax.add_line(li)

            if legend_flag:
                self.ax.legend(loc=(1.03,0))
            self.ax.set_ylim(-0.5*self.spurset.dspan, 0.5*self.spurset.dspan)
            self.ax.set_xlim(self.spurset.RFmin, self.spurset.RFmax)

        elif obj is self.fef:
            #remove old fef lines
            for line in self.feflines:
                self.ax.lines.remove(line)
            self.feflines = []
            # draw new ones
            def mkline(xys, pick=None):
                line = mpl.lines.Line2D(xys[0], xys[1], color='k', picker=pick)
                self.feflines.append(line)
                self.ax.add_line(line)
                return line
            self.fef.startline = mkline(self.fef.minf, 10)
            self.fef.stopline = mkline(self.fef.maxf, 10)
            mkline(self.fef.top)
            mkline(self.fef.bot)
        self.canvas.draw()
