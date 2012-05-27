#!/usr/bin/python2

from core.helper import styles, fmt_mn

class chart:
    def __init__(self, spurset, fef, parent):
        self.spurset, self.mx, self.fef = spurset, spurset.mixer, fef
        self.parent = parent
        self.spurstyles = styles()
        self.spurlines = {}
        self.feflines = []

    def draw_spurs(self, obj):
        lines = self.spurset.spurset()
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
                self.del_line(line['mpl'])
            del self.spurlines[key]

        # draw new ones
        for m,n in new:
            xys  = lines[(m,n)]
            self.spurlines[(m,n)] = []
            for (li, leg) in zip(xys, (fmt_mn(m,n), '')):
                line = self.mkline((li[0][0], li[1][0]), (li[0][1], li[1][1]),
                                   self.spurstyles[(m,n)], leg)
                self.add_line(line)
                self.spurlines[(m,n)].append({'xys': li, 'mpl': line})

        self.redraw()

    def draw_fef(self, obj):
        #remove old fef lines
        for line in self.feflines:
            self.del_line(line)
        self.feflines = []
        # draw new ones
        fef = self.fef
        for xys in (fef.minf, fef.maxf, fef.top, fef.bot):
            line = self.mkline(xys[0], xys[1], ('black','-'), '')
            self.feflines.append(line)
            self.add_line(line)
        
        self.fef.startline = self.feflines[0]
        self.fef.stopline = self.feflines[1]
        self.redraw()
