import time
import pyglet
import numpy
import random
import math
import Box2D as box2d
from pyglet.gl import *
from pyglet.window import key
from game import *
from util import TimeIndex
from world import *
from pygletlib import Menu, MainLoop, SoundPlayer, Renderer

Game.soundPlayer= SoundPlayer
Game.renderer= Renderer

CHAR_BIT = 2
WALL_BIT = 4
BULLET_BIT = 8
BALLGEN_BIT = 16
PISTONBALL_BIT=32
LAUNCHER_BIT = 64
ROCKGEN_BIT=128
ROCK_BIT=BULLET_BIT


playerPos=box2d.b2Vec2(5,15)

class PhyObject(object):
    
    def __init__(self):
        self.visible=False
    
    def onCollide(self, body, result):
        pass

    def collidable(self, body):
        return body.userData and hasattr(body.userData, 'catBits') 
    
    def loadImage(self, file, size, xCenterAnchor=True, yCenterAnchor=True, flip=None):
        return Game.renderer.loadImage(file, (size[0] * WorldConfig.WINDOW_PER_WORLD, size[1] * WorldConfig.WINDOW_PER_WORLD), xCenterAnchor, yCenterAnchor, flip)
    
    def drawCircle(self, body, color, shape=None):
        Game.renderer.drawCircle(body.position.x*WorldConfig.WINDOW_PER_WORLD, body.position.y*WorldConfig.WINDOW_PER_WORLD, body.shapeList[0].radius*WorldConfig.WINDOW_PER_WORLD, color, shape)
        
    def drawPolygon(self, body, color, shape=None):
        verts =[] 
        for x, y  in body.shapeList[0].asPolygon().getCoreVertices_tuple():
            v= body.GetWorldPoint(box2d.b2Vec2(x, y))
            verts.append((v.x*WorldConfig.WINDOW_PER_WORLD, v.y*WorldConfig.WINDOW_PER_WORLD))
                                
        Game.renderer.drawPolygon(verts, color, shape)
        
    def drawImage(self, body, image):
        Game.renderer.drawImage(body.GetWorldCenter().x*WorldConfig.WINDOW_PER_WORLD, body.GetWorldCenter().y*WorldConfig.WINDOW_PER_WORLD, body.angle, image)

    def drawSegment(self, p1, p2, color):
        Game.renderer.drawSegment( (p1.x*WorldConfig.WINDOW_PER_WORLD, p1.y*WorldConfig.WINDOW_PER_WORLD) , (p2.x*WorldConfig.WINDOW_PER_WORLD, p2.y*WorldConfig.WINDOW_PER_WORLD), color)            
  
    def onDraw(self):
        if  playerPos.x-30 <self.body.position.x <playerPos.x+30:
            self.draw()
            if self.visible==False:
                self.visible=True
                if hasattr(self, 'delay') and hasattr(self, '_update'):
                    pyglet.clock.schedule_interval(self._update, self.delay)
                
        else:
            if self.visible==True:
                self.visible=False
                if hasattr(self, 'delay') and hasattr(self, '_update'):
                    pyglet.clock.unschedule(self._update)
                    
    def kill(self):
#        if hasattr(self, 'body') and self.body:
        if self.body:
            WorldConfig.removeBody(self.typename, self.body)
        if hasattr(self, 'delay') and hasattr(self, '_update'):
            pyglet.clock.unschedule(self._update)                
            
class DynamicObject(PhyObject):
    def __init__(self, initPower=100, durability=0.5):
        super(DynamicObject, self).__init__()
        self.initPower=initPower
        self.power=initPower
        self.inv_durability=1.0/max(0.1,durability)
        self.healthImage= Game.renderer._loadImage('health4.png')
        self.touchTime=0
        
    def updatePower(self, p):
        self.power += p
        if self.power <= 0:
            self.kill()
            self.power = 0
        Game.soundPlayer.playSound('hit2.wav')
            
#    def kill(self):
#        if self.body:
#            WorldConfig.removeBody(self.typename, self.body)
        

    def drawHealth(self):
        w=40* self.power/self.initPower
        self.healthImage.width=max(1,w)
        self.healthImage.blit(self.body.position.x* WorldConfig.WINDOW_PER_WORLD, (self.body.position.y-0.2)* WorldConfig.WINDOW_PER_WORLD)     
                        
    def onCollide(self, body2, result):
        if self.collidable(body2) and body2.userData.catBits == CHAR_BIT:
            if time.time() - self.touchTime > 0.5:
#                print -result.normalImpulse / 3
#                self.updatePower(min(int(-result.normalImpulse*self.inv_durability), -10))
                self.updatePower(int(-result.normalImpulse*self.inv_durability))

                self.touchTime=time.time()

