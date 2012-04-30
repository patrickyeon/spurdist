#!/usr/bin/python2
from itertools import product

class observable(object):
    """A too-quick and too-ugly implementation of the observable pattern"""
    def __init__(self):
        self._watchers = []
    def register(self, fn):
        # Observer passes us the calback function to use, we will call it with
        # self as the only argument so that they know who fired.
        self._watchers.append(fn)
    def unregister(self, fn):
        while fn in self._watchers:
            self._watchers.remove(fn)
    def update_watchers(self):
        for fn in self._watchers:
            fn(self)

    @staticmethod
    def wprop(watched):
        # pretty sure this could be better, but given the name (as in, string)
        # of a class variable, it returns a property backed by that variable
        # that will trigger self.update_watchers() when it's changed.
        def get_prop(self):
            return getattr(self, watched)
        def set_prop(self, val):
            setattr(self, watched, val)
            getattr(self, 'update_watchers')()
        return property(get_prop, set_prop)

class styles:
    """A consistent set of line, colour styles"""
    # TODO inherit from defaultdict?
    def __init__(self, lines=['-', '--', ':', '-.'], colours=list('rgbym')):
        self.lines, self.colours = lines, colours
        self._iter = iter(())
        self._dict = {}

    def __getitem__(self, k):
        if k not in self._dict:
            self._dict[k] = self.next_style()
        return self._dict[k]

    def next_style(self):
        try:
            return self._iter.next()
        except StopIteration:
            self._iter = ((c, s) for s in self.lines for c in self.colours)
            return self.next_style()

class looping_test(object):
    def __init__(self, **kwargs):
        self.loopargs = kwargs

    def __call__(self, f):
        def wrapped(s):
            failures = 0
            firstfail = None
            keys = self.loopargs.keys()
            states = product(*[self.loopargs[k] for k in keys])
            for state in states:
                try:
                    args = dict(zip(keys, state))
                    f(s, **args)
                except(AssertionError):
                    failures += 1
                    if firstfail is None:
                        firstfail = state
            if failures > 0:
                raise AssertionError(('test failed %d times, ' +
                                      'first on state: %s') % (failures,
                                                               str(firstfail)))
        wrapped.__name__ = f.__name__
        return wrapped
