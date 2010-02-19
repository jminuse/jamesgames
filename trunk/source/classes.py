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
    class Empty:
	travelCost = 1
	def action(self): pass
    class Object():
        def __init__(self, data, player=None):
            self.w, self.h, self.player = 1,1,player
            self.image, self.rect = image(os.path.join('buildings',data[0].replace(' ','_')+'.png'), (self.w*Map.size, self.h*Map.size) ) #Image, bounding box
	    self.travelCost = int(data[1])
	    if self.travelCost < 0: self.travelCost = None
            self.once, self.eachTurn, self.eachTurnGroup, self.lost = [compile(data[i+2].replace('~','\n'), 'nofile', 'exec') for i in range(4)]
	    self.testParam = 0
	def action(self): print_now(self.testParam)
    class Pointer(): #Points to another square on the map
        travelCost = None
        def __init__(self, map, x, y):
            self.x,self.y,self.map = x,y,map
	    self.action = self.map.grid[self.x][self.y].action
    
    def __init__(self, w=3, h=3):
        self.w = w; self.h = h
        Map.pixw, Map.pixh = w*Map.size, h*Map.size
        self.possibleHeroes = [Hero(self, data.splitlines()) for data in open('data/heroes.txt').read().split('\n\n') if not data[0].startswith('#')]
        self.possibleShips = [Battle.Ship(data.splitlines()) for data in open('data/ships.txt').read().split('\n\n') if not data[0].startswith('#')]
        self.possibleObjects = [ Map.Object(data.splitlines()) for data in open('data/objects.txt').read().split('\n\n') if not data[0].startswith('#')]
        self.players = [ Player(self, "Quack") ]
        self.turns, self.whoseTurn = 0,0
        self.selectedHero = self.players[self.whoseTurn].heroes[0]
        self.randomMap()
        self.setBackground()
        self.renderImage()
    def update(self,time):
        for player in self.players:
            for hero in player.heroes: hero.update(time)
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
                #pygame.draw.rect(self.image, (0,100,0), (x*Map.size, y*Map.size, Map.size, Map.size), 1)
                #if item.__class__ is Map.Pointer:
                #    pygame.draw.rect(self.image, (0,200,0), (x*Map.size, y*Map.size, Map.size, Map.size), 1)
                #    pygame.draw.line(self.image, (255,0,0), (x*Map.size+Map.size/2, y*Map.size+Map.size/2), (item.x*Map.size+Map.size/2, item.y*Map.size+Map.size/2), 1)
                #    pygame.draw.circle(self.image, (0,0,200), (item.x*Map.size+Map.size/2, item.y*Map.size+Map.size/2), 8)
    def randomMap(self):
        self.grid = [[Map.Empty() for y in xrange(self.h)] for x in xrange(self.w)]
        self.backtiles = [[Map.Empty() for y in xrange(self.h)] for x in xrange(self.w)]
	objects, objectCount = 0, 100
        while True:
            if objects < objectCount: object = copy.copy(random.choice(self.possibleObjects)); objects+=1
            else: break
            freeArea = self.randomFreeArea(object.w, object.h)
            if freeArea is None: break
            rx,ry = freeArea
            self.grid[rx][ry] = object
            for x in range(rx,min(rx+object.w,self.w)):
                for y in range(ry,min(ry+object.h,self.h)):
                    if not (x==rx and y==ry): self.grid[x][y]=Map.Pointer(self,rx,ry)
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
        if self.grid[x][y].travelCost is None or self.grid[dx][dy].travelCost is None: return None,None
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
                path = []; cost = 0
                while test != (x,y): path.append(test); cost += self.grid[test[0]][test[1]].travelCost*(1 if (test[0]==came_from[test][0] or test[1]==came_from[test][1]) else 1.41); test = came_from[test]
                path.reverse()
                return path, cost
            tested.add(test)
            for sx in range(max(test[0]-1,0),min(test[0]+2,self.w)):
                for sy in [j for j in range(max(test[1]-1,0),min(test[1]+2,self.h)) if not ((sx,j)==test or (sx,j) in tested or self.grid[sx][j].travelCost==None)]:
                    tentative_cost = optimalCost[test]
                    if sx==test[0] or sy==test[1]: tentative_cost += self.grid[sx][sy].travelCost #Not diagonal
                    else: tentative_cost += self.grid[sx][sy].travelCost * 1.41 #Diagonal
                    isBetter = False
                    if (sx,sy) not in untested: untested.add((sx,sy)); isBetter = True
                    elif tentative_cost < optimalCost[(sx,sy)]: isBetter = True
                    if isBetter:
                        came_from[(sx,sy)] = test
                        optimalCost[ (sx,sy) ] = tentative_cost
                        approxCost[ (sx,sy) ] = distance(sx,sy,dx,dy)
                        approxCostThroughPoint[(sx,sy)] = optimalCost[(sx,sy)]+approxCost[(sx,sy)]
        return None,None #If no path is found       
    class PriorityDict(dict):
        def pop(self):
            smallest = min(self,key=self.__getitem__)
            del self[smallest]
            return smallest
    def nextTurn(self):
	self.turns+=1; self.whoseTurn+=1
	if self.whoseTurn >= len(self.players): self.whoseTurn = 0
	self.selectedHero = self.players[self.whoseTurn].heroes[0]
	self.players[self.whoseTurn].nextTurn()
    def mouse(self, event, offset):
        x,y = (event.pos[0]+offset[0])/Map.size, (event.pos[1]+offset[1])/Map.size
        self.selectedHero.travel(x,y)
    def key(self, event):
	if event.key==K_SPACE: self.nextTurn()
	elif event.key==K_TAB: pass