class Player(PhyObject):
    catBits=CHAR_BIT
    typename='players'
    def __init__(self, shape):
        super(Player, self).__init__()
        
        self.shape=shape
        self.bodies=[]
        self.load()
        self.power=100
        self.initPower=100
        self.touchTime=0
        self.healthImage= Game.renderer._loadImage('health4.png')        
        self.image = self.loadImage(self.shape.image, (2.0,1.0))
        WorldConfig.addObject(self.typename, self) 

    def load(self):
        sd1=box2d.b2PolygonDef()
#        sd1.SetAsBox(1,0.5)
            
        sd1.setVertices(self.shape.points)
        sd1.density = 2.0
        
        bd=box2d.b2BodyDef()
        bd.fixedRotation=True
#        bd.position = self.shape.center[0], self.shape.center[1]
        self.body = WorldConfig.world.CreateBody(bd)
        self.body.CreateShape(sd1)
        self.body.SetMassFromShapes()
        self.body.userData = self
#        self.bodies.append(self.body)
                
#        self.addPrismatic()
#        self.addRevolute()
        
    def shot(self):
#        self.forearm1.ApplyImpulse((80,0), self.forearm1.position)
        self.jarm1.SetMotorSpeed(100)
        angle= self.forearm1.GetAngle()-0.5*box2d.b2_pi    
        bd=box2d.b2BodyDef()
#        bd.position=self.forearm1.position.x+ 2*math.cos(angle), self.body.position.y+ 2*math.sin(angle)
        x, y =self.forearm1.shapeList[0].asPolygon().getCoreVertices_tuple()[0]
        bd.position= self.forearm1.GetWorldPoint(box2d.b2Vec2(x, y))
        
        sd=box2d.b2CircleDef()
        sd.radius=1
        sd.density=0.5
        sd.filter.categoryBits = Player.catBits        
        body=WorldConfig.world.CreateBody(bd)
        body.CreateShape(sd)
        body.SetMassFromShapes()

        body.ApplyImpulse( (500*math.cos(angle), 500*math.sin(angle) ), body.position)
            
    def up(self):
        if self.body.GetLinearVelocity().y <7:
            self.body.ApplyImpulse((0,7), self.body.position)
#        v=self.body.GetLinearVelocity()
#        self.body.SetLinearVelocity((v.x, 3))

    def down(self):
        if self.body.GetLinearVelocity().y >-7:
            self.body.ApplyImpulse((0,-7), self.body.position)
#        v=self.body.GetLinearVelocity()
#        self.body.SetLinearVelocity((v.x, -3))
    def left(self):
        if self.body.GetLinearVelocity().x >-7:
            self.body.ApplyImpulse((-7,0), self.body.position)
#        v=self.body.GetLinearVelocity()
#        self.body.SetLinearVelocity((-50, v.y))
    def right(self):
        if self.body.GetLinearVelocity().x <15:
            self.body.ApplyImpulse((7,0), self.body.position)
#        v=self.body.GetLinearVelocity()
#        self.body.SetLinearVelocity((50, v.y))

    def draw(self):
        self.drawImage(self.body, self.image)
        for body in self.bodies:
            self.drawPolygon(body, None, self.shape)
        self.drawHealth()

    def addPrismatic(self):
        sd1=box2d.b2CircleDef()
        sd1.radius = 2
        sd1.density = 2.0


        bd1=box2d.b2BodyDef()
        ppos= self.body.GetWorldCenter()
        
        bd1.position = (ppos.x+6, ppos.y)
        body_punch = WorldConfig.world.CreateBody(bd1)
        body_punch.CreateShape(sd1)
        body_punch.SetMassFromShapes()
        
        jointDef = box2d.b2PrismaticJointDef()
        jointDef.Initialize(self.body, body_punch,playerPos, (1.0,0.0))
        jointDef.lowerTranslation = 0.0
        jointDef.upperTranslation = 10
        jointDef.enableLimit      = True
        jointDef.motorSpeed       = 100.0
        jointDef.enableMotor      = True        
        WorldConfig.world.CreateJoint(jointDef).getAsType() 
        self.bodies.append(body_punch)

    def addRevolute(self):
        sd=box2d.b2PolygonDef()
        sd.SetAsBox(1, 0.2)
        sd.density = 2.0
        sd.filter.groupIndex=-2

        bd1=box2d.b2BodyDef()
        ppos= self.body.GetWorldCenter()
        bd1.position = (ppos.x-0.2, ppos.y+0.8)
        body_arm1 = WorldConfig.world.CreateBody(bd1)
        body_arm1.CreateShape(sd)
        body_arm1.SetMassFromShapes()
        
        jointDef1 = box2d.b2RevoluteJointDef()
        jointDef1.Initialize(self.body, body_arm1, (body_arm1.position.x-1, body_arm1.position.y))
#        jointDef1.collideConnected = True      
        jointDef1.lowerAngle    = 0.1 * box2d.b2_pi  # -90 degrees
        jointDef1.upperAngle    = 0.2 * box2d.b2_pi  #  45 degrees
        jointDef1.enableLimit   = True
