from resource import *
        
class Battle():
    class Mass():
        def __init__(self, world, mass=1, angle=0, x=500, y=500, dx=0, dy=0, angle_velocity = 0, imageName='mass.png', poly=None):
            self.dx = dx; self.dy = dy #Velocity
            self.mass = mass; self.world = world #Mass, world
            self.imageName = imageName #Image, bounding box
	    self.image, self.rect = image(imageName)
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
            self.image, self.rect = image(self.imageName, None, math.floor(math.degrees(self.angle)/10)*10 )
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
        def __init__(self, data):
            Battle.Mass.__init__(self, None, imageName=os.path.join('ships',data[0].replace(' ','_')+'.png'))
            self.thrust = 0
            self.mass, self.maxThrust = [float(i) for i in data[1].split(',')]
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
        cost = None
        def __init__(self, imageName, w=1, h=1, player=None):
            self.w, self.h, self.player = w,h,player
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
    class Building(Object):
	def __init__(self, data):
            Map.Object.__init__(self, os.path.join('buildings',data[0].replace(' ','_')+'.png'), 1, 1)
	    self.once, self.eachTurn, self.eachTurnGroup, self.lost = [compile(data[i+1].replace('~','\n'), 'nofile', 'exec') for i in range(4)]
    class Pointer(): #Points to another square on the map
        cost = None
        def __init__(self, x, y):
            self.x=x; self.y=y
    
    def __init__(self, w=3, h=3):
        self.w = w; self.h = h
        Map.pixw, Map.pixh = w*Map.size, h*Map.size
	self.possibleHeroes = [Hero(data.splitlines()) for data in open('data/heroes.txt').read().split('\n\n') if not data[0].startswith('#')]
	self.possibleShips = [Battle.Ship(data.splitlines()) for data in open('data/ships.txt').read().split('\n\n') if not data[0].startswith('#')]
	self.possibleBuildings = [ Map.Building(data.splitlines()) for data in open('data/buildings.txt').read().split('\n\n') if not data[0].startswith('#')]
	self.players = [ Player(self, "Quack") ]
	self.whoseTurn = 0
	self.selectedHero = self.players[self.whoseTurn].heroes[0]
        self.randomMap()
        self.setBackground()
        self.renderImage()
    def display(self, surface, size, offset):
        surface.blit(self.image, (0,0), (offset[0],offset[1],size[0],size[1]) )
	for player in self.players:
	    for hero in player.heroes: hero.display(surface,offset)	
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
		pygame.draw.rect(self.image, (0,100,0), (x*Map.size, y*Map.size, Map.size, Map.size), 1)
                #if item.__class__ is Map.Pointer:
                #    pygame.draw.rect(self.image, (0,200,0), (x*Map.size, y*Map.size, Map.size, Map.size), 1)
                #    pygame.draw.line(self.image, (255,0,0), (x*Map.size+Map.size/2, y*Map.size+Map.size/2), (item.x*Map.size+Map.size/2, item.y*Map.size+Map.size/2), 1)
                #    pygame.draw.circle(self.image, (0,0,200), (item.x*Map.size+Map.size/2, item.y*Map.size+Map.size/2), 8)
    def randomMap(self):
        self.grid = [[Map.Empty() for y in xrange(self.h)] for x in xrange(self.w)]
        self.backtiles = [[Map.Empty() for y in xrange(self.h)] for x in xrange(self.w)]
        planets = 0; planetCount = 3
        asteroids = 0; asteroidCount = 100
        buildings = 0; buildingCount = 20
        while True:
            if planets < planetCount: object = Map.Planet(); planets+=1
            elif asteroids < asteroidCount: object = Map.Asteroid(); asteroids+=1
            elif buildings < buildingCount: object = copy.copy(random.choice(self.possibleBuildings)); buildings+=1
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
	if self.grid[x][y].cost is None or self.grid[dx][dy].cost is None: return None
        tested = set()
	untested = set((x,y))
	came_from = {}
	optimalCost = { (x,y) : 0 }
	def distance(a,b,c,d): xDif = abs(a-c); yDif = abs(b-d); larger = max(xDif,yDif); smaller = min(xDif,yDif); return smaller*2**0.5+(larger-smaller)
	approxCost = { (x,y) : distance(x,y,dx,dy) }
	approxCostThroughPoint = Map.PriorityDict(); approxCostThroughPoint[(x,y)] = approxCost[(x,y)]
	while len(approxCostThroughPoint) > 0:
	    test = approxCostThroughPoint.pop()
	    if test == (dx,dy): #Success!
		path = []
		while test != (x,y): path.append(test); test = came_from[test]
		return path
	    tested.add(test)
	    for sx in range(max(test[0]-1,0),min(test[0]+2,self.w)):
		for sy in [j for j in range(max(test[1]-1,0),min(test[1]+2,self.h)) if not ((sx,j)==test or (sx,j) in tested or self.grid[sx][j].cost==None)]:
		    tentative_cost = optimalCost[test]
		    if sx==test[0] or sy==test[1]: tentative_cost += self.grid[sx][sy].cost #Not diagonal
		    else: tentative_cost += self.grid[sx][sy].cost * 2**0.5 #Diagonal
		    isBetter = False
		    if (sx,sy) not in untested: untested.add((sx,sy)); isBetter = True
		    elif tentative_cost < optimalCost[(sx,sy)]: isBetter = True
		    if isBetter:
			came_from[(sx,sy)] = test
			optimalCost[ (sx,sy) ] = tentative_cost
			approxCost[ (sx,sy) ] = distance(sx,sy,dx,dy)
			approxCostThroughPoint[(sx,sy)] = optimalCost[(sx,sy)]+approxCost[(sx,sy)]
	return None #If no path is found	    
    class PriorityDict(dict):
	def __init__(self): self.heap = []
	def pop(self):
	    smallest = min(self,key=self.__getitem__)
	    del self[smallest]
	    return smallest
    def mouse(self, event, offset):
	x,y = (event.pos[0]+offset[0])/Map.size, (event.pos[1]+offset[1])/Map.size
	hero = self.selectedHero
	path = self.shortestPath(hero.x,hero.y, x,y)
	if path is not None:
	    cost = sum([self.grid[p[0]][p[1]].cost for p in path])
	    print_now(hero.movementPoints)
	    if hero.movementPoints >= cost:
		hero.movementPoints -= cost
		hero.x, hero.y = x,y

class Hero():
    ranks = ('Petty Officer', 'Midshipman', 'Ensign', 'Lieutenant', 'Commander', 'Captain', 'Rear Admiral', 'Vice Admiral', 'Fleet Admiral', 'Grand Admiral', 'Stevenson-Level Awesomeness')
    def __init__(self, data):
	self.name = data[0]
	self.specialty = data[1]
	self.attack, self.defense, self.knowledge, self.power, self.speed = [int(i) for i in data[2].split(',')]
        self.image, self.rect = image(os.path.join('heroes',self.name.replace(' ','_')+'.png'))
	self.x, self.y = 0,0
	self.movementPoints = self.speed
	self.fleet = { 'snub': int(data[3]) }
	self.rankNumber = 0
	self.experience = 0
    def display(self, surface, offset):
	surface.blit(self.image, (self.x*Map.size-offset[0],self.y*Map.size-offset[1]) )

class Player():
    def __init__(self, map, type):
	self.map = map
        self.money = 0
        self.energy = 0
        self.ore = 0
        self.type = type
        self.heroes = [ map.possibleHeroes.pop() ]