class Hero():
    ranks = ('Petty Officer', 'Midshipman', 'Ensign', 'Lieutenant', 'Commander', 'Captain', 'Rear Admiral', 'Vice Admiral', 'Fleet Admiral', 'Grand Admiral', 'Stevenson-Level Awesomeness')
    def __init__(self, map, data):
        self.map = map
        self.name = data[0]
        self.specialty = data[1]
        self.attack, self.defense, self.knowledge, self.power, self.speed = [int(i) for i in data[2].split(',')]
	self.imageName = os.path.join('heroes',self.name.replace(' ','_')+'.png')
        self.image, self.rect = image(self.imageName)
        self.x, self.y, self.path = 0,0,None
        self.movementPoints = self.speed
        self.fleet = { 'snub': int(data[3]) }
        self.rankNumber = 0
        self.experience = 0
    def display(self, surface, offset):
        if self.path is not None:
            current, next = self.path[int(self.pathIndex)], self.path[min(int(self.pathIndex+1), len(self.path)-1)]
            x = (current[0]+cmp(next[0]-current[0],0)*self.pathIndex%1.0)*Map.size-offset[0]
            y = (current[1]+cmp(next[1]-current[1],0)*self.pathIndex%1.0)*Map.size-offset[1]
            surface.blit(self.image, (x,y))
        else: surface.blit(self.image, (self.x*Map.size-offset[0],self.y*Map.size-offset[1]) )
    def travel(self,x,y):
        if self.path is not None: return
        path,cost = self.map.shortestPath(self.x,self.y, x,y)
        if path is not None and self.movementPoints >= cost:
            self.movementPoints -= cost; self.x, self.y = x,y; self.path = path; self.pathIndex = 0.0
    angles = { (1,0):0, (1,1):45, (0,1):90, (-1,1):135, (-1,0):180, (-1,-1):225, (0,-1):270, (1,-1):315 } 
    def update(self,time):
        if self.path is not None:
	    current, next = self.path[int(self.pathIndex)], self.path[min(int(self.pathIndex+1), len(self.path)-1)]
	    if current!=next: self.image,self.rect = image(self.imageName,None,self.angles[(cmp(next[0],current[0]),-cmp(next[1],current[1]))])
            self.pathIndex += time/300.0
            if self.pathIndex >= len(self.path):
                self.map.grid[self.path[-1][0]][self.path[-1][1]].action(); self.path = None

class Player():
    def __init__(self, map, type):
        self.map = map
        self.money = 0
        self.energy = 0
        self.ore = 0
        self.type = type
        self.heroes = [ map.possibleHeroes.pop() ]
	self.mapObjects = {}
    def nextTurn(self):
	print_now('Next turn')