#        jointDef1.maxMotorTorque= 100.0
        jointDef1.motorSpeed    = 0.0
        jointDef1.enableMotor   = True
        WorldConfig.world.CreateJoint(jointDef1).getAsType() 
        self.bodies.append(body_arm1)


        bd1.position = (body_arm1.position.x+2, body_arm1.position.y)
        body_arm2 = WorldConfig.world.CreateBody(bd1)
        body_arm2.CreateShape(sd)
        body_arm2.SetMassFromShapes()
        
        jointDef1.Initialize(body_arm1, body_arm2, (body_arm2.position.x-1, body_arm2.position.y))
#        jointDef1.collideConnected = True      
        jointDef1.lowerAngle    = -0.25 * box2d.b2_pi  # -90 degrees
        jointDef1.upperAngle    = -0.1 * box2d.b2_pi  #  45 degrees
        jointDef1.enableLimit   = True
#        jointDef1.maxMotorTorque= 1000.0
        jointDef1.motorSpeed    = 0.0
        jointDef1.enableMotor   = True
        WorldConfig.world.CreateJoint(jointDef1).getAsType() 
        self.bodies.append(body_arm2)
        
        bd1.position = (body_arm2.position.x+2, body_arm2.position.y)
        body_arm3 = WorldConfig.world.CreateBody(bd1)
        body_arm3.CreateShape(sd)
        body_arm3.SetMassFromShapes()
        
        jointDef1.Initialize(body_arm2, body_arm3, (body_arm3.position.x-1, body_arm3.position.y))
#        jointDef1.collideConnected = True      
        jointDef1.lowerAngle    = -0.25 * box2d.b2_pi  # -90 degrees
        jointDef1.upperAngle    = -0.1 * box2d.b2_pi  #  45 degrees
        jointDef1.enableLimit   = True
#        jointDef1.maxMotorTorque= 1000.0
        jointDef1.motorSpeed    = 0.0
        jointDef1.enableMotor   = True
        WorldConfig.world.CreateJoint(jointDef1).getAsType() 
        self.bodies.append(body_arm3)
        
    def onCollide(self, body2, result):
        if self.collidable(body2) and (body2.userData.catBits == BULLET_BIT or body2.userData.catBits == PISTONBALL_BIT):
            if time.time() - self.touchTime > 0.5:
                self.updatePower(min(int(-result.normalImpulse / 1.5), -10))
                self.touchTime=time.time()
            if body2.userData.catBits == BULLET_BIT:
#                WorldConfig.removeBody(body2.userData.typename, body2)
                body2.userData.kill()
            return True
        return False
    
    def updatePower(self, p):
        self.power += p
        if self.power <= 0:
            self.kill()
            self.power = 0
        Game.soundPlayer.playSound('hit1.wav')
            
            
    def kill(self):
        Game.eventHandler.onEvent('PlayerKilled')  
        
    def update(self, dt):
        global playerPos
        playerPos=self.body.GetWorldCenter()

    def drawHealth(self):
        w=40* self.power/self.initPower
        self.healthImage.width=max(1,w)
        self.healthImage.blit(playerPos.x* WorldConfig.WINDOW_PER_WORLD, (playerPos.y-0.8)* WorldConfig.WINDOW_PER_WORLD)          


class BallGen(DynamicObject):
    catBits=BALLGEN_BIT
    
    typename='ballgens'
    def __init__(self, shape, delay=3):
        self.shape=shape
        super(BallGen, self).__init__(durability= float(shape.durability or 0.5))
        
        self.delay=float(shape.delay or delay)
        
        size= (2.0,4.0)
        self.image = self.loadImage(self.shape.image, size)
        self.load(size)
        WorldConfig.addObject(self.typename, self) 
        
    def load(self, size):
        bd=box2d.b2BodyDef()
        bd.position=self.shape.center[0], self.shape.center[1]

        sd=box2d.b2PolygonDef()
        sd.SetAsBox(size[0]/2.0, size[1]/2.0)
        sd.filter.categoryBits= BallGen.catBits
        self.body=WorldConfig.world.CreateBody(bd)
        self.body.CreateShape(sd)
        self.body.SetMassFromShapes()
        self.body.userData = self

        sd.density=2.0
        sd.SetAsBox(0.1, 1.8)
        bd.isBullet=True
        bd.position=self.body.position.x+1, self.body.position.y+4
        body_bar=WorldConfig.world.CreateBody(bd)
        body_bar.CreateShape(sd)
        body_bar.SetMassFromShapes()
                
        jd= box2d.b2RevoluteJointDef()
        jd.Initialize(self.body, body_bar, (self.body.position.x+1, self.body.position.y+size[1]/2.0))
        jd.maxMotorTorque= 30000.0
        jd.motorSpeed    = 2* box2d.b2_pi
        jd.enableMotor   = True        
        WorldConfig.world.CreateJoint(jd).getAsType()
        
        self.body_bar=body_bar
        
    def draw(self):
        self.drawImage(self.body, self.image)
        self.drawPolygon(self.body_bar, None, self.shape)
        self.drawHealth()

    def _update(self, dt):
        rnd=random.random()
        Bullet((self.body.position.x+rnd*2, self.body.position.y+2.2+rnd*3))
        Game.soundPlayer.playSound('ballgen1.wav')


    def kill(self):
        anim=Anim('man2.png', self.body.position, playerPos, 15)
        MachineWorldMainLayer.instance.addAnim(anim)
        MachineWorldMainLayer.main.foundEnemyCnt+=1
        
        super(BallGen, self).kill()
        if self.body_bar:
            WorldConfig.removeBody2(self.body_bar)

