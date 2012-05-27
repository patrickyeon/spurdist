#!/usr/bin/python2

from core.helper import styles

class chart:
    def __init__(self, spurset, fef, parent):
        self.spurset, self.mx, self.fef = spurset, spurset.mixer, fef
        self.parent = parent
        self.spurstyles = styles()
        self.spurlines = {}
        self.feflines = []

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
