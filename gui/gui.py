#!/usr/bin/python2

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sys import argv

from core.helper import *
from core.mixer import *
from chart import chart

class MainWin(QMainWindow):
    def __init__(self, mx, spurs, fef, parent=None):
        QMainWindow.__init__(self, parent)

        self.mx = mx
        self.spurset = spurs
        self.fef = fef

        self.chart = chart(self.spurset, self.fef, self)
        self.create_menu_bar()
        self.create_main_frame()
        self.hookup()

    def hookup(self):
        # connect all the objects that are supposed to be watching each other
        # for changes and updates.
        self.mx.register(self.chart.draw_spurs)
        self.spurset.register(self.chart.draw_spurs)
        #self.fef.hookup(self.chart.canvas)
        self.fef.register(self.chart.draw_fef)
        self.chart.draw_spurs(self.spurset)
        self.chart.draw_fef(self.fef)

    def IF_slide(self, i):
        """ callback method for the IF selection slider"""
        self.IFtextbox.setText(str(i))
        self.mx.IF = i

    def about(self):
        msg = '''
        A frequency-planing tool based on the method of spur distances.
        (A reference to the article will go here)
        For more info, view the README included with this program.

        Patrick Yeon, 2012'''
        QMessageBox.about(self, 'Spur Distance Chart', msg.strip())

    def mxtypecb(self, i):
        """ callback method for mixer configuration selection combobox"""
        self.mx.m, self.mx.n = [(-1, 1), (1, -1), (1,1)][i]
        # trigger anything watching the mixer
        self.mx.update_watchers()

    def create_main_frame(self):
        self.main_frame = QWidget()
        #self.chart.setParent(self.main_frame)
        # Looking at the main frame as two columns. On the left there is the
        # chart and the IF control. In the right column we'll have range
        # settings, mixer settings, and maybe other stuff that comes up?

        self.IFtextbox = QLineEdit()
        self.IFtextbox.setMinimumWidth(6)
        self.IFtextbox.setText(str(self.spurset.mixer.IF))
        # TODO link up the textbox so that it can also be input

        self.IFslider = QSlider(Qt.Horizontal)
        # TODO I'd really like some form of slider that doesn't actually limit
        # the user. Also, if IFtextbox could modify the IF, that'd be nice.
        self.IFslider.setRange(int(self.mx.IF * 0.1), (self.mx.IF * 5))
        self.IFslider.setValue(self.mx.IF)
        self.IFslider.setTracking(True)
        self.IFslider.setTickPosition(QSlider.TicksAbove)
        step = max(1, int(0.01 * self.mx.IF))
        self.IFslider.setSingleStep(step)
        self.IFslider.setPageStep(step * 10)
        self.IFcid = self.connect(self.IFslider, SIGNAL('valueChanged(int)'),
                                  self.IF_slide)

        IFbar = QHBoxLayout()
        IFbar.addWidget(QLabel('IF'))
        IFbar.addWidget(self.IFtextbox)
        IFbar.addWidget(self.IFslider)
        IFbar.addStretch()

        leftcol = QVBoxLayout()
        leftcol.addWidget(self.chart)
        leftcol.addLayout(IFbar)

        # left column done. Now the right-hand side
        rangebox = QVBoxLayout()
        for (prop, name, f) in [(spurset.RFmin, 'RFmin', self.spurset.RFmin),
                                (spurset.RFmax, 'RFmax', self.spurset.RFmax),
                                (spurset.dspan, 'dspan', self.spurset.dspan)]:
            rangebox.addLayout(Fbar(self.spurset, prop,
                                    name, f, 0, 10000))
        autocb = QCheckBox('Auto')
        # Disable it, won't be implemented for release
        # but leave it there, to nag me into doing it.
        autocb.setDisabled(True)
        rangebox.addWidget(autocb)

        # a line to report the front-end filter's limits
        fefstat = QHBoxLayout()
        fefstat.addWidget(QLabel('Filter Range: '))
        fefrange = QLabel('%d - %d' % (self.fef.start, self.fef.stop))
        # TODO not sure about the lambda here. Feels like if I give it time,
        # I'll sort out a sensible overall connection scheme.
        self.fef.register(lambda o: fefrange.setText('%d - %d' % 
                                                     (self.fef.start,
                                                      self.fef.stop)))
        fefstat.addWidget(fefrange)

        # mixer high/low-side injection picker
        mxbar = QHBoxLayout()
        mxbar.addWidget(QLabel('IF = '))
        mxtype = QComboBox()
        mxtype.addItem('LO - RF')
        mxtype.addItem('RF - LO')
        mxtype.addItem('RF + LO')
        # TODO this is ugly
        mxtype.setCurrentIndex([(-1, 1), (1, -1), (1,1)].index((self.mx.m,
                                                                self.mx.n)))
        self.mxtypecid = self.connect(mxtype,
                                      SIGNAL('currentIndexChanged(int)'),
                                      self.mxtypecb)
        mxbar.addWidget(mxtype)

        # alright, the actual column proper in the layout
        vbar = QVBoxLayout()
        vbar.addLayout(rangebox)
        vbar.addLayout(fefstat)
        vbar.addLayout(mxbar)
        vbar.addStretch()

        hbox = QHBoxLayout()
        hbox.addLayout(leftcol)
        hbox.addLayout(vbar)

        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)

    def create_menu_bar(self):
        filemenu = self.menuBar().addMenu('&File')
        close = QAction('&Quit', self)
        close.setShortcut('Ctrl+W')
        self.connect(close, SIGNAL('triggered()'), self.close)
        filemenu.addAction(close)

        helpmenu = self.menuBar().addMenu('&Help')
        about  = QAction('&About', self)
        about.setShortcut('F1')
        self.connect(about, SIGNAL('triggered()'), self.about)
        helpmenu.addAction(about)

class Fbar(QHBoxLayout):
    # An HBox for setting frequencies: label and spinbox
    def __init__(self, obj, prop, name, init, low, high):
        QHBoxLayout.__init__(self)
        self.addWidget(QLabel(name))
        self.spinbox = SpinBox(obj, prop)
        self.spinbox.setRange(low, high)
        self.spinbox.setValue(init)
        self.spinbox.setSingleStep(100)
        self.addWidget(self.spinbox)

class Slider(QSlider):
    # A QSlider tied to an appropriate observable's property.
    def __init__(self, observed, prop,
                 orientation=Qt.Vertical, parent=None):
        QSlider.__init__(self, orientation, parent)
        # TODO still not happy here
        self.getter = lambda: prop.fget(observed)
        self.setter = lambda x: prop.fset(observed, x)
        observed.register(self.update)
        self.setValue(self.getter())
        self.connect(self, SIGNAL('valueChanged(int)'), self.setter)

    def update(self, obj):
        if self.value() != self.getter():
            self.setValue(self.getter())

class SpinBox(QSpinBox):
    # A QSpinBox tied to an appropriate observable's property.
    def __init__(self, observed, prop, parent=None):
        QSpinBox.__init__(self, parent)
        self.getter = lambda: prop.fget(observed)
        self.setter = lambda x: prop.fset(observed, x)
        observed.register(self.update)
        self.setValue(self.getter())
        self.connect(self, SIGNAL('valueChanged(int)'), self.setter)

    def update(self, obj):
        if self.value() != self.getter():
            self.setValue(self.getter())