class RockGen(PhyObject):
    catBits=ROCKGEN_BIT
    typename='rockgens'
    def __init__(self, shape, delay=1):
        self.shape=shape

        super(RockGen, self).__init__()
        self.delay=float(shape.delay or delay)
        self.load()
        WorldConfig.addObject(self.typename, self) 
        
    def load(self):
        bd=box2d.b2BodyDef()
        bd.position=self.shape.center[0], self.shape.center[1]

        sd=box2d.b2PolygonDef()
        sd.SetAsBox(self.shape.width / 2, self.shape.height / 2)
        sd.filter.categoryBits= RockGen.catBits
        self.body=WorldConfig.world.CreateBody(bd)
        self.body.CreateShape(sd)
        self.body.userData = self
      
    def draw(self):
        self.drawPolygon(self.body, None, self.shape)

    def _update(self, dt):
        max_x=self.body.position.x+self.shape.width/2
        if self.body.position.x-self.shape.width/2 < playerPos.x <max_x :
            rnd=random.random()
            rnd2=random.random()
            rock=Rock((min(playerPos.x+rnd*3, max_x), self.body.position.y-1),(rnd*0.5+0.5, rnd2*1+0.5) )
            rock.body.ApplyImpulse( (0,-50), rock.body.position)

class Rock(PhyObject):
    
    catBits = ROCK_BIT
    typename='rocks'
    def __init__(self, position, size=(0.5,1)):
        super(Rock,self).__init__()
        
        self.body=None
        self.shapeDef=None

#        self.image = Game.renderer.loadImage2('rock1.png', size)
        
        self.load(position, size)
        WorldConfig.addObject(self.typename, self) 

    def load(self, position, size):
        bodyDef = box2d.b2BodyDef()
        bodyDef.position =position
        bodyDef.isBullet = True
                
        body = WorldConfig.world.CreateBody(bodyDef)
        body.CreateShape(self.getShapeDef(size))
        body.SetMassFromShapes()
        
        body.userData = self
        self.body=body
            
    def getShapeDef(self, size):
        if self.shapeDef == None:
            self.shapeDef = box2d.b2PolygonDef()
            self.shapeDef.SetAsBox(size[0]/2.0, size[1]/2.0)
            self.shapeDef.density = 5
            self.shapeDef.friction = 0.0
            self.shapeDef.restitution = 0.5
            self.shapeDef.filter.categoryBits = Rock.catBits
                    
        return self.shapeDef  
            
    def draw(self):
        self.drawPolygon(self.body, (255, 255, 255))
#        self.drawImage(self.body, self.image)
      
    def onCollide(self, body2, p):
        if self.collidable(body2) and (body2.userData.catBits == WALL_BIT):
            WorldConfig.removeBody(self.typename, self.body)
            return True
        return False

class Launcher(DynamicObject):
    catBits=LAUNCHER_BIT
    typename='launchers'
    def __init__(self, shape, delay=1):
        self.shape=shape
        super(Launcher, self).__init__(durability= float(shape.durability or 0.5))
        self.delay=float(shape.delay or delay)
        self.fireDelay=self.delay*4
        self.fireCounter=0
        size=(2,1)
        self.image = self.loadImage(self.shape.image, size)
        self.weaponImage = self.loadImage('lbar2.png', size, yCenterAnchor=True, xCenterAnchor=False)
        self.load(size)
        self.angle=90 # degree
        WorldConfig.addObject(self.typename, self) 
        
    def load(self, size):
        bd=box2d.b2BodyDef()
        bd.position=self.shape.center[0], self.shape.center[1]

        sd=box2d.b2PolygonDef()
        sd.SetAsBox(size[0]/2.0, size[1]/2.0)
        sd.filter.categoryBits= Launcher.catBits
        self.body=WorldConfig.world.CreateBody(bd)
        self.body.CreateShape(sd)
        self.body.SetMassFromShapes()
        self.body.userData = self
        
    def draw(self):
        self.drawImage(self.body, self.image)

        self.weaponImage.rotation = -self.angle
        self.weaponImage.set_position(self.body.GetWorldCenter().x * WorldConfig.WINDOW_PER_WORLD , self.body.GetWorldCenter().y * WorldConfig.WINDOW_PER_WORLD)
        self.weaponImage.draw() 
        
        self.drawHealth()
        
    def _update(self, dt):
        vec=(playerPos-self.body.position)            
        self.angle=math.degrees(math.atan2(vec.y, vec.x))
        self.fireCounter+=1
        if self.fireCounter%5==0:
            vec.Normalize()
            ms=Missile((self.body.position.x+vec.x*2, self.body.position.y+vec.y*2))
            ms.body.ApplyImpulse((100 *vec), ms.body.position)

    def kill(self):
        anim=Anim('man2.png', self.body.position, playerPos, 15)
        MachineWorldMainLayer.instance.addAnim(anim)
        MachineWorldMainLayer.main.foundEnemyCnt+=1
        
        super(Launcher, self).kill()

