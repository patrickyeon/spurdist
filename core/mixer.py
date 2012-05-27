#!/usr/bin/python2
# RFmn = frequency that, when tuned to receive RF, casues a mRF+nLO spur at the
#        IF.
# mRFmn + nLO = IF [+/-] (guard + IFbw/2)
# dmn = distance from RF to RFmn (RFmn - RF)
# dmn = (IF [+/-] G)/m - (n/m)LO - RF
# so, having selected IF, G, and mixer setup (eg IF = LO - RF), we can calculate
# the dmn for each (m,n) spur of interest, for any RF.
# IF = LO - RF .: LO = IF + RF
# dmn = (IF [+/-] G)/m - (n/m)(IF + RF) - RF
#     = (IF(1-n) [+/-] G)/m - RF(1 + n/m)
#
from collections import defaultdict
from core.helper import observable

# first, we'll have a mixer
class mixer(observable):
    def __init__(self, mRF, nLO, IF, IFbw, guard, spurs=[]):
        observable.__init__(self)
        # stick with what we know, for now (ie no subharmonic mixers)
        if mRF not in (1, -1) or nLO not in (1, -1):
            raise NotImplementedError
        self.m, self.n, self.spurs = mRF, nLO, spurs
        self._IF, self.IFbw, self.G = IF, IFbw, guard

    IF = observable.wprop('_IF')

    def spurs_from_list(self, spurlist):
        spurs = set([(abs(sp[0]), abs(sp[1])) for sp in spurlist])
        # using sets to get rid of +/-0 redundancies
        self.spurs = set(sum([[(m,n), (-m,n), (m,-n), (-m,-n)]
                              for m,n in spurs], []))
        for sp in [(self.m, self.n), (-self.m, -self.n), (0, 0)]:
            # don't consider our actual signal, nor DC, as a spur
            if sp in self.spurs:
                self.spurs.remove(sp)
        for sp in [(a,b) for (a,b) in self.spurs if a * b == 0 and a + b < 0]:
            # (-m,0) and (0, -n) spurs are the same as (m,0), (0,n) respectively
            self.spurs.remove(sp)

    def spurs_from_limits(self, m, n):
        """given (mm_max, n_max), spurs = (m,n) for m=0..m_max, n=0..n_max"""
        self.spurs_from_list([(a,b) for a in range(m+1) for b in range(n+1)])

    def lo(self, rf):
        """calculate the LO used to tune to the given rf"""
        # TODO need to force fp for subharmonic mixers
        # TODO is the abs() really needed? Is it hiding some understanding?
        return abs(self.IF/self.n - self.m*rf/self.n)

    # calculate distances, for a specific (m,n) spur
    def dmn(self, m, n, rf, override_spurs=False):
        # unless they really want it, don't report spurs that aren't a worry
        # TODO beginning to think this may be the wrong way to do it
        if override_spurs is False and (m,n) not in self.spurs:
            return None
        # force floating point division in the math
        m, n = float(m), float(n)
        # each m,n,rf triplet has a range of troublesome frequencies, mapping to
        # IF +/- (IFbw/2)
        if m == 0:
            (dmn_pos, dmn_neg) = self._d0n(n, rf)
        else:
            dmn_pos = ((self.IF + self.IFbw*0.5 + self.G)/m
                              - (n/m)*self.lo(rf)) - rf
            dmn_neg = ((self.IF - self.IFbw*0.5 - self.G)/m
                              - (n/m)*self.lo(rf)) - rf
        return (dmn_pos, dmn_neg)

    def _d0n(self, n, rf):
        # if m is 0, the more general calculations don't work, so we
        # special-case the math
        # TODO fix this for subharmonic mixers (self.m, self.n not in (1,-1))
        d_pos = n*self.lo(rf) - (rf + self.IFbw*0.5 + self.G)
        d_neg = n*self.lo(rf) - (rf - self.IFbw*0.5 - self.G)
        return (d_pos, d_neg)

    def cw(self, m, n):
        # instead of worrying about the distance at a single RF point, let's
        # deal with  the equations of the lines that we would draw to represent
        # a spur. With arbitrary variable names, d = w*RF + c
        if m == 0:
            return self._cw0(n)
        n, m = float(n), float(m)
        # TODO explain the math here
        w = (n/m) * (self.m/float(self.n)) - 1
        c1, c2 = [(self.IF * (1 - n/self.n)
                   + sign*(self.IFbw*0.5 + self.G)) / m for sign in (-1, 1)]
        return (c1, c2, w)

    def _cw0(self, n):
        # TODO ummm, I'm not exactly confident with w = -1
        w = -1
        c1 = (self.IF + self.G + self.IFbw*0.5) / float(n)
        c2 = (self.IF - self.G - self.IFbw*0.5) / float(n)
        return (c1, c2, w)

