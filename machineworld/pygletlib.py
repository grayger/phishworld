import sys, math
import pyglet
import time
from pyglet.window import key
from pyglet.gl import *
from game import Overlay, Game

class Menu(Overlay):
    def __init__(self, window, x=None, y=None, backGround=None, backGroundColor=(255, 255, 255)):
        super(Menu, self).__init__()
        self.x, self.y = x, y
        self.items = None
        self.selectedIndex = 0
        self.backGround = backGround
        self.window = window
#    
    def onStart(self):
        self.selectedIndex = 0
#        Game.soundPlayer.playBg('Home_Base_Groove.ogg')
        
    def setMenuItems(self, items):
        self.items = items
        self.selectedIndex = 0
   
    def on_key_press(self, symbol, modifiers):
        if symbol == key.DOWN:
            if self.selectedIndex < len(self.items) - 1:
                self.selectedIndex += 1 
                Game.soundPlayer.playSound('selection2.wav')
        elif symbol == key.UP:
            if self.selectedIndex > 0:
                self.selectedIndex -= 1
                Game.soundPlayer.playSound('selection2.wav')
        elif symbol == key.ENTER:
            self.items[self.selectedIndex][1]()            
            Game.soundPlayer.playSound('selection1.wav')
    
    def draw(self):
        self.window.clear()
        if self.backGround:
            self.backGround.draw()
                    
        i = 0
        for item in self.items:
            label = pyglet.text.Label(item[0],
                  font_size=(i == self.selectedIndex) and 35 or 30, color=(i == self.selectedIndex) and (255, 0, 0, 255) or (100, 100, 100, 255))
            label.x = self.x or (self.window.width - label.content_width) / 2
            label.y = self.y and (self.window.height - self.y) - i * 33 or self.window.height / 2 + (len(self.items) / 2. - i) * 33
            i += 1        
            label.draw()
            
class MainLoop(pyglet.window.Window):
    def __init__(self, width, height, **argv):
        config = Config(sample_buffers=1, samples=4, 
                    depth_size=16, double_buffer=True)
        try:
            super(MainLoop, self).__init__(width, height, config=config, **argv)
        except pyglet.window.NoSuchConfigException:
            super(MainLoop, self).__init__(width, height, **argv)
        
        self.currentLayer = None
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.update = None
#        PygletMainLoop.mainloop = self
        
    def loop(self):
        pyglet.app.run()

    def setLayer(self, layer):
        print 'set layer'
        if self.currentLayer:
            self.currentLayer.onExit()
        self.currentLayer = layer
        
        if hasattr(self.currentLayer, 'draw'):
            self.on_draw = self.currentLayer.draw
        
        for handler in ['on_key_press', 'on_mouse_motion', 'on_mouse_press' ]:
            if hasattr(self.currentLayer, handler):
                setattr(self, handler, getattr(self.currentLayer, handler))
            else:
                setattr(self, handler, lambda * arg: None)

        self.currentLayer.onStart()
                
    def update(self, dt):
        print 'update in mainloop'
    
    def quit(self):  
        sys.exit()     
    
    def executeAfter(self, func, sec):
        pyglet.clock.schedule_once(func, sec)
        
class SoundPlayer:
    sounds = {}
    currentBg=None
    player=None
    @staticmethod
    def loadSound(file, volume=0.5):
        if file in SoundPlayer.sounds:
            sound = SoundPlayer.sound[file]
        else:
            sound = pyglet.media.load(Game.getResource(file))
            sound.volume = volume
        return sound

    @staticmethod
    def playSound(file, volume=0.5):
        sound=SoundPlayer.loadSound(file, volume)
        sound.play()
    
    @staticmethod    
    def playBg(file, volume=0.5):
        if SoundPlayer.player:
            SoundPlayer.player.stop()
        SoundPlayer.player =pyglet.media.ManagedSoundPlayer()
        SoundPlayer.player.queue(SoundPlayer.loadSound(file, volume))
        SoundPlayer.player.play()
        
    @staticmethod
    def stopBg():
        if SoundPlayer.player:
            SoundPlayer.player.stop()

    @staticmethod
    def restartBg():
        SoundPlayer.bgPlayer.seek(SoundPlayer.startTime)
        SoundPlayer.bgPlayer.play()

        
        