class Missile(PhyObject):
    
    catBits = BULLET_BIT
    typename='missiles'
    def __init__(self, position, delay=1, radius=0.5):
        super(Missile,self).__init__()
        
        self.shapeDef = None
        self.body=None
        self.delay=delay
        ## override
        self.radius = radius
        self.image = self.loadImage('missile1.png', (radius*2, radius*2))
        
        self.load(position)
        WorldConfig.addObject(self.typename, self) 

    def load(self, position):
        bodyDef = box2d.b2BodyDef()
        bodyDef.position =position
        bodyDef.isBullet = True
                
        body = WorldConfig.world.CreateBody(bodyDef)
        body.CreateShape(self.getShapeDef())
        body.SetMassFromShapes()
        
        body.userData = self
        self.body=body
            
    def getShapeDef(self):
        if self.shapeDef == None:
            self.shapeDef = box2d.b2CircleDef()
            self.shapeDef.radius = self.radius
            self.shapeDef.density = 5
            self.shapeDef.friction = 0.0
            self.shapeDef.restitution = 0.5
            self.shapeDef.filter.categoryBits = Missile.catBits
                    
        return self.shapeDef  
            
    def draw(self):
#        self.drawCircle(self.body, (255, 255, 255))
        self.drawImage(self.body, self.image)
      
    def onCollide(self, body2, p):
        if self.collidable(body2) and (body2.userData.catBits is not CHAR_BIT):
            WorldConfig.removeBody(self.typename, self.body)
#            self.kill()
            Game.soundPlayer.playSound('explode1.wav')
            return True
        return False
    
    def _update(self, dt):
        vec=(playerPos-self.body.position)
        vec.Normalize()
        self.body.SetLinearVelocity(5*vec)

#    def kill(self):
##        super(Missile, self).kill()
#            return True

class Bullet(PhyObject):
    
    catBits = BULLET_BIT
    typename='bullets'
    def __init__(self, position, radius=0.1, color=(255, 0, 100)):
        super(Bullet,self).__init__()
        
        self.shapeDef = None
        self.body=None
        ## override
        self.radius = radius
        self.color = color
        
        self.load(position)
        WorldConfig.addObject(self.typename, self) 

    def load(self, position):
        bodyDef = box2d.b2BodyDef()
        bodyDef.position =position
        bodyDef.isBullet = True
                
        body = WorldConfig.world.CreateBody(bodyDef)
        body.CreateShape(self.getShapeDef())
        body.SetMassFromShapes()
        body.userData = self
        self.body=body
            
    def getShapeDef(self):
        if self.shapeDef == None:
            self.shapeDef = box2d.b2CircleDef()
            self.shapeDef.radius = self.radius
            self.shapeDef.density = 1
            self.shapeDef.friction = 0.0
            self.shapeDef.restitution = 0.5
            self.shapeDef.filter.categoryBits = Bullet.catBits
                    
        return self.shapeDef  
            
    def draw(self):
        self.drawCircle(self.body, (255, 255, 255))
      
    def onCollide(self, body2, p):
        if self.collidable(body2) and (body2.userData.catBits == WALL_BIT):
            WorldConfig.removeBody(self.typename, self.body)
            return True
        return False

