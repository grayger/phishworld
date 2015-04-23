import Box2D as box2d
import copy
from game import Game

class fwContactTypes:
    contactUnknown = 0
    contactAdded = 1
    contactPersisted = 2
    contactRemoved = 3
    contactResulted = 4

class fwContactPoint:
    shape1 = None
    shape2 = None
    normal = None
    position = None
    velocity = None
    id = box2d.b2ContactID()
    state = 0
    
class fwContactResult:
    shape1 = None
    shape2 = None
    normal = None
    position = None
    normalImpulse = None
    tangentImpulse = None
    id = box2d.b2ContactID()
    state = 0
        
class fwContactListener(box2d.b2ContactListener):
    test = None
    def __init__(self):
        super(fwContactListener, self).__init__()

    def handleCall(self, state, point):
        cp = fwContactPoint()
        cp.shape1 = point.shape1
        cp.shape2 = point.shape2
        cp.position = point.position.copy()
        cp.normal = point.normal.copy()
        cp.id = point.id
        cp.state = state
        WorldConfig.points.append(cp)

    def handleCall2(self, state, result):
        cp = fwContactPoint()
        cp.shape1 = result.shape1
        cp.shape2 = result.shape2
        cp.position = result.position.copy()
        cp.normal = result.normal.copy()
        cp.normalImpulse = result.normalImpulse
        cp.tangentImpulse = result.tangentImpulse
        cp.id = result.id
        cp.state = state
        WorldConfig.points.append(cp)


    def Add(self, point):
#        self.handleCall(fwContactTypes.contactAdded, point)
        pass

    def Persist(self, point):
        pass

    def Remove(self, point):
        pass
    
    def Result(self, result):
        self.handleCall2(fwContactTypes.contactResulted, result)
        
class WorldConfig:
    WINDOW_PER_WORLD = 20.0
    
#    gravity = (0, -10)
    gravity = (0, 0)
    doSleep = True
    objects = {}
    updatables = set()
    
    BOX = 1
    POLYGON = 2
    CIRCLE = 3
    
    points = []
    cleanCand = {} # objKey, set of body
    cleanCandList=[] # body
    
    WORLD_WIDTH=0
    WORLD_HEIGHT=0
            
    @staticmethod
    def init(width=Game.WINDOW_WIDTH, height=Game.WINDOW_HEIGHT, window_per_world=20.0):

        WorldConfig.WINDOW_PER_WORLD = window_per_world

        worldAABB = box2d.b2AABB()
        worldAABB.lowerBound.Set(0, 0)
        WorldConfig.WORLD_WIDTH= width / window_per_world
        WorldConfig.WORLD_HEIGHT=height/ window_per_world
        
        worldAABB.upperBound.Set(WorldConfig.WORLD_WIDTH, WorldConfig.WORLD_HEIGHT)
        WorldConfig.world = box2d.b2World(worldAABB, WorldConfig.gravity, WorldConfig.doSleep)
        WorldConfig.contactListener = fwContactListener()
        WorldConfig.world.SetContactListener(WorldConfig.contactListener)
        
                
    @staticmethod        
    def windowToWorld(x, y):
        return x / WorldConfig.WINDOW_PER_WORLD, y / WorldConfig.WINDOW_PER_WORLD

    @staticmethod   
    def addObject(key, obj):
        WorldConfig.objects.setdefault(key, []).append(obj)
        if hasattr(obj, 'update') and callable(obj.update):
            WorldConfig.updatables.add(obj)     
    
    @staticmethod   
    def removeObject(key, obj):
        if key in WorldConfig.objects:
            if obj in WorldConfig.objects[key]:
                if obj in copy.copy(WorldConfig.updatables):
                    WorldConfig.updatables.remove(obj)
                WorldConfig.world.DestroyBody(obj.body)
                WorldConfig.objects[key].remove(obj)
                del obj
            else:
                print '%s not found' % obj
                raise Exception
    
    @staticmethod 
    def removeBody(key, body):
        WorldConfig.cleanCand.setdefault(key, []).append(body)

    @staticmethod 
    def removeBody2(body):
        WorldConfig.cleanCandList.append(body)
    
    @staticmethod
    def removeBodyNow(body):
        if body:
            WorldConfig.world.DestroyBody(body)
    
#    @staticmethod         
#    def doCollision():
#        for point in WorldConfig.points:
#            body1, body2 = point.shape1.GetBody(), point.shape2.GetBody()
#            if not (body1.userData and body1.userData.onCollide(body2, point)):
#                body2.userData and body2.userData.onCollide(body1, point)
#                  
#        clearCheck = False        
#        for key, v in WorldConfig.cleanCand.items():
#            for body in set(v):
#                try:
#                    WorldConfig.removeObject(key, body.userData)
#                except:
#                    print 'error in delete %s' % body
#                clearCheck = True
#                
#        if clearCheck:
#            Game.eventHandler.onEvent('ObjectCleaned')
#        
#        WorldConfig.cleanCand.clear()
#        WorldConfig.points = []            

    @staticmethod         
    def doCollision():
        for point in WorldConfig.points:
            body1, body2 = point.shape1.GetBody(), point.shape2.GetBody()
            if not (body1.userData and hasattr(body1.userData, 'onCollide') and body1.userData.onCollide(body2, point)):
                body2.userData and hasattr(body2.userData, 'onCollide') and body2.userData.onCollide(body1, point)
                  
        for key, v in WorldConfig.cleanCand.items():
            for body in set(v):
                try:
                    WorldConfig.removeObject(key, body.userData)
                except:
                    print 'error in delete %s' % body
                    
        for body in WorldConfig.cleanCandList:
            WorldConfig.removeBodyNow(body)
        
        WorldConfig.cleanCand.clear()
        WorldConfig.cleanCandList=[]
        WorldConfig.points = [] 