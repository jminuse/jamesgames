from resource import *
        
class Battle():
    class Mass():
        def __init__(self, world, mass=1, angle=0, x=500, y=500, dx=0, dy=0, angle_velocity = 0, imageName='mass.png', poly=None):
            self.dx = dx; self.dy = dy #Velocity
            self.mass = mass; self.world = world #Mass, world
            self.original_image, self.rect = image(imageName) #Image, bounding box
            self.x = x; self.y = y
            if poly is None:
                poly = ( (-self.rect.centerx, self.rect.centery), (-self.rect.centerx, -self.rect.centery),
                    (self.rect.centerx, -self.rect.centery), (self.rect.centerx, self.rect.centery) )
            self.rotations = [ [ (math.cos(a)*p[0]-math.sin(a)*p[1], math.sin(a)*p[0]+math.cos(a)*p[1]) for p in poly] for a in range(100) ]
            self.angle = 0; self.rotate(angle)
            self.angle_velocity = angle_velocity
        def update(self, time):
            self.x += self.dx*time; self.y += self.dy*time; self.rotate(self.angle_velocity*time)
            if self.x > self.world.w: self.x = self.world.w; self.dx *= -1
            elif self.x < 0: self.x = 0; self.dx *= -1
            if self.y > self.world.h: self.y = self.world.h; self.dy *= -1
            elif self.y < 0: self.y = 0; self.dy *= -1
        def rotate(self, angle):
            self.angle += angle
            while self.angle<0: self.angle+=2*math.pi
            while self.angle>2*math.pi: self.angle-=2*math.pi
            self.poly = self.rotations[ int(len(self.rotations)*self.angle/(2*math.pi)) ]
            self.image = pygame.transform.rotozoom(self.original_image, math.degrees(self.angle), 1).convert_alpha()
            self.rect = self.image.get_rect()
        def display(self, surface, offset=(0,0)):
            surface.blit(self.image, (self.x-self.rect.centerx-offset[0], self.y-self.rect.centery-offset[1]) )
        def contacts(self, x, y):
            j = len(self.poly)-1; within = False
            for i in range(len(self.poly)):
                within ^= ( ((self.poly[i][1]>y) != (self.poly[j][1]>y)) and (x < (self.poly[j][0]-self.poly[i][0])
                    * (y-self.poly[i][1]) / (self.poly[j][1]-self.poly[i][1]) + self.poly[i][0]) ); j = i
            return within
        def collides(self,other):
            return False
            
    class Ship(Mass):
        def __init__(self, world):
            Mass.__init__(self, world, imageName='ship.png')
            self.thrust = 0
            self.maxThrust = 1
        def update(self, time):
            Mass.update(self, time)
    
    class SpaceRock(Mass):
        def __init__(self):
            Mass.__init__(self)
        def update(self, time):
            Mass.update(self, time)
        
    def __init__(self, w=1000, h=1000):
        self.w = w; self.h = h
        self.ships = []; self.planetoids = []; self.players = []
        for i in range(50):
            self.ships.append(Ship(self))
            self.ships[-1].dx = math.sin(i)/10
            self.ships[-1].dy = math.cos(i)/10
            self.ships[-1].angle_velocity = 0.001
    def update(self, time):
        for ship in self.ships:
            ship.update(time)
    def display(self, surface, size, background, offset):
        surface.blit(background, (0,0), (offset[0],offset[1],size[0],size[1]) )
        for ship in self.ships: ship.display(surface, offset)

