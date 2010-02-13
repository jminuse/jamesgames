#!/usr/bin/env python
# James Stevenson
VERSION = "0.02"

from resource import *
from classes import *

world = Map(100,100)
world.shortestPath(1,2,3,4)

background = pygame.Surface( (world.w, world.h) ).convert()
background.fill((0,0,0))

# Display some text
text = font.render("Hello, Pygame!", True, (0,230,30))
textpos = text.get_rect()
textpos.center = background.get_rect().center
background.blit(text, textpos)

# Blit everything to the screen
screen.blit(background, (0, 0))
pygame.display.flip()
clock = pygame.time.Clock()
offset = [0,0]
activeScreen = pygame.Surface((screenSize[0],screenSize[1]-50)).convert()
activeScreenSize = activeScreen.get_size()
screen.fill((50,50,50))

# Event loop
def mainLoop():
    while True:
        time = clock.tick(40)
        if len(pygame.event.get(QUIT)): return
        for event in pygame.event.get(MOUSEBUTTONDOWN):
            pass
        pygame.event.clear() #Get only what you want, clear the rest
        
        mousex,mousey = pygame.mouse.get_pos()
        if mousex < 20 and offset[0]>0: offset[0]-=10
        elif mousex > activeScreenSize[0]-20 and offset[0]<world.w*Map.size-activeScreenSize[0]: offset[0]+=10
        if mousey < 20 and offset[1]>0: offset[1]-=10
        elif mousey > activeScreenSize[1]-20 and offset[1]<world.h*Map.size-activeScreenSize[1]>0: offset[1]+=10
        
        #world.update(time)
        world.display(activeScreen, activeScreenSize, offset)
	screen.blit(activeScreen, (0,0))
	pygame.display.flip()

mainLoop()
