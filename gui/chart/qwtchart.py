#!/usr/bin/python2

from PyQt4.Qt import Qt, QPen, SIGNAL
from PyQt4.Qwt5 import (QwtPlot, QwtPicker, QwtPlotPicker, QwtPlotGrid,
                        QwtPlotCurve, QwtPlotItem, QwtLegend)

from gui.chart import chart

xaxis, yaxis = QwtPlot.xBottom, QwtPlot.yLeft

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
        return QPen(self.colours[colour], 1, self.styles[style])

    def __init__(self, spurset, fef, parent):
        chart.__init__(self, spurset, fef, parent)
        self.plot = QwtPlot(parent)

        self.plot.setAxisScale(xaxis, self.spurset.RFmin,
                               self.spurset.RFmax)
        self.plot.setAxisScale(yaxis, -self.spurset.dspan/2,
                               self.spurset.dspan/2)

        self.plot.setCanvasBackground(Qt.white)
        grid = QwtPlotGrid()
        grid.setMajPen(QPen(Qt.black, 1, Qt.DotLine))
        grid.attach(self.plot)

        self.plot.insertLegend(QwtLegend(self.parent), QwtPlot.ExternalLegend)

        # a picker to be used for the front-end filter parallelogram
        self.picker = QwtPlotPicker(xaxis, yaxis,
                                    QwtPicker.PointSelection,
                                    QwtPlotPicker.NoRubberBand,
                                    QwtPicker.AlwaysOff,
                                    self.plot.canvas())
        # gonna need this to implement ondrop()
        self._mouseRelease = self.picker.widgetMouseReleaseEvent
        self._picked_obj = None

        self.picker.connect(self.picker, SIGNAL('appended(const QPoint&)'),
                            self.onpick)
        self.picker.connect(self.picker, SIGNAL('moved(const QPoint&)'),
                            self.ondrag)
        # all about the monkey-patching
        self.picker.widgetMouseReleaseEvent = self.ondrop

    def redraw(self):
        xscale = self.plot.axisScaleDiv(xaxis)
        yscale = self.plot.axisScaleDiv(yaxis)
        #TODO check if it hurts to just set the scales every time, as in mpl
        if (xscale.lowerBound() != self.spurset.RFmin or
            xscale.upperBound() != self.spurset.RFmax):
            self.plot.setAxisScale(xaxis, self.spurset.RFmin,
                                   self.spurset.RFmax)
        if (yscale.lowerBound() != -self.spurset.dspan/2 or
            yscale.upperBound() != self.spurset.dspan/2):
            self.plot.setAxisScale(yaxis, -self.spurset.dspan/2,
                                   self.spurset.dspan/2)
        self.plot.replot()

    def mkline(self, xdata, ydata, style=('black','-'), title=''):
        line = QwtPlotCurve(title)
        if title is '':
            # don't display it in the legend
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

    def _xval(self, pos):
        # from a QPoint referring to a pixel on the plot, find the x value
        return self.plot.invTransform(xaxis, pos.x())

    def _yval(self, pos):
        # from a QPoint referring to a pixel on the plot, find the y value
        return self.plot.invTransform(yaxis, pos.y())

    def onpick(self, pos):
        # for now, we only worry about picking the two vertical lines of the
        # front-end filter parallelogram. Other clicks are no-ops.
        if abs(pos.x() - self.plot.transform(xaxis, self.fef.start)) <= 10:
            # TODO check pos.y() as well
            self._picked_obj = self.fef.startline
            self.pick(self.fef.startline, self._xval(pos), self._yval(pos))
        elif abs(pos.x() - self.plot.transform(xaxis, self.fef.stop)) <= 10:
            self._picked_obj  = self.fef.stopline
            self.pick(self.fef.stopline, self._xval(pos), self._yval(pos))
        else:
            return
        # TODO decide if a pick should also trigger a drag.
        # TODO this may be duplicated somewhere...
        self.ondrag(pos)

    def ondrag(self, pos):
        # no dragging action if we haven't already successfully picked something
        if self._picked_obj is not None:
            self.drag(self._picked_obj, self._xval(pos), self._yval(pos))

    def ondrop(self, evt):
        # need to make sure we're only triggering on left button releases
        if evt.button() == Qt.LeftButton and self._picked_obj is not None:
            self.drop(self._picked_obj, self._xval(evt), self._yval(evt))
            self._picked_obj = None
        # also important to let the original event handler happen
        self._mouseRelease(evt)
