'''
@author: machineworld
'''

import os, sys, imp
import time
from game import Game
from world import WorldConfig
from util import *
from parser import *
from objects import *

levels={}
levels[1] = dict(countDown=300, message='Use Arrow keys to move and attack.')
levels[2] = dict(countDown=400, message='Good luck.')
levels[3] = dict(countDown=500, message='Maybe, it is the last level.')
  
class Main:
    def __init__(self):
        self.mainLoop=None
        self.mainLayer=None
        self.player=None
        self.level=None
        self.playMode=None
        self.countDown=0
        self.enemyCnt=0
        self.foundEnemyCnt=0
        self.alarmTime=0
        self.currentLevel=0
        
    def setLevel(self, levelNo, isRestart=False):
#        print 'level %d' % levelNo
        self.playMode = True
        self.mainLayer.setText(None)
        
        self.currentLevel = levelNo
        if not self.loadLevel(levelNo=self.currentLevel, isRestart=isRestart):
            print 'invalid level'

#        Game.soundPlayer.playBg('Netherworld_Shanty.ogg')
        
    def start(self):
        self.mainLoop= MachineWorldMainLoop()
        self.mainLayer=MachineWorldMainLayer(main=self)
        self.menu = Menu(window=self.mainLoop, y=500, backGround=MachineWorldMenuBackground())
        self.menu.setMenuItems([('Start', self.startMainLayer),  ('Quit', lambda: self.mainLoop.quit())])
        self.mainLoop.setLayer(self.menu)
        self.registerEvents()
        self.loadSounds()
        self.mainLoop.loop()
        
    def showOptions(self):
        pass
    
    def registerEvents(self):
        Game.eventHandler.register('PlayerKilled', self.gameover)
        Game.eventHandler.register('FinishLineEntered', self.checkClear)
        Game.eventHandler.register('TimeOver', lambda: self.gameover('Time Over'))
        
    def gameover(self, text='Game Over'):
        if self.playMode == False:
#            print 'playMode off'
            return
                
        self.mainLayer.setText(text)
        self.playMode = False
        self.mainLoop.executeAfter(lambda dt=0: self.switchToMenu(), 2)
        
#        self.clean()

    def checkClear(self):
        if self.playMode == False:
            return
        if self.foundEnemyCnt== self.enemyCnt:   
            self.clearLevel()
        else:
            if time.time()-self.alarmTime> 10:
                self.mainLayer.setText('Missed living things. Go back!!!')
                self.mainLoop.executeAfter(lambda dt=0: self.mainLayer.setText(None), 2)
                self.alarmTime=time.time()
    def clearLevel(self):
        if self.playMode == False:
#            print 'playMode off'
            return
        
        level = self.currentLevel + 1
        if level > len(levels):
            self.mainLayer.setText('All Levels Cleared')
            self.playMode = False            
            self.mainLoop.executeAfter(lambda dt=0: self.clearGame(), 2)
        else:
            self.mainLayer.setText('Level %d Cleared' % self.currentLevel)
            self.playMode = False
            self.mainLoop.executeAfter(lambda dt=0: self.setLevel(level), 2)
        
#        self.clean()

    def clearGame(self):
#        print 'game cleared'
        self.currentLevel = 1
        self.switchToMenu()

    def switchToMenu(self):
#        print 'switch'
        
        self.mainLoop.setLayer(self.menu)
        self.menu.setMenuItems([('Restart', self.restart),  ('Quit', lambda: self.mainLoop.quit())])
        self.mainLayer.setText(None)        

    def restart(self):
        self.setLevel(self.currentLevel, isRestart=True)
        self.mainLoop.setLayer(self.mainLayer)
        
    def startMainLayer(self):
        self.setLevel(1)
        self.mainLoop.setLayer(self.mainLayer)
                
    def loadLevel(self, levelNo, isRestart=False):
        
        _file = 'map' + str(levelNo) + '.svg'
        parser = SvgParser(Game.getResource(_file))
        parser.parse()
        w,h=parser.width, parser.height
 
        if isRestart or levelNo>1:
            self.clean()
#            pass
        else:
            WorldConfig.init(width=w, height=h)
            
        self.mainLayer.setText(levels[levelNo]['message'])
        self.mainLoop.executeAfter(lambda dt=0: self.mainLayer.setText(None), 2)
            
        self.enemyCnt=0
        self.foundEnemyCnt=0  
        self.countDown=levels[levelNo]['countDown']     
        
        for shape in parser.shape_list:    
            if shape.role=='player':
                self.player=Player(shape)
            elif shape.role=='ballgen':
                BallGen(shape, delay=max(1, 3-(0.5*levelNo)))
                self.enemyCnt+=1         
            elif shape.role=='launcher':
                Launcher(shape, delay=max(1, 2-(0.3*levelNo)))   
                self.enemyCnt+=1
            elif shape.role=='piston':
                Piston(shape, num=3+random.randrange(0, 4), delay=max(0.5, 2-(0.3*levelNo)))
                self.enemyCnt+=1
            elif shape.role=='rockgen':
                RockGen(shape)    
            else:
                Wall(shape)
                
#        Game.soundPlayer.playSound('32953__HardPCM__Chip053.ogg')

            
        return True     
    
    def loadSounds(self):
        Game.soundPlayer.loadSound('explode1.wav')
        Game.soundPlayer.loadSound('hit1.wav')
        Game.soundPlayer.loadSound('hit2.wav')
        Game.soundPlayer.loadSound('ballgen1.wav')
    
    def clean(self):
        for objKey in WorldConfig.objects.keys():
            if objKey in WorldConfig.objects:
                for obj in copy.copy(WorldConfig.objects[objKey]):
                    WorldConfig.removeObject(objKey, obj)
                    if hasattr(obj, 'delay') and hasattr(obj, '_update'):
                        pyglet.clock.unschedule(obj._update) 
                WorldConfig.objects[objKey] = []
        
        bodies =WorldConfig.world.GetBodyList()
        joints= WorldConfig.world.GetJointList()
        for joint in list(joints):
            WorldConfig.world.DestroyJoint(joint)
        for body in list(bodies):
            WorldConfig.world.DestroyBody(body)

#        WorldConfig.world=None
#        for k in WorldConfig.objects.keys():
#            objs = WorldConfig.objects[k]
#            for obj in list(objs):
##                obj=None
#
#                print 'del', obj
#                del obj                
#            objs=[]
        WorldConfig.objects={}

