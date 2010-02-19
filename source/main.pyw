#!/usr/bin/env python
# James Stevenson
VERSION = "0.03"

from resource import *
from classes import *

random.seed(2)
world = Map(50,50)
storedWorld = None
import time
startTime = time.clock()
for i in range(0):
    startx, starty, endx, endy = 1,7,random.randint(0,49),random.randint(0,49)
    #pygame.draw.line(world.image, (0,0,255), (startx*Map.size,starty*Map.size), (endx*Map.size,endy*Map.size) )
    path = []
    path = world.shortestPath(startx, starty, endx, endy)
    if path is not None:
	for i in range(len(path)-1):
	    x,y,dx,dy = path[i][0],path[i][1],path[i+1][0],path[i+1][1]
	    pygame.draw.line(world.image, (0,2*i,255-2*i), (x*Map.size+Map.size/2,y*Map.size+Map.size/2), (dx*Map.size+Map.size/2,dy*Map.size+Map.size/2) )

clock = pygame.time.Clock()
offset = [0,0]
activeScreen = pygame.Surface((screenSize[0],screenSize[1]-50)).convert()
activeScreenSize = activeScreen.get_size()
screen.fill((50,50,50))

# Event loop
def mainLoop():
    while True:
        time = clock.tick(40)
	if not pygame.mouse.get_focused(): time = 0
        if len(pygame.event.get(QUIT)): return
        for event in pygame.event.get(MOUSEBUTTONDOWN):
	    if event.button==4 and offset[1]>30: offset[1]-=30 #Scroll up
	    elif event.button==5 and offset[1]<world.h*Map.size-activeScreenSize[1]-30: offset[1]+=30 #Scroll down
            elif event.button==1: world.mouse(event,offset) #Left click
        pygame.event.clear() #Get only what you want, clear the rest
        
        mousex,mousey = pygame.mouse.get_pos()
        if mousex < 20 and offset[0]>10: offset[0]-=10
        elif mousex > activeScreenSize[0]-20 and offset[0]<world.w*Map.size-activeScreenSize[0]-10: offset[0]+=10
        if mousey < 20 and offset[1]>10: offset[1]-=10
        elif mousey > activeScreenSize[1]-20 and offset[1]<world.h*Map.size-activeScreenSize[1]-10: offset[1]+=10
        
        #world.update(time)
	world.update(time)
        world.display(activeScreen, activeScreenSize, offset)
	screen.blit(activeScreen, (0,0))
	pygame.display.flip()

mainLoop()
