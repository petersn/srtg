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

                        
            
            

world = World(60,20,623245)

world.seed_dirt()

world.sculpt_dirt(1,4,2)

def printout(world):
    for i in range(len(world.blocks[0])):
        for j in range(len(world.blocks)):
            if(world.blocks[j][i].material == 1): print '#',
            else: print ' ',
        print '\n'

printout(world)

