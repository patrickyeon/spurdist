#!/usr/bin/python2

from PyQt4.Qt import *
from PyQt4.Qwt5 import *

from core.helper import styles

class chart(QwtPlot):
    colours = {'red'    : Qt.red,
               'green'  : Qt.green,
               'blue'   : Qt.blue,
               'yellow' : Qt.yellow,
               'magenta': Qt.magenta,
               'black'  : Qt.black}
    styles = {'-' : Qt.SolidLine,
              '--': Qt.DashLine,
              ':' : Qt.DotLine,
              '-.': Qt.DashDotLine}

    def getPen(self, colour, style):
        return QPen(self.colours[colour], 2, self.styles[style])

    def __init__(self, spurset, fef, parent):
        QwtPlot.__init__(self, parent)
        self.spurset, self.mx, self.fef = spurset, spurset.mixer, fef
        self.spurstyles = styles()
        self.spurlines = {}
        self.feflines = []

        self.setCanvasBackground(Qt.white)
        self.setAxisScale(QwtPlot.xBottom, self.spurset.RFmin,
                          self.spurset.RFmax)
        self.setAxisScale(QwtPlot.yLeft, -self.spurset.dspan/2,
                          self.spurset.dspan/2)

        grid = QwtPlotGrid()
        grid.setMajPen(QPen(Qt.black, 1, Qt.DashLine))
        grid.attach(self)

        self.insertLegend(QwtLegend(), QwtPlot.ExternalLegend)

    def replot(self):
        xscale = self.axisScaleDiv(QwtPlot.xBottom)
        yscale = self.axisScaleDiv(QwtPlot.yLeft)
        lims = (xscale.lowerBound(), xscale.upperBound(),
                yscale.lowerBound(), yscale.upperBound())
        if lims[0] != self.spurset.RFmin or lims[1] != self.spurset.RFmax:
            self.setAxisScale(QwtPlot.xBottom, self.spurset.RFmin,
                              self.spurset.RFmax)
        if lims[2] != -self.spurset.dspan/2 or lims[3] != self.spurset.dspan/2:
            self.setAxisScale(QwtPlot.yLeft, -self.spurset.dspan/2,
                              self.spurset.dspan/2)
        QwtPlot.replot(self)

    def mkline(self, xdata, ydata, pen=('black','-'), title=''):
        line = QwtPlotCurve(title)
        if title is '':
            line.setItemAttribute(QwtPlotItem.Legend, False)
        pen = self.getPen(*pen)
        line.setPen(pen)
        line.setRenderHint(QwtPlotItem.RenderAntialiased)
        line.setData(xdata, ydata)
        return line

    def draw_spurs(self, obj):
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
                line['mpl'].detach()
            del self.spurlines[key]

        # draw new ones
        for m,n in new:
            xys  = lines[(m,n)]
            self.spurlines[(m,n)] = []
            for (li, leg) in zip(xys, (fmt_mn(m,n), '')):
                chline = self.mkline((li[0][0], li[1][0]), (li[0][1], li[1][1]),
                                     self.spurstyles[(m,n)], leg)
                chline.attach(self)
                self.spurlines[(m,n)].append({'xys': li, 'mpl': chline})

        self.replot()

    def draw_fef(self, obj):
        #remove old fef lines
        for line in self.feflines:
            line.detach()
        self.feflines = []
        # draw new ones
        def mkline(xys, pick=None):
            line = self.mkline(xys[0], xys[1])
            self.feflines.append(line)
            line.attach(self)
            return line
        self.fef.startline = mkline(self.fef.minf, 10)
        self.fef.stopline = mkline(self.fef.maxf, 10)
        mkline(self.fef.top)
        mkline(self.fef.bot)

        self.replot()

def fmt_mn(m, n):
    rf = (str(abs(m)) if abs(m) > 1 else '') + 'RF'
    lo = (str(abs(n)) if abs(n) > 1 else '') + 'LO'
    if m * n > 0:
        return rf + ' + ' + lo
    elif m == 0:
        return lo
    elif n == 0:
        return rf
    elif m > 0:
        return rf + ' - ' + lo
    else:
        return lo + ' - ' + rf
