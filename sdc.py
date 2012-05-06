#!/usr/bin/env python2

import gui.gui as gui
from core.mixer import mixer, spurset, fefilt
from PyQt4.QtGui import QApplication

def sdc(mx, spurs, front_filter):
    app = QApplication([''])
    mainwin = gui.MainWin(mx, spurs, front_filter)
    mainwin.show()
    app.exec_()

    
if __name__ == '__main__':
    mx = mixer(-1, 1, 4030, 100, 215)
    mx.spurs_from_limits(2, 4)
    spurs = spurset(0, 8000, 5000, mx)
    front_filter = fefilt(4000, 6000, mx.IFbw)
    sdc(mx, spurs, front_filter)
