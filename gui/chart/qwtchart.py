#!/usr/bin/python2

from PyQt4.Qt import *
from PyQt4.Qwt5 import *

from gui.chart import chart

class qwtchart(chart):
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
        chart.__init__(self, spurset, fef, parent)
        self.plot = QwtPlot(parent)

        self.plot.setCanvasBackground(Qt.white)
        self.plot.setAxisScale(QwtPlot.xBottom, self.spurset.RFmin,
                               self.spurset.RFmax)
        self.plot.setAxisScale(QwtPlot.yLeft, -self.spurset.dspan/2,
                               self.spurset.dspan/2)

        grid = QwtPlotGrid()
        grid.setMajPen(QPen(Qt.black, 1, Qt.DotLine))
        grid.attach(self.plot)

        self.plot.insertLegend(QwtLegend(self.parent), QwtPlot.ExternalLegend)

    def redraw(self):
        xscale = self.plot.axisScaleDiv(QwtPlot.xBottom)
        yscale = self.plot.axisScaleDiv(QwtPlot.yLeft)
        lims = (xscale.lowerBound(), xscale.upperBound(),
                yscale.lowerBound(), yscale.upperBound())
        #TODO check if it hurts to just set the scales every time, as in mpl
        if lims[0] != self.spurset.RFmin or lims[1] != self.spurset.RFmax:
            self.plot.setAxisScale(QwtPlot.xBottom, self.spurset.RFmin,
                                   self.spurset.RFmax)
        if lims[2] != -self.spurset.dspan/2 or lims[3] != self.spurset.dspan/2:
            self.plot.setAxisScale(QwtPlot.yLeft, -self.spurset.dspan/2,
                                   self.spurset.dspan/2)
        self.plot.replot()

    def mkline(self, xdata, ydata, style=('black','-'), title=''):
        line = QwtPlotCurve(title)
        if title is '':
            # kind of ugly, that the title variable is doing double duty
            line.setItemAttribute(QwtPlotItem.Legend, False)
        pen = self.getPen(*style)
        line.setPen(pen)
        line.setRenderHint(QwtPlotItem.RenderAntialiased)
        line.setData(xdata, ydata)
        return line

    def add_line(self, line):
        line.attach(self.plot)

    def del_line(self, line):
        line.detach()

    def legend(self):
        return self.plot.legend()
