from world import *
import math

class Shape(object):
    def __init__(self):
        self.fillColor=None
        self.strokeColor=None
        self.strokeWidth=0
        self.stroke=False
        self.role=None
        self.image=None
        self.direction=None
        self.durability=None
        self.delay=None
        self.ext1=None
        self.id=None

class Rect(Shape):
    def __init__(self, x, y, width, height):
        super(Rect, self).__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius= math.sqrt(self.width/2**2+ self.height/2**2)
        
    def _get_center(self):
        return (2 * self.x + self.width) / 2, (2 * self.y - self.height) / 2
    
#    def _get_radius(self):
#        return math.sqrt(self.width/2**2+ self.height/2**2) 
    
    center = property(_get_center)
#    radius= property(_get_radius)
    type = WorldConfig.BOX
    
class Circle(Shape):
    def __init__(self, x, y, radius):
        super(Circle, self).__init__()
        self.x = x
        self.y = y
        self.radius = radius
    type = WorldConfig.CIRCLE
       
class Polygon(Shape):
    def __init__(self, x, y, radius):
        super(Polygon, self).__init__()
        self.x = x
        self.y = y
        self.radius = radius
        self.points = []
        
    def add(self, point):
        self.points.append(point)
    type = WorldConfig.POLYGON
    
