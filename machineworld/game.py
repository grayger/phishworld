import os
import ConfigParser

class Overlay(object):
    def doInLoop(self):
        pass 
    
    def onExit(self):
        pass
    
    def onStart(self):
        pass
    
class EventHandler:
    def __init__(self):
        self.items={}
    
    def register(self, name, handler):
        self.items.setdefault(name, []).append(handler)
    
    def onEvent(self, name):
        if name in self.items:
            for handler in self.items[name]:
                handler()  

class Game:
    WINDOW_HEIGHT = 600
    WINDOW_WIDTH = 800
    
    RESOURCE_PATH = None
                
    soundPlayer = None
    renderer = None
    eventHandler = EventHandler()
    
    @staticmethod
    def init(width=800, height=600, config=None):
        Game.WINDOW_WIDTH = width
        Game.WINDOW_HEIGHT = height
        if config:
            Game.readConfigFile(config)
    
    @staticmethod
    def readConfigFile(file):
        
        config = ConfigParser.ConfigParser()
        try:
            config.read(file)
            Game.RESOURCE_PATH = config.get('DEFAULT', 'resource')
        except:
#            Config.RESOURCE_PATH=None
            pass
            
    @staticmethod
    def getResource(filename):
        if Game.RESOURCE_PATH:
            return os.path.join(Game.RESOURCE_PATH, filename)
        else:
            raise ValueError('No resource path')
        