class PistonBall(PhyObject):
    
    catBits =PISTONBALL_BIT
    typename='pistonballs'
    def __init__(self, parent, angle, radius=1, length=3, color=(255, 0, 100)):
        super(PistonBall,self).__init__()
        
        self.shapeDef = None
        self.body=None
        ## override
        self.radius = radius
        self.color = color
        
        self.parent=parent
        self.joint=None
        self.image = self.loadImage('gear1.png', (radius*2, radius*2))
        self.load(angle, radius, length)
        WorldConfig.addObject(self.typename, self) 

    def load(self, angle, radius, length):
        _x, _y=length*math.cos(angle),length*math.sin(angle)
        position= self.parent.body.position.x+_x, self.parent.body.position.y+_y
        bd=box2d.b2BodyDef()
        bd.fixedRotation=False
        bd.position=position
        
        sd=box2d.b2CircleDef()
        sd.radius=radius
        sd.density=1.0
        sd.filter.categoryBits= PistonBall.catBits
      
        self.body=WorldConfig.world.CreateBody(bd)
        self.body.CreateShape(sd)
        self.body.SetMassFromShapes()
        self.body.userData=self
            
        pjd=box2d.b2PrismaticJointDef() 
        pjd.Initialize(self.parent.body, self.body, self.parent.body.position, (math.cos(angle), math.sin(angle)))
        pjd.motorSpeed = 30.0
        pjd.maxMotorForce = 1000.0
        pjd.enableMotor = True
        pjd.lowerTranslation = 0.0
        pjd.upperTranslation = 10.0
        pjd.enableLimit = True
        
        self.joint=WorldConfig.world.CreateJoint(pjd).getAsType()
                        
    def change(self):
        self.body.WakeUp()
        self.joint.motorSpeed*=-1
        
    def draw(self):
        self.drawImage(self.body,self.image)
               
#    def onCollide(self, body2, p):
#        if self.collidable(body2) and (body2.userData.catBits == WALL_BIT or body2.userData.catBits== CHAR_BIT):
#            WorldConfig.removeBody('bullets', self.body)
#            return True
#        return False


class Piston(DynamicObject):
    typename='pistons'
    def __init__(self, shape, angle=0, num=6, length=3, delay=1 ):
        self.shape=shape
        super(Piston, self).__init__(durability= float(shape.durability or 0.5))
        self.legs=[]
        self.joints=[]
#        self.delay=delay
        self.delay=float( shape.delay or delay)
        
        self.body=None
        self.image = self.loadImage(self.shape.image, (self.shape.width, self.shape.height))
        self.load(angle, int( shape.ext1 or num), length)
        WorldConfig.addObject(self.typename, self)           
        self.idx=0      
        
    def load(self, angle, num, length):
        bd=box2d.b2BodyDef()
        bd.fixedRotation=True
        pos=self.shape.center[0], self.shape.center[1]
        bd.position=pos
        
        sd=box2d.b2CircleDef()
        sd.radius=self.shape.width/2.0
        sd.density=1.0
      
        self.body=WorldConfig.world.CreateBody(bd)
        self.body.CreateShape(sd)
        self.body.userData=self
        
        for i in range(0, num):
            pb=PistonBall(self, angle=angle, length=length)
            self.legs.append(pb)
            angle+=2*box2d.b2_pi/num
            
    def draw(self):
        for leg in self.legs:
            self.drawSegment(self.body.position, leg.body.position, (100,100,100))  
        
        self.drawImage(self.body, self.image)
        self.drawHealth()
        
            
    def _update(self, dt):
        lst= random.sample(xrange(0, len(self.legs)), random.randrange(0,len(self.legs)))
        for idx in lst:
            self.legs[idx].change()
            
    def kill(self):
        anim=Anim('man2.png', self.body.position, playerPos, 15)
        MachineWorldMainLayer.instance.addAnim(anim)
        MachineWorldMainLayer.main.foundEnemyCnt+=1
        
        super(Piston, self).kill()        

class Wall(PhyObject):

    catBits = WALL_BIT
#    maskBits = CHAR_BIT | BUBBLE_BIT | BULLET_BIT
    typename='walls'
    def __init__(self, shape):
        super(Wall, self).__init__()
        self.shape = shape
        self.body = None

        self.load()
        WorldConfig.addObject(self.typename, self) 
    
    def load(self):
        bodyDef = box2d.b2BodyDef()

        if self.shape.type == WorldConfig.BOX:
            bodyDef.position = self.shape.center[0], self.shape.center[1]
            body = WorldConfig.world.CreateBody(bodyDef)
            
            shapeDef = box2d.b2PolygonDef()
            shapeDef.SetAsBox(self.shape.width / 2, self.shape.height / 2)            
        elif self.shape.type == WorldConfig.POLYGON:
            body = WorldConfig.world.CreateBody(bodyDef)
            
            shapeDef = box2d.b2PolygonDef()
            shapeDef.setVertices(self.shape.points)
        elif self.shape.type == WorldConfig.CIRCLE:
            bodyDef.position = self.shape.x, self.shape.y
            body = WorldConfig.world.CreateBody(bodyDef)
            
            shapeDef = box2d.b2CircleDef()
            shapeDef.radius = self.shape.radius
        else:
            raise 'unknown shape'
            return 
                         
#        shapeDef.density = 1
#        shapeDef.friction = 0.1
#        shapeDef.restitution = 1.0
        shapeDef.filter.categoryBits = Wall.catBits
#        shapeDef.filter.maskBits = Wall.maskBits
        body.CreateShape(shapeDef)
        body.SetMassFromShapes()
        body.userData = self
        self.body = body
       