# so, let's make a d vs. RF plot
class spurset(observable):
    def __init__(self, RFmin, RFmax, dspan, mixer):
        observable.__init__(self)
        self._RFmin, self._RFmax, self._dspan = RFmin, RFmax, dspan
        self.mixer = mixer

    RFmin = observable.wprop('_RFmin')
    RFmax = observable.wprop('_RFmax')
    dspan = observable.wprop('_dspan')

    # does a spur cross our chart?
    def is_in_plot(self, mRF, nLO):
        spurs = zip(self.mixer.dmn(mRF, nLO, self.RFmin),
                    self.mixer.dmn(mRF, nLO, self.RFmax))
        for (lo, hi) in spurs:
            if abs(lo) <= 0.5*self.dspan or abs(hi) <= 0.5*self.dspan:
                # the trouble band is within dspan, at least at one end of the
                # RF range of interest
                return True
            if ((lo < -0.5*self.dspan and hi > 0.5*self.dspan)
                or (lo > 0.5*self.dspan and hi < -0.5*self.dspan)):
                # the trouble band crosses through dspan at some point
                return True
        # TODO? edge case that fails: the entire (d,RF) plot fits _within_ a
        # trouble band. Really, I don't think designs that bad should get this
        # far.
        return False

    def spurset(self):
        spurs = defaultdict(list)
        for (m,n) in self.mixer.spurs:
            if self.is_in_plot(m,n):
                spurs[(self.mixer.dmn(m,n,self.RFmin),
                       self.mixer.dmn(m,n,self.RFmax))].append((m,n))
        # spurs is keyed on dmn pairs so that two different representations of
        # the same spur (eg: (m, -n) and (-m, n)) only get drawn once.
        # Arbitrarily, we return whichever showed up first. The value in the
        # returned dict is a pair of lines, as (x0,y0) and (x1,y1) that someone
        # could then plot.
        return dict([((m, n), self.clip_to_lims(m, n))
                     for (m, n) in [mn[0] for mn in spurs.values()]])

    def clip_to_lims(self, m, n):
        # dmn() returns lines where (x0, x1) = (RFmin, RFmax), but sometimes
        # those lines go out of the RF-dspan space we're covering. Instead, this
        # method will return the lines as pairs of points that are at the
        # RF-dspan space's edges.
        c1, c2, w = self.mixer.cw(m, n)
        # our two spurlines are now d = w*RF + {c1,c2}
        def pt_in_plot(w, c, rf):
            if w != 0 and abs(w*rf + c) > abs(self.dspan*0.5):
                # horiz. lines happen, nothing wrong with that (2RF - 2LO, etc)
                if w*rf + c > 0:
                    rf = (0.5*self.dspan - c)/float(w)
                else:
                    rf = (-0.5*self.dspan - c) / float(w)
            return (rf, w*rf + c)

        return [[pt_in_plot(w, c, r) for r in (self.RFmin, self.RFmax)]
                for c in (c1, c2)]

class fefilt(observable):
    """Front-end filter"""
    def __init__(self, start, stop, IFbw):
        observable.__init__(self)
        self._start, self._stop, self._bw = start, stop, IFbw
        self.minf, self.maxf, self.top, self.bot = None, None, None, None
        self.picked = None
        self.startline, self.stopline = None, None

        self.recalc(self)
        self.register(self.recalc)

    start = observable.wprop('_start')
    stop = observable.wprop('_stop')
    bw = observable.wprop('_bw')

    def onpick(self, event):
        # When either the min or max frequency is selected
        if event.artist == self.startline:
            self.picked = 'minf'
        elif event.artist == self.stopline:
            self.picked = 'maxf'
        else:
            # in case something else on the chart's been selected
            return
        self._drag = self.canvas.mpl_connect('motion_notify_event', self.ondrag)
        self.ondrag(event.mouseevent)

    def ondrag(self, event):
        # have to change our values to represent the new ones as they come in
        if event.xdata is None:
            # happens with matplotlib when the mouse tries to drag out of the
            # chart space
            return
        if self.picked is 'minf':
            self.start = event.xdata
        elif self.picked is 'maxf':
            self.stop = event.xdata

    def ondrop(self, event):
        if self.picked is not None:
            self.picked = None
        if self._drag is not None:
            self.canvas.mpl_disconnect(self._drag)
            self._drag = None

    def hookup(self, canvas):
        self.canvas = canvas
        self._pick = canvas.mpl_connect('pick_event', self.onpick)
        self._drop = canvas.mpl_connect('button_release_event', self.ondrop)
        self._drag = None

    def recalc(self, obj):
        start, stop, bw = self.start, self.stop, self.bw
        if start > stop:
            # switch maxf/minf around
            start, stop = stop, start
            if self.picked == 'minf':
                self.picked = 'maxf'
            elif self.picked == 'maxf':
                self.picked = 'minf'
        # these are all ((x0, x1), (y0, y1)), so that it's easy on mpl
        self.minf = ((start, start), (-0.5*bw, stop - start + 0.5*bw))
        self.maxf = ((stop, stop), (0.5*bw, start - stop - 0.5*bw))
        self.top = ((start, stop), (stop - start + 0.5*bw, 0.5*bw))
        self.bot = ((start, stop), (-0.5*bw, start - stop - 0.5*bw))
