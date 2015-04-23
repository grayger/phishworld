import xml.dom.minidom
import re
from world import *
from shape import *

class SvgParser:
    
    def __init__(self, file):
        self.shape_list = []
        self.dom = xml.dom.minidom.parse(file)
    
    def parse(self):
        svg_elem = self.dom.getElementsByTagName('svg')[0]
        self.width = int(svg_elem.attributes['width'].value) 
        self.height = int(svg_elem.attributes['height'].value)
        g_elem = self.dom.getElementsByTagName('g')[0]
        
#        x_ratio= float(Game.WINDOW_WIDTH)/(self.width *WorldConfig.WINDOW_PER_WORLD)
#        y_ratio= float(Game.WINDOW_HEIGHT)/(self.height *WorldConfig.WINDOW_PER_WORLD)
        x_ratio=y_ratio= 1.0/WorldConfig.WINDOW_PER_WORLD
        
        print x_ratio, y_ratio
        
        for node in g_elem.childNodes:
            knownNode = False
            if node.nodeName == 'rect':
                knownNode = True
            
                x = float(node.attributes['x'].value)* x_ratio
                y = (self.height - float(node.attributes['y'].value)) * y_ratio
                width = float(node.attributes['width'].value) * x_ratio
                height = float(node.attributes['height'].value) * y_ratio
                shape = Rect(x, y, width, height)

            elif  node.nodeName == 'path':
                knownNode = True

                if node.attributes.has_key('sodipodi:type') and node.attributes['sodipodi:type'].value == 'arc':
                    m = None
                    m1, m2 = 0, 0
                    if node.attributes.has_key('transform'):
                        m = re.search('translate\((.+)\,(.+)\)', node.attributes['transform'].value)
                        if m:
                            m1, m2 = float(m.group(1)), float(m.group(2))                     
                    x = (float(node.attributes['sodipodi:cx'].value) + m1) * x_ratio
                    y = (self.height - float(node.attributes['sodipodi:cy'].value) - m2) * y_ratio 
                    r = float(node.attributes['sodipodi:rx'].value) * x_ratio
                    shape = Circle(x, y, r) 
                else:
                    m = None
                    if node.attributes.has_key('transform'):
                        matx = node.attributes['transform'].value
                        m = re.search('matrix\((.+)\,(.+)\,(.+)\,(.+)\,(.+)\,(.+)\)', matx)
                        if m:
                            m1, m2, m3, m4, m5, m6 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)), float(m.group(6))
                        else:
                            m = re.search('translate\((.+)\,(.+)\)', matx)
                            if m:
                                m1, m2, m3, m4, m5, m6 = 1, 0, 0, 1, float(m.group(1)), float(m.group(2)) 
                    
                    x = float(node.attributes['sodipodi:cx'].value) * x_ratio
                    y = (self.height - float(node.attributes['sodipodi:cy'].value)) * y_ratio
                    r = (float(node.attributes['sodipodi:r1'].value) + float(node.attributes['sodipodi:r2'].value)) / (2 * WorldConfig.WINDOW_PER_WORLD)
                    shape = Polygon(x, y, r)
                    d = node.attributes['d'].value
                    for p in d.split()[:-2]:
                        if p.find(',') > 0:
                            x, y = map(float, p.split(','))
                            if m:
                                _x = m1 * x + m3 * y + m5
                                _y = m2 * x + m4 * y + m6
                                x,y = _x,_y
                            x = float(x) * x_ratio
                            y = (self.height - float(y)) * y_ratio
                            shape.add((x, y))
                    shape.points.reverse()
                    
            if knownNode:        
                shape.id=node.attributes['id'].value
                if node.attributes.has_key('style') :
                    style = node.attributes['style'].value
                    fill = re.search('fill:#([0-9a-f]+);', style)
                    if fill:
                        shape.fillColor = int(fill.group(1)[0:2], 16), int(fill.group(1)[2:4], 16), int(fill.group(1)[4:6], 16)
                    stroke = re.search('stroke:#([0-9a-f]+);', style)
                    if stroke:
                        shape.stroke=True
                        shape.strokeColor = int(stroke.group(1)[0:2], 16), int(stroke.group(1)[2:4], 16), int(stroke.group(1)[4:6], 16)
                        strokeWidth = re.search('stroke-width:([0-9\.]+);', style)
                        if strokeWidth:
                            shape.strokeWidth = float(strokeWidth.group(1))
                    else:
                        shape.stroke=False

                for prop in ['__role', '__image', '__durability', '__delay', '__ext1']:            
                    if node.attributes.has_key(prop):
                        setattr(shape, prop[2:], node.attributes[prop].value)                            
                self.shape_list.append(shape)
    