#    def update(self, dt):

    def onDraw(self):
        self.drawPolygon(self.body, None, self.shape)

class Pause(Overlay):
    def __init__(self):
        super(Pause, self).__init__()
        
    def draw(self):
        text = pyglet.text.Label("Paused",
              font_size=20, color=(255, 255, 255, 255))
        text.x = (Game.WINDOW_WIDTH - text.content_width) / 2
        text.y = (Game.WINDOW_HEIGHT + text.content_height) / 2
        text.draw()
        
    def on_key_press(self, symbol, modifiers):
        if symbol == key.P:
            MachineWorldMainLoop.instance.setLayer(MachineWorldMainLayer.instance)


class Anim:
    def __init__(self, image, startPos, endPos, tics):
        self.image=Game.renderer.loadImage(image)
        self.startPos=startPos
        self.endPos=endPos
        self.tics=tics # tic
        self.currentTic=0
        self.dPos=(endPos-startPos)/float(tics)

class MachineWorldMainLayer(Overlay):
    main = None
    instance = None
    def __init__(self, main):
        super(MachineWorldMainLayer, self).__init__()
        MachineWorldMainLayer.main = main
        self.text = None
        MachineWorldMainLayer.instance = self
        self.fps_display = pyglet.clock.ClockDisplay()
#        self.healthImage= pyglet.image.load(Game.getResource('health4.png')).get_texture()
#        self.healthImageWidth= self.healthImage.width
        self.anims=[]

    def checkTime(self, dt):
        
        t= MachineWorldMainLayer.main.countDown
        if t>0:
            MachineWorldMainLayer.main.countDown=t-1
            if t== 10:
                self.setText('Hurry Up!!!')
                MachineWorldMainLoop.instance.executeAfter(lambda dt=0: self.setText(None), 2)
        else:   
            Game.eventHandler.onEvent('TimeOver')  

    def addAnim(self, anim):
        self.anims.append(anim)

    def drawAnimations(self):
        for anim in list(self.anims):
            anim.currentTic+=1
            pos= anim.startPos+ anim.dPos*anim.currentTic
            anim.image.set_position(pos.x*WorldConfig.WINDOW_PER_WORLD, pos.y*WorldConfig.WINDOW_PER_WORLD)
            anim.image.draw()
            if anim.currentTic> anim.tics:
                self.anims.remove(anim)
        
    def onStart(self):
        pyglet.clock.schedule_interval(self.update, 1.0 / 30.0)
#        cursor = pyglet.window.ImageMouseCursor(pyglet.image.load(Game.getResource('cursor.png')), 8, 8)
#        MachineWorldMainLoop.instance.set_mouse_cursor(cursor)
        pyglet.clock.schedule_interval(self.checkTime, 1)
    
    def onExit(self):
        pyglet.clock.unschedule(self.update) 
        pyglet.clock.unschedule(self.checkTime)        

    def setText(self, text):
        self.text = text

    def checkKeys(self):
        keys = MachineWorldMainLoop.instance.keys
        if keys[pyglet.window.key.LEFT]:
            MachineWorldMainLayer.main.player.left()
        elif keys[pyglet.window.key.RIGHT]:
            MachineWorldMainLayer.main.player.right()    
        elif keys[pyglet.window.key.UP]:
            MachineWorldMainLayer.main.player.up()
        elif keys[pyglet.window.key.DOWN]:
            MachineWorldMainLayer.main.player.down()
#        elif keys[pyglet.window.key.P]:
#            MachineWorldMainLoop.instance.setLayer(Pause())
#        elif keys[pyglet.window.key.F]:
#            MachineWorldMainLoop.instance.set_fullscreen(not MachineWorldMainLoop.instance.fullscreen)

    def update(self, dt):
        self.checkKeys()            

        for obj in copy.copy(WorldConfig.updatables):
            obj.update(dt)

        WorldConfig.doCollision()
        WorldConfig.world.Step(dt, 10, 10)
#        MachineWorldMainLayer.main.elapse(dt)
        self.checkLines()
        
    def checkLines(self):
        if playerPos.x > WorldConfig.WORLD_WIDTH-20:
            Game.eventHandler.onEvent('FinishLineEntered')  


    def playerPosDelta(self):
#        pos=MachineWorldMainLayer.main.player.body.position
        
        x,y=playerPos.x*WorldConfig.WINDOW_PER_WORLD, playerPos.y*WorldConfig.WINDOW_PER_WORLD
        dx= min(Game.WINDOW_WIDTH/2-x,0)
#        dy=Game.WINDOW_HEIGHT/2-y
        dy=0.0
        return dx,dy, 0.0 
 
    def draw(self):
        MachineWorldMainLoop.instance.clear()
