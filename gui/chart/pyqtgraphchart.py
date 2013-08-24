import pyqtgraph as pg
from PyQt4.Qt import Qt, QPen
from PyQt4.QtGui import QWidget
from gui.chart import chart

class pyqtgraphchart(chart):
    colours = {'red'     : Qt.red,
               'green'   : Qt.green,
               'blue'    : Qt.blue,
               'yellow'  : Qt.yellow,
               'magenta' : Qt.magenta,
               'black'   : Qt.black}
    styles = {'-'  : Qt.SolidLine,
              '--' : Qt.DashLine,
              ':'  : Qt.DotLine,
              '-.' : Qt.DashDotLine}

    def getPen(self, colour, style):
        return QPen(self.colours[colour], 1, self.styles[style])

    def __init__(self, spurset, fef, parent):
        chart.__init__(self, spurset, fef, parent)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.plot = pg.PlotWidget(parent)

    def legend(self):
        # TODO create/return the legend
        return QWidget(self.parent)

    def mkline(self, xdata, ydata, style, title):
        return pg.PlotDataItem(xdata, ydata, pen=self.getPen(*style))

    def add_line(self, line):
        self.plot.addItem(line)

    def del_line(self, line):
        self.plot.removeItem(line)

    def redraw(self):
        pass
