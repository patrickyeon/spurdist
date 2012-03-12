import unittest
from core.mixer import *
from core.helper import looping_test

class mixerTests(unittest.TestCase):
    def setUp(self):
        self.mx = mixer(-1, 1, 4000, 100, 220)
        self.mx.spurs_from_limits(2, 4)

    def test_init(self):
        expected = set([(m, n) for m in range(-2, 3) for n in range(-4, 5)])
        for sp in [(0,0), (-1,1), (1,-1)]:
            # DC 'spur' and the actual down-converted signal
            expected.remove(sp)
        for sp in [(-2, 0), (-1, 0)] + [(0, -n) for n in range(1, 5)]:
            # -mRF and -nLO are the same as mRF and nLO, respectively
            expected.remove(sp)
        self.assertEqual(set(self.mx.spurs), expected)

    @looping_test(f=range(0, 10000, 100))
    def test_lo(self, f):
        self.assertEqual(self.mx.lo(f), self.mx.IF + f)

    @looping_test(f=range(0, 10000, 100), m=[2], n=[3])
    def test_dmn(self, f, m, n):
        a, b = self.mx.dmn(m, n, f, True)
        # a, b are (fbad - f) s.t. 2*fbad + 3*lo(f) = if +/- (ifbw/2 + G)
        self.assertEqual(2*(a + f) + 3*self.mx.lo(f),
                         self.mx.IF + self.mx.IFbw*0.5 + self.mx.G)
        self.assertEqual(2*(b + f) + 3*self.mx.lo(f),
                         self.mx.IF - self.mx.IFbw*0.5 - self.mx.G)


    @looping_test(f=range(0, 10000, 100))
    def test_dmn_vs_cw(self, f):
        for m,n in [(a,b) for a in range(1,5) for b in range(5)]:
            dp, dn = self.mx.dmn(m,n,f,True)
            c1,c2,w = self.mx.cw(m,n)
            self.assertLess(abs(w*f+c1 - dn), 1)
            self.assertLess(abs(w*f+c2 - dp), 1)

class spursetTests(unittest.TestCase):
    def setUp(self):
        self.mx = mixer(-1, 1, 4000, 100, 220)
        self.mx.spurs_from_limits(2, 4)
        self.spurset = spurset(0, 10000, 5000, self.mx)

    def test_is_in_plot(self):
        for (m,n) in self.mx.spurs:
            exp = False
            lines = zip(self.mx.dmn(m,n,0),
                        self.mx.dmn(m,n,10000))
            for (hi, lo) in lines:
                if abs(hi) <= 2500 or abs(lo) <= 2500:
                    exp = True
                if hi*lo < 0:
                    # If it crosses zero, by def'n must cross through chart
                    exp = True
            self.assertEqual(self.spurset.is_in_plot(m,n), exp)