#        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) ## which is better?
        Game.renderer.batch=pyglet.graphics.Batch()
        
        glPushMatrix()
        pos=self.playerPosDelta()
        glTranslatef(*pos)
        for x in filter(lambda x: x in WorldConfig.objects, ['walls', 'players', 'ballgens', 'rockgens', 'launchers', 'pistons','pistonballs', 'bullets', 'missiles', 'rocks']):
            for obj in filter(lambda x: x, WorldConfig.objects[x]):
                obj.onDraw()  

        Renderer.batch.draw()
        self.drawAnimations()        

        glPopMatrix()
        
#        self.drawHealth()
        self.drawText()     
        self.fps_display.draw()

        
    def drawText(self):
        level = pyglet.text.Label("Level: %02d" % MachineWorldMainLayer.main.currentLevel,
                  font_size=20,
                  x=20, y=575)        
        level.draw()

        score = pyglet.text.Label("Aliens: %02d/%02d" % (MachineWorldMainLayer.main.foundEnemyCnt, MachineWorldMainLayer.main.enemyCnt),
                  font_size=20,
                  x=300, y=575)        
        score.draw()

        countDown = pyglet.text.Label("Time: %02d" % MachineWorldMainLayer.main.countDown,
                  font_size=20,
                  x=650, y=575)        
        countDown.draw()
                
        if self.text:
            text = pyglet.text.Label(self.text,
                  font_size=20,
                  x=Game.WINDOW_WIDTH / 2, y=Game.WINDOW_HEIGHT / 2,
                  anchor_x='center', anchor_y='center')
            text.draw()    
            
#    def drawHealth(self):
#        w= self.healthImageWidth* MachineWorldMainLayer.main.player.power/100
#        self.healthImage.width=max(1,w)
# 
#
#        batch=pyglet.graphics.Batch()
#        ll = []
#        ll.extend((Game.WINDOW_WIDTH - 120, Game.WINDOW_HEIGHT - 9))
#        ll.extend((Game.WINDOW_WIDTH - 120, Game.WINDOW_HEIGHT - 19))
#        ll.extend((Game.WINDOW_WIDTH - 20, Game.WINDOW_HEIGHT - 19))
#        ll.extend((Game.WINDOW_WIDTH - 20, Game.WINDOW_HEIGHT - 9))
#        ll_count = len(ll) / 2
#        batch.add(ll_count, gl.GL_POLYGON, None,
#            ('v2f', ll),
#            ('c3B', (255, 255, 255) * (ll_count)))  
#        batch.draw()      
#        self.healthImage.blit(Game.WINDOW_WIDTH - 120, Game.WINDOW_HEIGHT - 20)     
#    def drawScore(self):
#        ll = []
#        ll.extend((Game.WINDOW_WIDTH - 120, Game.WINDOW_HEIGHT - 20))
#        ll.extend((Game.WINDOW_WIDTH - 120, Game.WINDOW_HEIGHT - 35))
#        ll.extend((Game.WINDOW_WIDTH - 20, Game.WINDOW_HEIGHT - 35))
#        ll.extend((Game.WINDOW_WIDTH - 20, Game.WINDOW_HEIGHT - 20))
#        ll_count = len(ll) / 2
#        Renderer.batch.add(ll_count, gl.GL_POLYGON, None,
#            ('v2f', ll),
#            ('c3B', (100, 100, 100) * (ll_count)))
#        
#        
#        ll = []
#        ll.extend((Game.WINDOW_WIDTH - 120, Game.WINDOW_HEIGHT - 20))
#        ll.extend((Game.WINDOW_WIDTH - 120, Game.WINDOW_HEIGHT - 35))
#        ll.extend((Game.WINDOW_WIDTH - 120 + MachineWorldMainLayer.main.player.power, Game.WINDOW_HEIGHT - 35))
#        ll.extend((Game.WINDOW_WIDTH - 120 + MachineWorldMainLayer.main.player.power, Game.WINDOW_HEIGHT - 20))
#        ll_count = len(ll) / 2
#        Renderer.batch.add(ll_count, gl.GL_POLYGON, None,
#            ('v2f', ll),
#            ('c3B', (200, 0, 0) * (ll_count)))
                     
#    def on_mouse_motion(self, x, y, dx, dy):
#       MachineWorldMainLayer.main.player.onMouseMotion(x, y)
#
#    def on_mouse_press(self, x, y, button, modifiers):
#       MachineWorldMainLayer.main.player.onMousePress(x, y, button, modifiers)
       

class MachineWorldMenuBackground:
    def __init__(self):
        self.image = pyglet.image.load(Game.getResource('main.png'))
                
    def draw(self):
        self.image.blit(150, 150)

      
class MachineWorldMainLoop(MainLoop):
    instance = None
        
    def __init__(self):
        super(MachineWorldMainLoop, self).__init__(Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT, caption='MachineWorld')
        MachineWorldMainLoop.instance = self    
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 
        
        
        
