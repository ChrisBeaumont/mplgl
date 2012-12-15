from time import time

class fps(object):
    """Print calls per second, once per second"""
    def __init__(self, func):
        self.ctr = 0
        self.t0 = time()
        self.func = func

    def __call__(self, *args, **kwargs):
        self.ctr += 1
        t = time()
        if t - self.t0 > 1:
            print "fps: %0.2f" % (self.ctr / (t - self.t0))
            self.ctr = 0
            self.t0 = t
        return self.func(*args, **kwargs)
