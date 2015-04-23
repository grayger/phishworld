import sys, imp, os

# http://www.py2exe.org/index.cgi/HowToDetermineIfRunningFromExe
def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
   if main_is_frozen():
       return os.path.dirname(sys.executable)
   return os.path.dirname(sys.argv[0])

class TimeIndex:
    def __init__(self, array, delay):
        self.array = array
        self.count = len(self.array)
        self.delay = delay # sec
        self.maxTime = self.count * self.delay
        self.timer = 0
        
    def elapse(self, dt): # sec
        self.timer += dt
        self.timer = self.timer % self.maxTime
        
    def get(self):
        try:
            return self.array[int(self.timer / self.delay)]
        except:
            print self.array, int(self.timer / self.delay), self.timer, self.delay
            return self.array[0]
    
    def reset(self):
        self.timer = 0

def half(x):
    """Halves x. For example:
    >>> half(6.8)
    3.4
    >>>
    """
    return x / 2

class Roll:
    def __init__(self, range=(0, 10), get=None):
        self.min = range[0]
        self.max = range[1]
        self.num = self.min
        if get == None:
            self.get = lambda : self.num
        
        self.get = get
        
    def incr(self):
        if self.num >= self.max:
            self.num = self.min
        else:
            self.num += 1
        
    def next(self):
        v = self.get(self.num)
        self.incr()
        return v
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
