import string, struct, random, copy

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
        
        for j in xrange(self.y):
            for i in xrange(self.x):
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
            for y in xrange(len(self.blocks)-2):
                for x in xrange(len(self.blocks)-2):
                    R1 = 0
                    for xblock in range(3): #old[x:x+3]:
                        for yblock in range(3):#old[xblock][y:y+3]:
                            R1 += old[x+xblock][y+yblock].material #THIS WILL BREAK IF DIRT ISN'T 1 AND THE REST OF BLOCKS ARE 0
                    self.blocks[x+1][y+1].material = R1/5 #I'm being clever here but be careful

        for i in xrange(secondpasses):
            old = copy.deepcopy(self.blocks)
            for y in xrange(self.y-4):
                for x in xrange(self.x-4):
                    R2 = 0
                    for xblock in range(5):
                        for yblock in range(5):
                            R2 += old[x+xblock][y+yblock].material #THIS WILL BREAK IF DIRT ISN'T 1 AND THE REST OF BLOCKS ARE 0
                    if(R2 < 3):
                        self.blocks[x+2][y+2].material = 1

                        
            
            

world = World(30,30,4623)

world.seed_dirt()

world.sculpt_dirt(1,4,3)

def printout(world):
    for j in range(len(world.blocks)):
        for i in range(len(world.blocks[j])):
            if(world.blocks[i][j].material == 1): print '#',
            else: print ' ',
        print '\n'

printout(world)

