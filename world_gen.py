import string, struct, random, copy, sys
import pygame


class Block:
    def __init__(self, x, y, material):
        self.x = x
        self.y = y
        self.material = material
        #self.compact = struct.pack('<hhB',x,y,material)

class World:

    def __init__(self, x, y, seed):
        self.x = x
        self.y = y
        self.seed = seed
        self.blocks = [[[]]*y for i in xrange(x)]

    def seed_dirt(self):
        fill_factor = .4

        random.seed(self.seed)
        
        for i in xrange(self.x):
            for j in xrange(self.y):
                if(random.random()<fill_factor):
                    self.blocks[i][j] = Block(i,j,1)
                else:
                    self.blocks[i][j] = Block(i,j,0)

        for block in self.blocks[0]:
            block.material = 1
        for block in self.blocks[self.x-1]:
            block.material = 1
        for block in [i[0] for i in self.blocks]:
            block.material = 1
        for block in [i[self.y-1] for i in self.blocks]:
            block.material = 1

    def sculpt_dirt(self, sculpt_size, firstpasses, secondpasses):

        for i in xrange(firstpasses):
            old = copy.deepcopy(self.blocks)
            for x in xrange(self.x-2):
                for y in xrange(self.y-2):
                    R1 = 0
                    for xblock in range(3): #old[x:x+3]:
                        for yblock in range(3):#old[xblock][y:y+3]:
                            R1 += old[x+xblock][y+yblock].material #THIS WILL BREAK IF DIRT ISN'T 1 AND THE REST OF BLOCKS ARE 0
                    self.blocks[x+1][y+1].material = R1/5 #I'm being clever here but be careful

            for x in xrange(self.x-4):
                for y in xrange(self.y-4):
                    R2 = 0
                    for xblock in range(5):
                        for yblock in range(5):
                            R2 += old[x+xblock][y+yblock].material #THIS WILL BREAK IF DIRT ISN'T 1 AND THE REST OF BLOCKS ARE 0
                    if(R2 < 3):
                        self.blocks[x+2][y+2].material = 1


        for i in xrange(secondpasses):
            old = copy.deepcopy(self.blocks)
            for x in xrange(self.x-2):
                for y in xrange(self.y-2):
                    R1 = 0
                    for xblock in range(3): #old[x:x+3]:
                        for yblock in range(3):#old[xblock][y:y+3]:
                            R1 += old[x+xblock][y+yblock].material #THIS WILL BREAK IF DIRT ISN'T 1 AND THE REST OF BLOCKS ARE 0
                    self.blocks[x+1][y+1].material = R1/5 #I'm being clever here but be careful

                        
            
world = World(64,40,623245)

world.seed_dirt()

world.sculpt_dirt(1,4,2)

def display_shit(world):
    pygame.init()
    windowSurfaceObj = pygame.display.set_mode((1280,800))
    fpsClock = pygame.time.Clock()
    for i in xrange(len(world.blocks)):
        for j in xrange(len(world.blocks[i])):
            if(world.blocks[i][j].material == 1):
                #print world.blocks[i][j].x, world.blocks[i][j].y
                pygame.draw.rect(windowSurfaceObj,pygame.Color(108,67,21),((world.blocks[i][j].x*20,world.blocks[i][j].y*20),(20,20)))
            else: pygame.draw.rect(windowSurfaceObj,pygame.Color(41,27,2),((world.blocks[i][j].x*20,world.blocks[i][j].y*20),(20,20)))
            pygame.display.update()
    pygame.display.update()
    fpsClock.tick(30)
    
display_shit(world)


