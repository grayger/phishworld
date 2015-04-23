'''
@author: grayger
'''

import os
import pyglet
import Box2D as box2d
from machineworld.game import Game
from machineworld.main import *
        
if __name__ == "__main__":       
#    Game.init(config=os.path.join(get_main_dir(),'MachineWorld.cfg'))
    Game.init()
    Game.RESOURCE_PATH= os.path.join(get_main_dir(),'resources_mw')

    main=Main()
    main.start()