class Renderer:
    batch=None
    radiusCache = {}
    imageCache = {}

    @staticmethod            
    def drawSegment((x1,y1), (x2,y2), color):
        Renderer.batch.add(2, gl.GL_LINES, None,
            ('v2f', (x1,y1,x2,y2)),
            ('c3f', color*2))             
             
    @staticmethod            
    def drawCircle(x,y,radius, color, shape=None):
        strokeWidth = 0
        if shape:
            color = shape.fillColor or (100, 100, 100)
            strokeWidth = (shape.strokeWidth is not 0) and max(1, int(shape.strokeWidth)) or 0
            strokeColor = shape.strokeColor or (100, 100, 100)
                    
        if not Renderer.radiusCache.has_key(radius):
            Renderer.radiusCache[radius] = Renderer._circle_vertices(radius)

        ll = []
        ll2 = []
        radiuses = Renderer.radiusCache[radius]
        
        for i in range(len(radiuses)-1):
            ll.extend((x, y))
            ll.extend((radiuses[i][0] + x, radiuses[i][1] + y))
            ll2.extend((radiuses[i][0] + x, radiuses[i][1] + y))

            ll.extend((radiuses[i + 1][0] + x, radiuses[i + 1][1] + y))
            ll2.extend((radiuses[i + 1][0] + x, radiuses[i + 1][1] + y))

        ll.extend((x, y))
        ll.extend((radiuses[-1][0] + x, radiuses[-1][1] + y))
        ll2.extend((radiuses[-1][0] + x, radiuses[-1][1] + y))

        ll.extend((radiuses[0][0] + x, radiuses[0][1] + y))
        ll2.extend((radiuses[0][0] + x, radiuses[0][1] + y))
        
        ll_count = len(ll) / 2
        ll_count2 = len(ll2) / 2
        
        Renderer.batch.add(ll_count, gl.GL_TRIANGLES, None,
            ('v2f', ll),
            ('c3B', color * (ll_count)))

        if strokeWidth > 0:
            gl.glLineWidth(strokeWidth)
            Renderer.batch.add(ll_count2, gl.GL_LINES, None,
                ('v2f', ll2),
                ('c3B', strokeColor * (ll_count2)))
            
  
    @staticmethod
    def drawPolygon(verts, color, shape=None):
          
        ll = []
        ll2 = []
        
        center =verts[0][0], verts[0][1]
        for i in range(len(verts)-1):
            ll.extend(center)
            
            p=verts[i][0], verts[i][1]
            ll.extend(p)
            ll2.extend(p)
            
            p=verts[i+1][0], verts[i+1][1]
            ll.extend(p)
            ll2.extend(p)

        ll.extend(center)
        
        p=verts[-1][0], verts[-1][1]
        ll.extend(p)
        ll2.extend(p)
            
        p=verts[0][0], verts[0][1]
        ll.extend(p)
        ll2.extend(p)

        ll_count = len(ll) / 2
        ll_count2 = len(ll2) / 2

        if shape:
            color = shape.fillColor or (100, 100, 100)

        Renderer.batch.add(ll_count, gl.GL_TRIANGLES, None,
               ('v2f', ll),
               ('c3B', color * (ll_count)))
        
        if shape and shape.stroke:
            strokeWidth = (shape.strokeWidth is not 0) and max(1, int(shape.strokeWidth)) or 0
            strokeColor = shape.strokeColor or (100, 100, 100)

            gl.glLineWidth(strokeWidth)
            Renderer.batch.add(ll_count2, gl.GL_LINES, None,
                ('v2f', ll2),
                ('c3B', strokeColor * (ll_count2)))
                    
    @staticmethod   
    def _circle_vertices(radius):
        POINTS = max(int(radius / 4 + 4), 20)
        step = 2 * math.pi / POINTS
        
        n = 0
        ret = []
        for i in range(0, POINTS):
            ret.append((math.cos(n) * radius, math.sin(n) * radius))
            n += step
#            ret.append((math.cos(n) * radius, math.sin(n) * radius))
        
        return ret   
    
    @staticmethod       
    def drawImage(x, y, angle, image):
        image.rotation = -math.degrees(angle)
        image.set_position(x, y)
        image.draw()
#        image.blit(x,y)
     
#    @staticmethod   
#    def loadImage2(file, size):
#        if file in Renderer.imageCache:
#            image = Renderer.imageCache[file]
#        else:
#            image = pyglet.image.load(Game.getResource(file))
#            Renderer.imageCache[file] = image
#
#        texture=pyglet.image.Texture.create(int(size[0]), int(size[1]))
#        texture.blit_to_texture(image,0,0,0)
#
#        sprite = pyglet.sprite.Sprite(texture)
#
#        return sprite
            
    @staticmethod   
    def loadImage(file, size=None, xCenterAnchor=True, yCenterAnchor=True, flip=None):
        if file in Renderer.imageCache:
            image = Renderer.imageCache[file]
        else:
            image = pyglet.image.load(Game.getResource(file))
            Renderer.imageCache[file] = image
        
        _image=image
#        if flip:
#            _image = _image.texture.get_transform(flip_x=True).get_region(0, 0, image.width, image.height)

        if size:
            _image= _image.get_texture()
            _image.width=int(size[0])
            _image.height=int(size[1])

        if xCenterAnchor:
            _image.anchor_x = _image.width / 2
        if yCenterAnchor:
            _image.anchor_y = _image.height / 2
        
#        image =image.get_texture()
#        if size:
#            image.width=size[0]
#            image.height=size[1]
        sprite = pyglet.sprite.Sprite(_image)
#        if size:
#            sprite.scale = float(size[0]) / image.width
#            _image=sprite.image.get_texture()
#            _image.width=int(size[0])
#            _image.height=int(size[1])
#            sprite.image=_image
#        
        return sprite

    @staticmethod   
    def _loadImage(file, size=None, centerAnchor=True, flip=None):
        if file in Renderer.imageCache:
            image = Renderer.imageCache[file]
        else:
            image = pyglet.image.load(Game.getResource(file))
            Renderer.imageCache[file] = image
            
        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2            
        return image.get_texture()
                          