class Map():
    size = 32 #size of a grid square
    class Empty: cost = 1
    class Object():
        cost = 1e6
        def __init__(self, imageName, w=1, h=1):
            self.w, self.h = w,h
            self.image, self.rect = image(imageName, (w*Map.size, h*Map.size) ) #Image, bounding box
    class AsteroidField(Object):
        cost = 2
        def __init__(self, imageName='asteroid_tile.png'): Map.Object.__init__(self, imageName, 1, 1)
    class RadiationZone(Object):
        cost = 1
        def __init__(self, imageName='radiation_tile.png'): Map.Object.__init__(self, imageName, 1, 1)
    class Planet(Object):
        def __init__(self, imageName='planet1.png'):
            Map.Object.__init__(self, imageName, 6, 6)
    class Asteroid(Object):
        def __init__(self, imageName='asteroid1.png'):
            Map.Object.__init__(self, imageName, 2, 1)
    class Factory(Object):
        def __init__(self, imageName='ship6.png'):
            Map.Object.__init__(self, imageName, 1, 1)
    class Colony(Object):
        pass
    class Pointer(): #Points to another square on the map
        cost = 1e6
        def __init__(self, x, y):
            self.x=x; self.y=y
    
    def __init__(self, w=3, h=3):
        self.w = w; self.h = h
        Map.pixw, Map.pixh = w*Map.size, h*Map.size
        self.heroes = []
        self.possibleHeroes = []
        self.randomMap()
        self.setBackground()
        self.renderImage()
    def display(self, surface, size, offset):
        surface.blit(self.image, (0,0), (offset[0],offset[1],size[0],size[1]) )
    def setBackground(self):
        self.background = pygame.Surface((Map.pixw,Map.pixh)).convert()
        self.background.fill((5,0,10))
        for i in xrange(Map.pixw*Map.pixh/100):
            self.background.fill((255,255,255), (random.randint(0,Map.pixw),random.randint(0,Map.pixh),1,1))
    def renderImage(self):
        self.image = pygame.Surface((Map.pixw,Map.pixh)).convert()
        self.image.blit(self.background, (0,0))
        for x,list in enumerate(self.backtiles):
            for y,item in enumerate(list):
                if item.__class__ is not Map.Empty:
                    self.image.blit(item.image, (x*Map.size, y*Map.size))
        for x,list in enumerate(self.grid):
            for y,item in enumerate(list):
                if item.__class__ is not Map.Empty and item.__class__ is not Map.Pointer:
                    self.image.blit(item.image, (x*Map.size, y*Map.size))
                #if item.__class__ is Map.Pointer:
                #    pygame.draw.rect(self.image, (0,200,0), (x*Map.size, y*Map.size, Map.size, Map.size), 1)
                #    pygame.draw.line(self.image, (255,0,0), (x*Map.size+Map.size/2, y*Map.size+Map.size/2), (item.x*Map.size+Map.size/2, item.y*Map.size+Map.size/2), 1)
                #    pygame.draw.circle(self.image, (0,0,200), (item.x*Map.size+Map.size/2, item.y*Map.size+Map.size/2), 8)
    def randomMap(self):
        self.grid = [[Map.Empty() for y in xrange(self.h)] for x in xrange(self.w)]
        self.backtiles = [[Map.Empty() for y in xrange(self.h)] for x in xrange(self.w)]
        planets = 0; planetCount = 10
        asteroids = 0; asteroidCount = 400
        factories = 0; factoryCount = 100
        while True:
            if planets < planetCount: object = Map.Planet(); planets+=1
            elif asteroids < asteroidCount: object = Map.Asteroid(); asteroids+=1
            elif factories < factoryCount: object = Map.Factory(); factories+=1
            else: break
            freeArea = self.randomFreeArea(object.w, object.h)
            if freeArea is None: break
            rx,ry = freeArea
            self.grid[rx][ry] = object
            for x in range(rx,min(rx+object.w,self.w)):
                for y in range(ry,min(ry+object.h,self.h)):
                    if not (x==rx and y==ry): self.grid[x][y]=Map.Pointer(rx,ry)
    def randomFreeArea(self, width, height):
        for i in xrange(100):
            rx = random.randint(0,self.w-1); ry = random.randint(0,self.h-1)
            if rx+width>=self.w or ry+height>=self.h: continue
            areaFree = True
            for x in range(rx,rx+width):
                for y in range(ry,ry+height):
                    if self.grid[x][y].__class__ is not Map.Empty: areaFree = False
            if areaFree: return rx,ry
    def shortestPath(self,x,y,dx,dy):
        cost = 0
	untested = Map.PriorityDict()
	distances = {}
	"""
	queue.put((0,x,y))
	while not queue.empty():
	    next = queue.get()
	    if next[1]==dx and next[2]==dy: break #Finished!
	    for sx in range(max(next[1]-1,0),min(next[1]+2,self.w)):
		for sy in [j for j in range(max(next[2]-1,0),min(next[2]+2,self.h)) if not (sx==next[1] and j==next[2])]:
		    newCost = grid[sx][sy].cost
		    if (sx,sy) not in queue or vwLength < Q[w]:
			Q[w] = vwLength
			P[w] = v"""
    class PriorityDict():
	def __init__(self): self.heap = []; self.dict = {}
	def push(self, item, priority): heapq.heappush(self.heap, (priority, item)); self.dict[item] = priority
	def pop(self): priority,item = heapq.heappop(self.heap); self.dict.pop(item); return item,priority
	def get(self, item): return self.dict[item]
    
class Hero():
    def __init__(self, imageName):
        self.image, self.rect = image(imageName) #Image, bounding box

class Player():
    def __init__(self, type):
        self.money = 0
        self.energy = 0
        self.ore = 0
        self.type = type
        self.heroes = []
